import logging
import re
import json
from pathlib import Path
from typing import Dict, Any

from ...utils.exceptions import ParsingError, FileProcessingError
from ..models import ResumeData, ContactInfo, FileType, Experience, Education
from ..ai_integration.gemini_client import GeminiClient
from .parser import BaseResumeParser, TextExtractor


class GeminiResumeParser(BaseResumeParser):
    """Resume parser using Gemini AI for complex resume parsing."""

    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
        self.logger = logging.getLogger(__name__)
        self.text_extractor = TextExtractor()

    def parse(self, file_path: Path) -> ResumeData:
        """Parse resume from file and return structured data.

        This matches the SpacyResumeParser API signature.

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

            # Parse using Gemini
            gemini_data = self.parse_with_gemini(raw_text)

            # Convert to ResumeData object
            resume_data = self._convert_to_resume_data(gemini_data, raw_text, file_path, file_type)

            return resume_data

        except Exception as e:
            self.logger.error(f"Failed to parse resume with Gemini: {e}")
            raise ParsingError(f"Failed to parse resume from {file_path}: {e}")

    def parse_with_gemini(self, text: str) -> Dict[str, Any]:
        """Use Gemini to parse resume text.

        This sends a strict prompt asking Gemini to return ONLY valid JSON
        with Title‑Case keys (Strict Capitalization). If the first response
        is not valid JSON, a second strict conversion call is made.
        """
        try:
            system_prompt = """You are an expert resume parser. Convert the provided resume TEXT into STRICT JSON only.
- Use these exact Title‑Case keys (case sensitive): "Name","Email","Phone","LinkedIn","GitHub","Summary","Skills","Experience","Education","Certifications","Projects".
- Use null for missing scalar fields.
- Skills must be an array of strings.
- Experience must be an array of objects with keys: "Company","Position","Duration","Description","StartDate","EndDate". "Description" must be an array of strings.
- Education must be an array of objects with keys: "Institution","Degree","Field","Year","GPA","Description". "Description" must be an array of strings.
- Return only a single valid JSON object, nothing else (no surrounding text, no markdown, no comments).
Example:
{
  "Name": "Jane Doe",
  "Email": "jane@example.com",
  "Phone": "+1234567890",
  "LinkedIn": "https://linkedin.com/in/janedoe",
  "GitHub": "https://github.com/janedoe",
  "Summary": "Experienced software engineer...",
  "Skills": ["Python","Django","AWS"],
  "Experience": [
    {
      "Company": "Example Inc",
      "Position": "Senior Engineer",
      "Duration": "2019 - Present",
      "Description": ["Led backend team","Improved CI/CD"],
      "StartDate": "2019-06",
      "EndDate": null
    }
  ],
  "Education": [
    {
      "Institution": "State University",
      "Degree": "Bachelor of Science",
      "Field": "Computer Science",
      "Year": "2018",
      "GPA": null,
      "Description": []
    }
  ],
  "Certifications": null,
  "Projects": null
}"""

            user_prompt = f"Convert this resume text to the strict JSON schema above. Text:\n\n{text}"

            response = self.gemini_client.invoke(system_prompt, user_prompt)

            try:
                parsed_data = json.loads(response)
                return parsed_data
            except json.JSONDecodeError:
                self.logger.warning("Gemini first response not valid JSON — requesting strict JSON conversion again.")
                # Ask Gemini again to strictly convert the ORIGINAL text into Title‑Case JSON
                return self._extract_from_text_response(text)

        except Exception as e:
            self.logger.error(f"Gemini parsing failed: {e}")
            return {}
    
    # def parse_with_gemini(self, text: str) -> Dict[str, Any]:
    #     """Use Gemini to parse resume text.

    #     This is the internal method that sends text to Gemini for parsing.

    #     Args:
    #         text: Resume text to parse

    #     Returns:
    #         Dict containing parsed resume information
    #     """
    #     try:
    #         system_prompt = """You are an expert resume parser. Extract structured information from the resume text and return it in JSON format with these fields:
    #         - name: Full name of the person
    #         - email: Email address
    #         - phone: Phone number
    #         - linkedin: LinkedIn profile URL
    #         - github: GitHub profile URL
    #         - summary: Professional summary or objective
    #         - skills: List of technical and professional skills
    #         - experience: List of work experiences with company, position, duration, and description
    #         - education: List of education entries with institution, degree, field, year
    #         - certifications: Certifications and credentials
    #         - projects: Notable projects (if mentioned)

    #         For experience and education, return as arrays of objects with proper structure.
    #         Return only valid JSON, no additional text."""

    #         user_prompt = f"Parse this resume text:\n\n{text}"

    #         response = self.gemini_client.invoke(system_prompt, user_prompt)

    #         # Try to parse JSON response
    #         import json
    #         try:
    #             parsed_data = json.loads(response)
    #             return parsed_data
    #         except json.JSONDecodeError:
    #             # If not valid JSON, try to extract sections manually from response
    #             self.logger.warning("Gemini response is not valid JSON, using fallback extraction")
    #             return self._extract_from_text_response(response)

    #     except Exception as e:
    #         self.logger.error(f"Gemini parsing failed: {e}")
    #         return {}

    def _convert_to_resume_data(
        self, 
        gemini_data: Dict[str, Any], 
        raw_text: str, 
        file_path: Path, 
        file_type: FileType
    ) -> ResumeData:
        """Convert Gemini parsed dictionary to ResumeData object.

        Args:
            gemini_data: Dictionary from Gemini parser
            raw_text: Original resume text
            file_path: Path to the file
            file_type: Type of the file

        Returns:
            ResumeData: Structured resume data object
        """
        # Helper to normalize fields that may come as JSON-strings, nested JSON, dicts or lists
        def _normalize_possible_json_field(value):
            # If it's a string that looks like JSON, try to parse it
            if isinstance(value, str):
                s = value.strip()
                if (s.startswith('{') or s.startswith('[')):
                    try:
                        parsed = json.loads(s)
                        return parsed
                    except Exception:
                        # fall through and return original string
                        return value
            return value

        def _extract_text_from_possible_obj(v, keys=None):
            """Return a clean string from v which can be str/list/dict.
            If dict, prefer keys in `keys` (list) or join values.
            If list, join elements.
            """
            v = _normalize_possible_json_field(v)
            if v is None:
                return ""
            if isinstance(v, str):
                return v.strip()
            if isinstance(v, list):
                return " \n".join(str(x).strip() for x in v if x)
            if isinstance(v, dict):
                # Prefer requested keys if provided
                if keys:
                    for k in keys:
                        if k in v:
                            return _extract_text_from_possible_obj(v[k])
                # fallback: join values
                return " ".join(str(x).strip() for x in v.values() if x)
            return str(v)

        def _extract_list_from_possible_obj(v):
            """Return a list of strings from v which can be str/list/dict."""
            v = _normalize_possible_json_field(v)
            if v is None:
                return []
            if isinstance(v, list):
                return [str(x).strip() for x in v if x is not None and str(x).strip()]
            if isinstance(v, dict):
                # Common case: {'skills': [...]} or {'Skills': [...]}
                for key in ('Skills', 'skills'):
                    if key in v and isinstance(v[key], list):
                        return [str(x).strip() for x in v[key] if x]
                    if key in v and isinstance(v[key], str):
                        # parse string into list
                        return [s.strip() for s in re.split(r'[,\n•\u2022\|;]+', v[key]) if s.strip()]
                # fallback: use values
                vals = []
                for x in v.values():
                    vals.extend(_extract_list_from_possible_obj(x))
                return vals
            if isinstance(v, str):
                s = v.strip()
                # If string looks like JSON array, try parse
                if s.startswith('['):
                    try:
                        parsed = json.loads(s)
                        return _extract_list_from_possible_obj(parsed)
                    except Exception:
                        pass
                # Split by common separators
                items = [sitem.strip() for sitem in re.split(r'[,\n•\u2022\|;]+', s) if sitem.strip()]
                return items
            return [str(v).strip()]

        # Initialize ResumeData
        resume_data = ResumeData(
            raw_text=raw_text,
            file_path=file_path,
            file_type=file_type
        )

        # Populate contact info
        resume_data.contact_info = ContactInfo(
            name=_extract_text_from_possible_obj(gemini_data.get('Name', '')),
            email=_extract_text_from_possible_obj(gemini_data.get('Email', '')),
            phone=_extract_text_from_possible_obj(gemini_data.get('Phone', '')),
            linkedin=_extract_text_from_possible_obj(gemini_data.get('LinkedIn', '')),
            github=_extract_text_from_possible_obj(gemini_data.get('GitHub', ''))
        )

        # Populate summary (ensure it's a plain string)
        resume_data.summary = _extract_text_from_possible_obj(gemini_data.get('Summary', ''))

        # Populate skills (ensure it's a list of strings)
        resume_data.skills = _extract_list_from_possible_obj(gemini_data.get('Skills', []))

        # Populate experience
        experience_data = gemini_data.get('Experience', [])
        resume_data.experience = []
        experience_data = _normalize_possible_json_field(experience_data)
        if isinstance(experience_data, list):
            for exp in experience_data:
                if isinstance(exp, dict):
                    desc = exp.get('Description', [])
                    if isinstance(desc, str):
                        desc_list = [d.strip() for d in re.split(r'[\n•\u2022]+', desc) if d.strip()]
                    elif isinstance(desc, list):
                        desc_list = [str(d).strip() for d in desc if d]
                    else:
                        desc_list = [str(desc)]

                    exp_obj = Experience(
                        company=_extract_text_from_possible_obj(exp.get('Company', '')),
                        position=_extract_text_from_possible_obj(exp.get('Position', '')),
                        duration=_extract_text_from_possible_obj(exp.get('Duration', '')),
                        description=desc_list,
                        start_date=exp.get('StartDate'),
                        end_date=exp.get('EndDate')
                    )
                    resume_data.experience.append(exp_obj)

        # Populate education
        education_data = gemini_data.get('Education', [])
        resume_data.education = []
        education_data = _normalize_possible_json_field(education_data)
        if isinstance(education_data, list):
            for edu in education_data:
                if isinstance(edu, dict):
                    edu_obj = Education(
                        institution=_extract_text_from_possible_obj(edu.get('Institution', '')),
                        degree=_extract_text_from_possible_obj(edu.get('Degree', '')),
                        field=_extract_text_from_possible_obj(edu.get('Field', '')),
                        graduation_date=_extract_text_from_possible_obj(edu.get('Year', '')),
                        gpa=edu.get('GPA'),
                        description=_extract_list_from_possible_obj(edu.get('Description', []))
                    )
                    resume_data.education.append(edu_obj)

        # Certifications
        certifications_raw = gemini_data.get('Certifications', [])
        # treat literal "null" as empty
        if isinstance(certifications_raw, str) and certifications_raw.strip().lower() == 'null':
            certifications_raw = []
        resume_data.certifications = _extract_list_from_possible_obj(certifications_raw)

        # Projects (keep as string or empty) only if model supports it
        if hasattr(resume_data, 'projects'):
            resume_data.projects = _extract_text_from_possible_obj(gemini_data.get('Projects', ''))

        return resume_data

    def _get_file_type(self, file_path: Path) -> FileType:
        """Determine file type from extension.

        Args:
            file_path: Path to the file

        Returns:
            FileType: Enum representing the file type

        Raises:
            ParsingError: If file type is not supported
        """
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
        """Extract text based on file type.

        Args:
            file_path: Path to the file
            file_type: Type of the file

        Returns:
            str: Extracted text

        Raises:
            ParsingError: If extraction fails
        """
        if file_type == FileType.PDF:
            return self.text_extractor.extract_from_pdf(file_path)
        elif file_type == FileType.DOCX:
            return self.text_extractor.extract_from_docx(file_path)
        elif file_type == FileType.TXT:
            return self.text_extractor.extract_from_txt(file_path)
        else:
            raise ParsingError(f"Unsupported file type: {file_type}")

    # def _extract_from_text_response(self, response: str) -> Dict[str, Any]:
    #     """Extract data from Gemini's text response when JSON parsing fails.

    #     Args:
    #         response: Text response from Gemini

    #     Returns:
    #         Dict containing extracted information
    #     """
    #     data = {}

    #     # Extract email
    #     email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', response)
    #     if email_match:
    #         data['email'] = email_match.group()

    #     # Extract skills (look for lists)
    #     skills_section = re.search(r'skills?[:\-\s]*(.*?)(?:\n\n|\n[A-Z])', response, re.IGNORECASE | re.DOTALL)
    #     if skills_section:
    #         skills_text = skills_section.group(1)
    #         skills = re.findall(r'[A-Za-z][A-Za-z0-9\s\.\+#-]+', skills_text)
    #         data['skills'] = [skill.strip() for skill in skills if len(skill.strip()) > 2][:20]

    #     return data
    

    def _extract_from_text_response(self, text: str) -> Dict[str, Any]:
        """Fallback that asks Gemini explicitly to produce strict Title‑Case JSON from the raw text."""
        try:
            strict_system = """You MUST return a single VALID JSON object and NOTHING ELSE.
Use the exact Title‑Case keys and structure described previously:
"Name","Email","Phone","LinkedIn","GitHub","Summary","Skills","Experience","Education","Certifications","Projects".
Ensure arrays and nulls are used correctly. Do NOT include any explanatory text."""
            user_prompt = f"Strictly convert the following resume text into the required Title‑Case JSON schema. Respond ONLY with JSON.\n\n{text}"

            response = self.gemini_client.invoke(strict_system, user_prompt)

            try:
                parsed = json.loads(response)
                return parsed
            except json.JSONDecodeError:
                self.logger.error("Strict Gemini JSON conversion failed; response was not JSON.")
                return {}

        except Exception as e:
            self.logger.error(f"Strict JSON extraction via Gemini failed: {e}")
            return {}
