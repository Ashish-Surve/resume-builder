# src/resume_optimizer/core/job_analyzer/ollama_analyzer.py
"""
Ollama-based job description analyzer.
Uses local Ollama models for intelligent job description analysis.
"""

import logging
import json
from typing import Optional

from ..models import JobDescriptionData
from ..ai_integration.ollama_client import OllamaClient
from ...utils.exceptions import ParsingError


class OllamaJobAnalyzer:
    """
    Analyzes job descriptions using local Ollama models in a single API call.

    This analyzer maintains API compatibility with JobDescriptionAnalyzer
    and GeminiJobAnalyzer but uses locally-running Ollama models for
    private, offline job description analysis.

    Features:
    - Single API call for complete analysis
    - Intelligent extraction of skills, requirements, and keywords
    - No external API keys required
    - Runs completely locally for privacy
    """

    DEFAULT_MODEL = "llama3.1:8b"

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = "http://localhost:11434",
        timeout: int = 120,
        temperature: float = 0.2
    ):
        """
        Initialize the Ollama-based job analyzer.

        Args:
            model: Ollama model to use (default: llama3.1:8b)
            base_url: Ollama server URL (default: http://localhost:11434)
            timeout: Request timeout in seconds
            temperature: Temperature for generation (0.0-1.0, lower = more deterministic)
        """
        self.client = OllamaClient(
            model=model,
            base_url=base_url,
            timeout=timeout
        )
        self.temperature = temperature
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"OllamaJobAnalyzer initialized with model: {model}")

    def analyze(self, job_text: str, company_name: Optional[str] = None) -> JobDescriptionData:
        """
        Analyze job description text and extract structured information.

        This method maintains API compatibility with JobDescriptionAnalyzer.analyze()
        and GeminiJobAnalyzer.analyze(), returning the same JobDescriptionData structure.

        Args:
            job_text: Raw job description text
            company_name: Optional company name (if not in job text)

        Returns:
            JobDescriptionData: Structured job information

        Raises:
            ParsingError: If analysis fails
        """
        try:
            self.logger.info("Starting Ollama-based job description analysis")

            # Prepare the prompts
            system_prompt = self._get_system_prompt()
            user_prompt = self._get_user_prompt(job_text, company_name)

            # Call Ollama API
            response = self.client.invoke(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=self.temperature
            )

            # Parse JSON response
            parsed_data = self._extract_json(response)

            # Convert to JobDescriptionData model
            job_data = self._convert_to_job_data(parsed_data, job_text)

            self.logger.info("Job description analysis completed successfully")
            return job_data

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Ollama response as JSON: {e}")
            raise ParsingError(f"Failed to parse Ollama response: {e}")
        except Exception as e:
            self.logger.error(f"Failed to analyze job description with Ollama: {e}")
            raise ParsingError(f"Job description analysis failed: {e}")

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for Ollama.

        Returns:
            str: System prompt instructing the model on the analysis task
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

    def _extract_json(self, response: str) -> dict:
        """
        Extract JSON from the model response.

        Args:
            response: Raw model response

        Returns:
            dict: Parsed JSON data

        Raises:
            json.JSONDecodeError: If JSON cannot be extracted
        """
        import re

        # Try direct parsing first
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try to find JSON in markdown code blocks
        code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
        if code_block_match:
            try:
                return json.loads(code_block_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Try to find JSON object in response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # If all parsing fails, raise error
        raise json.JSONDecodeError("Could not extract JSON from response", response, 0)

    def _convert_to_job_data(self, parsed_data: dict, raw_text: str) -> JobDescriptionData:
        """
        Convert parsed JSON data to JobDescriptionData model.

        Args:
            parsed_data: Dictionary from model's JSON response
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

    def is_available(self) -> bool:
        """
        Check if Ollama server is running and model is available.

        Returns:
            bool: True if Ollama is available
        """
        return self.client.is_available()
