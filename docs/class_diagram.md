# UML Class Diagram (diagram-as-code)

This repo includes a small script that generates an offline UML-style class diagram for the main classes and components.

Script
- `scripts/generate_class_diagram.py` - builds a DOT file and renders PNG using the Python `graphviz` module (which uses Graphviz CLI).

What it includes
- Data models (ResumeData, JobDescriptionData, OptimizationResult, ContactInfo, Experience, Education)
- AI clients (GeminiClient, PerplexityClient)
- Resume parsers (SpacyResumeParser, GeminiResumeParser, BaseResumeParser, ResumeParserFactory)
- Parser extractors (TextExtractor, ContactInfoExtractor, SkillsExtractor, ExperienceExtractor, EducationExtractor, SectionExtractor)
- ATS components (ATSOptimizer, ATSCompatibilityChecker, KeywordOptimizer, ResumeScorer, GeminiResumeOptimizer)
- PDF generator (ATSFriendlyPDFGenerator, PDFGeneratorFactory)
- Streamlit app (ResumeOptimizerApp) and ConfigManager

How to run
1. Ensure Graphviz (CLI) is installed on your machine. On macOS:

```bash
brew install graphviz
```

2. Install the Python dependency (if needed):

```bash
pip install graphviz
```

3. Run the script from the repository root:

```bash
python scripts/generate_class_diagram.py
```

4. The diagram files are written to the `diagrams/` folder:
- `diagrams/class_diagram.dot`
- `diagrams/class_diagram.png`

Notes
- The diagram reflects the current code layout and common relationships.
- Edges are labeled with simple relationship types (uses, contains, creates, processes).
