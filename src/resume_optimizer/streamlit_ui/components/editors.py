"""Editable form components for resume and job data."""

import streamlit as st
import pandas as pd
from copy import deepcopy
from typing import Optional

from resume_optimizer.core.models import (
    ResumeData,
    ContactInfo,
    Experience,
    Education,
    JobDescriptionData,
    OptimizationResult
)


def render_resume_data_editor(resume_data: ResumeData) -> ResumeData:
    """Render editable form for ResumeData.

    Args:
        resume_data: ResumeData to edit

    Returns:
        Updated ResumeData with user edits
    """
    data = deepcopy(resume_data)

    # Contact Information
    st.subheader("👤 Contact Information")
    col1, col2 = st.columns(2)
    with col1:
        data.contact_info.name = st.text_input(
            "Full Name",
            value=data.contact_info.name or "",
            key="contact_name"
        )
        data.contact_info.email = st.text_input(
            "Email",
            value=data.contact_info.email or "",
            key="contact_email"
        )
        data.contact_info.phone = st.text_input(
            "Phone",
            value=data.contact_info.phone or "",
            key="contact_phone"
        )
    with col2:
        data.contact_info.linkedin = st.text_input(
            "LinkedIn URL",
            value=data.contact_info.linkedin or "",
            key="contact_linkedin"
        )
        data.contact_info.github = st.text_input(
            "GitHub URL",
            value=data.contact_info.github or "",
            key="contact_github"
        )
        data.contact_info.address = st.text_input(
            "Address",
            value=data.contact_info.address or "",
            key="contact_address"
        )

    st.divider()

    # Professional Summary
    st.subheader("📝 Professional Summary")
    data.summary = st.text_area(
        "Summary",
        value=data.summary or "",
        height=100,
        key="summary"
    )

    st.divider()

    # Skills
    st.subheader("🔧 Skills")
    skills_df = pd.DataFrame({"Skill": data.skills or []})
    edited_skills = st.data_editor(
        skills_df,
        use_container_width=True,
        num_rows="dynamic",
        key="skills_editor"
    )
    data.skills = edited_skills["Skill"].tolist() if not edited_skills.empty else []

    st.divider()

    # Experience
    st.subheader("💼 Work Experience")
    if not data.experience:
        data.experience = []

    # Experience entries
    for i, exp in enumerate(data.experience):
        with st.expander(f"Experience {i+1}: {exp.position or 'New Entry'} at {exp.company or ''}"):
            col1, col2 = st.columns(2)
            with col1:
                exp.company = st.text_input(
                    "Company",
                    value=exp.company or "",
                    key=f"exp_company_{i}"
                )
                exp.position = st.text_input(
                    "Position",
                    value=exp.position or "",
                    key=f"exp_position_{i}"
                )
            with col2:
                exp.duration = st.text_input(
                    "Duration",
                    value=exp.duration or "",
                    key=f"exp_duration_{i}"
                )

            # Description bullets
            desc_df = pd.DataFrame({"Description": exp.description or []})
            edited_desc = st.data_editor(
                desc_df,
                use_container_width=True,
                num_rows="dynamic",
                key=f"exp_desc_{i}"
            )
            exp.description = edited_desc["Description"].tolist() if not edited_desc.empty else []

            # Skills used
            skills_used_df = pd.DataFrame({"Skill": exp.skills_used or []})
            edited_skills_used = st.data_editor(
                skills_used_df,
                use_container_width=True,
                num_rows="dynamic",
                key=f"exp_skills_{i}"
            )
            exp.skills_used = edited_skills_used["Skill"].tolist() if not edited_skills_used.empty else []

            if st.button(f"Remove Experience {i+1}", key=f"remove_exp_{i}"):
                data.experience.pop(i)
                st.rerun()

    # Add new experience button
    if st.button("➕ Add Experience", use_container_width=True):
        data.experience.append(Experience())
        st.rerun()

    st.divider()

    # Education
    st.subheader("🎓 Education")
    if not data.education:
        data.education = []

    for i, edu in enumerate(data.education):
        with st.expander(f"Education {i+1}: {edu.degree or 'New Entry'} at {edu.institution or ''}"):
            col1, col2 = st.columns(2)
            with col1:
                edu.institution = st.text_input(
                    "Institution",
                    value=edu.institution or "",
                    key=f"edu_institution_{i}"
                )
                edu.degree = st.text_input(
                    "Degree",
                    value=edu.degree or "",
                    key=f"edu_degree_{i}"
                )
            with col2:
                edu.field = st.text_input(
                    "Field of Study",
                    value=edu.field or "",
                    key=f"edu_field_{i}"
                )
                edu.graduation_date = st.text_input(
                    "Graduation Date",
                    value=edu.graduation_date or "",
                    key=f"edu_grad_date_{i}"
                )

            edu.gpa = st.text_input(
                "GPA",
                value=edu.gpa or "",
                key=f"edu_gpa_{i}"
            )

            # Description
            desc_df = pd.DataFrame({"Description": edu.description or []})
            edited_desc = st.data_editor(
                desc_df,
                use_container_width=True,
                num_rows="dynamic",
                key=f"edu_desc_{i}"
            )
            edu.description = edited_desc["Description"].tolist() if not edited_desc.empty else []

            if st.button(f"Remove Education {i+1}", key=f"remove_edu_{i}"):
                data.education.pop(i)
                st.rerun()

    # Add new education button
    if st.button("➕ Add Education", use_container_width=True):
        data.education.append(Education())
        st.rerun()

    st.divider()

    # Certifications
    st.subheader("🏆 Certifications")
    certs_df = pd.DataFrame({"Certification": data.certifications or []})
    edited_certs = st.data_editor(
        certs_df,
        use_container_width=True,
        num_rows="dynamic",
        key="certifications_editor"
    )
    data.certifications = edited_certs["Certification"].tolist() if not edited_certs.empty else []

    st.divider()

    # Languages
    st.subheader("🌍 Languages")
    langs_df = pd.DataFrame({"Language": data.languages or []})
    edited_langs = st.data_editor(
        langs_df,
        use_container_width=True,
        num_rows="dynamic",
        key="languages_editor"
    )
    data.languages = edited_langs["Language"].tolist() if not edited_langs.empty else []

    return data


def render_job_data_editor(job_data: JobDescriptionData) -> JobDescriptionData:
    """Render editable form for JobDescriptionData.

    Args:
        job_data: JobDescriptionData to edit

    Returns:
        Updated JobDescriptionData with user edits
    """
    data = deepcopy(job_data)

    st.subheader("📋 Job Information")
    col1, col2 = st.columns(2)
    with col1:
        data.title = st.text_input(
            "Job Title",
            value=data.title or "",
            key="job_title"
        )
        data.company = st.text_input(
            "Company",
            value=data.company or "",
            key="job_company"
        )
    with col2:
        data.location = st.text_input(
            "Location",
            value=data.location or "",
            key="job_location"
        )
        data.experience_level = st.text_input(
            "Experience Level",
            value=data.experience_level or "",
            key="job_exp_level"
        )

    st.divider()

    # Full job description
    st.subheader("📝 Job Description")
    data.description = st.text_area(
        "Description",
        value=data.description or "",
        height=150,
        key="job_description"
    )

    st.divider()

    # Required Skills
    st.subheader("🔴 Required Skills")
    req_skills_df = pd.DataFrame({"Skill": data.required_skills or []})
    edited_req_skills = st.data_editor(
        req_skills_df,
        use_container_width=True,
        num_rows="dynamic",
        key="required_skills_editor"
    )
    data.required_skills = edited_req_skills["Skill"].tolist() if not edited_req_skills.empty else []

    st.divider()

    # Preferred Skills
    st.subheader("🟡 Preferred Skills")
    pref_skills_df = pd.DataFrame({"Skill": data.preferred_skills or []})
    edited_pref_skills = st.data_editor(
        pref_skills_df,
        use_container_width=True,
        num_rows="dynamic",
        key="preferred_skills_editor"
    )
    data.preferred_skills = edited_pref_skills["Skill"].tolist() if not edited_pref_skills.empty else []

    st.divider()

    # Keywords
    st.subheader("🔑 Keywords")
    keywords_df = pd.DataFrame({"Keyword": data.keywords or []})
    edited_keywords = st.data_editor(
        keywords_df,
        use_container_width=True,
        num_rows="dynamic",
        key="keywords_editor"
    )
    data.keywords = edited_keywords["Keyword"].tolist() if not edited_keywords.empty else []

    st.divider()

    # Education Requirements
    st.subheader("🎓 Education Requirements")
    edu_reqs_df = pd.DataFrame({"Requirement": data.education_requirements or []})
    edited_edu_reqs = st.data_editor(
        edu_reqs_df,
        use_container_width=True,
        num_rows="dynamic",
        key="education_requirements_editor"
    )
    data.education_requirements = edited_edu_reqs["Requirement"].tolist() if not edited_edu_reqs.empty else []

    return data


def render_optimization_result_editor(opt_result: OptimizationResult) -> OptimizationResult:
    """Render editable form for OptimizationResult.

    Args:
        opt_result: OptimizationResult to edit

    Returns:
        Updated OptimizationResult with user edits
    """
    data = deepcopy(opt_result)

    # Display scores as metrics
    st.subheader("📊 Optimization Scores")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Original Score", f"{data.original_score:.1f}", "/100")
    with col2:
        st.metric("Optimized Score", f"{data.optimized_score:.1f}", "/100")
    with col3:
        improvement = data.optimized_score - data.original_score
        st.metric("Improvement", f"{improvement:+.1f}")
    with col4:
        st.metric("ATS Compliance", f"{data.ats_compliance_score:.1f}%")

    st.divider()

    # Optimized resume editor
    st.subheader("📄 Optimized Resume")
    if data.optimized_resume:
        data.optimized_resume = render_resume_data_editor(data.optimized_resume)

    st.divider()

    # Recommendations
    st.subheader("💡 Recommendations")
    recs_df = pd.DataFrame({"Recommendation": data.recommendations or []})
    edited_recs = st.data_editor(
        recs_df,
        use_container_width=True,
        num_rows="dynamic",
        key="recommendations_editor"
    )
    data.recommendations = edited_recs["Recommendation"].tolist() if not edited_recs.empty else []

    st.divider()

    # Missing Keywords
    st.subheader("🔑 Missing Keywords")
    missing_kw_df = pd.DataFrame({"Keyword": data.missing_keywords or []})
    edited_missing_kw = st.data_editor(
        missing_kw_df,
        use_container_width=True,
        num_rows="dynamic",
        key="missing_keywords_editor"
    )
    data.missing_keywords = edited_missing_kw["Keyword"].tolist() if not edited_missing_kw.empty else []

    st.divider()

    # Improvements
    st.subheader("✅ Improvements Applied")
    improvements_df = pd.DataFrame({"Improvement": data.improvements or []})
    edited_improvements = st.data_editor(
        improvements_df,
        use_container_width=True,
        num_rows="dynamic",
        key="improvements_editor"
    )
    data.improvements = edited_improvements["Improvement"].tolist() if not edited_improvements.empty else []

    return data
