
# src/resume_optimizer/utils/exceptions.py
"""
Custom exceptions for the Resume Optimizer application.
"""


class ResumeOptimizerError(Exception):
    """Base exception for Resume Optimizer application."""
    pass


class ParsingError(ResumeOptimizerError):
    """Exception raised when resume or job description parsing fails."""
    pass


class AIServiceError(ResumeOptimizerError):
    """Exception raised when AI service calls fail."""
    pass


class ValidationError(ResumeOptimizerError):
    """Exception raised when data validation fails."""
    pass


class ConfigurationError(ResumeOptimizerError):
    """Exception raised when configuration is invalid."""
    pass


class FileProcessingError(ResumeOptimizerError):
    """Exception raised when file processing fails."""
    pass
