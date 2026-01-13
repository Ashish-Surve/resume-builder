# src/resume_optimizer/streamlit_ui/components/markdown_editor.py
"""
Markdown-based section editor component for inline resume editing.
Provides a tabbed interface for editing each resume section in markdown.
"""

import streamlit as st
from copy import deepcopy
from typing import Optional, Tuple, Dict, Any

from resume_optimizer.core.models import ResumeData, OptimizationResult
from resume_optimizer.core.converters.markdown_converter import MarkdownConverter


# Section configuration
SECTIONS = [
    {"key": "contact", "label": "Contact", "icon": "👤"},
    {"key": "summary", "label": "Summary", "icon": "📝"},
    {"key": "skills", "label": "Skills", "icon": "🔧"},
    {"key": "experience", "label": "Experience", "icon": "💼"},
    {"key": "education", "label": "Education", "icon": "🎓"},
    {"key": "certifications", "label": "Certifications", "icon": "🏆"},
    {"key": "languages", "label": "Languages", "icon": "🌍"},
]


def render_section_tabs_editor(
    resume_data: ResumeData,
    key_prefix: str = "section_editor"
) -> Tuple[ResumeData, bool]:
    """
    Render a tabbed interface for editing resume sections.
    Each tab shows the section in markdown format for easy editing.

    Args:
        resume_data: The resume data to edit
        key_prefix: Prefix for session state keys

    Returns:
        Tuple of (updated ResumeData, whether any changes were made)
    """
    data = deepcopy(resume_data)
    changes_made = False

    # Initialize session state for markdown content if not exists
    state_key = f"{key_prefix}_markdown"
    if state_key not in st.session_state:
        st.session_state[state_key] = {}
        for section in SECTIONS:
            section_md = MarkdownConverter.get_section_markdown(data, section["key"])
            st.session_state[state_key][section["key"]] = section_md

    # Create tabs for each section
    tab_labels = [f"{s['icon']} {s['label']}" for s in SECTIONS]
    tabs = st.tabs(tab_labels)

    for i, (tab, section) in enumerate(zip(tabs, SECTIONS)):
        with tab:
            section_key = section["key"]
            current_md = st.session_state[state_key].get(section_key, "")

            # Section editor with preview
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("**Edit Markdown**")
                new_md = st.text_area(
                    f"Edit {section['label']}",
                    value=current_md,
                    height=300,
                    key=f"{key_prefix}_{section_key}_textarea",
                    label_visibility="collapsed"
                )

                if new_md != current_md:
                    st.session_state[state_key][section_key] = new_md
                    changes_made = True

            with col2:
                st.markdown("**Preview**")
                st.markdown(new_md)

    # Parse all sections back into ResumeData when user clicks apply
    if st.button("✅ Apply All Changes", type="primary", width='stretch', key=f"{key_prefix}_apply"):
        # Combine all section markdown
        full_markdown = f"# {data.contact_info.name or 'Resume'}\n\n"
        for section in SECTIONS:
            section_md = st.session_state[state_key].get(section["key"], "")
            if section_md.strip():
                full_markdown += section_md + "\n"

        # Parse back to ResumeData
        data = MarkdownConverter.markdown_to_resume(full_markdown, data)
        changes_made = True
        st.success("Changes applied!")

    return data, changes_made


def render_full_markdown_editor(
    resume_data: ResumeData,
    key_prefix: str = "full_md_editor"
) -> Tuple[ResumeData, bool]:
    """
    Render a full-page markdown editor for the entire resume.

    Args:
        resume_data: The resume data to edit
        key_prefix: Prefix for session state keys

    Returns:
        Tuple of (updated ResumeData, whether any changes were made)
    """
    data = deepcopy(resume_data)
    changes_made = False

    # Initialize session state
    state_key = f"{key_prefix}_full_markdown"
    if state_key not in st.session_state:
        st.session_state[state_key] = MarkdownConverter.resume_to_markdown(data)

    current_md = st.session_state[state_key]

    # Two-column layout: editor and preview
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ✏️ Edit Resume (Markdown)")
        new_md = st.text_area(
            "Edit Resume Markdown",
            value=current_md,
            height=500,
            key=f"{key_prefix}_textarea",
            label_visibility="collapsed"
        )

        if new_md != current_md:
            st.session_state[state_key] = new_md
            changes_made = True

    with col2:
        st.markdown("### 👁️ Live Preview")
        st.markdown(new_md)

    # Action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ Apply Changes", type="primary", width='stretch', key=f"{key_prefix}_apply"):
            data = MarkdownConverter.markdown_to_resume(new_md, data)
            st.success("Changes applied to resume!")
            changes_made = True

    with col2:
        if st.button("🔄 Reset", width='stretch', key=f"{key_prefix}_reset"):
            st.session_state[state_key] = MarkdownConverter.resume_to_markdown(resume_data)
            st.rerun()

    with col3:
        # Download markdown button
        st.download_button(
            label="📥 Download .md",
            data=new_md,
            file_name="resume.md",
            mime="text/markdown",
            width='stretch',
            key=f"{key_prefix}_download"
        )

    return data, changes_made


def render_optimization_markdown_editor(
    opt_result: OptimizationResult,
    key_prefix: str = "opt_md_editor"
) -> Tuple[OptimizationResult, bool]:
    """
    Render markdown editor for the optimized resume within an OptimizationResult.

    Args:
        opt_result: The optimization result containing the optimized resume
        key_prefix: Prefix for session state keys

    Returns:
        Tuple of (updated OptimizationResult, whether any changes were made)
    """
    result = deepcopy(opt_result)
    changes_made = False

    if not result.optimized_resume:
        st.warning("No optimized resume data available to edit.")
        return result, False

    # Show scores first
    st.markdown("### 📊 Optimization Scores")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Original", f"{result.original_score:.1f}")
    with col2:
        st.metric("Optimized", f"{result.optimized_score:.1f}")
    with col3:
        improvement = result.optimized_score - result.original_score
        st.metric("Improvement", f"{improvement:+.1f}")
    with col4:
        st.metric("ATS Score", f"{result.ats_compliance_score:.1f}%")

    st.divider()

    # Choose editing mode
    edit_mode = st.radio(
        "Editing Mode",
        ["Section-by-Section", "Full Document"],
        horizontal=True,
        key=f"{key_prefix}_mode"
    )

    st.divider()

    if edit_mode == "Section-by-Section":
        result.optimized_resume, changes_made = render_section_tabs_editor(
            result.optimized_resume,
            key_prefix=f"{key_prefix}_sections"
        )
    else:
        result.optimized_resume, changes_made = render_full_markdown_editor(
            result.optimized_resume,
            key_prefix=f"{key_prefix}_full"
        )

    return result, changes_made


def render_inline_section_editor(
    resume_data: ResumeData,
    section_key: str,
    key_prefix: str = "inline"
) -> Tuple[ResumeData, bool]:
    """
    Render an inline editor for a single section.
    Useful for quick edits without opening full editor.

    Args:
        resume_data: The resume data
        section_key: The section to edit ('contact', 'summary', etc.)
        key_prefix: Prefix for session state keys

    Returns:
        Tuple of (updated ResumeData, whether changes were made)
    """
    data = deepcopy(resume_data)
    changes_made = False

    # Get section config
    section_config = next((s for s in SECTIONS if s["key"] == section_key), None)
    if not section_config:
        st.error(f"Unknown section: {section_key}")
        return data, False

    # Get current markdown for section
    current_md = MarkdownConverter.get_section_markdown(data, section_key)

    with st.expander(f"{section_config['icon']} Edit {section_config['label']}", expanded=False):
        new_md = st.text_area(
            f"Edit {section_config['label']}",
            value=current_md,
            height=200,
            key=f"{key_prefix}_{section_key}",
            label_visibility="collapsed"
        )

        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("Apply", key=f"{key_prefix}_{section_key}_apply", type="primary"):
                # Parse just this section
                # Create a minimal markdown with just this section for parsing
                temp_md = f"# {data.contact_info.name or 'Resume'}\n\n{new_md}"
                temp_data = MarkdownConverter.markdown_to_resume(temp_md, data)

                # Copy only the relevant section back
                if section_key == "contact":
                    data.contact_info = temp_data.contact_info
                elif section_key == "summary":
                    data.summary = temp_data.summary
                elif section_key == "skills":
                    data.skills = temp_data.skills
                elif section_key == "experience":
                    data.experience = temp_data.experience
                elif section_key == "education":
                    data.education = temp_data.education
                elif section_key == "certifications":
                    data.certifications = temp_data.certifications
                elif section_key == "languages":
                    data.languages = temp_data.languages

                changes_made = True
                st.success(f"{section_config['label']} updated!")

        with col2:
            st.markdown("**Preview:**")
            st.markdown(new_md)

    return data, changes_made


def get_resume_markdown(resume_data: ResumeData) -> str:
    """
    Get the full markdown representation of a resume.

    Args:
        resume_data: The resume data

    Returns:
        Markdown string
    """
    return MarkdownConverter.resume_to_markdown(resume_data)


def parse_markdown_to_resume(markdown_text: str, existing_resume: Optional[ResumeData] = None) -> ResumeData:
    """
    Parse markdown text into ResumeData.

    Args:
        markdown_text: The markdown to parse
        existing_resume: Optional existing resume to update

    Returns:
        ResumeData object
    """
    return MarkdownConverter.markdown_to_resume(markdown_text, existing_resume)
