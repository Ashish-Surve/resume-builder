
# AI-Powered Resume Optimizer

🚀 **Transform your resume with AI-powered optimization for better ATS compatibility and job matching.**

## Features

- **🎯 ATS Optimization**: Improve compatibility with Applicant Tracking Systems
- **🤖 AI-Powered Analysis**: Leverage Perplexity AI and Google Gemini for intelligent recommendations
- **📊 Job Matching**: Analyze resume against specific job descriptions
- **🔑 Keyword Optimization**: Identify and suggest missing keywords
- **📄 PDF Generation**: Create professionally formatted, ATS-compliant resumes
- **🎨 Streamlit UI**: User-friendly web interface

## Architecture

The application follows a modular, object-oriented architecture with clear separation of concerns:

```
src/
├── resume_optimizer/
│   ├── config/          # Configuration management
│   ├── core/            # Core business logic
│   │   ├── resume_parser/     # Resume parsing and extraction
│   │   ├── job_analyzer/      # Job description analysis
│   │   ├── ai_integration/    # AI service clients
│   │   ├── ats_optimizer/     # ATS optimization engine
│   │   └── pdf_generator/     # PDF generation
│   ├── streamlit_ui/    # Streamlit web interface
│   └── utils/           # Utilities and helpers
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/resume-optimizer.git
cd resume-optimizer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install spaCy model:
```bash
python -m spacy download en_core_web_sm
```

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### Streamlit Web Interface (Recommended)

```bash
python main.py
```

Then open http://localhost:8501 in your browser.

### Command Line Interface

```bash
python main.py --cli \
    --resume path/to/resume.pdf \
    --job path/to/job_description.txt \
    --output optimized_resume.pdf \
    --name "John Doe" \
    --company "TechCorp"
```

## Configuration

### Required API Keys

- **Perplexity AI**: Get from https://perplexity.ai/
- **Google Gemini**: Get from https://makersuite.google.com/

### Environment Variables

```bash
# AI Service API Keys
PERPLEXITY_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# Application Settings
DATA_DIR=data
TEMP_DIR=data/temp
DEBUG=false
```

## Development

### Project Structure

The project follows PEP 8 standards and modern Python best practices:

- **Modular Design**: Clear separation of concerns with dedicated modules
- **Object-Oriented**: Uses design patterns like Factory, Strategy, and Observer
- **Type Hints**: Full type annotation support
- **Error Handling**: Comprehensive exception handling
- **Logging**: Structured logging throughout the application
- **Configuration**: Centralized configuration management

### Key Components

1. **Resume Parser**: Extracts structured data from PDF/DOCX/TXT files
2. **Job Analyzer**: Analyzes job descriptions for requirements and keywords
3. **AI Integration**: Interfaces with Perplexity AI and Google Gemini
4. **ATS Optimizer**: Improves resume for ATS compatibility
5. **PDF Generator**: Creates professional, ATS-friendly PDFs

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- 📧 Email: support@resume-optimizer.com
- 🐛 Issues: GitHub Issues
- 📚 Documentation: See docs/ directory
