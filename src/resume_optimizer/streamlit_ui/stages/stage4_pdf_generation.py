"""Stage 4: PDF Generation implementation."""

import streamlit as st
import tempfile
from pathlib import Path
import logging

from resume_optimizer.core.pdf_generator.generator import ATSFriendlyPDFGenerator
from resume_optimizer.streamlit_ui.state.session_manager import SessionStateManager


logger = logging.getLogger(__name__)


def render_stage4_pdf_generation() -> None:
    """Render Stage 4: PDF Generation."""
    st.header("Stage 4: PDF Generation")
    st.markdown("Preview your optimized resume and download it as a PDF")

    # Display info
    st.subheader("📋 Resume Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Applicant", value=st.session_state.applicant_name, disabled=True)
    with col2:
        st.text_input("Company", value=st.session_state.company_name, disabled=True)
    with col3:
        st.text_input("Job", value=st.session_state.job_data_edited.title if st.session_state.job_data_edited else "", disabled=True)

    st.divider()

    # Preview
    st.subheader("👁️ Resume Preview")
    if st.session_state.optimization_result_edited and st.session_state.optimization_result_edited.optimized_resume:
        resume = st.session_state.optimization_result_edited.optimized_resume

        # Contact info
        st.markdown("#### Contact Information")
        contact_lines = []
        if resume.contact_info.name:
            contact_lines.append(resume.contact_info.name)
        if resume.contact_info.email:
            contact_lines.append(resume.contact_info.email)
        if resume.contact_info.phone:
            contact_lines.append(resume.contact_info.phone)
        if resume.contact_info.linkedin:
            contact_lines.append(resume.contact_info.linkedin)
        st.write(" | ".join(contact_lines))

        # Summary
        if resume.summary:
            st.markdown("#### Professional Summary")
            st.write(resume.summary)

        # Skills
        if resume.skills:
            st.markdown("#### Technical Skills")
            st.write(", ".join(resume.skills))

        # Experience
        if resume.experience:
            st.markdown("#### Work Experience")
            for exp in resume.experience:
                st.markdown(f"**{exp.position}** @ {exp.company}")
                if exp.duration:
                    st.text(exp.duration)
                if exp.description:
                    for bullet in exp.description:
                        st.write(f"• {bullet}")

        # Education
        if resume.education:
            st.markdown("#### Education")
            for edu in resume.education:
                st.markdown(f"**{edu.degree}** in {edu.field}")
                st.text(edu.institution)
                if edu.graduation_date:
                    st.text(edu.graduation_date)

        # Certifications
        if resume.certifications:
            st.markdown("#### Certifications")
            for cert in resume.certifications:
                st.write(f"• {cert}")

        # Languages
        if resume.languages:
            st.markdown("#### Languages")
            for lang in resume.languages:
                st.write(f"• {lang}")

    st.divider()

    # Generate PDF button
    if st.button("📥 Generate PDF", type="primary", use_container_width=True):
        with st.spinner("Generating PDF..."):
            try:
                # Create temp directory for PDF
                temp_dir = Path(tempfile.gettempdir()) / "resume_optimizer" / st.session_state.session_id
                temp_dir.mkdir(parents=True, exist_ok=True)
                pdf_path = temp_dir / f"{st.session_state.applicant_name.replace(' ', '_')}_optimized_resume.pdf"

                # Generate PDF
                generator = ATSFriendlyPDFGenerator()
                generator.generate_pdf(
                    resume_data=st.session_state.optimization_result_edited.optimized_resume,
                    optimization_result=st.session_state.optimization_result_edited,
                    output_path=pdf_path,
                    applicant_name=st.session_state.applicant_name,
                    company_name=st.session_state.company_name
                )

                st.session_state.pdf_path = str(pdf_path)
                st.success("✅ PDF generated successfully!")
                st.session_state.stage_status[3] = 'completed'

            except Exception as e:
                logger.error(f"PDF generation error: {e}")
                st.error(f"Error generating PDF: {e}")

    st.divider()

    # Download button
    if st.session_state.pdf_path and Path(st.session_state.pdf_path).exists():
        st.subheader("⬇️ Download Resume")

        with open(st.session_state.pdf_path, 'rb') as f:
            pdf_data = f.read()

        st.download_button(
            label="Download PDF",
            data=pdf_data,
            file_name=f"{st.session_state.applicant_name.replace(' ', '_')}_optimized_resume.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        st.divider()

        # Success message
        st.success("""
        🎉 **You're all set!**

        Your optimized resume is ready to download. It's formatted for ATS compatibility and includes:
        - Keyword optimization
        - ATS-friendly formatting
        - Improved skill alignment
        - Enhanced content quality

        Good luck with your application!
        """)

    st.divider()

    # Navigation
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Back to Optimization"):
            st.session_state.current_stage = 2
            st.rerun()
    with col2:
        if st.button("🔄 Start New Resume"):
            SessionStateManager.reset_session()
            st.session_state.current_stage = 0
            st.rerun()
    with col3:
        st.text("")
