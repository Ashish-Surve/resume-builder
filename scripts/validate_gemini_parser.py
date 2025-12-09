from pathlib import Path
from resume_optimizer.core.resume_parser.GeminiParser import GeminiResumeParser

parser = GeminiResumeParser(None)
# Simulate problematic nested JSON strings in fields
gemini_data = {
    "Name": "Ashish Surve",
    "Email": "ashish@example.com",
    "Summary": '{ "summary": "Highly accomplished Data Scientist with 6+ years of experience architecting and deploying end-to-end Machine Learning systems..." }',
    "Skills": '{ "skills": ["Machine Learning", "Python", "PyTorch"] }',
    "Experience": [
        {
            "Company": "Example Inc",
            "Position": "Lead Data Scientist",
            "Duration": "2019 - Present",
            "Description": "- Built models\n- Deployed to production"
        }
    ],
    "Certifications": "AWS Certified Solutions Architect\n• TensorFlow Developer" 
}

rd = parser._convert_to_resume_data(gemini_data, raw_text="raw text here", file_path=Path('test.pdf'), file_type=None)
print('SUMMARY:', repr(rd.summary))
print('TYPE SUMMARY:', type(rd.summary))
print('SKILLS:', rd.skills)
print('TYPE SKILLS:', type(rd.skills))
print('CERTIFICATIONS:', rd.certifications)
print('TYPE CERTIFICATIONS:', type(rd.certifications))
print('EXPERIENCE DESC:', rd.experience[0].description)
print('TYPE EXP DESC:', type(rd.experience[0].description))
