"""Stage 4: Export & Download - Redesigned with Markdown editing and sequential export flow."""

import streamlit as st
import tempfile
from pathlib import Path
import logging
from copy import deepcopy

from resume_optimizer.core.pdf_generator.generator import ATSFriendlyPDFGenerator
from resume_optimizer.core.pdf_generator.weasyprint_generator import WeasyPrintResumeGenerator
from resume_optimizer.core.converters.markdown_converter import MarkdownConverter
from resume_optimizer.core.converters.docx_converter import DocxConverter
from resume_optimizer.streamlit_ui.state.session_manager import SessionStateManager
from resume_optimizer.streamlit_ui.components.markdown_editor import (
    render_section_tabs_editor,
    render_full_markdown_editor,
    get_resume_markdown
)


logger = logging.getLogger(__name__)


def render_stage4_pdf_generation() -> None:
    """Render Stage 4: Export & Download with inline editing and sequential conversion."""
    st.header("Stage 4: Edit & Export Resume")
    st.markdown("Edit your resume in Markdown format, then export to DOCX or PDF")

    # Check for valid data
    if not st.session_state.optimization_result_edited or not st.session_state.optimization_result_edited.optimized_resume:
        st.error("No optimized resume found. Please complete the optimization step first.")
        if st.button("⬅️ Back to Optimization"):
            st.session_state.current_stage = 2
            st.rerun()
        return

    resume = st.session_state.optimization_result_edited.optimized_resume

    # Display info header
    _render_info_header()

    st.divider()

    # Main content with tabs: Edit | Preview | Export
    tab_edit, tab_preview, tab_export = st.tabs(["✏️ Edit Resume", "👁️ Preview", "📥 Export"])

    with tab_edit:
        _render_edit_tab(resume)

    with tab_preview:
        _render_preview_tab(resume)

    with tab_export:
        _render_export_tab(resume)

    st.divider()

    # Navigation
    _render_navigation()


def _render_info_header() -> None:
    """Render the applicant/job information header."""
    st.subheader("📋 Resume Information")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.text_input("Applicant", value=st.session_state.applicant_name, disabled=True)
    with col2:
        st.text_input("Company", value=st.session_state.company_name, disabled=True)
    with col3:
        job_title = st.session_state.job_data_edited.title if st.session_state.job_data_edited else ""
        st.text_input("Job", value=job_title, disabled=True)
    with col4:
        # Show scores
        opt_result = st.session_state.optimization_result_edited
        st.metric("ATS Score", f"{opt_result.ats_compliance_score:.0f}%")


def _render_edit_tab(resume) -> None:
    """Render the markdown editing tab."""
    st.markdown("### Edit Your Resume")
    st.info("Edit each section of your resume in Markdown format. Changes are saved automatically when you click 'Apply'.")

    # Choose editing mode
    edit_mode = st.radio(
        "Editing Mode",
        ["📑 Section-by-Section", "📄 Full Document"],
        horizontal=True,
        key="stage4_edit_mode"
    )

    st.divider()

    if edit_mode == "📑 Section-by-Section":
        updated_resume, changed = render_section_tabs_editor(
            resume,
            key_prefix="stage4_section_editor"
        )
    else:
        updated_resume, changed = render_full_markdown_editor(
            resume,
            key_prefix="stage4_full_editor"
        )

    # Update session state if changes were made
    if changed:
        st.session_state.optimization_result_edited.optimized_resume = updated_resume
        st.session_state.resume_edited_after_stage4 = True


def _render_preview_tab(resume) -> None:
    """Render the resume preview tab."""
    st.markdown("### Resume Preview")

    # Preview format selector
    preview_format = st.radio(
        "Preview Format",
        ["Markdown", "Formatted"],
        horizontal=True,
        key="stage4_preview_format"
    )

    st.divider()

    if preview_format == "Markdown":
        # Show raw markdown
        markdown_content = get_resume_markdown(resume)
        st.code(markdown_content, language="markdown")
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
    if resume.contact_info.address:
        contact_parts.append(resume.contact_info.address)
    if contact_parts:
        st.markdown(" | ".join(contact_parts))

    links = []
    if resume.contact_info.linkedin:
        links.append(f"[LinkedIn]({resume.contact_info.linkedin})")
    if resume.contact_info.github:
        links.append(f"[GitHub]({resume.contact_info.github})")
    if links:
        st.markdown(" | ".join(links))

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
            if edu.graduation_date:
                st.caption(edu.graduation_date)

    # Certifications
    if resume.certifications:
        st.markdown("---")
        st.markdown("### Certifications")
        for cert in resume.certifications:
            st.write(f"• {cert}")

    # Languages
    if resume.languages:
        st.markdown("---")
        st.markdown("### Languages")
        st.write(" • ".join(resume.languages))


def _render_export_tab(resume) -> None:
    """Render the export tab with sequential conversion flow."""
    st.markdown("### Export Your Resume")
    st.info("**Export Flow:** Markdown → DOCX → PDF. Each format can be downloaded and edited.")

    # Create temp directory
    temp_dir = Path(tempfile.gettempdir()) / "resume_optimizer" / st.session_state.session_id
    temp_dir.mkdir(parents=True, exist_ok=True)

    applicant_name = st.session_state.applicant_name.replace(' ', '_') if st.session_state.applicant_name else "resume"

    # Initialize session state for generated files
    if 'generated_files' not in st.session_state:
        st.session_state.generated_files = {}

    st.markdown("---")

    # Step 1: Markdown
    st.markdown("#### Step 1: Markdown (.md)")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("Your resume in Markdown format - easy to edit with any text editor.")

    with col2:
        markdown_content = get_resume_markdown(resume)
        st.download_button(
            label="📥 Download Markdown",
            data=markdown_content,
            file_name=f"{applicant_name}_resume.md",
            mime="text/markdown",
            width='stretch',
            key="download_md"
        )

    # Save markdown to file for reference
    md_path = temp_dir / f"{applicant_name}_resume.md"
    md_path.write_text(markdown_content, encoding='utf-8')
    st.session_state.generated_files['markdown'] = str(md_path)

    st.markdown("---")

    # Step 2: DOCX
    st.markdown("#### Step 2: Word Document (.docx)")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("Professional Word format - edit in Microsoft Word, Google Docs, or LibreOffice.")

    with col2:
        if st.button("🔄 Generate DOCX", width='stretch', key="gen_docx"):
            with st.spinner("Generating DOCX..."):
                try:
                    docx_path = temp_dir / f"{applicant_name}_resume.docx"
                    docx_bytes = DocxConverter.resume_to_docx(resume, docx_path)
                    st.session_state.generated_files['docx'] = str(docx_path)
                    st.session_state.generated_files['docx_bytes'] = docx_bytes
                    st.success("DOCX generated!")
                except Exception as e:
                    logger.error(f"DOCX generation error: {e}")
                    st.error(f"Error generating DOCX: {e}")

    # Show download button if DOCX exists
    if st.session_state.generated_files.get('docx_bytes'):
        st.download_button(
            label="📥 Download DOCX",
            data=st.session_state.generated_files['docx_bytes'],
            file_name=f"{applicant_name}_resume.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            width='stretch',
            key="download_docx"
        )

    st.markdown("---")

    # Step 3: PDF
    st.markdown("#### Step 3: PDF Document (.pdf)")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("ATS-optimized PDF format - ready to submit to job applications.")

    with col2:
        pdf_method = st.selectbox(
            "PDF Method",
            ["Modern (WeasyPrint)", "Classic (ReportLab)", "From DOCX (LibreOffice)"],
            key="pdf_method",
            help="Modern: Beautiful HTML/CSS-based formatting | Classic: ATS-focused formatting | DOCX: Convert via LibreOffice",
            label_visibility="collapsed"
        )

    # Generate PDF button
    if st.button("🔄 Generate PDF", type="primary", width='stretch', key="gen_pdf"):
        with st.spinner("Generating PDF..."):
            try:
                pdf_path = temp_dir / f"{applicant_name}_resume.pdf"

                if pdf_method == "Modern (WeasyPrint)":
                    # Use the new WeasyPrint generator for beautiful formatting
                    generator = WeasyPrintResumeGenerator()
                    generator.generate_pdf(
                        resume_data=resume,
                        optimization_result=st.session_state.optimization_result_edited,
                        output_path=pdf_path,
                        applicant_name=st.session_state.applicant_name,
                        company_name=st.session_state.company_name
                    )
                elif pdf_method == "Classic (ReportLab)":
                    # Use the existing ReportLab PDF generator
                    generator = ATSFriendlyPDFGenerator()
                    generator.generate_pdf(
                        resume_data=resume,
                        optimization_result=st.session_state.optimization_result_edited,
                        output_path=pdf_path,
                        applicant_name=st.session_state.applicant_name,
                        company_name=st.session_state.company_name
                    )
                else:
                    # Convert from DOCX
                    docx_path = temp_dir / f"{applicant_name}_resume.docx"

                    # Generate DOCX first if it doesn't exist
                    if not docx_path.exists():
                        DocxConverter.resume_to_docx(resume, docx_path)

                    # Convert to PDF
                    DocxConverter.docx_to_pdf(docx_path, pdf_path)

                st.session_state.pdf_path = str(pdf_path)
                st.session_state.generated_files['pdf'] = str(pdf_path)

                # Read PDF bytes for download
                with open(pdf_path, 'rb') as f:
                    st.session_state.generated_files['pdf_bytes'] = f.read()

                st.success("PDF generated!")
                st.session_state.stage_status[3] = 'completed'

            except RuntimeError as e:
                # Handle WeasyPrint system dependency errors
                logger.error(f"PDF generation error: {e}")
                st.error(f"⚠️ WeasyPrint System Dependencies Missing")
                st.info(
                    "To use the Modern (WeasyPrint) PDF generator, install system libraries:\n\n"
                    "**macOS:**\n"
                    "```\n"
                    "brew install glib gobject-introspection\n"
                    "```\n\n"
                    "**Linux:**\n"
                    "```\n"
                    "sudo apt install libgobject-2.0-0 libpango-1.0-0 libpangocairo-1.0-0\n"
                    "```\n\n"
                    "Meanwhile, try using **Classic (ReportLab)** or **From DOCX** method."
                )
            except Exception as e:
                logger.error(f"PDF generation error: {e}")
                st.error(f"Error generating PDF: {e}")

    # Show download button if PDF exists
    if st.session_state.generated_files.get('pdf_bytes'):
        st.download_button(
            label="📥 Download PDF",
            data=st.session_state.generated_files['pdf_bytes'],
            file_name=f"{applicant_name}_resume.pdf",
            mime="application/pdf",
            width='stretch',
            key="download_pdf"
        )

    st.markdown("---")

    # Download All button
    st.markdown("#### Download All Formats")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📦 Generate All Formats", width='stretch', key="gen_all"):
            with st.spinner("Generating all formats..."):
                try:
                    # Markdown
                    md_path = temp_dir / f"{applicant_name}_resume.md"
                    md_path.write_text(get_resume_markdown(resume), encoding='utf-8')

                    # DOCX
                    docx_path = temp_dir / f"{applicant_name}_resume.docx"
                    docx_bytes = DocxConverter.resume_to_docx(resume, docx_path)
                    st.session_state.generated_files['docx_bytes'] = docx_bytes

                    # PDF
                    pdf_path = temp_dir / f"{applicant_name}_resume.pdf"
                    generator = ATSFriendlyPDFGenerator()
                    generator.generate_pdf(
                        resume_data=resume,
                        optimization_result=st.session_state.optimization_result_edited,
                        output_path=pdf_path,
                        applicant_name=st.session_state.applicant_name,
                        company_name=st.session_state.company_name
                    )

                    with open(pdf_path, 'rb') as f:
                        st.session_state.generated_files['pdf_bytes'] = f.read()

                    st.session_state.pdf_path = str(pdf_path)
                    st.session_state.stage_status[3] = 'completed'

                    st.success("All formats generated successfully!")

                except Exception as e:
                    logger.error(f"Error generating formats: {e}")
                    st.error(f"Error: {e}")

    # Success message
    if st.session_state.stage_status.get(3) == 'completed':
        st.success("""
        **Your resume is ready!**

        All formats have been optimized for ATS compatibility:
        - **Markdown:** Easy to edit and version control
        - **DOCX:** Professional Word format for further editing
        - **PDF:** Ready to submit to job applications

        Good luck with your application!
        """)


def _render_navigation() -> None:
    """Render navigation buttons."""
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⬅️ Back to Optimization", width='stretch'):
            st.session_state.current_stage = 2
            st.rerun()

    with col2:
        if st.button("🔄 Start New Resume", width='stretch'):
            # Clear generated files
            if 'generated_files' in st.session_state:
                del st.session_state.generated_files
            SessionStateManager.reset_session()
            st.session_state.current_stage = 0
            st.rerun()

    with col3:
        # Show completion status
        if st.session_state.stage_status.get(3) == 'completed':
            st.success("✅ Complete")
        else:
            st.info("📝 In Progress")
