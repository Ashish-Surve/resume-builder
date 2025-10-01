
# src/resume_optimizer/core/resume_parser/parser.py
"""
Resume parser module using spaCy and other NLP libraries.
Implements Strategy pattern for different parsing approaches.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
import spacy
from pypdf import PdfReader
import docx
import re

from ...utils.exceptions import ParsingError, FileProcessingError
from ..models import ResumeData, ContactInfo, FileType


class BaseResumeParser(ABC):
    """Abstract base class for resume parsers."""

    @abstractmethod
    def parse(self, file_path: Path) -> ResumeData:
        """Parse resume from file and return structured data."""
        pass


class TextExtractor:
    """Handles text extraction from different file formats."""

    @staticmethod
    def extract_from_pdf(file_path: Path) -> str:
        """Extract text from PDF file."""
        try:
            reader = PdfReader(str(file_path))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise FileProcessingError(f"Failed to extract text from PDF: {e}")

    @staticmethod
    def extract_from_docx(file_path: Path) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(str(file_path))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise FileProcessingError(f"Failed to extract text from DOCX: {e}")

    @staticmethod
    def extract_from_txt(file_path: Path) -> str:
        """Extract text from TXT file."""
        try:
            return file_path.read_text(encoding='utf-8')
        except Exception as e:
            raise FileProcessingError(f"Failed to extract text from TXT: {e}")


class ContactInfoExtractor:
    """Extracts contact information from resume text."""

    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\b(?:\+?1[-.]?)?\(?[0-9]{3}\)?[-.]?[0-9]{3}[-.]?[0-9]{4}\b')
        self.linkedin_pattern = re.compile(r'linkedin\.com/in/[A-Za-z0-9-]+', re.IGNORECASE)
        self.github_pattern = re.compile(r'github\.com/[A-Za-z0-9-]+', re.IGNORECASE)

    def extract(self, text: str, nlp_doc) -> ContactInfo:
        """Extract contact information from text."""
        contact = ContactInfo()

        # Extract email
        email_match = self.email_pattern.search(text)
        if email_match:
            contact.email = email_match.group()

        # Extract phone
        phone_match = self.phone_pattern.search(text)
        if phone_match:
            contact.phone = phone_match.group()

        # Extract LinkedIn
        linkedin_match = self.linkedin_pattern.search(text)
        if linkedin_match:
            contact.linkedin = linkedin_match.group()

        # Extract GitHub
        github_match = self.github_pattern.search(text)
        if github_match:
            contact.github = github_match.group()

        # Extract name using NER
        for ent in nlp_doc.ents:
            if ent.label_ == "PERSON" and not contact.name:
                contact.name = ent.text
                break

        return contact


class SkillsExtractor:
    """Extracts skills from resume text."""

    def __init__(self):
        # Common technical skills (can be expanded or loaded from file)
        self.tech_skills = {
            'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'swift',
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express',
            'django', 'flask', 'spring', 'laravel', 'mongodb', 'mysql', 
            'postgresql', 'redis', 'docker', 'kubernetes', 'aws', 'azure',
            'git', 'jenkins', 'terraform', 'ansible', 'linux', 'windows',
            'machine learning', 'data science', 'artificial intelligence',
            'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn'
        }

    def extract(self, text: str, nlp_doc) -> List[str]:
        """Extract skills from text."""
        text_lower = text.lower()
        found_skills = []

        # Find technical skills
        for skill in self.tech_skills:
            if skill in text_lower:
                found_skills.append(skill.title())

        # Remove duplicates and return
        return list(set(found_skills))


class SpacyResumeParser(BaseResumeParser):
    """Resume parser using spaCy NLP library."""

    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise ParsingError("spaCy English model not found. Run: python -m spacy download en_core_web_sm")

        self.text_extractor = TextExtractor()
        self.contact_extractor = ContactInfoExtractor()
        self.skills_extractor = SkillsExtractor()
        self.logger = logging.getLogger(__name__)

    def parse(self, file_path: Path) -> ResumeData:
        """Parse resume from file and return structured data."""
        try:
            # Determine file type
            file_type = self._get_file_type(file_path)

            # Extract text
            raw_text = self._extract_text(file_path, file_type)

            # Process with spaCy
            doc = self.nlp(raw_text)

            # Extract structured information
            resume_data = ResumeData(
                raw_text=raw_text,
                file_path=file_path,
                file_type=file_type
            )

            # Extract contact information
            resume_data.contact_info = self.contact_extractor.extract(raw_text, doc)

            # Extract skills
            resume_data.skills = self.skills_extractor.extract(raw_text, doc)

            # Extract sections
            self._extract_sections(resume_data, raw_text, doc)

            return resume_data

        except Exception as e:
            self.logger.error(f"Failed to parse resume: {e}")
            raise ParsingError(f"Failed to parse resume from {file_path}: {e}")

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

    def _extract_sections(self, resume_data: ResumeData, text: str, doc) -> None:
        """Extract resume sections like experience, education, etc."""
        lines = text.split('\n')
        current_section = None

        section_keywords = {
            'experience': ['experience', 'work history', 'employment', 'professional experience'],
            'education': ['education', 'academic background', 'qualifications'],
            'summary': ['summary', 'profile', 'objective', 'about'],
            'skills': ['skills', 'technical skills', 'competencies'],
            'certifications': ['certifications', 'certificates', 'credentials']
        }

        for line in lines:
            line_lower = line.strip().lower()

            # Check if line indicates a section header
            for section, keywords in section_keywords.items():
                if any(keyword in line_lower for keyword in keywords):
                    current_section = section
                    break

            # Process content based on current section
            if current_section == 'summary' and line.strip() and not any(kw in line_lower for keywords in section_keywords.values() for kw in keywords):
                if not resume_data.summary:
                    resume_data.summary = line.strip()
                else:
                    resume_data.summary += " " + line.strip()


class ResumeParserFactory:
    """Factory class for creating resume parsers."""

    @staticmethod
    def create_parser(parser_type: str = "spacy") -> BaseResumeParser:
        """Create a resume parser instance."""
        if parser_type == "spacy":
            return SpacyResumeParser()
        else:
            raise ValueError(f"Unknown parser type: {parser_type}")
