"""Stage 1: Resume Parsing implementation."""

import streamlit as st
import tempfile
from pathlib import Path
import logging

from resume_optimizer.core.resume_parser import SpacyResumeParser, GeminiResumeParser, OllamaResumeParser
from resume_optimizer.core.ai_integration.gemini_client import GeminiClient
from resume_optimizer.core.ai_integration.ollama_client import OllamaClient
from resume_optimizer.streamlit_ui.components.editors import render_resume_data_editor
from resume_optimizer.streamlit_ui.components.validators import render_validation_results
from resume_optimizer.streamlit_ui.components.common import render_navigation_buttons
from resume_optimizer.streamlit_ui.state.validators import validate_resume_data
from resume_optimizer.streamlit_ui.state.session_manager import SessionStateManager
from resume_optimizer.streamlit_ui.utils import (
    get_gemini_api_key,
    has_gemini_api_key,
    is_ollama_available,
    get_ollama_models,
    get_default_ollama_model
)


logger = logging.getLogger(__name__)


def render_stage1_resume_parsing() -> None:
    """Render Stage 1: Resume Parsing."""
    from resume_optimizer.streamlit_ui.utils.storage import BrowserStorage

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

    # Show if resume is already loaded
    if st.session_state.resume_data_edited is not None:
        st.success("✅ Resume already loaded! You can edit it below or upload a new one.")

        col_info, col_action = st.columns([3, 1])
        with col_info:
            st.info(f"📋 Current resume: {st.session_state.get('uploaded_file_name', 'Previously parsed resume')}")
        with col_action:
            if st.button("🔄 Parse New Resume", use_container_width=True):
                # Clear current resume data to allow new upload
                st.session_state.resume_data_raw = None
                st.session_state.resume_data_edited = None
                st.session_state.uploaded_file_path = None
                st.session_state.uploaded_file_name = None
                st.rerun()

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
        st.session_state.uploaded_file_name = uploaded_file.name
        st.success("✅ Resume uploaded successfully!")

    st.divider()

    # Parser selection
    st.subheader("🔧 Parser Selection")
    parser_options = ["spacy"]
    parser_labels = {}
    parser_labels["spacy"] = "Spacy Parser (Fast, Offline)"

    # Check for Ollama availability
    ollama_available = is_ollama_available()
    if ollama_available:
        parser_options.insert(0, "ollama")  # Make Ollama the default/first option
        ollama_models = get_ollama_models()
        default_model = get_default_ollama_model()
        model_info = f" - {default_model}" if default_model else ""
        parser_labels["ollama"] = f"Ollama Parser (Local AI{model_info}) - Recommended"
    else:
        parser_labels["ollama"] = "Ollama Parser (not running)"

    # Check for Gemini availability
    if has_gemini_api_key():
        parser_options.append("gemini")
        parser_labels["gemini"] = "Gemini Parser (Cloud AI)"
    else:
        parser_labels["gemini"] = "Gemini Parser (requires API key)"

    st.session_state.parser_choice = st.radio(
        "Choose parser type",
        parser_options,
        format_func=lambda x: parser_labels.get(x, x),
        key="stage1_parser_choice",
        help="Ollama uses local Llama 3.1 for best results. Spacy is fast but basic. Gemini requires API key."
    )

    # Show Ollama model selector if Ollama is selected and available
    if st.session_state.parser_choice == "ollama" and ollama_available:
        ollama_models = get_ollama_models()
        if ollama_models:
            default_idx = 0
            for i, model in enumerate(ollama_models):
                if 'llama3.1' in model.lower():
                    default_idx = i
                    break

            st.session_state.ollama_model = st.selectbox(
                "Select Ollama Model",
                ollama_models,
                index=default_idx,
                key="stage1_ollama_model",
                help="Llama 3.1 8B is recommended for resume parsing"
            )
    elif st.session_state.parser_choice == "ollama" and not ollama_available:
        st.warning("⚠️ Ollama is not running. Start Ollama with: `ollama serve`")
        st.info("Then pull a model: `ollama pull llama3.1:8b`")

    st.divider()

    # Parse button
    if st.session_state.uploaded_file_path:
        if st.button("📖 Parse Resume", type="primary", width='stretch'):
            with st.spinner("Parsing resume..."):
                try:
                    file_path = Path(st.session_state.uploaded_file_path)

                    if st.session_state.parser_choice == "ollama":
                        # Ollama parser with local LLM
                        if not is_ollama_available():
                            st.error("❌ Ollama is not running")
                            st.info("Start Ollama with: `ollama serve`")
                            st.stop()

                        model = getattr(st.session_state, 'ollama_model', 'llama3.1:8b')
                        ollama_client = OllamaClient(model=model)
                        parser = OllamaResumeParser(ollama_client=ollama_client)
                        st.info(f"Using Ollama with model: {model}")

                    elif st.session_state.parser_choice == "gemini":
                        # Gemini parser with API key from .env
                        api_key = get_gemini_api_key()
                        if not api_key:
                            st.error("❌ Gemini API key not found in .env file")
                            st.info("Please add GOOGLE_API_KEY to your .env file or select a different parser.")
                            st.stop()

                        gemini_client = GeminiClient(api_key=api_key)
                        parser = GeminiResumeParser(gemini_client=gemini_client)

                    else:
                        # Default to Spacy parser
                        parser = SpacyResumeParser()

                    resume_data = parser.parse(file_path)
                    st.session_state.resume_data_raw = resume_data
                    st.session_state.resume_data_edited = resume_data.model_copy(deep=True)

                    st.success("✅ Resume parsed successfully!")
                    st.session_state.stage_status[0] = 'completed'

                    # Auto-save to browser storage
                    from resume_optimizer.streamlit_ui.utils.storage import BrowserStorage
                    BrowserStorage.auto_save()

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
        if st.button("✅ Confirm and Continue", type="primary", width='stretch', disabled=not is_valid):
            st.session_state.stage1_confirmed = True
            # Don't mark as edited during confirmation - only when actually edited later
            st.session_state.current_stage = 1
            st.rerun()

    # Back button
    st.divider()
    if st.button("⬅️ Back", width='stretch', disabled=True):
        pass
