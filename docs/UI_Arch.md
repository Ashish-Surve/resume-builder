# Multi-Step Editable Resume Optimizer UI - Implementation Plan

## Overview
Complete rewrite of the Streamlit app to implement a 4-stage workflow where users can edit data at each stage before proceeding to the next.

## Current State
- **Main App**: `src/resume_optimizer/streamlit_ui/app.py` - Currently mocks all processing
- **Entry Point**: `main.py` - Launches Streamlit app
- **Components**: Core processing classes exist and are fully functional (parsers, analyzers, optimizers, PDF generator)

## User Requirements

### 4-Stage Editable Workflow

1. **Stage 1: Resume Parsing**
   - Upload resume file (PDF/DOCX/TXT)
   - Parse using Spacy or Gemini parser
   - Display parsed `ResumeData` in editable form
   - Allow user to add/edit/remove: contact info, summary, skills, experience entries, education, certifications
   - Validate and confirm before proceeding

2. **Stage 2: Job Analysis**
   - Input job description text
   - Analyze using standard or Gemini analyzer
   - Display parsed `JobDescriptionData` in editable form
   - Allow user to edit: job title, company, required/preferred skills, keywords, experience level
   - Validate and confirm before proceeding

3. **Stage 3: ATS Optimization**
   - Run ATS optimization on Stage 1 + Stage 2 data
   - Display `OptimizationResult` with scores and optimized resume
   - Allow user to edit: optimized resume content, recommendations, keywords
   - Validate and confirm before proceeding

4. **Stage 4: PDF Generation**
   - Preview optimized resume
   - Generate ATS-friendly PDF
   - Download final resume

### Key Features
- **Editable at Every Stage**: After processing, display data in editable forms (not just JSON)
- **Data Flow**: Each stage passes edited/confirmed data to next stage
- **Navigation**: Allow backward navigation to review/edit previous stages
- **Validation**: Validate data before allowing progression
- **Re-processing**: If user edits earlier stage data, warn them but let them decide when to re-process
- **User Choices**: Users can choose parser type (Spacy/Gemini) and analyzer type (Standard/Gemini)
- **Preview**: Show text preview of resume before PDF generation

## Architecture

### Component-Based Structure

```
src/resume_optimizer/streamlit_ui/
├── app.py                          # REWRITE: Main orchestrator
├── components/                      # NEW: Reusable UI components
│   ├── __init__.py
│   ├── editors.py                  # NEW: Editable form components
│   ├── validators.py               # NEW: Validation UI widgets
│   ├── progress.py                 # NEW: Progress indicators
│   └── common.py                   # NEW: Shared UI elements
├── stages/                         # NEW: Stage implementations
│   ├── __init__.py
│   ├── stage1_resume_parsing.py   # NEW: Stage 1 component
│   ├── stage2_job_analysis.py     # NEW: Stage 2 component
│   ├── stage3_ats_optimization.py # NEW: Stage 3 component
│   └── stage4_pdf_generation.py   # NEW: Stage 4 component
└── state/                          # NEW: State management
    ├── __init__.py
    ├── session_manager.py         # NEW: Session state helpers
    └── validators.py              # NEW: Validation logic
```

### Session State Schema

```python
st.session_state = {
    # Workflow control
    'session_id': str,
    'current_stage': int,  # 0-3
    'stage_status': {0: 'pending', 1: 'pending', 2: 'pending', 3: 'pending'},

    # Stage 1: Resume Parsing
    'uploaded_file_path': Path | None,
    'parser_choice': str,  # 'spacy' | 'gemini'
    'applicant_name': str,  # Collected at Stage 1
    'company_name': str,    # Collected at Stage 1
    'resume_data_raw': ResumeData | None,
    'resume_data_edited': ResumeData | None,
    'stage1_confirmed': bool,

    # Stage 2: Job Analysis
    'job_description_text': str,
    'analyzer_choice': str,  # 'standard' | 'gemini'
    'job_data_raw': JobDescriptionData | None,
    'job_data_edited': JobDescriptionData | None,
    'stage2_confirmed': bool,

    # Stage 3: ATS Optimization
    'optimization_result_raw': OptimizationResult | None,
    'optimization_result_edited': OptimizationResult | None,
    'stage3_confirmed': bool,

    # Stage 4: PDF Generation
    'pdf_path': Path | None,
}
```

## Implementation Plan

### Phase 1: Foundation & State Management

**Files to Create:**
1. `src/resume_optimizer/streamlit_ui/state/session_manager.py`
   - `SessionStateManager` class with `initialize()`, `reset()` methods
   - Initialize all session state variables with defaults

2. `src/resume_optimizer/streamlit_ui/state/validators.py`
   - `validate_resume_data(data: ResumeData) -> (bool, List[str])`
   - `validate_job_data(data: JobDescriptionData) -> (bool, List[str])`
   - Return validation status and error messages

3. `src/resume_optimizer/streamlit_ui/components/common.py`
   - `render_header()` - App header
   - `render_navigation_buttons(back_enabled, forward_enabled, forward_text)`
   - Common UI elements

4. `src/resume_optimizer/streamlit_ui/components/progress.py`
   - `render_progress_sidebar(current_stage, stage_status)` - Progress tracker

### Phase 2: Core Editing Components

**File to Create:**
5. `src/resume_optimizer/streamlit_ui/components/editors.py` - **CRITICAL COMPONENT**

This file contains the editable form builders:

#### `render_resume_data_editor(resume_data: ResumeData) -> ResumeData`
Creates editable form for `ResumeData` using:
- **Contact Info**: `st.text_input()` for name, email, phone, linkedin, github
- **Summary**: `st.text_area()` for professional summary
- **Skills**: `st.data_editor()` with dynamic rows for skill list
- **Experience**: For each experience entry:
  - `st.expander()` to collapse/expand
  - Text inputs for company, position, duration
  - **`st.data_editor()` table for description bullets** - Each row = one bullet point with add/remove capability
  - "Remove Experience" button
  - "Add Experience" button at bottom
- **Education**: Similar pattern with expanders and dynamic fields
- **Certifications**: `st.data_editor()` for list editing
- **Languages**: `st.data_editor()` for list editing

Returns updated `ResumeData` object with user edits.

#### `render_job_data_editor(job_data: JobDescriptionData) -> JobDescriptionData`
Creates editable form for `JobDescriptionData`:
- Text inputs: job title, company, location, experience level
- `st.text_area()` for full description
- `st.data_editor()` for required_skills (dynamic list)
- `st.data_editor()` for preferred_skills (dynamic list)
- `st.data_editor()` for keywords (dynamic list)
- `st.data_editor()` for education_requirements (dynamic list)

Returns updated `JobDescriptionData` object.

#### `render_optimization_result_editor(opt_result: OptimizationResult) -> OptimizationResult`
Creates editable form for `OptimizationResult`:
- Display scores as read-only metrics (original, optimized, ATS compliance)
- **Optimized Resume**: Call `render_resume_data_editor(opt_result.optimized_resume)`
- `st.data_editor()` for recommendations (editable list)
- `st.data_editor()` for missing_keywords (editable list)

Returns updated `OptimizationResult` object.

**Key Implementation Details:**
- Use `model_copy(deep=True)` to create editable copies
- Use unique widget keys: `key=f"exp_company_{i}"`
- Handle add/remove operations with `st.rerun()`
- Convert Pydantic models to DataFrames for `st.data_editor()` and back

**File to Create:**
6. `src/resume_optimizer/streamlit_ui/components/validators.py`
   - `render_validation_results(is_valid, errors)` - Display validation UI

### Phase 3: Stage Components

**Files to Create:**

7. `src/resume_optimizer/streamlit_ui/stages/stage1_resume_parsing.py`

Flow:
- **Collect applicant name and target company name** (text inputs at top)
- File uploader for resume
- Save to temp path: `data/temp/{session_id}_{filename}`
- **Parser selection: Radio buttons for Spacy vs Gemini** (user chooses)
- "Parse Resume" button → Run parser → Store in `resume_data_raw` and `resume_data_edited`
- Display `render_resume_data_editor(resume_data_edited)`
- Validation check
- "Confirm and Continue" button → Advance to stage 2

8. `src/resume_optimizer/streamlit_ui/stages/stage2_job_analysis.py`

Flow:
- Display applicant name and company (read-only from Stage 1)
- **Warning if resume data was edited after earlier processing**: "Resume was modified. You may need to re-run optimization in Stage 3."
- Text area for job description
- **Analyzer selection: Radio buttons for Standard vs Gemini** (user chooses)
- "Analyze Job" button → Run analyzer → Store in `job_data_raw` and `job_data_edited`
- Display `render_job_data_editor(job_data_edited)`
- Validation check
- "Confirm and Continue" button → Advance to stage 3

9. `src/resume_optimizer/streamlit_ui/stages/stage3_ats_optimization.py`

Flow:
- Display applicant name and company (read-only from Stage 1)
- **Warning if data from Stage 1 or 2 was edited**: "Resume or job data was modified. Click 'Re-run Optimization' to update results."
- "Run ATS Optimization" button (or "Re-run" if already done) → Call `ATSOptimizer.optimize()` with `resume_data_edited` + `job_data_edited` + applicant_name + company_name
- Store in `optimization_result_raw` and `optimization_result_edited`
- Display scores (original, optimized, improvement)
- Display `render_optimization_result_editor(optimization_result_edited)`
- Validation check
- "Confirm and Continue" button → Advance to stage 4

10. `src/resume_optimizer/streamlit_ui/stages/stage4_pdf_generation.py`

Flow:
- **Show text preview of optimized resume** (formatted display of what will be in PDF):
  - Contact information section
  - Professional summary
  - Technical skills
  - Work experience with bullets
  - Education
  - Certifications
- **Warning if optimization was re-run**: "Optimization results updated. Review preview before generating PDF."
- "Generate PDF" button → Call `ATSFriendlyPDFGenerator.generate_pdf()` with `optimization_result_edited.optimized_resume`
- Store PDF path in session state
- Display success message
- Download button with PDF file
- "Start New Resume" button → Reset session

### Phase 4: Main App Orchestration

**File to Modify:**

11. **`src/resume_optimizer/streamlit_ui/app.py`** - **COMPLETE REWRITE**

New structure:
```python
import streamlit as st
from state.session_manager import SessionStateManager
from components.progress import render_progress_sidebar
from components.common import render_header
from stages.stage1_resume_parsing import render_stage1_resume_parsing
from stages.stage2_job_analysis import render_stage2_job_analysis
from stages.stage3_ats_optimization import render_stage3_ats_optimization
from stages.stage4_pdf_generation import render_stage4_pdf_generation

class ResumeOptimizerApp:
    def __init__(self):
        SessionStateManager.initialize()

    def run(self):
        render_header()
        render_progress_sidebar()

        # Stage routing
        current_stage = st.session_state.current_stage

        if current_stage == 0:
            render_stage1_resume_parsing()
        elif current_stage == 1:
            render_stage2_job_analysis()
        elif current_stage == 2:
            render_stage3_ats_optimization()
        elif current_stage == 3:
            render_stage4_pdf_generation()

def main():
    app = ResumeOptimizerApp()
    app.run()

if __name__ == "__main__":
    main()
```

## Data Flow

```
Stage 1: Upload file → Parse → Edit → Validate → resume_data_edited
                                                        ↓
Stage 2: Input job text → Analyze → Edit → Validate → job_data_edited
                                                        ↓
Stage 3: resume_data_edited + job_data_edited → Optimize → Edit → Validate → optimization_result_edited
                                                        ↓
Stage 4: optimization_result_edited.optimized_resume → Generate PDF → Download
```

## Navigation Logic

- **Forward**: Enabled only when current stage is validated and confirmed
- **Backward**: Always enabled to review previous stages
- Edits are preserved in session state
- Advancing stage increments `current_stage`
- Going back decrements `current_stage`

### Re-processing Logic
- Track data snapshots when stages are confirmed
- When user returns to Stage 1 or 2 and edits data:
  - Store edit timestamp
  - Show warning in subsequent stages: "Data was modified. Results may be outdated."
  - Provide "Re-run" button to re-process with new data
  - **User decides when to re-process** - don't auto-invalidate results

## Integration with Existing Components

The implementation uses these existing, fully-functional components:

1. **Parsers** (`src/resume_optimizer/core/resume_parser/`):
   - `SpacyResumeParser.parse(file_path) -> ResumeData`
   - `GeminiResumeParser.parse(file_path) -> ResumeData`

2. **Analyzers** (`src/resume_optimizer/core/job_analyzer/`):
   - `JobDescriptionAnalyzer.analyze(job_text) -> JobDescriptionData`
   - `GeminiJobAnalyzer.analyze(job_text) -> JobDescriptionData`

3. **Optimizer** (`src/resume_optimizer/core/ats_optimizer/optimizer.py`):
   - `ATSOptimizer.optimize(resume_data, job_data, applicant_name, company_name) -> OptimizationResult`

4. **PDF Generator** (`src/resume_optimizer/core/pdf_generator/generator.py`):
   - `ATSFriendlyPDFGenerator.generate_pdf(resume_data, optimization_result, output_path, applicant_name, company_name) -> Path`

5. **Data Models** (`src/resume_optimizer/core/models.py`):
   - `ResumeData`, `JobDescriptionData`, `OptimizationResult`
   - All are Pydantic models with validation

## Key Technical Decisions

1. **Editable Forms**: Use `st.data_editor()` for dynamic lists (skills, experience bullets) with add/remove capability
2. **Experience Bullets**: Use `st.data_editor()` table where each row = one bullet point (easier to add/remove)
3. **Nested Structures**: Use `st.expander()` to organize complex nested data (experience entries)
4. **State Management**: Store both raw (AI-generated) and edited (user-modified) versions for comparison
5. **Validation**: Validate on "Confirm" button, not real-time, to avoid disrupting user flow
6. **File Handling**: Save uploaded files to disk immediately to persist across Streamlit reruns
7. **User Choice**: Provide parser selection (Spacy/Gemini) and analyzer selection (Standard/Gemini) via radio buttons
8. **Re-processing**: Warn user when data is modified, but let them decide when to re-run optimization
9. **Applicant Info**: Collect applicant name and company name at Stage 1 (beginning of workflow)
10. **PDF Preview**: Show formatted text preview of resume before generating PDF in Stage 4

## Error Handling

- Wrap API calls (parsers/analyzers/optimizer) in try-except
- Display errors using `st.error()`
- Provide "Retry" buttons for failed operations
- Allow manual editing as fallback when AI services fail
- Set stage status to 'error' on failures

## Files Summary

### New Files (13 files):
1. `src/resume_optimizer/streamlit_ui/state/__init__.py`
2. `src/resume_optimizer/streamlit_ui/state/session_manager.py`
3. `src/resume_optimizer/streamlit_ui/state/validators.py`
4. `src/resume_optimizer/streamlit_ui/components/__init__.py`
5. `src/resume_optimizer/streamlit_ui/components/editors.py` ⭐ CRITICAL
6. `src/resume_optimizer/streamlit_ui/components/validators.py`
7. `src/resume_optimizer/streamlit_ui/components/progress.py`
8. `src/resume_optimizer/streamlit_ui/components/common.py`
9. `src/resume_optimizer/streamlit_ui/stages/__init__.py`
10. `src/resume_optimizer/streamlit_ui/stages/stage1_resume_parsing.py`
11. `src/resume_optimizer/streamlit_ui/stages/stage2_job_analysis.py`
12. `src/resume_optimizer/streamlit_ui/stages/stage3_ats_optimization.py`
13. `src/resume_optimizer/streamlit_ui/stages/stage4_pdf_generation.py`

### Modified Files (1 file):
1. `src/resume_optimizer/streamlit_ui/app.py` - Complete rewrite

### No Changes Required:
- `main.py` - Entry point remains unchanged
- All core processing components - Already functional

## Implementation Order

1. State management (session_manager.py, validators.py)
2. Common components (common.py, progress.py)
3. **Editors** (editors.py) - Most critical component
4. Validation UI (components/validators.py)
5. Stage 1 (stage1_resume_parsing.py)
6. Stage 2 (stage2_job_analysis.py)
7. Stage 3 (stage3_ats_optimization.py)
8. Stage 4 (stage4_pdf_generation.py)
9. Main app rewrite (app.py)
10. End-to-end testing

## Testing Strategy

- Test each editor independently with sample data
- Test each stage workflow in isolation
- Test navigation (forward/backward) with data persistence
- Test validation with invalid data
- Test complete workflow end-to-end
- Test API failure scenarios
- Test file upload with different formats (PDF, DOCX, TXT)

## Success Criteria

- ✅ User can upload and parse resume
- ✅ User can edit all parsed resume fields (contact, skills, experience, education)
- ✅ User can add/remove experience entries and description bullets
- ✅ User can analyze job description and edit results
- ✅ User can run ATS optimization and edit optimized content
- ✅ User can navigate back to previous stages without losing edits
- ✅ User can generate and download final PDF
- ✅ All validation errors are displayed clearly
- ✅ Progress is tracked across stages
