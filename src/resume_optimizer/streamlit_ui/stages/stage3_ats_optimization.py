"""Stage 3: ATS Optimization implementation."""

import streamlit as st
import logging

from resume_optimizer.core.ats_optimizer.optimizer import ATSOptimizer
from resume_optimizer.streamlit_ui.components.editors import render_optimization_result_editor
from resume_optimizer.streamlit_ui.components.validators import render_validation_results
from resume_optimizer.streamlit_ui.state.session_manager import SessionStateManager


logger = logging.getLogger(__name__)


def render_stage3_ats_optimization() -> None:
    """Render Stage 3: ATS Optimization."""
    st.header("Stage 3: ATS Optimization")
    st.markdown("Run ATS optimization on your resume based on the job description")

    # Display info from previous stages
    st.subheader("📋 Workflow Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Applicant", value=st.session_state.applicant_name, disabled=True)
    with col2:
        st.text_input("Company", value=st.session_state.company_name, disabled=True)
    with col3:
        st.text_input("Job", value=st.session_state.job_data_edited.title if st.session_state.job_data_edited else "", disabled=True)

    st.divider()

    # Warnings if data was edited
    if st.session_state.resume_edited_after_confirmation:
        st.warning("⚠️ Resume was modified after Stage 1. Click 'Re-run Optimization' to update results.")
    if st.session_state.job_edited_after_confirmation:
        st.warning("⚠️ Job data was modified after Stage 2. Click 'Re-run Optimization' to update results.")

    st.divider()

    # Optimization button
    button_text = "Re-run Optimization" if st.session_state.optimization_result_edited else "Run Optimization"

    if st.button(f"⚡ {button_text}", type="primary", use_container_width=True):
        with st.spinner("Running ATS optimization..."):
            try:
                optimizer = ATSOptimizer()
                optimization_result = optimizer.optimize(
                    resume_data=st.session_state.resume_data_edited,
                    job_data=st.session_state.job_data_edited,
                    applicant_name=st.session_state.applicant_name,
                    company_name=st.session_state.company_name
                )

                st.session_state.optimization_result_raw = optimization_result
                st.session_state.optimization_result_edited = optimization_result.model_copy(deep=True)

                # Clear edit flags after re-running
                st.session_state.resume_edited_after_confirmation = False
                st.session_state.job_edited_after_confirmation = False

                st.success("✅ Optimization completed successfully!")
                st.session_state.stage_status[2] = 'completed'

            except Exception as e:
                logger.error(f"Optimization error: {e}")
                st.error(f"Error running optimization: {e}")

    st.divider()

    # Display and edit optimization results
    if st.session_state.optimization_result_edited:
        st.subheader("✏️ Review and Edit Optimization Results")
        st.session_state.optimization_result_edited = render_optimization_result_editor(
            st.session_state.optimization_result_edited
        )

        st.divider()

        # Simple validation for optimization (just check if result exists)
        is_valid = st.session_state.optimization_result_edited is not None
        if is_valid:
            st.success("✅ Optimization results ready for download!")

        st.divider()

        # Confirm button
        if st.button("✅ Confirm and Continue", type="primary", use_container_width=True, disabled=not is_valid):
            st.session_state.stage3_confirmed = True
            st.session_state.current_stage = 3
            st.rerun()

    # Navigation
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Job Analysis"):
            st.session_state.current_stage = 1
            st.rerun()
    with col2:
        st.button("➡️ Continue", disabled=True, use_container_width=True)
