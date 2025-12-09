"""Validation logic for resume and job data."""

from typing import Tuple, List
from resume_optimizer.core.models import ResumeData, JobDescriptionData


def validate_resume_data(data: ResumeData) -> Tuple[bool, List[str]]:
    """Validate resume data.

    Args:
        data: ResumeData to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check contact info
    if not data.contact_info.name or not data.contact_info.name.strip():
        errors.append("Contact name is required")

    if not data.contact_info.email or '@' not in data.contact_info.email:
        errors.append("Valid email is required")

    # Check skills
    if not data.skills or len(data.skills) == 0:
        errors.append("At least one skill is required")

    # Check experience
    if not data.experience or len(data.experience) == 0:
        errors.append("At least one experience entry is required")
    else:
        for i, exp in enumerate(data.experience):
            if not exp.company or not exp.company.strip():
                errors.append(f"Experience {i+1}: Company name is required")
            if not exp.position or not exp.position.strip():
                errors.append(f"Experience {i+1}: Position is required")

    # Check education
    if not data.education or len(data.education) == 0:
        errors.append("At least one education entry is required")
    else:
        for i, edu in enumerate(data.education):
            if not edu.institution or not edu.institution.strip():
                errors.append(f"Education {i+1}: Institution is required")
            if not edu.degree or not edu.degree.strip():
                errors.append(f"Education {i+1}: Degree is required")

    return len(errors) == 0, errors


def validate_job_data(data: JobDescriptionData) -> Tuple[bool, List[str]]:
    """Validate job description data.

    Args:
        data: JobDescriptionData to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check job title
    if not data.title or not data.title.strip():
        errors.append("Job title is required")

    # Check company
    if not data.company or not data.company.strip():
        errors.append("Company name is required")

    # Check description
    if not data.description or not data.description.strip():
        errors.append("Job description is required")

    # Check required skills
    if not data.required_skills or len(data.required_skills) == 0:
        errors.append("At least one required skill is needed")

    return len(errors) == 0, errors
