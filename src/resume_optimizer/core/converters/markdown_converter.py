# src/resume_optimizer/core/converters/markdown_converter.py
"""
Markdown converter for resume data.
Converts ResumeData to/from Markdown format for editing.
"""

import re
from typing import Optional, List
from pathlib import Path

from ..models import ResumeData, ContactInfo, Experience, Education


class MarkdownConverter:
    """
    Converts ResumeData to Markdown format and vice versa.
    Each section is clearly delimited for easy editing.
    """

    SECTION_MARKERS = {
        'contact': '## Contact Information',
        'summary': '## Professional Summary',
        'skills': '## Skills',
        'experience': '## Work Experience',
        'education': '## Education',
        'certifications': '## Certifications',
        'languages': '## Languages',
    }

    @classmethod
    def resume_to_markdown(cls, resume_data: ResumeData) -> str:
        """
        Convert ResumeData to a well-formatted Markdown string.

        Args:
            resume_data: The resume data to convert

        Returns:
            Markdown formatted string
        """
        sections = []

        # Header with name
        name = resume_data.contact_info.name or "Your Name"
        sections.append(f"# {name}\n")

        # Contact Information
        sections.append(cls._contact_to_markdown(resume_data.contact_info))

        # Professional Summary
        if resume_data.summary:
            sections.append(cls._summary_to_markdown(resume_data.summary))

        # Skills
        if resume_data.skills:
            sections.append(cls._skills_to_markdown(resume_data.skills))

        # Work Experience
        if resume_data.experience:
            sections.append(cls._experience_to_markdown(resume_data.experience))

        # Education
        if resume_data.education:
            sections.append(cls._education_to_markdown(resume_data.education))

        # Certifications
        if resume_data.certifications:
            sections.append(cls._certifications_to_markdown(resume_data.certifications))

        # Languages
        if resume_data.languages:
            sections.append(cls._languages_to_markdown(resume_data.languages))

        return "\n".join(sections)

    @classmethod
    def _contact_to_markdown(cls, contact: ContactInfo) -> str:
        """Convert contact info to markdown."""
        lines = [cls.SECTION_MARKERS['contact'], ""]

        if contact.email:
            lines.append(f"- **Email:** {contact.email}")
        if contact.phone:
            lines.append(f"- **Phone:** {contact.phone}")
        if contact.address:
            lines.append(f"- **Location:** {contact.address}")
        if contact.linkedin:
            lines.append(f"- **LinkedIn:** {contact.linkedin}")
        if contact.github:
            lines.append(f"- **GitHub:** {contact.github}")

        lines.append("")
        return "\n".join(lines)

    @classmethod
    def _summary_to_markdown(cls, summary: str) -> str:
        """Convert summary to markdown."""
        # Handle dict/JSON summary
        if isinstance(summary, dict):
            for key in ['optimized_summary', 'summary', 'value']:
                if key in summary:
                    summary = summary[key]
                    break
            else:
                summary = str(next(iter(summary.values()), ''))

        return f"{cls.SECTION_MARKERS['summary']}\n\n{summary}\n"

    @classmethod
    def _skills_to_markdown(cls, skills: List[str]) -> str:
        """Convert skills to markdown."""
        lines = [cls.SECTION_MARKERS['skills'], ""]
        for skill in skills:
            if skill and skill.strip():
                lines.append(f"- {skill.strip()}")
        lines.append("")
        return "\n".join(lines)

    @classmethod
    def _experience_to_markdown(cls, experiences: List[Experience]) -> str:
        """Convert work experience to markdown."""
        lines = [cls.SECTION_MARKERS['experience'], ""]

        for exp in experiences:
            # Job header
            position = exp.position or "Position"
            company = exp.company or "Company"
            lines.append(f"### {position} @ {company}")

            # Duration
            if exp.duration:
                lines.append(f"*{exp.duration}*")
            elif exp.start_date or exp.end_date:
                date_range = f"{exp.start_date or ''} - {exp.end_date or 'Present'}"
                lines.append(f"*{date_range}*")

            lines.append("")

            # Description bullets
            for desc in exp.description:
                if desc and desc.strip():
                    lines.append(f"- {desc.strip()}")

            # Skills used
            if exp.skills_used:
                skills_str = ", ".join(exp.skills_used)
                lines.append(f"\n**Skills:** {skills_str}")

            lines.append("")

        return "\n".join(lines)

    @classmethod
    def _education_to_markdown(cls, education: List[Education]) -> str:
        """Convert education to markdown."""
        lines = [cls.SECTION_MARKERS['education'], ""]

        for edu in education:
            degree = edu.degree or "Degree"
            field = edu.field or ""
            institution = edu.institution or "Institution"

            if field:
                lines.append(f"### {degree} in {field}")
            else:
                lines.append(f"### {degree}")

            lines.append(f"**{institution}**")

            if edu.graduation_date:
                lines.append(f"*{edu.graduation_date}*")

            if edu.gpa:
                lines.append(f"GPA: {edu.gpa}")

            for desc in edu.description:
                if desc and desc.strip():
                    lines.append(f"- {desc.strip()}")

            lines.append("")

        return "\n".join(lines)

    @classmethod
    def _certifications_to_markdown(cls, certifications: List[str]) -> str:
        """Convert certifications to markdown."""
        lines = [cls.SECTION_MARKERS['certifications'], ""]
        for cert in certifications:
            if cert and cert.strip():
                lines.append(f"- {cert.strip()}")
        lines.append("")
        return "\n".join(lines)

    @classmethod
    def _languages_to_markdown(cls, languages: List[str]) -> str:
        """Convert languages to markdown."""
        lines = [cls.SECTION_MARKERS['languages'], ""]
        for lang in languages:
            if lang and lang.strip():
                lines.append(f"- {lang.strip()}")
        lines.append("")
        return "\n".join(lines)

    @classmethod
    def markdown_to_resume(cls, markdown_text: str, existing_resume: Optional[ResumeData] = None) -> ResumeData:
        """
        Parse Markdown text back into ResumeData.

        Args:
            markdown_text: The markdown string to parse
            existing_resume: Optional existing resume to update

        Returns:
            ResumeData object
        """
        resume = existing_resume or ResumeData()

        # Extract name from H1
        name_match = re.search(r'^#\s+(.+)$', markdown_text, re.MULTILINE)
        if name_match:
            resume.contact_info.name = name_match.group(1).strip()

        # Parse each section
        resume.contact_info = cls._parse_contact_section(markdown_text, resume.contact_info)
        resume.summary = cls._parse_summary_section(markdown_text)
        resume.skills = cls._parse_skills_section(markdown_text)
        resume.experience = cls._parse_experience_section(markdown_text)
        resume.education = cls._parse_education_section(markdown_text)
        resume.certifications = cls._parse_certifications_section(markdown_text)
        resume.languages = cls._parse_languages_section(markdown_text)

        return resume

    @classmethod
    def _extract_section(cls, markdown_text: str, section_marker: str) -> str:
        """Extract content between a section marker and the next ## header."""
        pattern = rf'{re.escape(section_marker)}\s*\n(.*?)(?=\n##\s|\Z)'
        match = re.search(pattern, markdown_text, re.DOTALL)
        return match.group(1).strip() if match else ""

    @classmethod
    def _parse_contact_section(cls, markdown_text: str, existing_contact: ContactInfo) -> ContactInfo:
        """Parse contact information from markdown."""
        section = cls._extract_section(markdown_text, cls.SECTION_MARKERS['contact'])
        if not section:
            return existing_contact

        contact = existing_contact or ContactInfo()

        # Parse each field
        email_match = re.search(r'\*\*Email:\*\*\s*(.+)', section)
        if email_match:
            contact.email = email_match.group(1).strip()

        phone_match = re.search(r'\*\*Phone:\*\*\s*(.+)', section)
        if phone_match:
            contact.phone = phone_match.group(1).strip()

        location_match = re.search(r'\*\*Location:\*\*\s*(.+)', section)
        if location_match:
            contact.address = location_match.group(1).strip()

        linkedin_match = re.search(r'\*\*LinkedIn:\*\*\s*(.+)', section)
        if linkedin_match:
            contact.linkedin = linkedin_match.group(1).strip()

        github_match = re.search(r'\*\*GitHub:\*\*\s*(.+)', section)
        if github_match:
            contact.github = github_match.group(1).strip()

        return contact

    @classmethod
    def _parse_summary_section(cls, markdown_text: str) -> str:
        """Parse professional summary from markdown."""
        return cls._extract_section(markdown_text, cls.SECTION_MARKERS['summary'])

    @classmethod
    def _parse_skills_section(cls, markdown_text: str) -> List[str]:
        """Parse skills from markdown."""
        section = cls._extract_section(markdown_text, cls.SECTION_MARKERS['skills'])
        if not section:
            return []

        skills = []
        for line in section.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                skills.append(line[2:].strip())

        return skills

    @classmethod
    def _parse_experience_section(cls, markdown_text: str) -> List[Experience]:
        """Parse work experience from markdown."""
        section = cls._extract_section(markdown_text, cls.SECTION_MARKERS['experience'])
        if not section:
            return []

        experiences = []
        # Split by ### headers
        exp_blocks = re.split(r'\n###\s+', section)

        for block in exp_blocks:
            if not block.strip():
                continue

            exp = Experience()
            lines = block.strip().split('\n')

            # First line: Position @ Company
            if lines:
                title_line = lines[0]
                if ' @ ' in title_line:
                    parts = title_line.split(' @ ', 1)
                    exp.position = parts[0].strip()
                    exp.company = parts[1].strip()
                else:
                    exp.position = title_line.strip()

            # Parse rest of lines
            description = []
            skills_used = []

            for line in lines[1:]:
                line = line.strip()

                # Duration (italic)
                if line.startswith('*') and line.endswith('*'):
                    exp.duration = line.strip('*')
                # Bullet points
                elif line.startswith('- '):
                    description.append(line[2:].strip())
                # Skills line
                elif line.startswith('**Skills:**'):
                    skills_str = line.replace('**Skills:**', '').strip()
                    skills_used = [s.strip() for s in skills_str.split(',')]

            exp.description = description
            exp.skills_used = skills_used

            if exp.position or exp.company:
                experiences.append(exp)

        return experiences

    @classmethod
    def _parse_education_section(cls, markdown_text: str) -> List[Education]:
        """Parse education from markdown."""
        section = cls._extract_section(markdown_text, cls.SECTION_MARKERS['education'])
        if not section:
            return []

        education_list = []
        # Split by ### headers
        edu_blocks = re.split(r'\n###\s+', section)

        for block in edu_blocks:
            if not block.strip():
                continue

            edu = Education()
            lines = block.strip().split('\n')

            # First line: Degree in Field
            if lines:
                degree_line = lines[0]
                if ' in ' in degree_line:
                    parts = degree_line.split(' in ', 1)
                    edu.degree = parts[0].strip()
                    edu.field = parts[1].strip()
                else:
                    edu.degree = degree_line.strip()

            # Parse rest of lines
            description = []

            for line in lines[1:]:
                line = line.strip()

                # Institution (bold)
                if line.startswith('**') and line.endswith('**'):
                    edu.institution = line.strip('*')
                # Date (italic)
                elif line.startswith('*') and line.endswith('*'):
                    edu.graduation_date = line.strip('*')
                # GPA
                elif line.startswith('GPA:'):
                    edu.gpa = line.replace('GPA:', '').strip()
                # Bullet points
                elif line.startswith('- '):
                    description.append(line[2:].strip())

            edu.description = description

            if edu.degree or edu.institution:
                education_list.append(edu)

        return education_list

    @classmethod
    def _parse_certifications_section(cls, markdown_text: str) -> List[str]:
        """Parse certifications from markdown."""
        section = cls._extract_section(markdown_text, cls.SECTION_MARKERS['certifications'])
        if not section:
            return []

        certs = []
        for line in section.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                certs.append(line[2:].strip())

        return certs

    @classmethod
    def _parse_languages_section(cls, markdown_text: str) -> List[str]:
        """Parse languages from markdown."""
        section = cls._extract_section(markdown_text, cls.SECTION_MARKERS['languages'])
        if not section:
            return []

        languages = []
        for line in section.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                languages.append(line[2:].strip())

        return languages

    @classmethod
    def get_section_markdown(cls, resume_data: ResumeData, section: str) -> str:
        """
        Get markdown for a specific section only.

        Args:
            resume_data: The resume data
            section: Section name ('contact', 'summary', 'skills', 'experience', 'education', 'certifications', 'languages')

        Returns:
            Markdown string for that section
        """
        if section == 'contact':
            return cls._contact_to_markdown(resume_data.contact_info)
        elif section == 'summary':
            return cls._summary_to_markdown(resume_data.summary) if resume_data.summary else ""
        elif section == 'skills':
            return cls._skills_to_markdown(resume_data.skills) if resume_data.skills else ""
        elif section == 'experience':
            return cls._experience_to_markdown(resume_data.experience) if resume_data.experience else ""
        elif section == 'education':
            return cls._education_to_markdown(resume_data.education) if resume_data.education else ""
        elif section == 'certifications':
            return cls._certifications_to_markdown(resume_data.certifications) if resume_data.certifications else ""
        elif section == 'languages':
            return cls._languages_to_markdown(resume_data.languages) if resume_data.languages else ""
        else:
            return ""

    @classmethod
    def save_to_file(cls, resume_data: ResumeData, file_path: Path) -> Path:
        """
        Save resume as markdown file.

        Args:
            resume_data: The resume data
            file_path: Path to save the markdown file

        Returns:
            Path to the saved file
        """
        markdown_content = cls.resume_to_markdown(resume_data)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(markdown_content, encoding='utf-8')
        return file_path

    @classmethod
    def load_from_file(cls, file_path: Path) -> ResumeData:
        """
        Load resume from markdown file.

        Args:
            file_path: Path to the markdown file

        Returns:
            ResumeData object
        """
        markdown_content = file_path.read_text(encoding='utf-8')
        return cls.markdown_to_resume(markdown_content)
