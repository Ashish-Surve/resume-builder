# Quick Start Guide

## Installation & Setup (First Time)

```bash
# 1. Sync dependencies
uv sync

# 2. Load environment variables (optional, for Gemini API)
# Copy .env.example to .env and add your GOOGLE_API_KEY
cp .env.example .env
# Edit .env and add your Gemini API key (get it from https://makersuite.google.com/)
```

## Running the App

```bash
# Method 1: Direct (Recommended)
uv run streamlit run src/resume_optimizer/streamlit_ui/app.py

# Method 2: Using the startup script (kills old processes)
bash start_app.sh

# Method 3: Using Python directly
python main.py
```

The app will open at: **http://localhost:8501**

## Features

### Stage 1: Resume Parsing
- Upload your resume (PDF, DOCX, or TXT)
- Choose parser:
  - **Spacy Parser** (fast, offline, no API needed)
  - **Gemini Parser** (AI-powered, requires GOOGLE_API_KEY in .env)
- Edit parsed resume data before confirming

### Stage 2: Job Analysis
- Paste a job description
- Choose analyzer:
  - **Standard Analyzer** (keyword matching, no API needed)
  - **Gemini Analyzer** (AI-powered, requires GOOGLE_API_KEY in .env)
- Edit analyzed job requirements before confirming

### Stage 3: ATS Optimization
- Automatically optimizes your resume to match the job
- Edit optimization results if needed
- Re-run if you made changes to resume or job data

### Stage 4: PDF Generation
- Generate an optimized PDF of your resume
- Download the file
- Start a new optimization workflow

## Troubleshooting

### Port 8501 Already in Use
```bash
# Kill old Streamlit processes
pkill -f "streamlit run"

# Or use the startup script
bash start_app.sh
```

### ModuleNotFoundError
```bash
# Make sure dependencies are installed
uv sync

# Run from the project root directory
cd /path/to/resume-builder
```

### White Screen at localhost:8501
- Clear your browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
- Close and reopen the app
- Try a different browser

### Gemini Parser/Analyzer Shows Error
- Make sure you have a valid `GOOGLE_API_KEY` in your `.env` file
- See [GEMINI_API_SETUP.md](GEMINI_API_SETUP.md) for detailed setup instructions
- Use Spacy Parser or Standard Analyzer instead (no API key needed)

## File Structure

```
resume-builder/
├── src/resume_optimizer/
│   ├── streamlit_ui/          # Streamlit app UI
│   │   ├── app.py            # Main entry point
│   │   ├── stages/           # 4-stage workflow
│   │   ├── components/       # UI components
│   │   ├── state/            # Session state management
│   │   └── utils.py          # Utility functions
│   ├── core/
│   │   ├── resume_parser/    # Resume parsing (Spacy, Gemini)
│   │   ├── job_analyzer/     # Job analysis (Standard, Gemini)
│   │   ├── optimizer/        # ATS optimization
│   │   ├── pdf_generator/    # PDF generation
│   │   └── ai_integration/   # Gemini client
│   └── utils/                # Shared utilities
├── .env                        # API keys (add your GOOGLE_API_KEY here)
├── .env.example               # Example config (template)
├── pyproject.toml             # Python project configuration
├── main.py                    # Alternative CLI entry point
└── start_app.sh               # Startup script
```

## Development

### View Logs
```bash
tail -f logs/resume_optimizer.log
```

### Run Tests
```bash
uv run pytest tests/
```

### Add Dependencies
```bash
uv add <package-name>
```

## Performance Tips

1. **First run is slow** - Spacy downloads the language model (~50MB)
2. **API calls are rate-limited** - Gemini has 15 requests per minute limit (free tier)
3. **Responses are cached** - Identical requests within 24 hours use cached results
4. **Use Spacy for testing** - Faster and no API key needed

## API Limits (Free Tier)

- Gemini API: 1,500 requests per day
- Typical session: 2-4 requests (1 for parsing + 1 for analysis)
- Enough for 300+ resume optimizations per day

## Next Steps

1. Start the app: `uv run streamlit run src/resume_optimizer/streamlit_ui/app.py`
2. Upload a resume and try Stage 1
3. Paste a job description in Stage 2
4. Watch your resume get optimized in Stage 3
5. Generate your ATS-friendly PDF in Stage 4

For advanced setup with Gemini API, see [GEMINI_API_SETUP.md](GEMINI_API_SETUP.md)
