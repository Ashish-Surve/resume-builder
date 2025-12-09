# src/resume_optimizer/streamlit_ui/app.py
"""
Main Streamlit application for Resume Optimizer.
4-stage workflow: Parse → Analyze → Optimize → Download
"""

import streamlit as st

# Configure page FIRST - before any other imports or st commands
st.set_page_config(
    page_title="AI Resume Optimizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

import logging

from resume_optimizer.streamlit_ui.state.session_manager import SessionStateManager
from resume_optimizer.streamlit_ui.components.common import render_header
from resume_optimizer.streamlit_ui.components.progress import render_progress_sidebar
from resume_optimizer.streamlit_ui.stages.stage1_resume_parsing import render_stage1_resume_parsing
from resume_optimizer.streamlit_ui.stages.stage2_job_analysis import render_stage2_job_analysis
from resume_optimizer.streamlit_ui.stages.stage3_ats_optimization import render_stage3_ats_optimization
from resume_optimizer.streamlit_ui.stages.stage4_pdf_generation import render_stage4_pdf_generation


class ResumeOptimizerApp:
    """Main application orchestrator for 4-stage workflow."""

    def __init__(self):
        """Initialize the application."""
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        SessionStateManager.initialize()

    def setup_logging(self) -> None:
        """Configure logging for the application."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def run(self) -> None:
        """Main application entry point."""
        try:
            # Render header
            render_header()

            # Render progress sidebar
            render_progress_sidebar(st.session_state.current_stage, st.session_state.stage_status)

            # Main content area
            st.divider()

            # Route to appropriate stage
            if st.session_state.current_stage == 0:
                render_stage1_resume_parsing()
            elif st.session_state.current_stage == 1:
                render_stage2_job_analysis()
            elif st.session_state.current_stage == 2:
                render_stage3_ats_optimization()
            elif st.session_state.current_stage == 3:
                render_stage4_pdf_generation()
            else:
                st.error(f"Unknown stage: {st.session_state.current_stage}")

        except Exception as e:
            self.logger.error(f"Application error: {e}")
            st.error(f"An error occurred: {e}")


def main():
    """Application entry point."""
    try:
        app = ResumeOptimizerApp()
        app.run()
    except Exception as e:
        st.error(f"Application failed to start: {e}")
        logging.error(f"Application startup error: {e}")


if __name__ == "__main__":
    main()
