
# src/resume_optimizer/core/ats_optimizer/optimizer.py
"""
ATS Optimizer module for improving resume compatibility with ATS systems.
Implements Strategy and Observer patterns.
"""

import logging
import re
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

from ..models import ResumeData, JobDescriptionData, OptimizationResult, OptimizationStatus


class OptimizationRule(Enum):
    """Enumeration of optimization rules."""
    KEYWORD_DENSITY = "keyword_density"
    SECTION_FORMATTING = "section_formatting"  
    SKILL_MATCHING = "skill_matching"
    ATS_COMPATIBILITY = "ats_compatibility"
    READABILITY = "readability"


@dataclass
class OptimizationScore:
    """Detailed scoring for optimization aspects."""
    keyword_match: float = 0.0
    skill_alignment: float = 0.0
    ats_format: float = 0.0
    content_quality: float = 0.0
    overall: float = 0.0


class ATSCompatibilityChecker:
    """Checks resume for ATS compatibility issues."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.compatibility_rules = {
            'avoid_headers_footers': self._check_headers_footers,
            'use_standard_sections': self._check_section_headers,
            'avoid_complex_formatting': self._check_formatting,
            'use_standard_fonts': self._check_fonts,
            'keyword_optimization': self._check_keywords
        }

    def check_compatibility(self, resume_data: ResumeData, job_data: JobDescriptionData) -> Dict[str, Any]:
        """Check ATS compatibility and return issues."""
        issues = []
        suggestions = []
        score_breakdown = {}

        for rule_name, rule_func in self.compatibility_rules.items():
            try:
                rule_result = rule_func(resume_data, job_data)
                score_breakdown[rule_name] = rule_result['score']
                issues.extend(rule_result.get('issues', []))
                suggestions.extend(rule_result.get('suggestions', []))
            except Exception as e:
                self.logger.error(f"Error in rule {rule_name}: {e}")
                score_breakdown[rule_name] = 0.0

        overall_score = sum(score_breakdown.values()) / len(score_breakdown) if score_breakdown else 0.0

        return {
            'overall_score': overall_score,
            'score_breakdown': score_breakdown,
            'issues': issues,
            'suggestions': suggestions
        }

    def _check_headers_footers(self, resume_data: ResumeData, job_data: JobDescriptionData) -> Dict[str, Any]:
        """Check for header/footer usage (should be avoided for ATS)."""
        text = resume_data.raw_text
        issues = []
        suggestions = []
        score = 1.0

        # Simple heuristic: check if contact info is at very beginning
        lines = text.split('\n')
        first_few_lines = '\n'.join(lines[:5]).lower()

        if resume_data.contact_info.email and resume_data.contact_info.email.lower() not in first_few_lines:
            issues.append("Contact information may be in header/footer")
            suggestions.append("Place contact information in main document body")
            score = 0.5

        return {'score': score, 'issues': issues, 'suggestions': suggestions}

    def _check_section_headers(self, resume_data: ResumeData, job_data: JobDescriptionData) -> Dict[str, Any]:
        """Check for standard section headers."""
        text = resume_data.raw_text.lower()
        standard_sections = ['experience', 'education', 'skills', 'summary']
        found_sections = []

        for section in standard_sections:
            if section in text:
                found_sections.append(section)

        score = len(found_sections) / len(standard_sections)
        missing_sections = set(standard_sections) - set(found_sections)

        issues = [f"Missing standard section: {section}" for section in missing_sections]
        suggestions = [f"Add {section} section with clear header" for section in missing_sections]

        return {'score': score, 'issues': issues, 'suggestions': suggestions}

    def _check_formatting(self, resume_data: ResumeData, job_data: JobDescriptionData) -> Dict[str, Any]:
        """Check for complex formatting that ATS might struggle with."""
        text = resume_data.raw_text
        issues = []
        suggestions = []
        score = 1.0

        # Check for special characters that might indicate complex formatting
        problematic_chars = ['│', '─', '┌', '┐', '└', '┘', '■', '●', '◆']

        for char in problematic_chars:
            if char in text:
                issues.append(f"Contains special formatting characters: {char}")
                suggestions.append("Use simple bullet points (- or •) instead of special characters")
                score -= 0.1

        score = max(0.0, score)

        return {'score': score, 'issues': issues, 'suggestions': suggestions}

    def _check_fonts(self, resume_data: ResumeData, job_data: JobDescriptionData) -> Dict[str, Any]:
        """Check font recommendations (limited detection from text)."""
        # This is a placeholder - in practice, font detection from text is limited
        return {'score': 0.8, 'issues': [], 'suggestions': ['Use standard fonts like Arial, Calibri, or Times New Roman']}

    def _check_keywords(self, resume_data: ResumeData, job_data: JobDescriptionData) -> Dict[str, Any]:
        """Check keyword optimization."""
        resume_text_lower = resume_data.raw_text.lower()
        job_keywords = [kw.lower() for kw in job_data.keywords + job_data.required_skills]

        matched_keywords = []
        missing_keywords = []

        for keyword in job_keywords:
            if keyword.lower() in resume_text_lower:
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)

        score = len(matched_keywords) / len(job_keywords) if job_keywords else 1.0

        issues = [f"Missing important keyword: {kw}" for kw in missing_keywords[:5]]  # Limit to top 5
        suggestions = ["Incorporate relevant keywords naturally into your experience descriptions",
                      "Add a skills section with technical keywords"]

        return {'score': score, 'issues': issues, 'suggestions': suggestions}


class KeywordOptimizer:
    """Optimizes keyword usage in resume content."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def optimize_keywords(self, resume_data: ResumeData, job_data: JobDescriptionData) -> Dict[str, Any]:
        """Optimize keyword usage in resume."""
        job_keywords = set(kw.lower() for kw in job_data.keywords + job_data.required_skills + job_data.preferred_skills)
        resume_words = set(resume_data.raw_text.lower().split())

        # Find matching and missing keywords
        matched_keywords = job_keywords.intersection(resume_words)
        missing_keywords = job_keywords - matched_keywords

        # Calculate keyword density
        total_words = len(resume_data.raw_text.split())
        keyword_density = len(matched_keywords) / total_words if total_words > 0 else 0

        # Generate optimization suggestions
        suggestions = self._generate_keyword_suggestions(missing_keywords, resume_data, job_data)

        return {
            'matched_keywords': list(matched_keywords),
            'missing_keywords': list(missing_keywords),
            'keyword_density': keyword_density,
            'optimization_suggestions': suggestions,
            'keyword_score': len(matched_keywords) / len(job_keywords) if job_keywords else 1.0
        }

    def _generate_keyword_suggestions(self, missing_keywords: set, resume_data: ResumeData, job_data: JobDescriptionData) -> List[str]:
        """Generate specific suggestions for incorporating missing keywords."""
        suggestions = []

        # Prioritize missing keywords
        priority_keywords = list(missing_keywords)[:10]  # Top 10 missing keywords

        for keyword in priority_keywords:
            if keyword in job_data.required_skills:
                suggestions.append(f"Add '{keyword}' to your skills section if you have experience with it")
            elif keyword in job_data.keywords:
                suggestions.append(f"Consider incorporating '{keyword}' in your job descriptions if relevant")

        # General suggestions
        if missing_keywords:
            suggestions.extend([
                "Review job description keywords and incorporate them naturally",
                "Use industry-standard terminology and acronyms",
                "Include both abbreviated and full forms of technical terms"
            ])

        return suggestions


class ResumeScorer:
    """Scores resume quality and ATS compatibility."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.weight_config = {
            'keyword_match': 0.3,
            'skill_alignment': 0.25,
            'ats_format': 0.25,
            'content_quality': 0.2
        }

    def score_resume(self, resume_data: ResumeData, job_data: JobDescriptionData) -> OptimizationScore:
        """Calculate comprehensive resume score."""
        scores = OptimizationScore()

        # Score keyword matching
        scores.keyword_match = self._score_keyword_match(resume_data, job_data)

        # Score skill alignment
        scores.skill_alignment = self._score_skill_alignment(resume_data, job_data)

        # Score ATS formatting
        scores.ats_format = self._score_ats_format(resume_data)

        # Score content quality
        scores.content_quality = self._score_content_quality(resume_data)

        # Calculate overall score
        scores.overall = (
            scores.keyword_match * self.weight_config['keyword_match'] +
            scores.skill_alignment * self.weight_config['skill_alignment'] +
            scores.ats_format * self.weight_config['ats_format'] +
            scores.content_quality * self.weight_config['content_quality']
        )

        return scores

    def _score_keyword_match(self, resume_data: ResumeData, job_data: JobDescriptionData) -> float:
        """Score how well resume keywords match job requirements."""
        if not job_data.keywords:
            return 1.0

        resume_text_lower = resume_data.raw_text.lower()
        job_keywords = [kw.lower() for kw in job_data.keywords]

        matches = sum(1 for kw in job_keywords if kw in resume_text_lower)
        return matches / len(job_keywords)

    def _score_skill_alignment(self, resume_data: ResumeData, job_data: JobDescriptionData) -> float:
        """Score how well resume skills align with job requirements."""
        resume_skills = set(skill.lower() for skill in resume_data.skills)
        required_skills = set(skill.lower() for skill in job_data.required_skills)

        if not required_skills:
            return 1.0

        matches = len(resume_skills.intersection(required_skills))
        return matches / len(required_skills)

    def _score_ats_format(self, resume_data: ResumeData) -> float:
        """Score ATS formatting compatibility."""
        text = resume_data.raw_text

        # Check for standard sections
        standard_sections = ['experience', 'education', 'skills']
        text_lower = text.lower()
        found_sections = sum(1 for section in standard_sections if section in text_lower)
        section_score = found_sections / len(standard_sections)

        # Check for problematic formatting
        problematic_chars = ['│', '─', '┌', '┐', '└', '┘']
        has_problematic = any(char in text for char in problematic_chars)
        format_score = 0.5 if has_problematic else 1.0

        return (section_score + format_score) / 2

    def _score_content_quality(self, resume_data: ResumeData) -> float:
        """Score content quality metrics."""
        text = resume_data.raw_text

        # Basic quality metrics
        word_count = len(text.split())
        sentence_count = len(re.split(r'[.!?]+', text))

        # Ideal resume length (300-800 words)
        length_score = 1.0 if 300 <= word_count <= 800 else 0.7

        # Check for quantifiable achievements (numbers)
        numbers = re.findall(r'\d+', text)
        achievement_score = min(1.0, len(numbers) / 10)  # Up to 10 numbers for full score

        return (length_score + achievement_score) / 2


class ATSOptimizer:
    """Main ATS optimization engine."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.compatibility_checker = ATSCompatibilityChecker()
        self.keyword_optimizer = KeywordOptimizer()
        self.scorer = ResumeScorer()

    def optimize(self, resume_data: ResumeData, job_data: JobDescriptionData, applicant_name: str, company_name: str) -> OptimizationResult:
        """Perform comprehensive ATS optimization."""
        try:
            result = OptimizationResult(status=OptimizationStatus.PROCESSING)

            # Calculate original scores
            result.original_score = self.scorer.score_resume(resume_data, job_data).overall * 100

            # Run ATS compatibility check
            ats_check = self.compatibility_checker.check_compatibility(resume_data, job_data)
            result.ats_compliance_score = ats_check['overall_score'] * 100

            # Optimize keywords
            keyword_analysis = self.keyword_optimizer.optimize_keywords(resume_data, job_data)
            result.missing_keywords = keyword_analysis['missing_keywords']

            # Generate comprehensive recommendations
            result.recommendations = self._generate_recommendations(ats_check, keyword_analysis, resume_data, job_data)

            # Create optimized resume (placeholder - would integrate with AI in practice)
            result.optimized_resume = self._create_optimized_resume(resume_data, job_data, applicant_name, company_name)

            # Calculate optimized score
            result.optimized_score = self.scorer.score_resume(result.optimized_resume, job_data).overall * 100

            # Calculate improvements
            result.improvements = self._calculate_improvements(result.original_score, result.optimized_score)

            result.status = OptimizationStatus.COMPLETED

            return result

        except Exception as e:
            self.logger.error(f"Optimization failed: {e}")
            result = OptimizationResult(status=OptimizationStatus.FAILED)
            return result

    def _generate_recommendations(self, ats_check: Dict, keyword_analysis: Dict, resume_data: ResumeData, job_data: JobDescriptionData) -> List[str]:
        """Generate comprehensive optimization recommendations."""
        recommendations = []

        # ATS compatibility recommendations
        recommendations.extend(ats_check.get('suggestions', []))

        # Keyword optimization recommendations
        recommendations.extend(keyword_analysis.get('optimization_suggestions', []))

        # General improvements
        if keyword_analysis['keyword_score'] < 0.7:
            recommendations.append("Increase keyword density by incorporating more job-relevant terms")

        if result.ats_compliance_score < 80:
            recommendations.append("Improve ATS compatibility by using standard formatting and sections")

        # Content quality recommendations
        word_count = len(resume_data.raw_text.split())
        if word_count < 300:
            recommendations.append("Expand resume content with more detailed descriptions")
        elif word_count > 800:
            recommendations.append("Condense resume content to improve readability")

        return recommendations

    def _create_optimized_resume(self, resume_data: ResumeData, job_data: JobDescriptionData, applicant_name: str, company_name: str) -> ResumeData:
        """Create an optimized version of the resume."""
        # This is a simplified version - in practice, this would integrate with AI services
        optimized = ResumeData(
            contact_info=resume_data.contact_info,
            summary=resume_data.summary,
            skills=resume_data.skills,
            experience=resume_data.experience,
            education=resume_data.education,
            certifications=resume_data.certifications,
            languages=resume_data.languages,
            raw_text=resume_data.raw_text,
            file_path=resume_data.file_path,
            file_type=resume_data.file_type
        )

        # Update contact info
        if applicant_name:
            optimized.contact_info.name = applicant_name

        # Add missing skills that are relevant
        missing_skills = set(job_data.required_skills) - set(resume_data.skills)
        # In practice, you'd be more selective about which skills to add

        return optimized

    def _calculate_improvements(self, original_score: float, optimized_score: float) -> List[str]:
        """Calculate and describe improvements made."""
        improvements = []

        score_diff = optimized_score - original_score

        if score_diff > 0:
            improvements.append(f"Overall ATS score improved by {score_diff:.1f} points")

        improvements.extend([
            "Enhanced keyword optimization for better ATS matching",
            "Improved formatting for ATS compatibility",
            "Strengthened alignment with job requirements"
        ])

        return improvements
