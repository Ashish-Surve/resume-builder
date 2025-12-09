from pathlib import Path
import os
from resume_optimizer.core.resume_parser.GeminiParser import GeminiResumeParser
from resume_optimizer.core.pdf_generator.generator import PDFGeneratorFactory
from resume_optimizer.core.models import OptimizationResult, ResumeData

# Prepare sample gemini_data (possibly malformed originally) but we'll feed it to converter
gemini_data = {
    "Name": "Ashish Surve",
    "Email": "ashish@example.com",
    "Phone": "+1-555-123-4567",
    "LinkedIn": "https://linkedin.com/in/ashishsurve",
    "GitHub": "https://github.com/ashishsurve",
    "Summary": '{ "summary": "Highly accomplished Data Scientist with 6+ years of experience architecting and deploying end-to-end Machine Learning systems, specializing in PyTorch and TensorFlow for complex business challenges." }',
    "Skills": '{ "skills": ["Machine Learning", "Artificial Intelligence", "Data Science", "Python", "PyTorch", "TensorFlow", "SQL"] }',
    "Experience": [
        {
            "Company": "Example Inc",
            "Position": "Lead Data Scientist",
            "Duration": "2019 - Present",
            "Description": "- Architected ML pipelines\n- Deployed models to production"
        }
    ],
    "Education": [
        {
            "Institution": "State University",
            "Degree": "Bachelor of Science",
            "Field": "Computer Science",
            "Year": "2016",
            "GPA": None,
            "Description": []
        }
    ],
    "Certifications": "AWS Certified Solutions Architect\n• TensorFlow Developer",
    "Projects": None
}

# Convert to ResumeData using converter (we avoid calling external Gemini API)
parser = GeminiResumeParser(None)
resume_data = parser._convert_to_resume_data(gemini_data, raw_text="(stubbed raw text)", file_path=Path('data/input/resumes/example.pdf'), file_type=None)

# Create a fake OptimizationResult wrapping this resume (no actual optimization)
opt_result = OptimizationResult()
opt_result.optimized_resume = resume_data
opt_result.original_score = 50.0
opt_result.optimized_score = 50.0

# Ensure output dir exists
out_dir = Path('output/pdfs')
out_dir.mkdir(parents=True, exist_ok=True)
output_path = out_dir / 'test_stub.pdf'

# Generate PDF
gen = PDFGeneratorFactory().create_generator()
try:
    gen.generate_pdf(resume_data, opt_result, output_path, applicant_name=resume_data.contact_info.name or 'Applicant', company_name='ACME')
    print(f"PDF generated at: {output_path.resolve()}")
except Exception as e:
    print(f"PDF generation failed: {e}")
