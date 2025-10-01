# src/resume_optimizer/core/ats_optimizer/optimizer.py
"""
ATS Optimizer module for improving resume compatibility with ATS systems.
Implements Strategy and Observer patterns with Gemini AI integration.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, replace
from enum import Enum

from ..models import ResumeData, JobDescriptionData, OptimizationResult, OptimizationStatus, Experience
from ...utils.exceptions import ValidationError, AIServiceError
from ..ai_integration.gemini_client import GeminiClient


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
        score = 1.0
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


class GeminiResumeOptimizer:
    """Uses Gemini AI to optimize resume content."""

    def __init__(self, api_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        try:
            self.gemini_client = GeminiClient(api_key=api_key)
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini client: {e}")
            raise e

    def optimize_summary(self, current_summary: str, job_data: JobDescriptionData, applicant_name: str) -> str:
        """Optimize professional summary using Gemini."""
        if not self.gemini_client:
            return current_summary

        try:
            keywords = job_data.required_skills + job_data.keywords[:5]  # Top keywords
            prompt = f"""
            Optimize this professional summary for ATS compatibility and job relevance.
            
            Current Summary: {current_summary}
            
            Job Title: {job_data.title}
            Company: {job_data.company}
            Key Requirements: {', '.join(job_data.required_skills[:8])}
            Important Keywords: {', '.join(keywords)}
            
            Create a compelling 2-3 sentence professional summary that:
            1. Incorporates relevant keywords naturally
            2. Highlights alignment with the role
            3. Uses strong action words
            4. Remains truthful to the original content
            5. Is ATS-friendly (no special formatting)
            
            Return only the optimized summary text.
            """
            
            system_message = "You are an expert resume writer specializing in ATS optimization. Create compelling, keyword-rich content that remains truthful and professional."
            
            optimized_summary = self.gemini_client.invoke(system_message, prompt)
            return optimized_summary.strip()
            
        except Exception as e:
            self.logger.error(f"Failed to optimize summary with Gemini: {e}")
            return current_summary

    def optimize_experience_description(self, experience: Experience, job_data: JobDescriptionData) -> List[str]:
        """Optimize experience descriptions using Gemini."""
        if not self.gemini_client or not experience.description:
            return experience.description or []

        try:
            current_desc = '\n'.join(experience.description)
            relevant_keywords = [kw for kw in job_data.required_skills + job_data.keywords 
                               if kw.lower() in current_desc.lower() or kw.lower() in experience.position.lower()][:6]
            
            prompt = f"""
            Optimize these job experience bullet points for ATS compatibility:
            
            Position: {experience.position}
            Company: {experience.company}
            Current Description:
            {current_desc}
            
            Target Job Requirements: {', '.join(job_data.required_skills[:6])}
            Relevant Keywords to Incorporate: {', '.join(relevant_keywords)}
            
            Improve the bullet points to:
            1. Start with strong action verbs
            2. Include quantifiable achievements where possible
            3. Incorporate relevant keywords naturally
            4. Make them ATS-friendly (simple formatting)
            5. Keep them truthful to the original content
            6. Limit to 3-4 bullet points maximum
            
            Return only the bullet points, one per line, starting with "•"
            """
            
            system_message = "You are an expert resume writer. Create impactful, ATS-optimized bullet points that showcase achievements with relevant keywords."
            
            optimized_desc = self.gemini_client.invoke(system_message, prompt)
            
            # Parse the response into bullet points
            bullet_points = []
            for line in optimized_desc.strip().split('\n'):
                line = line.strip()
                if line:
                    # Remove bullet symbols and clean up
                    cleaned_line = re.sub(r'^[•\-\*]\s*', '', line).strip()
                    if cleaned_line:
                        bullet_points.append(cleaned_line)
            
            return bullet_points[:4] if bullet_points else experience.description
            
        except Exception as e:
            self.logger.error(f"Failed to optimize experience description with Gemini: {e}")
            return experience.description or []

    def enhance_skills_section(self, current_skills: List[str], job_data: JobDescriptionData) -> List[str]:
        """Enhance skills section using Gemini recommendations."""
        if not self.gemini_client:
            return current_skills

        try:
            prompt = f"""
            Optimize this skills list for the target job:
            
            Current Skills: {', '.join(current_skills)}
            
            Job Requirements: {', '.join(job_data.required_skills)}
            Preferred Skills: {', '.join(job_data.preferred_skills[:5])}
            Job Keywords: {', '.join(job_data.keywords[:8])}
            
            Provide an optimized skills list that:
            1. Prioritizes job-relevant skills
            2. Groups related skills logically
            3. Uses industry-standard terminology
            4. Includes both technical and soft skills
            5. Maintains truthfulness to original skills
            6. Limits to 15-20 skills maximum
            
            Return only the skills list, comma-separated.
            """
            
            system_message = "You are an expert resume writer. Organize and optimize skills sections for maximum ATS compatibility and relevance."
            
            optimized_skills = self.gemini_client.invoke(system_message, prompt)
            
            # Parse skills from response
            skills_list = []
            for skill in optimized_skills.split(','):
                skill = skill.strip()
                if skill and len(skill) <= 50:  # Reasonable skill name length
                    skills_list.append(skill)
            
            return skills_list[:20] if skills_list else current_skills
            
        except Exception as e:
            self.logger.error(f"Failed to enhance skills with Gemini: {e}")
            return current_skills

    def generate_optimization_recommendations(self, resume_data: ResumeData, job_data: JobDescriptionData, 
                                           missing_keywords: List[str]) -> List[str]:
        """Generate specific optimization recommendations using Gemini."""
        if not self.gemini_client:
            return ["Consider incorporating more job-relevant keywords naturally into your resume"]

        try:
            prompt = f"""
            Analyze this resume against the job requirements and provide specific optimization recommendations:
            
            Resume Summary: {resume_data.summary[:200]}...
            Resume Skills: {', '.join(resume_data.skills[:10])}
            
            Job Title: {job_data.title}
            Job Requirements: {', '.join(job_data.required_skills)}
            Missing Keywords: {', '.join(missing_keywords[:8])}
            
            Provide 5-7 specific, actionable recommendations to improve ATS compatibility and job match:
            1. Focus on missing keywords and skills
            2. Content structure improvements
            3. Formatting suggestions for ATS
            4. Quantifiable achievement opportunities
            5. Industry-specific terminology
            
            Return recommendations as a numbered list, each under 100 characters.
            """
            
            system_message = "You are an ATS optimization expert. Provide specific, actionable recommendations to improve resume performance."
            
            recommendations_text = self.gemini_client.invoke(system_message, prompt)
            
            # Parse recommendations
            recommendations = []
            for line in recommendations_text.strip().split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Remove numbering and formatting
                    clean_rec = re.sub(r'^\d+[\.\)]\s*|^[\-•]\s*', '', line).strip()
                    if clean_rec and len(clean_rec) <= 200:
                        recommendations.append(clean_rec)
            
            return recommendations[:7] if recommendations else ["Incorporate more job-relevant keywords naturally"]
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations with Gemini: {e}")
            return ["Consider incorporating more job-relevant keywords naturally into your resume"]


class ATSOptimizer:
    """Main ATS optimization engine with Gemini AI integration."""

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.compatibility_checker = ATSCompatibilityChecker()
        self.keyword_optimizer = KeywordOptimizer()
        self.scorer = ResumeScorer()
        self.gemini_optimizer = GeminiResumeOptimizer(api_key=gemini_api_key)

    def optimize(self, resume_data: ResumeData, job_data: JobDescriptionData, 
                applicant_name: str, company_name: str) -> OptimizationResult:
        """Perform comprehensive ATS optimization with Gemini AI."""
        try:
            self.logger.info(f"Starting optimization for {applicant_name} at {company_name}")
            result = OptimizationResult(status=OptimizationStatus.PROCESSING)

            # Calculate original scores
            original_scores = self.scorer.score_resume(resume_data, job_data)
            result.original_score = original_scores.overall * 100

            # Run ATS compatibility check
            ats_check = self.compatibility_checker.check_compatibility(resume_data, job_data)
            result.ats_compliance_score = ats_check['overall_score'] * 100

            # Optimize keywords
            keyword_analysis = self.keyword_optimizer.optimize_keywords(resume_data, job_data)
            result.missing_keywords = keyword_analysis['missing_keywords']

            # Create AI-optimized resume
            result.optimized_resume = self._create_gemini_optimized_resume(
                resume_data, job_data, applicant_name, company_name
            )

            # Calculate optimized score
            optimized_scores = self.scorer.score_resume(result.optimized_resume, job_data)
            result.optimized_score = optimized_scores.overall * 100

            # Generate AI-powered recommendations
            result.recommendations = self._generate_comprehensive_recommendations(
                ats_check, keyword_analysis, resume_data, job_data
            )

            # Calculate improvements
            result.improvements = self._calculate_detailed_improvements(
                original_scores, optimized_scores, result.recommendations
            )

            result.status = OptimizationStatus.COMPLETED
            self.logger.info(f"Optimization completed successfully. Score improved from {result.original_score:.1f} to {result.optimized_score:.1f}")

            return result

        except Exception as e:
            self.logger.error(f"Optimization failed: {e}")
            result = OptimizationResult(status=OptimizationStatus.FAILED)
            raise e

    def _create_gemini_optimized_resume(self, resume_data: ResumeData, job_data: JobDescriptionData, 
                                      applicant_name: str, company_name: str) -> ResumeData:
        """Create an AI-optimized version of the resume using Gemini."""
        try:
            # Start with the original resume data
            optimized = replace(resume_data)

            # Update applicant name if provided
            if applicant_name and applicant_name.strip():
                optimized.contact_info.name = applicant_name.strip()

            # Optimize professional summary
            if resume_data.summary:
                optimized.summary = self.gemini_optimizer.optimize_summary(
                    resume_data.summary, job_data, applicant_name
                )

            # Optimize experience descriptions
            if resume_data.experience:
                optimized_experiences = []
                for exp in resume_data.experience:
                    optimized_desc = self.gemini_optimizer.optimize_experience_description(exp, job_data)
                    optimized_exp = replace(exp, description=optimized_desc)
                    optimized_experiences.append(optimized_exp)
                optimized.experience = optimized_experiences

            # Enhance skills section
            if resume_data.skills:
                optimized.skills = self.gemini_optimizer.enhance_skills_section(resume_data.skills, job_data)

            # Update raw text with optimized content
            optimized.raw_text = self._generate_optimized_raw_text(optimized)

            self.logger.info("Resume optimization with Gemini completed successfully")
            return optimized

        except Exception as e:
            self.logger.error(f"Failed to create Gemini-optimized resume: {e}")
            # Return original data if optimization fails
            raise e

    def _generate_optimized_raw_text(self, resume_data: ResumeData) -> str:
        """Generate optimized raw text from structured resume data."""
        sections = []

        # Contact Information
        if resume_data.contact_info.name:
            sections.append(resume_data.contact_info.name)
        if resume_data.contact_info.email:
            sections.append(f"Email: {resume_data.contact_info.email}")
        if resume_data.contact_info.phone:
            sections.append(f"Phone: {resume_data.contact_info.phone}")
        if resume_data.contact_info.linkedin:
            sections.append(f"LinkedIn: {resume_data.contact_info.linkedin}")

        sections.append("")  # Empty line

        # Professional Summary
        if resume_data.summary:
            sections.extend(["PROFESSIONAL SUMMARY", resume_data.summary, ""])

        # Skills
        if resume_data.skills:
            sections.extend(["TECHNICAL SKILLS", "• " + "\n• ".join(resume_data.skills), ""])

        # Experience
        if resume_data.experience:
            sections.append("PROFESSIONAL EXPERIENCE")
            for exp in resume_data.experience:
                exp_header = f"{exp.position} | {exp.company}"
                if exp.start_date or exp.end_date:
                    dates = f" | {exp.start_date or 'Present'} - {exp.end_date or 'Present'}"
                    exp_header += dates
                sections.append(exp_header)
                if exp.description:
                    sections.extend([f"• {desc}" for desc in exp.description])
                sections.append("")

        # Education
        if resume_data.education:
            sections.append("EDUCATION")
            for edu in resume_data.education:
                edu_line = f'{edu.degree} in {edu.field}' if (edu.degree and edu.field) else (edu.degree or 'Education')
                if hasattr(edu, 'institution'):
                    edu_line += f" | {edu.institution}"
                sections.append(edu_line)
            sections.append("")

        # Certifications
        if resume_data.certifications:
            if type(resume_data.certifications) == list:
                # list 
                sections.extend(["CERTIFICATIONS", "• " + "\n• ".join(resume_data.certifications)])
            else:
                # str 
                sections.extend(["CERTIFICATIONS", resume_data.certifications])

        return "\n".join(sections)

    def _generate_comprehensive_recommendations(self, ats_check: Dict, keyword_analysis: Dict, 
                                             resume_data: ResumeData, job_data: JobDescriptionData) -> List[str]:
        """Generate comprehensive optimization recommendations using Gemini AI."""
        recommendations = []

        # Get AI-generated recommendations
        ai_recommendations = self.gemini_optimizer.generate_optimization_recommendations(
            resume_data, job_data, keyword_analysis['missing_keywords']
        )
        recommendations.extend(ai_recommendations)

        # Add ATS compatibility recommendations
        recommendations.extend(ats_check.get('suggestions', []))

        # Add keyword optimization recommendations
        keyword_suggestions = keyword_analysis.get('optimization_suggestions', [])
        recommendations.extend(keyword_suggestions[:3])  # Limit keyword suggestions

        # Add scoring-based recommendations
        if keyword_analysis['keyword_score'] < 0.7:
            recommendations.append("Incorporate more job-specific keywords naturally throughout your resume")

        if ats_check['overall_score'] < 0.8:
            recommendations.append("Improve ATS formatting by using standard section headers and simple formatting")

        # Content quality recommendations
        word_count = len(resume_data.raw_text.split())
        if word_count < 300:
            recommendations.append("Expand resume with more detailed accomplishments and quantified results")
        elif word_count > 800:
            recommendations.append("Streamline content to focus on most relevant and impactful achievements")

        # Remove duplicates and limit to reasonable number
        unique_recommendations = list(dict.fromkeys(recommendations))  # Preserve order while removing duplicates
        return unique_recommendations[:10]

    def _calculate_detailed_improvements(self, original_scores: OptimizationScore, 
                                       optimized_scores: OptimizationScore, 
                                       recommendations: List[str]) -> List[str]:
        """Calculate and describe detailed improvements made."""
        improvements = []

        score_diff = (optimized_scores.overall - original_scores.overall) * 100

        if score_diff > 0:
            improvements.append(f"Overall ATS score improved by {score_diff:.1f} points")

        # Specific score improvements
        keyword_diff = (optimized_scores.keyword_match - original_scores.keyword_match) * 100
        if keyword_diff > 5:
            improvements.append(f"Keyword matching improved by {keyword_diff:.1f}%")

        skill_diff = (optimized_scores.skill_alignment - original_scores.skill_alignment) * 100
        if skill_diff > 5:
            improvements.append(f"Skill alignment with job requirements improved by {skill_diff:.1f}%")

        content_diff = (optimized_scores.content_quality - original_scores.content_quality) * 100
        if content_diff > 5:
            improvements.append(f"Content quality score improved by {content_diff:.1f}%")

        # AI-powered improvements
        improvements.extend([
            "Professional summary optimized with relevant keywords and stronger positioning",
            "Experience descriptions enhanced with action verbs and quantifiable achievements",
            "Skills section reorganized to highlight job-relevant technical competencies",
            "Content structure improved for better ATS parsing and readability"
        ])

        return improvements