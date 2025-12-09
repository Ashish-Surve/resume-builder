# src/resume_optimizer/core/job_analyzer/gemini_analyzer.py
"""
Gemini-based job description analyzer.
Uses Google's Gemini API for intelligent job description analysis in one call.
"""

import logging
import json
from typing import Optional

from ..models import JobDescriptionData
from ..ai_integration.gemini_client import GeminiClient
from ...utils.exceptions import ParsingError


class GeminiJobAnalyzer:
    """
    Analyzes job descriptions using Gemini AI in a single API call.

    This analyzer maintains API compatibility with JobDescriptionAnalyzer
    but uses Gemini's language understanding capabilities for more accurate
    and comprehensive job description analysis.

    Features:
    - Single API call for complete analysis
    - Intelligent extraction of skills, requirements, and keywords
    - Context-aware understanding of job descriptions
    - Automatic caching to reduce API costs
    - Rate limiting for API compliance
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash-lite",
        temperature: float = 0.2,
        enable_cache: bool = True
    ):
        """
        Initialize the Gemini-based job analyzer.

        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model: Gemini model to use (default: gemini-2.5-flash-lite - fastest and most cost-effective)
            temperature: Temperature for generation (0.0-1.0, lower = more deterministic)
            enable_cache: Enable response caching to reduce API calls
        """
        self.gemini = GeminiClient(
            api_key=api_key,
            model=model,
            temperature=temperature,
            enable_cache=enable_cache
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"GeminiJobAnalyzer initialized with model: {model}")

    def analyze(self, job_text: str, company_name: Optional[str] = None) -> JobDescriptionData:
        """
        Analyze job description text and extract structured information.

        This method maintains API compatibility with JobDescriptionAnalyzer.analyze()
        and returns the same JobDescriptionData structure.

        Args:
            job_text: Raw job description text
            company_name: Optional company name (if not in job text)

        Returns:
            JobDescriptionData: Structured job information

        Raises:
            ParsingError: If analysis fails
        """
        try:
            self.logger.info("Starting Gemini-based job description analysis")

            # Prepare the system prompt
            system_prompt = self._get_system_prompt()

            # Prepare the user prompt with job text
            user_prompt = self._get_user_prompt(job_text, company_name)

            # Call Gemini API
            response = self.gemini.invoke(system=system_prompt, user=user_prompt)

            # Parse JSON response
            parsed_data = json.loads(response)

            # Convert to JobDescriptionData model
            job_data = self._convert_to_job_data(parsed_data, job_text)

            self.logger.info("Job description analysis completed successfully")
            return job_data

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Gemini response as JSON: {e}")
            self.logger.error(f"Response was: {response[:200]}...")
            raise ParsingError(f"Failed to parse Gemini response: {e}")
        except Exception as e:
            self.logger.error(f"Failed to analyze job description with Gemini: {e}")
            raise ParsingError(f"Job description analysis failed: {e}")

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for Gemini.

        Returns:
            str: System prompt instructing Gemini on the analysis task
        """
        return """You are an expert job description analyzer. Your task is to analyze job postings and extract structured information.

Analyze the job description and extract the following information in JSON format:

1. **title**: The job title/position name
2. **company**: Company name (if mentioned)
3. **location**: Job location (city, state, or remote status)
4. **description**: A clean, concise summary of the role (2-3 sentences)
5. **required_skills**: Array of must-have technical and soft skills explicitly marked as required
6. **preferred_skills**: Array of nice-to-have skills or those marked as preferred/bonus
7. **experience_level**: Required experience (e.g., "3-5 years", "Senior level", "Entry level")
8. **education_requirements**: Array of education requirements (degrees, certifications)
9. **keywords**: Array of 15-20 important keywords for ATS optimization (technical terms, tools, methodologies, industry-specific terms)

Guidelines:
- Be precise and extract only what's explicitly mentioned
- For skills, include specific technologies, programming languages, frameworks, tools, and methodologies
- Distinguish clearly between required (must-have) and preferred (nice-to-have) skills
- Keywords should include both technical terms and important domain concepts
- If information is not found, use empty string for strings or empty array for arrays
- Ensure all arrays contain unique, non-duplicate items
- Return ONLY valid JSON, no additional text or explanation

Example output format:
{
  "title": "Senior Software Engineer",
  "company": "Tech Corp",
  "location": "San Francisco, CA (Remote)",
  "description": "A senior software engineer role focused on building scalable backend systems. The position involves designing APIs, optimizing databases, and mentoring junior developers.",
  "required_skills": ["Python", "Django", "PostgreSQL", "REST API", "Docker", "AWS"],
  "preferred_skills": ["Kubernetes", "GraphQL", "React", "Machine Learning"],
  "experience_level": "5+ years of experience",
  "education_requirements": ["Bachelor's degree in Computer Science or related field"],
  "keywords": ["Python", "Django", "PostgreSQL", "REST API", "Docker", "AWS", "backend", "scalable systems", "API design", "database optimization", "microservices", "CI/CD", "agile", "team leadership"]
}"""

    def _get_user_prompt(self, job_text: str, company_name: Optional[str] = None) -> str:
        """
        Create the user prompt with job description text.

        Args:
            job_text: Raw job description text
            company_name: Optional company name

        Returns:
            str: User prompt with job text
        """
        prompt = f"Analyze this job description and extract structured information:\n\n{job_text}"

        if company_name:
            prompt += f"\n\nNote: The company name is: {company_name}"

        return prompt

    def _convert_to_job_data(self, parsed_data: dict, raw_text: str) -> JobDescriptionData:
        """
        Convert parsed JSON data to JobDescriptionData model.

        Args:
            parsed_data: Dictionary from Gemini's JSON response
            raw_text: Original job description text

        Returns:
            JobDescriptionData: Validated Pydantic model
        """
        # Create JobDescriptionData with parsed information
        job_data = JobDescriptionData(
            title=parsed_data.get("title"),
            company=parsed_data.get("company"),
            location=parsed_data.get("location"),
            description=parsed_data.get("description", ""),
            required_skills=parsed_data.get("required_skills", []),
            preferred_skills=parsed_data.get("preferred_skills", []),
            experience_level=parsed_data.get("experience_level"),
            education_requirements=parsed_data.get("education_requirements", []),
            keywords=parsed_data.get("keywords", []),
            raw_text=raw_text
        )

        return job_data

    def clear_cache(self):
        """Clear the Gemini client's cache."""
        self.gemini.clear_cache()
        self.logger.info("Gemini cache cleared")

    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            dict: Cache statistics from Gemini client
        """
        return self.gemini.get_cache_stats()
