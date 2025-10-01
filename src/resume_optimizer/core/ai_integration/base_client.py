
# src/resume_optimizer/core/ai_integration/base_client.py
"""
Base AI client implementation with common functionality.
Implements Template Method pattern.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from ...utils.exceptions import AIServiceError


class BaseAIClient(ABC):
    """Abstract base class for AI service clients."""

    def __init__(self, api_key: str, max_retries: int = 3, timeout: int = 30):
        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def _initialize_client(self) -> Any:
        """Initialize the specific AI client."""
        pass

    @abstractmethod
    def _make_request(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Make a request to the AI service."""
        pass

    def analyze_resume_job_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Analyze how well a resume matches a job description."""
        prompt = f"""
        As an expert ATS (Applicant Tracking System) analyst and career counselor, analyze the following resume against the job description.

        Job Description:
        {job_description}

        Resume:
        {resume_text}

        Please provide:
        1. A match score (0-100)
        2. Missing keywords that should be added
        3. Specific recommendations for improvement
        4. ATS optimization suggestions
        5. Skills alignment analysis

        Format your response as structured data that can be parsed.
        """

        try:
            response = self._make_request_with_retry([
                {"role": "system", "content": "You are an expert ATS analyst and career counselor."},
                {"role": "user", "content": prompt}
            ])

            return self._parse_analysis_response(response)

        except Exception as e:
            self.logger.error(f"Failed to analyze resume-job match: {e}")
            raise AIServiceError(f"AI analysis failed: {e}")

    def optimize_resume_section(self, section_text: str, job_keywords: List[str], section_type: str) -> str:
        """Optimize a specific resume section."""
        keywords_str = ", ".join(job_keywords)

        prompt = f"""
        Optimize the following {section_type} section of a resume to better match the target job keywords while maintaining truthfulness and professional tone.

        Target Keywords: {keywords_str}

        Current {section_type} Section:
        {section_text}

        Please provide an optimized version that:
        1. Incorporates relevant keywords naturally
        2. Maintains truthfulness
        3. Uses action verbs and quantifiable achievements
        4. Is ATS-friendly
        5. Follows best practices for resume writing
        """

        try:
            response = self._make_request_with_retry([
                {"role": "system", "content": "You are an expert resume writer and career counselor."},
                {"role": "user", "content": prompt}
            ])

            return response.strip()

        except Exception as e:
            self.logger.error(f"Failed to optimize resume section: {e}")
            raise AIServiceError(f"Section optimization failed: {e}")

    def _make_request_with_retry(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Make request with retry logic."""
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                return self._make_request(messages, **kwargs)
            except Exception as e:
                last_exception = e
                wait_time = 2 ** attempt  # Exponential backoff
                self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)

        raise AIServiceError(f"All retry attempts failed. Last error: {last_exception}")

    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured data."""
        # This is a simplified parser - in practice, you'd want more robust parsing
        # possibly using structured output from the AI or regex patterns

        result = {
            "match_score": 0,
            "missing_keywords": [],
            "recommendations": [],
            "ats_suggestions": [],
            "raw_response": response
        }

        # Basic parsing logic (can be enhanced)
        lines = response.split('\n')
        for line in lines:
            if "score" in line.lower() and any(char.isdigit() for char in line):
                # Extract numeric score
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    result["match_score"] = int(numbers[0])

        return result
