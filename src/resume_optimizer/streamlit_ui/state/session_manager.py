"""Session state management for the application."""

import streamlit as st
import uuid
from typing import Dict, Any


class SessionStateManager:
    """Manages Streamlit session state initialization and reset."""

    @staticmethod
    def initialize() -> None:
        """Initialize all session state variables with defaults."""
        # Core workflow control
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())

        if 'current_stage' not in st.session_state:
            st.session_state.current_stage = 0

        if 'stage_status' not in st.session_state:
            st.session_state.stage_status = {0: 'pending', 1: 'pending', 2: 'pending', 3: 'pending'}

        # Stage 1: Resume Parsing
        if 'uploaded_file_path' not in st.session_state:
            st.session_state.uploaded_file_path = None

        if 'uploaded_file_name' not in st.session_state:
            st.session_state.uploaded_file_name = None

        if 'parser_choice' not in st.session_state:
            st.session_state.parser_choice = 'spacy'

        if 'applicant_name' not in st.session_state:
            st.session_state.applicant_name = 'Ashish Surve'

        if 'company_name' not in st.session_state:
            st.session_state.company_name = ''

        if 'resume_data_raw' not in st.session_state:
            st.session_state.resume_data_raw = None

        if 'resume_data_edited' not in st.session_state:
            st.session_state.resume_data_edited = None

        if 'stage1_confirmed' not in st.session_state:
            st.session_state.stage1_confirmed = False

        # Auto-save tracking
        if 'last_auto_save' not in st.session_state:
            st.session_state.last_auto_save = None

        # Stage 2: Job Analysis
        if 'job_description_text' not in st.session_state:
            st.session_state.job_description_text = ''

        if 'analyzer_choice' not in st.session_state:
            st.session_state.analyzer_choice = 'standard'

        if 'job_data_raw' not in st.session_state:
            st.session_state.job_data_raw = None

        if 'job_data_edited' not in st.session_state:
            st.session_state.job_data_edited = None

        if 'stage2_confirmed' not in st.session_state:
            st.session_state.stage2_confirmed = False

        # Stage 3: ATS Optimization
        if 'optimization_result_raw' not in st.session_state:
            st.session_state.optimization_result_raw = None

        if 'optimization_result_edited' not in st.session_state:
            st.session_state.optimization_result_edited = None

        if 'stage3_confirmed' not in st.session_state:
            st.session_state.stage3_confirmed = False

        # Stage 4: PDF Generation
        if 'pdf_path' not in st.session_state:
            st.session_state.pdf_path = None

        # Generated files tracking
        if 'generated_files' not in st.session_state:
            st.session_state.generated_files = {}

        # Tracking flags for edits
        if 'resume_edited_after_confirmation' not in st.session_state:
            st.session_state.resume_edited_after_confirmation = False

        if 'job_edited_after_confirmation' not in st.session_state:
            st.session_state.job_edited_after_confirmation = False

        # Stage 4 edit tracking
        if 'resume_edited_after_stage4' not in st.session_state:
            st.session_state.resume_edited_after_stage4 = False

    @staticmethod
    def reset_session() -> None:
        """Reset all session state for a new workflow."""
        keys_to_keep = {'session_id'}
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]
        SessionStateManager.initialize()

    @staticmethod
    def mark_resume_edited() -> None:
        """Mark that resume data was edited."""
        if st.session_state.stage1_confirmed:
            st.session_state.resume_edited_after_confirmation = True

    @staticmethod
    def mark_job_edited() -> None:
        """Mark that job data was edited."""
        if st.session_state.stage2_confirmed:
            st.session_state.job_edited_after_confirmation = True
