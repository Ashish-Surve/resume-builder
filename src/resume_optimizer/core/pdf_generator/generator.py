
# src/resume_optimizer/core/pdf_generator/generator.py
"""
PDF Generator module for creating ATS-compliant resume PDFs.
Implements Factory and Template Method patterns.
"""

import logging
from pathlib import Path
from typing import Dict
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
from reportlab.lib.colors import black
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

from ..models import ResumeData, OptimizationResult
from ...utils.exceptions import FileProcessingError


class ATSFriendlyPDFGenerator:
    """
    Generates ATS-friendly PDF resumes using ReportLab.
    Follows ATS best practices for formatting and structure.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.styles = self._create_ats_styles()
        self.page_size = letter  # Standard US letter size for ATS compatibility

    def generate_pdf(self, resume_data: ResumeData, optimization_result: OptimizationResult, 
                    output_path: Path, applicant_name: str, company_name: str) -> Path:
        """Generate ATS-compliant PDF resume."""
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=self.page_size,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )

            # Build document content
            story = []

            # Add header
            self._add_header(story, resume_data, applicant_name)

            # Add summary/objective
            if resume_data.summary:
                self._add_summary(story, resume_data.summary)

            # Add skills section
            if resume_data.skills:
                self._add_skills(story, resume_data.skills)

            # Add experience section
            if resume_data.experience:
                self._add_experience(story, resume_data.experience)

            # Add education section
            if resume_data.education:
                self._add_education(story, resume_data.education)

            # Add certifications if any
            if resume_data.certifications:
                self._add_certifications(story, resume_data.certifications)

            # Build PDF
            doc.build(story)

            self.logger.info(f"PDF generated successfully: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to generate PDF: {e}")
            raise FileProcessingError(f"PDF generation failed: {e}")

    def _create_ats_styles(self) -> Dict[str, ParagraphStyle]:
        """Create ATS-friendly paragraph styles."""
        styles = getSampleStyleSheet()

        ats_styles = {
            'name': ParagraphStyle(
                'ATSName',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=6,
                alignment=TA_CENTER,
                textColor=black
            ),
            'contact': ParagraphStyle(
                'ATSContact',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=12,
                alignment=TA_CENTER,
                textColor=black
            ),
            'section_header': ParagraphStyle(
                'ATSSectionHeader',
                parent=styles['Heading2'],
                fontSize=12,
                spaceAfter=6,
                spaceBefore=12,
                textColor=black,
                borderWidth=1,
                borderColor=black,
                borderRadius=0,
                backColor=None
            ),
            'job_title': ParagraphStyle(
                'ATSJobTitle',
                parent=styles['Heading3'],
                fontSize=11,
                spaceAfter=3,
                textColor=black,
                leftIndent=0
            ),
            'company_info': ParagraphStyle(
                'ATSCompanyInfo',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=3,
                textColor=black,
                leftIndent=0
            ),
            'body': ParagraphStyle(
                'ATSBody',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                alignment=TA_JUSTIFY,
                textColor=black,
                leftIndent=0
            ),
            'bullet': ParagraphStyle(
                'ATSBullet',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=3,
                leftIndent=12,
                textColor=black
            )
        }

        return ats_styles

    def _add_header(self, story: list, resume_data: ResumeData, applicant_name: str) -> None:
        """Add contact information header."""
        contact = resume_data.contact_info

        # Name
        name = applicant_name or contact.name or "Your Name"
        story.append(Paragraph(name.upper(), self.styles['name']))

        # Contact information
        contact_info = []
        if contact.phone:
            contact_info.append(contact.phone)
        if contact.email:
            contact_info.append(contact.email)
        if contact.address:
            contact_info.append(contact.address)

        if contact_info:
            contact_text = " | ".join(contact_info)
            story.append(Paragraph(contact_text, self.styles['contact']))

        # LinkedIn and GitHub on separate line if available
        links = []
        if contact.linkedin:
            links.append(f"LinkedIn: {contact.linkedin}")
        if contact.github:
            links.append(f"GitHub: {contact.github}")

        if links:
            links_text = " | ".join(links)
            story.append(Paragraph(links_text, self.styles['contact']))

        story.append(Spacer(1, 6))

    def _add_summary(self, story: list, summary) -> None:
        """Add professional summary section, flattening dict/JSON if needed."""
        import json
        def flatten_summary(val):
            import json
            # If dict, extract the first value (e.g., 'optimized_summary' or 'summary')
            if isinstance(val, dict):
                for k in ['optimized_summary', 'summary', 'value']:
                    if k in val:
                        return flatten_summary(val[k])
                # fallback: first value
                if val:
                    return flatten_summary(next(iter(val.values())))
                return ''
            if isinstance(val, list):
                # Join list items as sentences
                return ' '.join(str(x).strip() for x in val if x)
            if isinstance(val, str):
                s = val.strip()
                # Try to parse JSON string
                if s.startswith('{'):
                    try:
                        parsed = json.loads(s)
                        return flatten_summary(parsed)
                    except Exception:
                        pass
                # Remove leading/trailing brackets/quotes
                s = s.strip('"\'{}[]')
                return s
            return str(val)
        section = []
        section.append(Paragraph("PROFESSIONAL SUMMARY", self.styles['section_header']))
        section.append(Paragraph(flatten_summary(summary), self.styles['body']))
        section.append(Spacer(1, 6))
        story.append(KeepTogether(section))

    def _add_skills(self, story: list, skills) -> None:
        """Add skills section, flattening dict/JSON if needed."""
        import json
        def flatten_skills(val):
            import re, json
            def pre_clean(s):
                # Remove curly braces, quotes, and 'skills' key, and leading/trailing bullets
                s = s.replace('{', '').replace('}', '').replace('"', '').replace("'", '')
                s = re.sub(r'\bskills\b\s*:\s*', '', s, flags=re.IGNORECASE)
                s = s.strip()
                # Remove leading/trailing bullets and whitespace
                s = re.sub(r'^[•\u2022\u2023\u25CF\u2024•·\*\|,;\n\r\-\s]+', '', s)
                s = re.sub(r'[•\u2022\u2023\u25CF\u2024•·\*\|,;\n\r\-\s]+$', '', s)
                return s

            def split_skills(s):
                s = pre_clean(s)
                # Split on all common separators, including bullets, dots, pipes, commas, semicolons, and newlines
                items = re.split(r'[•\u2022\u2023\u25CF\u2024•·\*\|,;\n\r\-]+', s)
                return [item.strip() for item in items if item and item.strip()]

            # If dict, extract 'skills' key or flatten all values
            if isinstance(val, dict):
                if 'skills' in val:
                    return flatten_skills(val['skills'])
                # fallback: flatten all values
                flat = []
                for v in val.values():
                    flat.extend(flatten_skills(v))
                return flat
            # If list, flatten all items
            if isinstance(val, list):
                flat = []
                for x in val:
                    flat.extend(flatten_skills(x))
                return flat
            # If string, try to parse as JSON array or split
            if isinstance(val, str):
                s = val.strip()
                # Try to parse JSON array
                if s.startswith('['):
                    try:
                        parsed = json.loads(s)
                        if isinstance(parsed, list):
                            return flatten_skills(parsed)
                    except Exception:
                        pass
                # Try to parse JSON object
                if s.startswith('{'):
                    try:
                        parsed = json.loads(s)
                        return flatten_skills(parsed)
                    except Exception:
                        pass
                return split_skills(s)
            # fallback: treat as string
            return split_skills(str(val))

        section = []
        section.append(Paragraph("TECHNICAL SKILLS", self.styles['section_header']))
        skills_list = flatten_skills(skills)
        skills_text = " • ".join(skills_list)
        section.append(Paragraph(skills_text, self.styles['body']))
        section.append(Spacer(1, 6))
        story.append(KeepTogether(section))

    def _add_experience(self, story: list, experiences: list) -> None:
        """Add work experience section."""
        section = []
        section.append(Paragraph("PROFESSIONAL EXPERIENCE", self.styles['section_header']))

        for exp in experiences:
            exp_section = []
            # Job title and company
            if exp.position and exp.company:
                title_text = f"<b>{exp.position}</b>"
                exp_section.append(Paragraph(title_text, self.styles['job_title']))

                company_text = f"{exp.company}"
                if exp.start_date or exp.end_date:
                    date_range = f"{exp.start_date or ''} - {exp.end_date or 'Present'}"
                    company_text += f" | {date_range}"

                exp_section.append(Paragraph(company_text, self.styles['company_info']))

            # Job description
            for desc in exp.description:
                if desc.strip():
                    bullet_text = f"• {desc}"
                    exp_section.append(Paragraph(bullet_text, self.styles['bullet']))

            exp_section.append(Spacer(1, 6))
            section.append(KeepTogether(exp_section))
        story.append(KeepTogether(section))

    def _add_education(self, story: list, education: list) -> None:
        """Add education section."""
        section = []
        section.append(Paragraph("EDUCATION", self.styles['section_header']))

        for edu in education:
            edu_section = []
            if edu.degree and edu.institution:
                edu_text = f"<b>{edu.degree}</b>"
                if edu.field:
                    edu_text += f" in {edu.field}"

                edu_section.append(Paragraph(edu_text, self.styles['job_title']))

                institution_text = edu.institution
                if edu.graduation_date:
                    institution_text += f" | {edu.graduation_date}"
                if edu.gpa:
                    institution_text += f" | GPA: {edu.gpa}"

                edu_section.append(Paragraph(institution_text, self.styles['company_info']))
                edu_section.append(Spacer(1, 3))
                section.append(KeepTogether(edu_section))
        story.append(KeepTogether(section))

    def _add_certifications(self, story: list, certifications: list | str) -> None:
        """Add certifications section."""
        import re
        section = []
        section.append(Paragraph("CERTIFICATIONS", self.styles['section_header']))

        if certifications:
            if isinstance(certifications, list):
                for cert in certifications:
                    cert_text = f"• {cert}"
                    section.append(Paragraph(cert_text, self.styles['bullet']))
            elif isinstance(certifications, str):
                # Split string by bullets or newlines and format properly
                cert_list = [c.strip() for c in re.split(r'[•\n]', certifications) if c.strip()]
                for cert in cert_list:
                    cert_text = f"• {cert}"
                    section.append(Paragraph(cert_text, self.styles['bullet']))

        section.append(Spacer(1, 6))
        story.append(KeepTogether(section))


class PDFGeneratorFactory:
    """Factory for creating PDF generators."""

    @staticmethod
    def create_generator(generator_type: str = "ats_friendly") -> ATSFriendlyPDFGenerator:
        """Create a PDF generator instance."""
        if generator_type == "ats_friendly":
            return ATSFriendlyPDFGenerator()
        else:
            raise ValueError(f"Unknown generator type: {generator_type}")
