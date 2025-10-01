
# src/resume_optimizer/core/models.py
"""
Data models for the Resume Optimizer application.
Implements dataclasses following PEP 8 standards.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from pathlib import Path


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


@dataclass
class ContactInfo:
    """Contact information data model."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None


@dataclass
class Experience:
    """Work experience data model."""
    company: Optional[str] = None
    position: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: List[str] = field(default_factory=list)
    skills_used: List[str] = field(default_factory=list)


@dataclass
class Education:
    """Education data model."""
    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None


@dataclass
class ResumeData:
    """Resume data model containing all parsed information."""
    contact_info: ContactInfo = field(default_factory=ContactInfo)
    summary: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    experience: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    raw_text: str = ""
    file_path: Optional[Path] = None
    file_type: Optional[FileType] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class JobDescriptionData:
    """Job description data model."""
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description: str = ""
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    experience_level: Optional[str] = None
    education_requirements: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    raw_text: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationResult:
    """Optimization result data model."""
    original_score: float = 0.0
    optimized_score: float = 0.0
    improvements: List[str] = field(default_factory=list)
    missing_keywords: List[str] = field(default_factory=list)
    suggested_additions: List[str] = field(default_factory=list)
    ats_compliance_score: float = 0.0
    readability_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    optimized_resume: Optional[ResumeData] = None
    status: OptimizationStatus = OptimizationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProcessingSession:
    """Session data for tracking processing state."""
    session_id: str
    resume_data: Optional[ResumeData] = None
    job_data: Optional[JobDescriptionData] = None
    optimization_result: Optional[OptimizationResult] = None
    company_name: Optional[str] = None
    applicant_name: Optional[str] = None
    status: OptimizationStatus = OptimizationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
