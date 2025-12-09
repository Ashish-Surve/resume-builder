# Setup and Run the Streamlit UI

## Prerequisites

You need `uv` installed. If not:
```bash
pip install uv
```

## Step 1: Install Dependencies

Since you're using `uv`, sync all dependencies:

```bash
uv sync
```

This will install all packages in `pyproject.toml` including:
- streamlit
- langchain
- spacy
- pandas
- reportlab
- and all others

If you want to add streamlit manually:
```bash
uv add streamlit
```

## Step 2: Run the Application

Once dependencies are installed, you have two options:

### Option 1: Direct with uv
```bash
uv run streamlit run src/resume_optimizer/streamlit_ui/app.py
```

### Option 2: Using main.py
```bash
uv run python main.py
```

### Option 3: With activated venv
```bash
source .venv/bin/activate
streamlit run src/resume_optimizer/streamlit_ui/app.py
```

## Step 3: Open Browser

The app will automatically open at:
```
http://localhost:8501
```

If not, manually open your browser to that URL.

## Troubleshooting

### "streamlit: command not found"
- Make sure dependencies are installed: `uv sync`
- Or run with: `uv run streamlit run ...`

### "ModuleNotFoundError: No module named 'streamlit'"
- Run: `uv sync`
- Or: `uv add streamlit`

### "Runtime instance already exists!"
- This should not happen anymore (main.py has been fixed)
- If it does, restart your terminal/venv

### Dependencies missing
- Run: `uv sync --all-groups` to install all including dev dependencies

## What the App Does

The 4-stage Resume Optimizer workflow:

1. **Upload & Parse Resume** - Choose parser, upload file, edit parsed data
2. **Analyze Job Description** - Paste job text, choose analyzer, edit job data
3. **Run ATS Optimization** - Optimize resume, edit results, re-run if needed
4. **Generate & Download PDF** - Preview resume, generate PDF, download

## Quick Checklist

- [ ] `uv sync` ran successfully
- [ ] No error messages about missing packages
- [ ] Streamlit starts and shows app
- [ ] Can navigate through 4 stages
- [ ] Can edit forms at each stage
- [ ] Can upload a resume file
- [ ] Can paste job description
- [ ] Can generate PDF

## Need Help?

Check the documentation:
- **STREAMLIT_QUICKSTART.md** - User guide
- **IMPLEMENTATION_COMPLETE.md** - Feature details
- **FIXED_AND_READY.md** - Technical summary
