"""Stage 2: Job Analysis implementation."""

import streamlit as st
import logging

from resume_optimizer.core.job_analyzer import JobDescriptionAnalyzer, GeminiJobAnalyzer
from resume_optimizer.streamlit_ui.components.editors import render_job_data_editor
from resume_optimizer.streamlit_ui.components.validators import render_validation_results
from resume_optimizer.streamlit_ui.state.validators import validate_job_data
from resume_optimizer.streamlit_ui.state.session_manager import SessionStateManager
from resume_optimizer.streamlit_ui.utils import get_gemini_api_key, has_gemini_api_key


logger = logging.getLogger(__name__)


def render_stage2_job_analysis() -> None:
    """Render Stage 2: Job Analysis."""
    st.header("Stage 2: Job Analysis")
    st.markdown("Paste the job description and review the analyzed information")

    # Display info from Stage 1
    st.subheader("📋 Target Information (from Stage 1)")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Applicant", value=st.session_state.applicant_name, disabled=True)
    with col2:
        st.text_input("Company", value=st.session_state.company_name, disabled=True)

    st.divider()

    # Warning if resume was edited
    if st.session_state.resume_edited_after_confirmation:
        st.warning(
            "⚠️ Your resume was modified after Stage 1. You may need to re-run optimization in Stage 3."
        )

    st.divider()

    # Job description input
    st.subheader("💼 Job Description")
    st.session_state.job_description_text = st.text_area(
        "Paste the full job description",
        value=st.session_state.job_description_text,
        height=200,
        key="stage2_job_description"
    )

    st.divider()

    # Analyzer selection
    st.subheader("🔧 Analyzer Selection")
    analyzer_options = ["standard"]
    analyzer_labels = {}
    analyzer_labels["standard"] = "Standard Analyzer (keyword matching)"

    if has_gemini_api_key():
        analyzer_options.append("gemini")
        analyzer_labels["gemini"] = "Gemini Analyzer (AI-powered)"
    else:
        analyzer_labels["gemini"] = "Gemini Analyzer (requires API key)"

    st.session_state.analyzer_choice = st.radio(
        "Choose analyzer type",
        analyzer_options,
        format_func=lambda x: analyzer_labels[x],
        key="stage2_analyzer_choice",
        help="Standard is fast and works offline. Gemini provides AI-powered analysis (requires API key in .env)."
    )

    st.divider()

    # Analyze button
    if st.session_state.job_description_text.strip():
        if st.button("🔍 Analyze Job Description", type="primary", use_container_width=True):
            with st.spinner("Analyzing job description..."):
                try:
                    job_text = st.session_state.job_description_text

                    if st.session_state.analyzer_choice == "standard":
                        analyzer = JobDescriptionAnalyzer()
                    else:
                        # Gemini analyzer with API key from .env
                        api_key = get_gemini_api_key()
                        if not api_key:
                            st.error("❌ Gemini API key not found in .env file")
                            st.info("Please add GOOGLE_API_KEY to your .env file or select Standard Analyzer instead.")
                            st.stop()

                        analyzer = GeminiJobAnalyzer(api_key=api_key)

                    job_data = analyzer.analyze(job_text)
                    st.session_state.job_data_raw = job_data
                    st.session_state.job_data_edited = job_data.model_copy(deep=True)

                    st.success("✅ Job description analyzed successfully!")
                    st.session_state.stage_status[1] = 'completed'

                except Exception as e:
                    logger.error(f"Analysis error: {e}")
                    st.error(f"Error analyzing job description: {e}")
                    st.info("Try manually editing the job data below or try a different analyzer.")
    else:
        st.info("👆 Paste a job description first")

    st.divider()

    # Job data editor
    if st.session_state.job_data_edited:
        st.subheader("✏️ Edit Job Data")
        st.session_state.job_data_edited = render_job_data_editor(st.session_state.job_data_edited)

        st.divider()

        # Validation
        st.subheader("✔️ Validation")
        is_valid, errors = validate_job_data(st.session_state.job_data_edited)
        render_validation_results(is_valid, errors)

        st.divider()

        # Confirm button
        if st.button("✅ Confirm and Continue", type="primary", use_container_width=True, disabled=not is_valid):
            st.session_state.stage2_confirmed = True
            SessionStateManager.mark_job_edited()
            st.session_state.current_stage = 2
            st.rerun()

    # Navigation
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Resume Parsing"):
            st.session_state.current_stage = 0
            st.rerun()
    with col2:
        st.button("➡️ Continue", disabled=True, use_container_width=True)
