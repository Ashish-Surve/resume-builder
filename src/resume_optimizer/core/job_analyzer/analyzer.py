
# src/resume_optimizer/core/job_analyzer/analyzer.py
"""
Job description analyzer module.
Implements Strategy pattern for different analysis approaches.
"""

import logging
import re
from typing import List, Set, Optional
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

from ..models import JobDescriptionData
from ...utils.exceptions import ParsingError


class JobDescriptionAnalyzer:
    """Analyzes job descriptions to extract key information and requirements."""

    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise ParsingError("spaCy English model not found. Run: python -m spacy download en_core_web_sm")

        self.logger = logging.getLogger(__name__)
        self.skill_keywords = self._load_skill_keywords()
        self.stop_words = set(self.nlp.Defaults.stop_words)

    def analyze(self, job_text: str, company_name: Optional[str] = None) -> JobDescriptionData:
        """Analyze job description text and extract structured information."""
        try:
            job_data = JobDescriptionData(
                raw_text=job_text,
                company=company_name
            )

            # Process with spaCy
            doc = self.nlp(job_text)

            # Extract basic information
            job_data.title = self._extract_job_title(job_text, doc)
            job_data.location = self._extract_location(job_text, doc)
            job_data.description = self._clean_description(job_text)

            # Extract requirements
            job_data.required_skills = self._extract_required_skills(job_text)
            job_data.preferred_skills = self._extract_preferred_skills(job_text)
            job_data.experience_level = self._extract_experience_level(job_text)
            job_data.education_requirements = self._extract_education_requirements(job_text)

            # Extract keywords using TF-IDF
            job_data.keywords = self._extract_keywords(job_text)

            return job_data

        except Exception as e:
            self.logger.error(f"Failed to analyze job description: {e}")
            raise ParsingError(f"Job description analysis failed: {e}")

    def _extract_job_title(self, text: str, doc) -> Optional[str]:
        """Extract job title from the text."""
        # Look for common job title patterns
        title_patterns = [
            r'^(.+?)(?:\n|$)',  # First line
            r'(?:position|role|job|title)\s*:?\s*([^\n]+)',
            r'(?:seeking|hiring)\s+(?:a|an)?\s*([^\n]+)'
        ]

        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                title = match.group(1).strip()
                if len(title) < 100 and not any(skip in title.lower() for skip in ['we are', 'company', 'about']):
                    return title

        return None

    def _extract_location(self, text: str, doc) -> Optional[str]:
        """Extract location information."""
        # Use NER to find locations
        locations = []
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC']:  # Geopolitical entities, locations
                locations.append(ent.text)

        # Also look for common location patterns
        location_patterns = [
            r'location\s*:?\s*([^\n]+)',
            r'(?:based in|located in)\s+([^\n,.]+)',
            r'([A-Z][a-z]+,\s*[A-Z]{2})\b'  # City, State format
        ]

        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                locations.append(match.group(1).strip())

        return locations[0] if locations else None

    def _clean_description(self, text: str) -> str:
        """Clean and normalize job description text."""
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text)
        cleaned = re.sub(r'[^\w\s.,;:()\-]', '', cleaned)
        return cleaned.strip()

    def _extract_required_skills(self, text: str) -> List[str]:
        """Extract required skills from job text."""
        skills = set()

        # Look for required skills sections
        required_sections = re.findall(
            r'(?:required|must have|essential).*?(?:preferred|nice to have|qualifications|responsibilities|$)',
            text, re.IGNORECASE | re.DOTALL
        )

        for section in required_sections:
            skills.update(self._find_skills_in_text(section))

        # If no specific section found, extract from entire text
        if not skills:
            skills.update(self._find_skills_in_text(text))

        return list(skills)

    def _extract_preferred_skills(self, text: str) -> List[str]:
        """Extract preferred/nice-to-have skills from job text."""
        skills = set()

        # Look for preferred skills sections
        preferred_sections = re.findall(
            r'(?:preferred|nice to have|bonus|plus).*?(?:required|responsibilities|qualifications|$)',
            text, re.IGNORECASE | re.DOTALL
        )

        for section in preferred_sections:
            skills.update(self._find_skills_in_text(section))

        return list(skills)

    def _find_skills_in_text(self, text: str) -> Set[str]:
        """Find technical skills in text."""
        found_skills = set()
        text_lower = text.lower()

        for skill in self.skill_keywords:
            if skill.lower() in text_lower:
                found_skills.add(skill)

        return found_skills

    def _extract_experience_level(self, text: str) -> Optional[str]:
        """Extract required experience level."""
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(?:entry|junior|mid|senior|principal|lead|director)\s*level',
            r'(?:0-2|2-4|4-6|6-8|8-10|10\+)\s*years?'
        ]

        for pattern in experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)

        return None

    def _extract_education_requirements(self, text: str) -> List[str]:
        """Extract education requirements."""
        education = []

        education_patterns = [
            r"(?:bachelor'?s?|ba|bs)\s*(?:degree)?\s*(?:in\s*[^\n.,]+)?",
            r"(?:master'?s?|ma|ms)\s*(?:degree)?\s*(?:in\s*[^\n.,]+)?",
            r"(?:phd|doctorate)\s*(?:in\s*[^\n.,]+)?",
            r"(?:high school|hs)\s*(?:diploma|graduate)",
            r"associate'?s?\s*degree"
        ]

        for pattern in education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            education.extend(matches)

        return list(set(education))

    def _extract_keywords(self, text: str, max_features: int = 20) -> List[str]:
        """Extract important keywords using TF-IDF."""
        try:
            # Clean text for TF-IDF
            cleaned_text = self._clean_text_for_tfidf(text)

            # Use TF-IDF to find important terms
            vectorizer = TfidfVectorizer(
                max_features=max_features * 2,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1
            )

            tfidf_matrix = vectorizer.fit_transform([cleaned_text])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]

            # Get top keywords
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)

            # Filter and return top keywords
            keywords = []
            for keyword, score in keyword_scores[:max_features]:
                if len(keyword) > 2 and not keyword.isdigit():
                    keywords.append(keyword)

            return keywords

        except Exception as e:
            self.logger.error(f"Failed to extract keywords: {e}")
            return []

    def _clean_text_for_tfidf(self, text: str) -> str:
        """Clean text for TF-IDF processing."""
        # Remove special characters and normalize
        cleaned = re.sub(r'[^a-zA-Z\s]', ' ', text)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.lower().strip()

    def _load_skill_keywords(self) -> List[str]:
        """Load list of technical skills and keywords."""
        # This would typically be loaded from a file or database
        return [
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'PHP', 'Ruby', 'Swift',
            'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express',
            'Django', 'Flask', 'Spring', 'Laravel', 'MongoDB', 'MySQL', 
            'PostgreSQL', 'Redis', 'Docker', 'Kubernetes', 'AWS', 'Azure',
            'Git', 'Jenkins', 'Terraform', 'Ansible', 'Linux', 'Windows',
            'Machine Learning', 'Data Science', 'Artificial Intelligence',
            'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn',
            'SQL', 'NoSQL', 'REST API', 'GraphQL', 'Microservices',
            'Agile', 'Scrum', 'DevOps', 'CI/CD', 'Test Driven Development',
            'Object Oriented Programming', 'Functional Programming',
            'Data Structures', 'Algorithms', 'System Design'
        ]
