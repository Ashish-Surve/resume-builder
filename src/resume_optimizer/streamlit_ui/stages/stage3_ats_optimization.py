"""Stage 3: ATS Optimization implementation with inline editing."""

import streamlit as st
import logging

from resume_optimizer.core.ats_optimizer.optimizer import ATSOptimizer
from resume_optimizer.streamlit_ui.components.editors import render_optimization_result_editor
from resume_optimizer.streamlit_ui.components.validators import render_validation_results
from resume_optimizer.streamlit_ui.components.markdown_editor import (
    render_section_tabs_editor,
    render_optimization_markdown_editor,
    get_resume_markdown
)
from resume_optimizer.streamlit_ui.state.session_manager import SessionStateManager
from resume_optimizer.streamlit_ui.utils import (
    is_ollama_available,
    get_ollama_models,
    get_default_ollama_model,
    has_gemini_api_key
)


logger = logging.getLogger(__name__)


def render_stage3_ats_optimization() -> None:
    """Render Stage 3: ATS Optimization with inline markdown editing."""
    st.header("Stage 3: ATS Optimization")
    st.markdown("Run ATS optimization on your resume, then edit sections in Markdown format")

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

    if st.button(f"⚡ {button_text}", type="primary", width='stretch'):
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
        # Tabs for different views
        tab_scores, tab_edit, tab_preview = st.tabs(["📊 Scores & Recommendations", "✏️ Edit Resume", "👁️ Preview"])

        with tab_scores:
            _render_scores_tab()

        with tab_edit:
            _render_edit_tab()

        with tab_preview:
            _render_preview_tab()

        st.divider()

        # Simple validation for optimization (just check if result exists)
        is_valid = st.session_state.optimization_result_edited is not None
        if is_valid:
            st.success("✅ Optimization results ready! Edit sections above or continue to export.")

        st.divider()

        # Confirm button
        if st.button("✅ Confirm and Continue to Export", type="primary", width='stretch', disabled=not is_valid):
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
        st.button("➡️ Continue", disabled=True, width='stretch')


def _render_scores_tab() -> None:
    """Render the scores and recommendations tab."""
    opt_result = st.session_state.optimization_result_edited

    # Display scores as metrics
    st.subheader("📊 Optimization Scores")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Original Score", f"{opt_result.original_score:.1f}", "/100")
    with col2:
        st.metric("Optimized Score", f"{opt_result.optimized_score:.1f}", "/100")
    with col3:
        improvement = opt_result.optimized_score - opt_result.original_score
        st.metric("Improvement", f"{improvement:+.1f}")
    with col4:
        st.metric("ATS Compliance", f"{opt_result.ats_compliance_score:.1f}%")

    st.divider()

    # Recommendations
    if opt_result.recommendations:
        st.subheader("💡 Recommendations")
        for rec in opt_result.recommendations:
            st.write(f"• {rec}")

    # Missing Keywords
    if opt_result.missing_keywords:
        st.subheader("🔑 Keywords to Consider Adding")
        keywords_text = " • ".join(opt_result.missing_keywords[:10])
        st.write(keywords_text)

    # Improvements Applied
    if opt_result.improvements:
        st.subheader("✅ Improvements Applied")
        for imp in opt_result.improvements:
            st.write(f"• {imp}")


def _render_edit_tab() -> None:
    """Render the markdown editing tab for the optimized resume."""
    opt_result = st.session_state.optimization_result_edited

    if not opt_result.optimized_resume:
        st.warning("No optimized resume data available to edit.")
        return

    st.subheader("✏️ Edit Optimized Resume")
    st.info("Edit each section of your resume in Markdown format. Click 'Apply All Changes' when done.")

    # Choose editing mode
    edit_mode = st.radio(
        "Editing Mode",
        ["📑 Section-by-Section", "📄 Full Document"],
        horizontal=True,
        key="stage3_edit_mode"
    )

    st.divider()

    if edit_mode == "📑 Section-by-Section":
        updated_resume, changed = render_section_tabs_editor(
            opt_result.optimized_resume,
            key_prefix="stage3_section_editor"
        )
    else:
        from resume_optimizer.streamlit_ui.components.markdown_editor import render_full_markdown_editor
        updated_resume, changed = render_full_markdown_editor(
            opt_result.optimized_resume,
            key_prefix="stage3_full_editor"
        )

    # Update session state if changes were made
    if changed:
        st.session_state.optimization_result_edited.optimized_resume = updated_resume


def _render_preview_tab() -> None:
    """Render the resume preview tab."""
    opt_result = st.session_state.optimization_result_edited

    if not opt_result.optimized_resume:
        st.warning("No optimized resume data available to preview.")
        return

    resume = opt_result.optimized_resume

    st.subheader("👁️ Resume Preview")

    # Preview format selector
    preview_format = st.radio(
        "Preview Format",
        ["Markdown", "Formatted"],
        horizontal=True,
        key="stage3_preview_format"
    )

    st.divider()

    if preview_format == "Markdown":
        # Show raw markdown
        markdown_content = get_resume_markdown(resume)
        st.code(markdown_content, language="markdown")

        # Download button
        st.download_button(
            label="📥 Download Markdown",
            data=markdown_content,
            file_name="resume_optimized.md",
            mime="text/markdown",
            key="stage3_download_md"
        )
    else:
        # Show formatted preview
        _render_formatted_preview(resume)


def _render_formatted_preview(resume) -> None:
    """Render a nicely formatted preview of the resume."""
    # Contact header
    st.markdown(f"## {resume.contact_info.name or 'Your Name'}")

    contact_parts = []
    if resume.contact_info.email:
        contact_parts.append(resume.contact_info.email)
    if resume.contact_info.phone:
        contact_parts.append(resume.contact_info.phone)
    if contact_parts:
        st.markdown(" | ".join(contact_parts))

    # Summary
    if resume.summary:
        st.markdown("---")
        st.markdown("### Professional Summary")
        summary_text = resume.summary
        if isinstance(summary_text, dict):
            summary_text = summary_text.get('optimized_summary', summary_text.get('summary', str(summary_text)))
        st.write(summary_text)

    # Skills
    if resume.skills:
        st.markdown("---")
        st.markdown("### Technical Skills")
        skills_text = " • ".join(resume.skills)
        st.write(skills_text)

    # Experience
    if resume.experience:
        st.markdown("---")
        st.markdown("### Professional Experience")
        for exp in resume.experience:
            st.markdown(f"**{exp.position or 'Position'}** @ {exp.company or 'Company'}")
            if exp.duration:
                st.caption(exp.duration)
            for bullet in exp.description:
                if bullet:
                    st.write(f"• {bullet}")
            st.write("")

    # Education
    if resume.education:
        st.markdown("---")
        st.markdown("### Education")
        for edu in resume.education:
            degree_text = edu.degree or "Degree"
            if edu.field:
                degree_text += f" in {edu.field}"
            st.markdown(f"**{degree_text}**")
            st.write(edu.institution or "")

    # Certifications
    if resume.certifications:
        st.markdown("---")
        st.markdown("### Certifications")
        for cert in resume.certifications:
            st.write(f"• {cert}")
