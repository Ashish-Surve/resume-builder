"""WeasyPrint-based PDF generator for beautiful resume formatting."""

import logging
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from resume_optimizer.core.models import ResumeData, OptimizationResult

logger = logging.getLogger(__name__)

# Try to import WeasyPrint - it requires system libraries
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    WEASYPRINT_ERROR = str(e)
    logger.warning(f"WeasyPrint is not available: {e}")


class WeasyPrintResumeGenerator:
    """Generate beautifully formatted PDFs using HTML/CSS templates and WeasyPrint.

    This generator uses Jinja2 templates for HTML structure and CSS for styling,
    providing pixel-perfect control over layout and typography for professional
    resume PDFs that rival commercial resume builders.
    """

    def __init__(self, template_dir: Optional[Path] = None):
        """Initialize the WeasyPrint PDF generator.

        Args:
            template_dir: Directory containing templates. If None, uses default templates
                         directory adjacent to this file.

        Raises:
            RuntimeError: If WeasyPrint is not available due to missing system libraries
        """
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError(
                f"WeasyPrint is not available. Please install system dependencies:\n"
                f"  macOS: brew install glib gobject-introspection\n"
                f"  Linux: sudo apt install libgobject-2.0-0 libpango-1.0-0 libpangocairo-1.0-0\n"
                f"Error: {WEASYPRINT_ERROR}"
            )

        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"

        self.template_dir = template_dir

        # Set up Jinja2 environment
        try:
            self.env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                autoescape=True,  # Security best practice
                trim_blocks=True,
                lstrip_blocks=True
            )
            logger.info(f"Initialized WeasyPrint generator with templates from {template_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize Jinja2 environment: {e}")
            raise

    def generate_pdf(
        self,
        resume_data: ResumeData,
        optimization_result: OptimizationResult,
        output_path: Path,
        applicant_name: str,
        company_name: str,
        template_name: str = "resume_template.html",
        css_name: str = "resume_style.css"
    ) -> Path:
        """Generate a beautifully formatted PDF resume.

        Args:
            resume_data: The resume data to render
            optimization_result: Optimization results (for potential future use)
            output_path: Path where the PDF should be saved
            applicant_name: Name of the applicant (for potential customization)
            company_name: Company name (for potential customization)
            template_name: Name of the HTML template file
            css_name: Name of the CSS stylesheet file

        Returns:
            Path to the generated PDF file

        Raises:
            TemplateNotFound: If the specified template doesn't exist
            Exception: For other PDF generation errors
        """
        try:
            # Load and render HTML template
            logger.info(f"Loading template: {template_name}")
            template = self.env.get_template(template_name)

            # Prepare context for template rendering
            context = {
                'contact_info': resume_data.contact_info,
                'summary': resume_data.summary,
                'skills': resume_data.skills,
                'experience': resume_data.experience,
                'education': resume_data.education,
                'certifications': resume_data.certifications,
                'languages': resume_data.languages,
                'applicant_name': applicant_name,
                'company_name': company_name,
                'ats_score': optimization_result.ats_compliance_score if optimization_result else None,
            }

            # Render HTML
            logger.info("Rendering HTML template with resume data")
            html_content = template.render(**context)

            # Load CSS stylesheet
            css_path = self.template_dir / css_name
            stylesheets = []

            if css_path.exists():
                logger.info(f"Loading CSS stylesheet: {css_name}")
                stylesheets.append(CSS(filename=str(css_path)))
            else:
                logger.warning(f"CSS file not found: {css_path}. PDF will be generated without custom styles.")

            # Generate PDF
            logger.info(f"Generating PDF at {output_path}")
            HTML(string=html_content).write_pdf(
                str(output_path),
                stylesheets=stylesheets
            )

            logger.info(f"Successfully generated PDF: {output_path}")
            return output_path

        except TemplateNotFound as e:
            logger.error(f"Template not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            raise Exception(f"PDF generation failed: {str(e)}") from e

    def list_available_templates(self) -> list[str]:
        """List all available HTML templates in the template directory.

        Returns:
            List of template filenames
        """
        try:
            templates = [
                f.name for f in self.template_dir.glob("*.html")
            ]
            return sorted(templates)
        except Exception as e:
            logger.error(f"Failed to list templates: {e}")
            return []
