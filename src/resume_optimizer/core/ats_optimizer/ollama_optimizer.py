# src/resume_optimizer/core/ats_optimizer/ollama_optimizer.py
"""
Ollama-based Resume Optimizer using local Llama 3.1 model.
Optimizes each section of the resume for ATS compatibility.
"""

import logging
import re
import json
from typing import List, Optional, Dict, Any

from ..models import ResumeData, JobDescriptionData, Experience
from ..ai_integration.ollama_client import OllamaClient


class OllamaResumeOptimizer:
    """
    Uses local Ollama (Llama 3.1) to optimize resume content.
    Optimizes each section individually for better ATS compatibility.
    """

    def __init__(self, model: str = "llama3.1:8b", ollama_client: Optional[OllamaClient] = None):
        """
        Initialize OllamaResumeOptimizer.

        Args:
            model: Ollama model to use
            ollama_client: Optional pre-configured OllamaClient
        """
        self.logger = logging.getLogger(__name__)
        self.ollama_client = ollama_client or OllamaClient(model=model, timeout=180)

    def optimize_summary(self, current_summary: str, job_data: JobDescriptionData, applicant_name: str) -> str:
        """
        Optimize professional summary using Ollama.

        Args:
            current_summary: Current professional summary
            job_data: Target job description data
            applicant_name: Applicant's name

        Returns:
            Optimized summary string
        """
        if not current_summary:
            return current_summary

        try:
            keywords = job_data.required_skills + job_data.keywords[:5]

            system_prompt = """You are an expert resume writer specializing in ATS optimization.
Your task is to rewrite the professional summary to be more compelling and ATS-friendly.
Return ONLY the optimized summary text, nothing else. No quotes, no labels, just the summary."""

            user_prompt = f"""Optimize this professional summary for ATS compatibility:

Current Summary: {current_summary}

Target Job: {job_data.title}
Company: {job_data.company}
Key Requirements: {', '.join(job_data.required_skills[:8])}
Important Keywords: {', '.join(keywords[:10])}

Create a compelling 2-3 sentence professional summary that:
1. Incorporates relevant keywords naturally
2. Highlights alignment with the role
3. Uses strong action words
4. Remains truthful to the original content
5. Is ATS-friendly (no special formatting)

Return ONLY the optimized summary text:"""

            optimized = self.ollama_client.invoke(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3
            )

            # Clean up the response
            optimized = optimized.strip()
            # Remove any quotes or labels
            optimized = re.sub(r'^["\'](.*)["\']$', r'\1', optimized)
            optimized = re.sub(r'^(Optimized Summary:|Summary:)\s*', '', optimized, flags=re.IGNORECASE)

            if optimized and len(optimized) > 50:
                self.logger.info("Summary optimized successfully with Ollama")
                return optimized
            else:
                return current_summary

        except Exception as e:
            self.logger.error(f"Failed to optimize summary with Ollama: {e}")
            return current_summary

    def optimize_experience_description(self, experience: Experience, job_data: JobDescriptionData) -> List[str]:
        """
        Optimize a single experience description using Ollama.

        Args:
            experience: Experience object to optimize
            job_data: Target job description data

        Returns:
            List of optimized bullet points
        """
        if not experience.description:
            return experience.description or []

        try:
            current_desc = '\n'.join(f"- {d}" for d in experience.description)
            relevant_keywords = [kw for kw in job_data.required_skills + job_data.keywords
                               if kw.lower() in current_desc.lower() or
                               kw.lower() in (experience.position or '').lower()][:6]

            system_prompt = """You are an expert resume writer.
Create impactful, ATS-optimized bullet points that showcase achievements.
Return ONLY the bullet points, one per line, starting with a dash (-). No other text."""

            user_prompt = f"""Optimize these job experience bullet points for ATS:

Position: {experience.position}
Company: {experience.company}
Current Description:
{current_desc}

Target Job Requirements: {', '.join(job_data.required_skills[:6])}
Keywords to incorporate: {', '.join(relevant_keywords)}

Improve the bullet points to:
1. Start with strong action verbs (Led, Developed, Implemented, etc.)
2. Include quantifiable achievements where possible
3. Incorporate relevant keywords naturally
4. Keep them truthful to original content
5. Limit to 3-4 bullet points

Return ONLY the bullet points, one per line starting with dash (-):"""

            response = self.ollama_client.invoke(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3
            )

            # Parse bullet points
            bullet_points = []
            for line in response.strip().split('\n'):
                line = line.strip()
                if line:
                    # Remove bullet symbols and clean up
                    cleaned = re.sub(r'^[\-•\*]\s*', '', line).strip()
                    if cleaned and len(cleaned) > 20:
                        bullet_points.append(cleaned)

            if bullet_points:
                return bullet_points[:4]
            else:
                return experience.description

        except Exception as e:
            self.logger.error(f"Failed to optimize experience: {e}")
            return experience.description or []

    def optimize_all_experiences_batch(self, experiences: List[Experience], job_data: JobDescriptionData) -> List[Experience]:
        """
        Optimize all experiences in a single API call for efficiency.

        Args:
            experiences: List of Experience objects
            job_data: Target job description data

        Returns:
            List of optimized Experience objects
        """
        if not experiences:
            return experiences

        try:
            # Build batch prompt
            experiences_text = []
            for i, exp in enumerate(experiences, 1):
                desc = '\n'.join(f"  - {d}" for d in (exp.description or []))
                exp_text = f"""Experience #{i}:
Position: {exp.position or 'Not specified'}
Company: {exp.company or 'Not specified'}
Duration: {exp.duration or 'Not specified'}
Current Description:
{desc if desc else '  No description'}"""
                experiences_text.append(exp_text)

            all_experiences = "\n\n".join(experiences_text)

            system_prompt = """You are an expert resume writer.
Optimize job experiences for ATS compatibility.
Return your response as valid JSON only. No explanations."""

            user_prompt = f"""Optimize ALL these job experiences for ATS:

{all_experiences}

Target Job: {job_data.title}
Requirements: {', '.join(job_data.required_skills[:8])}
Keywords: {', '.join(job_data.keywords[:10])}

For EACH experience, provide 3-4 optimized bullet points that:
1. Start with strong action verbs
2. Include quantifiable achievements
3. Incorporate relevant keywords
4. Are truthful to original content

Return as JSON:
{{
  "1": ["bullet 1", "bullet 2", "bullet 3"],
  "2": ["bullet 1", "bullet 2", "bullet 3"]
}}

JSON only:"""

            response = self.ollama_client.invoke(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2,
                max_tokens=4096
            )

            # Parse JSON response
            optimized_data = self._parse_json_response(response)

            if optimized_data:
                optimized_experiences = []
                for i, exp in enumerate(experiences, 1):
                    key = str(i)
                    if key in optimized_data and optimized_data[key]:
                        bullets = [b for b in optimized_data[key] if isinstance(b, str) and len(b) > 10]
                        if bullets:
                            optimized_exp = exp.model_copy(update={'description': bullets[:4]})
                            optimized_experiences.append(optimized_exp)
                        else:
                            optimized_experiences.append(exp)
                    else:
                        optimized_experiences.append(exp)

                self.logger.info(f"Batch optimized {len(experiences)} experiences with Ollama")
                return optimized_experiences

            # Fallback to individual optimization
            return self._optimize_experiences_individually(experiences, job_data)

        except Exception as e:
            self.logger.error(f"Batch optimization failed: {e}, falling back to individual")
            return self._optimize_experiences_individually(experiences, job_data)

    def _optimize_experiences_individually(self, experiences: List[Experience], job_data: JobDescriptionData) -> List[Experience]:
        """Fallback: optimize each experience individually."""
        optimized = []
        for exp in experiences:
            try:
                new_desc = self.optimize_experience_description(exp, job_data)
                optimized.append(exp.model_copy(update={'description': new_desc}))
            except Exception as e:
                self.logger.error(f"Individual optimization failed: {e}")
                optimized.append(exp)
        return optimized

    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """Parse JSON from model response."""
        if not response:
            return None

        # Clean up response
        response = response.strip()

        # Remove markdown code blocks
        if response.startswith('```'):
            response = re.sub(r'^```(?:json)?\n?', '', response)
            response = re.sub(r'\n?```$', '', response)

        # Try direct parsing
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON object
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return None

    def enhance_skills_section(self, current_skills: List[str], job_data: JobDescriptionData) -> List[str]:
        """
        Enhance and prioritize skills section using Ollama.

        Args:
            current_skills: Current list of skills
            job_data: Target job description data

        Returns:
            Optimized list of skills
        """
        if not current_skills:
            return current_skills

        try:
            system_prompt = """You are an expert resume writer.
Optimize the skills list for ATS compatibility.
Return ONLY a comma-separated list of skills. No other text."""

            user_prompt = f"""Optimize this skills list for the target job:

Current Skills: {', '.join(current_skills)}

Job Requirements: {', '.join(job_data.required_skills)}
Preferred Skills: {', '.join(job_data.preferred_skills[:5])}
Job Keywords: {', '.join(job_data.keywords[:8])}

Create an optimized skills list that:
1. Prioritizes job-relevant skills first
2. Uses industry-standard terminology
3. Includes both technical and soft skills from original
4. Stays truthful to original skills
5. Maximum 15-20 skills

Return ONLY a comma-separated list:"""

            response = self.ollama_client.invoke(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2
            )

            # Parse skills
            skills_list = []
            for skill in response.split(','):
                skill = skill.strip()
                # Remove any bullet points or numbers
                skill = re.sub(r'^[\d\.\-\*•]+\s*', '', skill).strip()
                if skill and len(skill) <= 50 and len(skill) > 1:
                    skills_list.append(skill)

            if skills_list:
                return skills_list[:20]
            else:
                return current_skills

        except Exception as e:
            self.logger.error(f"Failed to enhance skills: {e}")
            return current_skills

    def generate_optimization_recommendations(
        self,
        resume_data: ResumeData,
        job_data: JobDescriptionData,
        missing_keywords: List[str]
    ) -> List[str]:
        """
        Generate specific optimization recommendations using Ollama.

        Args:
            resume_data: Resume data
            job_data: Job description data
            missing_keywords: List of missing keywords

        Returns:
            List of recommendations
        """
        try:
            summary_preview = (resume_data.summary or '')[:200]

            system_prompt = """You are an ATS optimization expert.
Provide specific, actionable recommendations.
Return a numbered list of 5-7 recommendations. Keep each under 100 characters."""

            user_prompt = f"""Analyze this resume against the job requirements:

Resume Summary: {summary_preview}...
Resume Skills: {', '.join(resume_data.skills[:10])}

Job Title: {job_data.title}
Job Requirements: {', '.join(job_data.required_skills)}
Missing Keywords: {', '.join(missing_keywords[:8])}

Provide 5-7 specific recommendations to improve ATS compatibility:
1. Focus on missing keywords
2. Content structure improvements
3. Formatting for ATS
4. Quantifiable achievements
5. Industry terminology

Numbered list:"""

            response = self.ollama_client.invoke(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3
            )

            # Parse recommendations
            recommendations = []
            for line in response.strip().split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    clean_rec = re.sub(r'^\d+[\.\)]\s*|^[\-•]\s*', '', line).strip()
                    if clean_rec and 10 < len(clean_rec) <= 200:
                        recommendations.append(clean_rec)

            if recommendations:
                return recommendations[:7]
            else:
                return ["Incorporate more job-relevant keywords naturally into your resume"]

        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
            return ["Consider incorporating more job-relevant keywords naturally into your resume"]

    def optimize_full_resume(
        self,
        resume_data: ResumeData,
        job_data: JobDescriptionData,
        applicant_name: str
    ) -> ResumeData:
        """
        Perform full resume optimization in one comprehensive call.
        More efficient than optimizing each section separately.

        Args:
            resume_data: Original resume data
            job_data: Target job description
            applicant_name: Applicant's name

        Returns:
            Optimized ResumeData
        """
        try:
            # Create deep copy
            optimized = resume_data.model_copy(deep=True)

            # Update name if provided
            if applicant_name and applicant_name.strip():
                optimized.contact_info.name = applicant_name.strip()

            self.logger.info("Starting full resume optimization with Ollama...")

            # 1. Optimize Summary
            if resume_data.summary:
                self.logger.info("Optimizing summary...")
                optimized.summary = self.optimize_summary(
                    resume_data.summary, job_data, applicant_name
                )

            # 2. Optimize All Experiences (batch)
            if resume_data.experience:
                self.logger.info(f"Optimizing {len(resume_data.experience)} experiences...")
                optimized.experience = self.optimize_all_experiences_batch(
                    resume_data.experience, job_data
                )

            # 3. Enhance Skills
            if resume_data.skills:
                self.logger.info("Enhancing skills section...")
                optimized.skills = self.enhance_skills_section(
                    resume_data.skills, job_data
                )

            self.logger.info("Full resume optimization completed with Ollama")
            return optimized

        except Exception as e:
            self.logger.error(f"Full optimization failed: {e}")
            raise e
