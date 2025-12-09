
# src/resume_optimizer/core/models.py
"""
Data models for the Resume Optimizer application.
Implements Pydantic models for validation and serialization.
"""

from typing import List, Optional
from datetime import datetime
from enum import Enum
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


class FileType(Enum):
    """Supported file types enumeration."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class OptimizationStatus(Enum):
    """Status of optimization process."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ContactInfo(BaseModel):
    """Contact information data model.

    Attributes:
        name: Full name of the person
        email: Email address (validated)
        phone: Phone number
        address: Physical address
        linkedin: LinkedIn profile URL
        github: GitHub profile URL
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format."""
        if v and '@' not in v:
            raise ValueError(f"Invalid email format: {v}")
        return v

    @field_validator('linkedin', 'github')
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Ensure URLs are properly formatted."""
        if v and not v.startswith(('http://', 'https://', 'linkedin.com', 'github.com')):
            # Try to construct a proper URL if it's just a username/path
            if 'linkedin' in cls.model_fields and v:
                return v
            if 'github' in cls.model_fields and v:
                return v
        return v


class Experience(BaseModel):
    """Work experience data model.

    Attributes:
        company: Company or organization name
        position: Job title or role
        duration: Human-readable duration (e.g., "May 2021 - Present", "2020-2023")
        start_date: Start date (ISO format preferred)
        end_date: End date (ISO format preferred) or None if current
        description: List of responsibilities and achievements
        skills_used: Technical and soft skills used in this role
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    company: Optional[str] = None
    position: Optional[str] = None
    duration: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: List[str] = Field(default_factory=list)
    skills_used: List[str] = Field(default_factory=list)

    @field_validator('description', mode='before')
    @classmethod
    def ensure_description_list(cls, v):
        """Ensure description is always a list."""
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return v


class Education(BaseModel):
    """Education data model.

    Attributes:
        institution: School, university, or institution name
        degree: Degree type (e.g., Bachelor of Science, MBA)
        field: Field of study or major
        graduation_date: Graduation date or expected graduation
        gpa: Grade point average
        description: Additional details (honors, coursework, achievements)
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None
    description: List[str] = Field(default_factory=list)

    @field_validator('description', mode='before')
    @classmethod
    def ensure_description_list(cls, v):
        """Ensure description is always a list."""
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return v


class ResumeData(BaseModel):
    """Resume data model containing all parsed information.

    Attributes:
        contact_info: Contact information (name, email, phone, etc.)
        summary: Professional summary or objective statement
        skills: List of technical and soft skills
        experience: Work experience entries
        education: Education background
        certifications: Professional certifications and credentials
        languages: Spoken/written languages
        raw_text: Original raw text from the resume file
        file_path: Path to the original resume file
        file_type: Type of the file (PDF, DOCX, TXT)
        created_at: Timestamp when the resume was parsed
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    raw_text: str = ""
    file_path: Optional[Path] = None
    file_type: Optional[FileType] = None
    created_at: datetime = Field(default_factory=datetime.now)


class JobDescriptionData(BaseModel):
    """Job description data model.

    Attributes:
        title: Job title
        company: Company name
        location: Job location
        description: Full job description text
        required_skills: Must-have skills
        preferred_skills: Nice-to-have skills
        experience_level: Required experience level
        education_requirements: Education requirements
        keywords: Important keywords for ATS
        raw_text: Original job posting text
        created_at: Timestamp when parsed
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description: str = ""
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_level: Optional[str] = None
    education_requirements: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    raw_text: str = ""
    created_at: datetime = Field(default_factory=datetime.now)


class OptimizationResult(BaseModel):
    """Optimization result data model.

    Attributes:
        original_score: Score of original resume (0-100)
        optimized_score: Score after optimization (0-100)
        improvements: List of improvements made
        missing_keywords: Keywords missing from resume
        suggested_additions: Suggested content to add
        ats_compliance_score: ATS compatibility score (0-100)
        readability_score: Readability score (0-100)
        recommendations: List of recommendations
        optimized_resume: The optimized resume data
        status: Current optimization status
        created_at: Timestamp of optimization
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    original_score: float = 0.0
    optimized_score: float = 0.0
    improvements: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    suggested_additions: List[str] = Field(default_factory=list)
    ats_compliance_score: float = 0.0
    readability_score: float = 0.0
    recommendations: List[str] = Field(default_factory=list)
    optimized_resume: Optional['ResumeData'] = None
    status: OptimizationStatus = OptimizationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)


class ProcessingSession(BaseModel):
    """Session data for tracking processing state.

    Attributes:
        session_id: Unique session identifier
        resume_data: Parsed resume data
        job_data: Parsed job description data
        optimization_result: Optimization results
        company_name: Target company name
        applicant_name: Name of the applicant
        status: Current session status
        created_at: Session creation timestamp
        updated_at: Last update timestamp
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    session_id: str
    resume_data: Optional[ResumeData] = None
    job_data: Optional[JobDescriptionData] = None
    optimization_result: Optional[OptimizationResult] = None
    company_name: Optional[str] = None
    applicant_name: Optional[str] = None
    status: OptimizationStatus = OptimizationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# Update forward references for Pydantic
OptimizationResult.model_rebuild()
