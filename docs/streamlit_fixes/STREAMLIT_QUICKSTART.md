# Streamlit Resume Optimizer - Quick Start

## Installation

The app is already implemented. Just ensure Streamlit is installed:

```bash
uv add streamlit
```

## Running the App

```bash
uv run streamlit run main.py
```

The app will launch at `http://localhost:8501`

## 4-Stage Workflow

### Stage 1: Resume Parsing
1. Enter your full name
2. Enter target company name
3. Upload your resume (PDF, DOCX, or TXT)
4. Choose parser: Spacy (fast) or Gemini (AI-powered)
5. Click "Parse Resume"
6. Edit the parsed resume data as needed
7. Click "Confirm and Continue"

### Stage 2: Job Analysis
1. Paste the complete job description
2. Choose analyzer: Standard or Gemini
3. Click "Analyze Job Description"
4. Edit the job data as needed
5. Click "Confirm and Continue"

### Stage 3: ATS Optimization
1. Click "Run Optimization" to optimize your resume against the job
2. Edit the optimization results (resume, recommendations, keywords)
3. Click "Confirm and Continue"

### Stage 4: PDF Generation
1. Review the text preview of your optimized resume
2. Click "Generate PDF" to create the ATS-friendly PDF
3. Click "Download PDF" to save to your computer
4. Optionally click "Start New Resume" to process another application

## Key Features

✨ **Editable at Every Stage**: Make changes after parsing/analysis without re-uploading

🔄 **Smart Re-processing**: If you edit earlier stages, the app warns you to re-run optimization

📊 **Progress Tracking**: Sidebar shows which stage you're on and what's completed

✅ **Validation**: All fields are validated before moving to the next stage

📄 **ATS-Optimized PDF**: Final PDF follows ATS best practices for maximum compatibility

## File Structure

```
src/resume_optimizer/streamlit_ui/
├── app.py                          # Main orchestrator
├── state/                          # Session state management
│   ├── session_manager.py
│   └── validators.py
├── components/                     # Reusable UI components
│   ├── common.py                  # Header and navigation
│   ├── progress.py                # Progress sidebar
│   ├── editors.py                 # Editable form builders
│   └── validators.py              # Validation UI
└── stages/                        # Stage implementations
    ├── stage1_resume_parsing.py
    ├── stage2_job_analysis.py
    ├── stage3_ats_optimization.py
    └── stage4_pdf_generation.py
```

## Troubleshooting

**Resume parsing fails**
- Try the Gemini parser instead of Spacy
- Or manually edit the parsed resume data

**Job analysis doesn't extract data**
- Try the Gemini analyzer instead of Standard
- Or manually fill in the job data form

**PDF generation fails**
- Ensure all required fields are filled in
- Check that the optimized resume data is complete

**App won't start**
- Make sure Streamlit is installed: `uv add streamlit`
- Check that all dependencies in `pyproject.toml` are installed: `uv sync`

## Tips

- **Spacy Parser**: Fast, no API calls required
- **Gemini Parser**: Better AI extraction, requires API key
- **Standard Analyzer**: Fast keyword matching
- **Gemini Analyzer**: Better understanding of job requirements
- **Re-run Optimization**: Use if you edit resume or job data after initial optimization
- **Preview Before Download**: Always review the text preview before generating PDF

## Architecture

The app uses:
- **Streamlit** for the UI
- **Pydantic** models for data validation
- **ReportLab** for PDF generation
- **Spacy** and **Gemini API** for NLP parsing
- **Session state** for data persistence across reruns

## Development

All code is in `src/resume_optimizer/streamlit_ui/` with clear separation:
- `state/` - Session and validation logic (testable, non-UI)
- `components/` - Reusable UI widgets (composable, isolated)
- `stages/` - Stage-specific workflows (independent, clean)

Code is designed to be simple, readable, and easy to debug.
