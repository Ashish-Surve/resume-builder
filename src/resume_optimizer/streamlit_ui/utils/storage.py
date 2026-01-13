"""Browser-based storage utilities for persisting resume data across sessions."""

import streamlit as st
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BrowserStorage:
    """Handles browser-based session storage for resume data persistence."""

    # Storage keys
    RESUME_LIST_KEY = "resume_optimizer_resumes"
    CURRENT_RESUME_KEY = "resume_optimizer_current"

    @staticmethod
    def _init_storage():
        """Initialize browser storage if not already done."""
        if 'browser_storage_initialized' not in st.session_state:
            st.session_state.browser_storage_initialized = True

            # Initialize resume storage list
            if BrowserStorage.RESUME_LIST_KEY not in st.session_state:
                st.session_state[BrowserStorage.RESUME_LIST_KEY] = []

            # Initialize current resume ID
            if BrowserStorage.CURRENT_RESUME_KEY not in st.session_state:
                st.session_state[BrowserStorage.CURRENT_RESUME_KEY] = None

    @staticmethod
    def save_resume_data(
        resume_data_raw: Any,
        resume_data_edited: Any,
        applicant_name: str,
        company_name: str,
        file_name: str = None
    ) -> str:
        """Save resume data to browser storage.

        Args:
            resume_data_raw: Raw parsed resume data
            resume_data_edited: Edited resume data
            applicant_name: Name of the applicant
            company_name: Target company name
            file_name: Original file name

        Returns:
            Resume ID
        """
        BrowserStorage._init_storage()

        # Generate resume ID
        resume_id = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create resume entry
        resume_entry = {
            'id': resume_id,
            'applicant_name': applicant_name,
            'company_name': company_name,
            'file_name': file_name,
            'timestamp': datetime.now().isoformat(),
            'resume_data_raw': resume_data_raw,
            'resume_data_edited': resume_data_edited,
        }

        # Add to storage
        resume_list = st.session_state[BrowserStorage.RESUME_LIST_KEY]

        # Check if this resume already exists (update instead of create)
        existing_idx = None
        current_id = st.session_state.get(BrowserStorage.CURRENT_RESUME_KEY)

        if current_id:
            for idx, resume in enumerate(resume_list):
                if resume['id'] == current_id:
                    existing_idx = idx
                    resume_id = current_id  # Keep same ID
                    resume_entry['id'] = current_id
                    resume_entry['timestamp'] = datetime.now().isoformat()
                    break

        if existing_idx is not None:
            resume_list[existing_idx] = resume_entry
        else:
            resume_list.append(resume_entry)

        st.session_state[BrowserStorage.RESUME_LIST_KEY] = resume_list
        st.session_state[BrowserStorage.CURRENT_RESUME_KEY] = resume_id

        logger.info(f"Saved resume data for {applicant_name} (ID: {resume_id})")
        return resume_id

    @staticmethod
    def load_resume_data(resume_id: str) -> Optional[Dict[str, Any]]:
        """Load resume data from browser storage.

        Args:
            resume_id: ID of the resume to load

        Returns:
            Resume data dict or None if not found
        """
        BrowserStorage._init_storage()

        resume_list = st.session_state.get(BrowserStorage.RESUME_LIST_KEY, [])

        for resume in resume_list:
            if resume['id'] == resume_id:
                logger.info(f"Loaded resume data (ID: {resume_id})")
                return resume

        logger.warning(f"Resume not found (ID: {resume_id})")
        return None

    @staticmethod
    def get_resume_list() -> List[Dict[str, Any]]:
        """Get list of all saved resumes.

        Returns:
            List of resume metadata dicts
        """
        BrowserStorage._init_storage()

        resume_list = st.session_state.get(BrowserStorage.RESUME_LIST_KEY, [])

        # Return metadata only (not full resume data)
        return [
            {
                'id': r['id'],
                'applicant_name': r['applicant_name'],
                'company_name': r['company_name'],
                'file_name': r.get('file_name', 'Unknown'),
                'timestamp': r['timestamp']
            }
            for r in resume_list
        ]

    @staticmethod
    def delete_resume(resume_id: str) -> bool:
        """Delete a resume from storage.

        Args:
            resume_id: ID of resume to delete

        Returns:
            True if deleted, False if not found
        """
        BrowserStorage._init_storage()

        resume_list = st.session_state.get(BrowserStorage.RESUME_LIST_KEY, [])

        for idx, resume in enumerate(resume_list):
            if resume['id'] == resume_id:
                resume_list.pop(idx)
                st.session_state[BrowserStorage.RESUME_LIST_KEY] = resume_list

                # Clear current if it was deleted
                if st.session_state.get(BrowserStorage.CURRENT_RESUME_KEY) == resume_id:
                    st.session_state[BrowserStorage.CURRENT_RESUME_KEY] = None

                logger.info(f"Deleted resume (ID: {resume_id})")
                return True

        return False

    @staticmethod
    def get_current_resume_id() -> Optional[str]:
        """Get the ID of the currently active resume.

        Returns:
            Current resume ID or None
        """
        BrowserStorage._init_storage()
        return st.session_state.get(BrowserStorage.CURRENT_RESUME_KEY)

    @staticmethod
    def set_current_resume(resume_id: str):
        """Set the currently active resume.

        Args:
            resume_id: ID of resume to make active
        """
        BrowserStorage._init_storage()
        st.session_state[BrowserStorage.CURRENT_RESUME_KEY] = resume_id
        logger.info(f"Set current resume to {resume_id}")

    @staticmethod
    def auto_save():
        """Auto-save current resume data from session state."""
        if st.session_state.get('resume_data_edited') is None:
            return  # Nothing to save

        try:
            BrowserStorage.save_resume_data(
                resume_data_raw=st.session_state.get('resume_data_raw'),
                resume_data_edited=st.session_state.get('resume_data_edited'),
                applicant_name=st.session_state.get('applicant_name', 'Unknown'),
                company_name=st.session_state.get('company_name', ''),
                file_name=st.session_state.get('uploaded_file_name', None)
            )
            st.session_state['last_auto_save'] = datetime.now()
        except Exception as e:
            logger.error(f"Auto-save failed: {e}")


class ProgressTracker:
    """Track and calculate progress across workflow stages."""

    @staticmethod
    def calculate_progress() -> float:
        """Calculate overall progress percentage.

        Returns:
            Progress as percentage (0-100)
        """
        stage_weights = {
            0: 25,  # Resume Parsing
            1: 25,  # Job Analysis
            2: 30,  # ATS Optimization
            3: 20   # PDF Generation
        }

        total_progress = 0
        stage_status = st.session_state.get('stage_status', {})

        for stage_num, weight in stage_weights.items():
            status = stage_status.get(stage_num, 'pending')
            if status == 'completed':
                total_progress += weight

        # Add partial credit for current stage
        current_stage = st.session_state.get('current_stage', 0)
        if current_stage > 0 and stage_status.get(current_stage) != 'completed':
            # Give 50% credit for being on the stage
            total_progress += stage_weights.get(current_stage, 0) * 0.5

        return min(100, total_progress)

    @staticmethod
    def is_stage_accessible(stage_num: int) -> bool:
        """Check if a stage is accessible for navigation.

        Args:
            stage_num: Stage number to check

        Returns:
            True if stage can be accessed
        """
        # Stage 0 (Resume Parsing) is always accessible
        if stage_num == 0:
            return True

        # Stage 1 (Job Analysis) requires resume data
        if stage_num == 1:
            return st.session_state.get('resume_data_edited') is not None

        # Stage 2 (Optimization) requires both resume and job data
        if stage_num == 2:
            return (
                st.session_state.get('resume_data_edited') is not None and
                st.session_state.get('job_data_edited') is not None
            )

        # Stage 3 (PDF Generation) requires optimization results
        if stage_num == 3:
            return st.session_state.get('optimization_result_edited') is not None

        return False

    @staticmethod
    def get_stage_accessibility_message(stage_num: int) -> Optional[str]:
        """Get a message explaining why a stage is not accessible.

        Args:
            stage_num: Stage number to check

        Returns:
            Warning message or None if accessible
        """
        if ProgressTracker.is_stage_accessible(stage_num):
            return None

        messages = {
            1: "Complete Stage 1: Resume Parsing first",
            2: "Complete Stage 1 (Resume) and Stage 2 (Job Analysis) first",
            3: "Complete Stage 3: ATS Optimization first"
        }

        return messages.get(stage_num, "Previous stages required")
