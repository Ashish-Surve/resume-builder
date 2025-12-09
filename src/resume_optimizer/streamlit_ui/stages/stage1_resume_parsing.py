"""Stage 1: Resume Parsing implementation."""

import streamlit as st
import tempfile
from pathlib import Path
import logging

from resume_optimizer.core.resume_parser import SpacyResumeParser, GeminiResumeParser
from resume_optimizer.core.ai_integration.gemini_client import GeminiClient
from resume_optimizer.streamlit_ui.components.editors import render_resume_data_editor
from resume_optimizer.streamlit_ui.components.validators import render_validation_results
from resume_optimizer.streamlit_ui.components.common import render_navigation_buttons
from resume_optimizer.streamlit_ui.state.validators import validate_resume_data
from resume_optimizer.streamlit_ui.state.session_manager import SessionStateManager
from resume_optimizer.streamlit_ui.utils import get_gemini_api_key, has_gemini_api_key


logger = logging.getLogger(__name__)


def render_stage1_resume_parsing() -> None:
    """Render Stage 1: Resume Parsing."""
    st.header("Stage 1: Resume Parsing")
    st.markdown("Upload your resume and review the parsed information")

    col1, col2 = st.columns(2)

    # Applicant name
    with col1:
        st.subheader("👤 Applicant Information")
        st.session_state.applicant_name = st.text_input(
            "Your Full Name",
            value=st.session_state.applicant_name,
            key="stage1_applicant_name"
        )

    # Target company
    with col2:
        st.subheader("🏢 Target Company")
        st.session_state.company_name = st.text_input(
            "Target Company Name",
            value=st.session_state.company_name,
            key="stage1_company_name"
        )

    st.divider()

    # Resume upload
    st.subheader("📄 Resume Upload")
    uploaded_file = st.file_uploader(
        "Choose your resume file",
        type=['pdf', 'docx', 'txt'],
        help="Upload your resume in PDF, DOCX, or TXT format"
    )

    if uploaded_file is not None:
        # Save uploaded file temporarily
        temp_dir = Path(tempfile.gettempdir()) / "resume_optimizer" / st.session_state.session_id
        temp_dir.mkdir(parents=True, exist_ok=True)
        file_path = temp_dir / uploaded_file.name

        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        st.session_state.uploaded_file_path = str(file_path)
        st.success("✅ Resume uploaded successfully!")

    st.divider()

    # Parser selection
    st.subheader("🔧 Parser Selection")
    parser_options = ["spacy"]
    parser_labels = {}
    parser_labels["spacy"] = "Spacy Parser"

    if has_gemini_api_key():
        parser_options.append("gemini")
        parser_labels["gemini"] = "Gemini Parser (AI-powered)"
    else:
        parser_labels["gemini"] = "Gemini Parser (requires API key)"

    st.session_state.parser_choice = st.radio(
        "Choose parser type",
        parser_options,
        format_func=lambda x: parser_labels[x],
        key="stage1_parser_choice",
        help="Spacy is fast and works offline. Gemini provides AI-powered parsing (requires API key in .env)."
    )

    st.divider()

    # Parse button
    if st.session_state.uploaded_file_path:
        if st.button("📖 Parse Resume", type="primary", use_container_width=True):
            with st.spinner("Parsing resume..."):
                try:
                    file_path = Path(st.session_state.uploaded_file_path)

                    if st.session_state.parser_choice == "spacy":
                        parser = SpacyResumeParser()
                    else:
                        # Gemini parser with API key from .env
                        api_key = get_gemini_api_key()
                        if not api_key:
                            st.error("❌ Gemini API key not found in .env file")
                            st.info("Please add GOOGLE_API_KEY to your .env file or select Spacy Parser instead.")
                            st.stop()

                        gemini_client = GeminiClient(api_key=api_key)
                        parser = GeminiResumeParser(gemini_client=gemini_client)

                    resume_data = parser.parse(file_path)
                    st.session_state.resume_data_raw = resume_data
                    st.session_state.resume_data_edited = resume_data.model_copy(deep=True)

                    st.success("✅ Resume parsed successfully!")
                    st.session_state.stage_status[0] = 'completed'

                except Exception as e:
                    logger.error(f"Parsing error: {e}")
                    st.error(f"Error parsing resume: {e}")
                    st.info("Try manually editing the resume data below or try a different parser.")
    else:
        st.info("👆 Upload a resume file first")

    st.divider()

    # Resume data editor
    if st.session_state.resume_data_edited:
        st.subheader("✏️ Edit Resume Data")
        st.session_state.resume_data_edited = render_resume_data_editor(st.session_state.resume_data_edited)

        st.divider()

        # Validation
        st.subheader("✔️ Validation")
        is_valid, errors = validate_resume_data(st.session_state.resume_data_edited)
        render_validation_results(is_valid, errors)

        st.divider()

        # Confirm button
        if st.button("✅ Confirm and Continue", type="primary", use_container_width=True, disabled=not is_valid):
            st.session_state.stage1_confirmed = True
            SessionStateManager.mark_resume_edited()
            st.session_state.current_stage = 1
            st.rerun()

    # Back button
    st.divider()
    if st.button("⬅️ Back", use_container_width=True, disabled=True):
        pass
