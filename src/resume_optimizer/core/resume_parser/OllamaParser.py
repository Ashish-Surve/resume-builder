# src/resume_optimizer/core/resume_parser/OllamaParser.py
"""
Resume parser using Ollama with Llama 3.1 for local AI-powered parsing.
Parses resume in one go without external API calls.
"""

import logging
import re
import json
from pathlib import Path
from typing import Dict, Any

from ...utils.exceptions import ParsingError, FileProcessingError
from ..models import ResumeData, ContactInfo, FileType, Experience, Education
from ..ai_integration.ollama_client import OllamaClient
from .parser import BaseResumeParser, TextExtractor


class OllamaResumeParser(BaseResumeParser):
    """
    Resume parser using Ollama with Llama 3.1 for local AI-powered parsing.
    Parses the entire resume in one go for speed and consistency.
    """

    def __init__(self, ollama_client: OllamaClient = None, model: str = "llama3.1:8b"):
        """
        Initialize OllamaResumeParser.

        Args:
            ollama_client: Optional pre-configured OllamaClient
            model: Model to use (default: llama3.1:8b)
        """
        self.ollama_client = ollama_client or OllamaClient(model=model)
        self.logger = logging.getLogger(__name__)
        self.text_extractor = TextExtractor()

    def parse(self, file_path: Path) -> ResumeData:
        """
        Parse resume from file and return structured data.

        Args:
            file_path: Path to the resume file (PDF, DOCX, or TXT)

        Returns:
            ResumeData: Structured resume data

        Raises:
            ParsingError: If parsing fails
        """
        try:
            # Determine file type
            file_type = self._get_file_type(file_path)

            # Extract text from file
            raw_text = self._extract_text(file_path, file_type)

            if not raw_text.strip():
                raise ParsingError("No text could be extracted from the file")

            self.logger.info("Parsing resume with Ollama (Llama 3.1)...")

            # Parse using Ollama in one go
            parsed_data = self._parse_with_ollama(raw_text)

            # Convert to ResumeData object
            resume_data = self._convert_to_resume_data(parsed_data, raw_text, file_path, file_type)

            return resume_data

        except Exception as e:
            self.logger.error(f"Failed to parse resume with Ollama: {e}")
            raise ParsingError(f"Failed to parse resume from {file_path}: {e}")

    def _parse_with_ollama(self, text: str) -> Dict[str, Any]:
        """
        Use Ollama (Llama 3.1) to parse resume text in one go.

        Args:
            text: Resume text to parse

        Returns:
            Dict containing parsed resume information
        """
        system_prompt = """You are an expert resume parser. Your task is to extract ALL information from the resume and return it as a valid JSON object.

IMPORTANT RULES:
1. Return ONLY a valid JSON object - no explanations, no markdown, no extra text
2. Use these EXACT keys (case-sensitive):
   - "Name": string (full name)
   - "Email": string (email address)
   - "Phone": string (phone number)
   - "LinkedIn": string or null (LinkedIn URL)
   - "GitHub": string or null (GitHub URL)
   - "Address": string or null (location/address)
   - "Summary": string (professional summary/objective)
   - "Skills": array of strings (all technical and soft skills)
   - "Experience": array of experience objects
   - "Education": array of education objects
   - "Certifications": array of strings or null
   - "Languages": array of strings or null

3. Each Experience object must have:
   - "Company": string
   - "Position": string
   - "Duration": string (e.g., "Jan 2020 - Present")
   - "StartDate": string or null
   - "EndDate": string or null
   - "Description": array of strings (bullet points/responsibilities)

4. Each Education object must have:
   - "Institution": string
   - "Degree": string
   - "Field": string (field of study)
   - "Year": string (graduation year)
   - "GPA": string or null
   - "Description": array of strings

5. Extract ALL skills mentioned anywhere in the resume
6. Extract ALL experience entries with full descriptions
7. Use null for missing fields, empty arrays [] for empty lists

RESPOND WITH ONLY THE JSON OBJECT."""

        user_prompt = f"""Parse this resume and extract all information into the JSON format specified.

RESUME TEXT:
---
{text}
---

Return only valid JSON:"""

        try:
            response = self.ollama_client.invoke(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                max_tokens=4096
            )

            # Try to parse JSON from response
            parsed_data = self._extract_json(response)

            if parsed_data:
                self.logger.info("Successfully parsed resume with Ollama")
                return parsed_data
            else:
                self.logger.warning("First Ollama response not valid JSON, retrying...")
                return self._retry_parsing(text)

        except Exception as e:
            self.logger.error(f"Ollama parsing failed: {e}")
            return {}

    def _retry_parsing(self, text: str) -> Dict[str, Any]:
        """Retry parsing with a stricter prompt."""
        strict_prompt = """You MUST return ONLY a valid JSON object. No text before or after.
Extract resume information into this exact structure:
{
  "Name": "...",
  "Email": "...",
  "Phone": "...",
  "LinkedIn": null,
  "GitHub": null,
  "Address": null,
  "Summary": "...",
  "Skills": ["skill1", "skill2"],
  "Experience": [{"Company": "...", "Position": "...", "Duration": "...", "StartDate": null, "EndDate": null, "Description": ["..."]}],
  "Education": [{"Institution": "...", "Degree": "...", "Field": "...", "Year": "...", "GPA": null, "Description": []}],
  "Certifications": [],
  "Languages": []
}

Return ONLY JSON, nothing else."""

        user_prompt = f"Parse this resume into JSON:\n\n{text[:3000]}"  # Limit text length for retry

        try:
            response = self.ollama_client.invoke(
                system_prompt=strict_prompt,
                user_prompt=user_prompt,
                temperature=0.05,
                max_tokens=4096
            )
            return self._extract_json(response)
        except Exception as e:
            self.logger.error(f"Retry parsing failed: {e}")
            return {}

    def _extract_json(self, response: str) -> Dict[str, Any]:
        """Extract JSON from model response."""
        if not response:
            return {}

        # Clean up common issues
        response = response.strip()

        # Remove markdown code blocks if present
        if response.startswith('```'):
            response = re.sub(r'^```(?:json)?\n?', '', response)
            response = re.sub(r'\n?```$', '', response)

        # Try direct parsing
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object in response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return {}

    def _convert_to_resume_data(
        self,
        parsed_data: Dict[str, Any],
        raw_text: str,
        file_path: Path,
        file_type: FileType
    ) -> ResumeData:
        """Convert parsed dictionary to ResumeData object."""

        def safe_str(value) -> str:
            """Safely convert value to string."""
            if value is None:
                return ""
            if isinstance(value, str):
                return value.strip()
            if isinstance(value, dict):
                # Try to get a meaningful value from dict
                for key in ['value', 'text', 'content']:
                    if key in value:
                        return safe_str(value[key])
                return str(value)
            return str(value).strip()

        def safe_list(value) -> list:
            """Safely convert value to list of strings."""
            if value is None:
                return []
            if isinstance(value, list):
                return [safe_str(item) for item in value if item]
            if isinstance(value, str):
                # Split by common separators
                items = re.split(r'[,\n•\u2022\|;]+', value)
                return [item.strip() for item in items if item.strip()]
            return []

        # Initialize ResumeData
        resume_data = ResumeData(
            raw_text=raw_text,
            file_path=file_path,
            file_type=file_type
        )

        # Populate contact info
        resume_data.contact_info = ContactInfo(
            name=safe_str(parsed_data.get('Name', '')),
            email=safe_str(parsed_data.get('Email', '')),
            phone=safe_str(parsed_data.get('Phone', '')),
            linkedin=safe_str(parsed_data.get('LinkedIn', '')),
            github=safe_str(parsed_data.get('GitHub', '')),
            address=safe_str(parsed_data.get('Address', ''))
        )

        # Populate summary
        resume_data.summary = safe_str(parsed_data.get('Summary', ''))

        # Populate skills
        resume_data.skills = safe_list(parsed_data.get('Skills', []))

        # Populate experience
        experience_data = parsed_data.get('Experience', [])
        resume_data.experience = []

        if isinstance(experience_data, list):
            for exp in experience_data:
                if isinstance(exp, dict):
                    exp_obj = Experience(
                        company=safe_str(exp.get('Company', '')),
                        position=safe_str(exp.get('Position', '')),
                        duration=safe_str(exp.get('Duration', '')),
                        start_date=safe_str(exp.get('StartDate', '')),
                        end_date=safe_str(exp.get('EndDate', '')),
                        description=safe_list(exp.get('Description', []))
                    )
                    if exp_obj.company or exp_obj.position:
                        resume_data.experience.append(exp_obj)

        # Populate education
        education_data = parsed_data.get('Education', [])
        resume_data.education = []

        if isinstance(education_data, list):
            for edu in education_data:
                if isinstance(edu, dict):
                    edu_obj = Education(
                        institution=safe_str(edu.get('Institution', '')),
                        degree=safe_str(edu.get('Degree', '')),
                        field=safe_str(edu.get('Field', '')),
                        graduation_date=safe_str(edu.get('Year', '')),
                        gpa=safe_str(edu.get('GPA', '')),
                        description=safe_list(edu.get('Description', []))
                    )
                    if edu_obj.institution or edu_obj.degree:
                        resume_data.education.append(edu_obj)

        # Populate certifications
        resume_data.certifications = safe_list(parsed_data.get('Certifications', []))

        # Populate languages
        resume_data.languages = safe_list(parsed_data.get('Languages', []))

        return resume_data

    def _get_file_type(self, file_path: Path) -> FileType:
        """Determine file type from extension."""
        suffix = file_path.suffix.lower()
        if suffix == '.pdf':
            return FileType.PDF
        elif suffix == '.docx':
            return FileType.DOCX
        elif suffix == '.txt':
            return FileType.TXT
        else:
            raise ParsingError(f"Unsupported file type: {suffix}")

    def _extract_text(self, file_path: Path, file_type: FileType) -> str:
        """Extract text based on file type."""
        if file_type == FileType.PDF:
            return self.text_extractor.extract_from_pdf(file_path)
        elif file_type == FileType.DOCX:
            return self.text_extractor.extract_from_docx(file_path)
        elif file_type == FileType.TXT:
            return self.text_extractor.extract_from_txt(file_path)
        else:
            raise ParsingError(f"Unsupported file type: {file_type}")
