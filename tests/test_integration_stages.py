"""
Integration tests for all stages of the Resume Optimizer.

These tests use REAL APIs and services (no mocks) to verify end-to-end functionality.
Uses test.pdf from the project root for testing.

Requirements:
- Ollama running with llama3.1:8b model (for parser tests)
- OR GOOGLE_API_KEY set (for Gemini fallback)

Run with: uv run pytest tests/test_integration_stages.py -v -s
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path

# Import models and core components
from resume_optimizer.core.models import (
    ResumeData,
    JobDescriptionData,
    OptimizationResult,
    ContactInfo,
    Experience,
    Education
)

# Import parsers
from resume_optimizer.core.resume_parser import (
    SpacyResumeParser,
    OllamaResumeParser,
    GeminiResumeParser
)
from resume_optimizer.core.ai_integration.ollama_client import OllamaClient, check_ollama_available
from resume_optimizer.core.ai_integration.gemini_client import GeminiClient

# Import job analyzers
from resume_optimizer.core.job_analyzer import JobDescriptionAnalyzer
from resume_optimizer.core.job_analyzer.gemini_analyzer import GeminiJobAnalyzer

# Import optimizer
from resume_optimizer.core.ats_optimizer.optimizer import ATSOptimizer

# Import converters
from resume_optimizer.core.converters.markdown_converter import MarkdownConverter
from resume_optimizer.core.converters.docx_converter import DocxConverter

# Import PDF generator
from resume_optimizer.core.pdf_generator.generator import ATSFriendlyPDFGenerator


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def test_pdf_path() -> Path:
    """Get path to test.pdf."""
    pdf_path = Path(__file__).parent.parent / "test.pdf"
    if not pdf_path.exists():
        pytest.skip(f"test.pdf not found at {pdf_path}")
    return pdf_path


@pytest.fixture(scope="module")
def temp_output_dir() -> Path:
    """Create temporary directory for test outputs."""
    temp_dir = Path(tempfile.mkdtemp(prefix="resume_test_"))
    yield temp_dir
    # Cleanup after all tests
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="module")
def sample_job_description() -> str:
    """Sample job description for testing."""
    return """
    Senior Data Scientist
    TechCorp Inc. - San Francisco, CA

    About the Role:
    We are looking for an experienced Data Scientist to join our AI/ML team.
    You will work on cutting-edge machine learning projects and help build
    data-driven solutions for our enterprise clients.

    Required Qualifications:
    - 5+ years of experience in data science or machine learning
    - Strong proficiency in Python, SQL, and statistical analysis
    - Experience with TensorFlow, PyTorch, or similar ML frameworks
    - Knowledge of cloud platforms (AWS, GCP, or Azure)
    - Experience with big data technologies (Spark, Hadoop)

    Preferred Qualifications:
    - PhD in Computer Science, Statistics, or related field
    - Experience with NLP and deep learning
    - Knowledge of MLOps and model deployment
    - Experience leading data science projects

    Education:
    - Master's degree or higher in Computer Science, Data Science,
      Statistics, or a related quantitative field

    We offer competitive salary, equity, and comprehensive benefits.
    """


# ============================================================================
# STAGE 1: RESUME PARSING TESTS
# ============================================================================

class TestStage1ResumeParsing:
    """Integration tests for Stage 1: Resume Parsing."""

    def test_spacy_parser(self, test_pdf_path: Path):
        """Test SpaCy parser with real PDF."""
        parser = SpacyResumeParser()
        result = parser.parse(test_pdf_path)

        # Verify we got a valid ResumeData object
        assert isinstance(result, ResumeData)
        assert result.raw_text is not None
        assert len(result.raw_text) > 0

        # Print parsed data for inspection
        print("\n=== SpaCy Parser Results ===")
        print(f"Name: {result.contact_info.name}")
        print(f"Email: {result.contact_info.email}")
        print(f"Phone: {result.contact_info.phone}")
        print(f"Skills count: {len(result.skills)}")
        print(f"Experience count: {len(result.experience)}")
        print(f"Education count: {len(result.education)}")

    @pytest.mark.skipif(
        not check_ollama_available(),
        reason="Ollama not running"
    )
    def test_ollama_parser(self, test_pdf_path: Path):
        """Test Ollama parser with real PDF (requires Ollama running)."""
        # Use default model or find available one
        client = OllamaClient(model="llama3.1:8b")

        # Check if model is available
        models = client.list_models()
        if not models:
            pytest.skip("No Ollama models available")

        # Prefer llama3.1, fallback to any available model
        model_to_use = "llama3.1:8b"
        for model in models:
            if "llama3.1" in model.lower():
                model_to_use = model
                break
        else:
            model_to_use = models[0]

        print(f"\nUsing Ollama model: {model_to_use}")

        client = OllamaClient(model=model_to_use, timeout=180)
        parser = OllamaResumeParser(ollama_client=client)
        result = parser.parse(test_pdf_path)

        # Verify we got a valid ResumeData object
        assert isinstance(result, ResumeData)
        assert result.raw_text is not None
        assert len(result.raw_text) > 0

        # Ollama should extract more structured data
        print("\n=== Ollama Parser Results ===")
        print(f"Name: {result.contact_info.name}")
        print(f"Email: {result.contact_info.email}")
        print(f"Phone: {result.contact_info.phone}")
        print(f"LinkedIn: {result.contact_info.linkedin}")
        print(f"GitHub: {result.contact_info.github}")
        print(f"Summary: {result.summary[:100] if result.summary else 'None'}...")
        print(f"Skills: {result.skills[:10]}..." if result.skills else "Skills: None")
        print(f"Experience count: {len(result.experience)}")
        for i, exp in enumerate(result.experience[:2]):
            print(f"  Exp {i+1}: {exp.position} @ {exp.company}")
        print(f"Education count: {len(result.education)}")
        for i, edu in enumerate(result.education[:2]):
            print(f"  Edu {i+1}: {edu.degree} @ {edu.institution}")

        # Verify key fields were extracted
        assert result.contact_info.name or result.contact_info.email, "Should extract at least name or email"

    @pytest.mark.skipif(
        not os.getenv("GOOGLE_API_KEY"),
        reason="GOOGLE_API_KEY not set"
    )
    def test_gemini_parser(self, test_pdf_path: Path):
        """Test Gemini parser with real PDF (requires API key)."""
        api_key = os.getenv("GOOGLE_API_KEY")
        gemini_client = GeminiClient(api_key=api_key)
        parser = GeminiResumeParser(gemini_client=gemini_client)
        result = parser.parse(test_pdf_path)

        # Verify we got a valid ResumeData object
        assert isinstance(result, ResumeData)
        assert result.raw_text is not None

        print("\n=== Gemini Parser Results ===")
        print(f"Name: {result.contact_info.name}")
        print(f"Email: {result.contact_info.email}")
        print(f"Skills count: {len(result.skills)}")
        print(f"Experience count: {len(result.experience)}")

    def test_parser_comparison(self, test_pdf_path: Path):
        """Compare output from different parsers."""
        results = {}

        # SpaCy (always available)
        spacy_parser = SpacyResumeParser()
        results['spacy'] = spacy_parser.parse(test_pdf_path)

        # Ollama (if available)
        if check_ollama_available():
            client = OllamaClient(model="llama3.1:8b", timeout=180)
            ollama_parser = OllamaResumeParser(ollama_client=client)
            try:
                results['ollama'] = ollama_parser.parse(test_pdf_path)
            except Exception as e:
                print(f"Ollama parsing failed: {e}")

        print("\n=== Parser Comparison ===")
        for parser_name, result in results.items():
            print(f"\n{parser_name.upper()}:")
            print(f"  Name: {result.contact_info.name}")
            print(f"  Email: {result.contact_info.email}")
            print(f"  Skills: {len(result.skills)} found")
            print(f"  Experience: {len(result.experience)} entries")
            print(f"  Education: {len(result.education)} entries")


# ============================================================================
# STAGE 2: JOB ANALYSIS TESTS
# ============================================================================

class TestStage2JobAnalysis:
    """Integration tests for Stage 2: Job Description Analysis."""

    def test_standard_analyzer(self, sample_job_description: str):
        """Test standard job description analyzer."""
        analyzer = JobDescriptionAnalyzer()
        result = analyzer.analyze(sample_job_description, company_name="TechCorp Inc.")

        # Verify we got a valid JobDescriptionData object
        assert isinstance(result, JobDescriptionData)
        assert result.raw_text == sample_job_description

        print("\n=== Standard Job Analyzer Results ===")
        print(f"Title: {result.title}")
        print(f"Company: {result.company}")
        print(f"Location: {result.location}")
        print(f"Required Skills: {result.required_skills[:5]}...")
        print(f"Preferred Skills: {result.preferred_skills[:3]}...")
        print(f"Keywords: {result.keywords[:5]}...")
        print(f"Experience Level: {result.experience_level}")

        # Verify key extractions
        assert len(result.required_skills) > 0 or len(result.keywords) > 0

    @pytest.mark.skipif(
        not os.getenv("GOOGLE_API_KEY"),
        reason="GOOGLE_API_KEY not set"
    )
    def test_gemini_analyzer(self, sample_job_description: str):
        """Test Gemini job analyzer (requires API key)."""
        analyzer = GeminiJobAnalyzer()
        result = analyzer.analyze(sample_job_description, company_name="TechCorp Inc.")

        # Verify we got a valid JobDescriptionData object
        assert isinstance(result, JobDescriptionData)

        print("\n=== Gemini Job Analyzer Results ===")
        print(f"Title: {result.title}")
        print(f"Company: {result.company}")
        print(f"Required Skills: {result.required_skills}")
        print(f"Preferred Skills: {result.preferred_skills}")
        print(f"Experience Level: {result.experience_level}")

        # Gemini should extract more accurate data
        assert result.title is not None


# ============================================================================
# STAGE 3: ATS OPTIMIZATION TESTS
# ============================================================================

class TestStage3ATSOptimization:
    """Integration tests for Stage 3: ATS Optimization."""

    @pytest.fixture
    def parsed_resume(self, test_pdf_path: Path) -> ResumeData:
        """Parse resume for optimization tests."""
        # Use Ollama if available, else SpaCy
        if check_ollama_available():
            client = OllamaClient(model="llama3.1:8b", timeout=180)
            parser = OllamaResumeParser(ollama_client=client)
        else:
            parser = SpacyResumeParser()

        return parser.parse(test_pdf_path)

    @pytest.fixture
    def parsed_job(self, sample_job_description: str) -> JobDescriptionData:
        """Parse job description for optimization tests."""
        analyzer = JobDescriptionAnalyzer()
        return analyzer.analyze(sample_job_description, company_name="TechCorp Inc.")

    @pytest.mark.skipif(
        not os.getenv("GOOGLE_API_KEY"),
        reason="GOOGLE_API_KEY required for optimization"
    )
    def test_ats_optimization(
        self,
        parsed_resume: ResumeData,
        parsed_job: JobDescriptionData
    ):
        """Test ATS optimization with real data."""
        optimizer = ATSOptimizer()

        result = optimizer.optimize(
            resume_data=parsed_resume,
            job_data=parsed_job,
            applicant_name="Test Applicant",
            company_name="TechCorp Inc."
        )

        # Verify we got a valid OptimizationResult
        assert isinstance(result, OptimizationResult)
        assert result.optimized_resume is not None

        print("\n=== ATS Optimization Results ===")
        print(f"Original Score: {result.original_score:.1f}")
        print(f"Optimized Score: {result.optimized_score:.1f}")
        print(f"Improvement: {result.optimized_score - result.original_score:+.1f}")
        print(f"ATS Compliance: {result.ats_compliance_score:.1f}%")
        print(f"Missing Keywords: {result.missing_keywords[:5]}...")
        print(f"Recommendations: {len(result.recommendations)} items")
        for rec in result.recommendations[:3]:
            print(f"  - {rec[:80]}...")

        # Verify optimization improved the score
        assert result.optimized_score >= result.original_score, "Optimization should improve or maintain score"


# ============================================================================
# STAGE 4: EXPORT TESTS (Markdown, DOCX, PDF)
# ============================================================================

class TestStage4Export:
    """Integration tests for Stage 4: Export functionality."""

    @pytest.fixture
    def sample_resume(self) -> ResumeData:
        """Create a sample resume for export tests."""
        return ResumeData(
            contact_info=ContactInfo(
                name="John Doe",
                email="john.doe@email.com",
                phone="+1-555-123-4567",
                linkedin="linkedin.com/in/johndoe",
                github="github.com/johndoe",
                address="San Francisco, CA"
            ),
            summary="Experienced software engineer with 10+ years in Python and cloud technologies.",
            skills=["Python", "Django", "AWS", "Docker", "Kubernetes", "PostgreSQL", "Machine Learning"],
            experience=[
                Experience(
                    company="TechCorp Inc.",
                    position="Senior Software Engineer",
                    duration="2020 - Present",
                    start_date="2020-01",
                    end_date=None,
                    description=[
                        "Led development of microservices architecture",
                        "Improved system performance by 40%",
                        "Mentored team of 5 junior developers"
                    ],
                    skills_used=["Python", "AWS", "Docker"]
                ),
                Experience(
                    company="StartupXYZ",
                    position="Software Engineer",
                    duration="2017 - 2020",
                    start_date="2017-06",
                    end_date="2020-01",
                    description=[
                        "Built RESTful APIs using Django",
                        "Implemented CI/CD pipelines"
                    ],
                    skills_used=["Python", "Django", "PostgreSQL"]
                )
            ],
            education=[
                Education(
                    institution="Stanford University",
                    degree="Master of Science",
                    field="Computer Science",
                    graduation_date="2017",
                    gpa="3.8",
                    description=["Focus on Machine Learning"]
                )
            ],
            certifications=["AWS Solutions Architect", "Kubernetes Administrator"],
            languages=["English (Native)", "Spanish (Intermediate)"],
            raw_text="Sample raw text"
        )

    def test_markdown_conversion(self, sample_resume: ResumeData):
        """Test ResumeData to Markdown conversion."""
        # Convert to markdown
        markdown = MarkdownConverter.resume_to_markdown(sample_resume)

        print("\n=== Markdown Output ===")
        print(markdown[:500])
        print("...")

        # Verify markdown contains key sections
        assert "# John Doe" in markdown
        assert "## Contact Information" in markdown
        assert "## Professional Summary" in markdown
        assert "## Skills" in markdown
        assert "## Work Experience" in markdown
        assert "## Education" in markdown
        assert "john.doe@email.com" in markdown
        assert "Python" in markdown

        # Test parsing back to ResumeData
        parsed_back = MarkdownConverter.markdown_to_resume(markdown)
        assert parsed_back.contact_info.name == "John Doe"
        assert parsed_back.contact_info.email == "john.doe@email.com"
        assert "Python" in parsed_back.skills

    def test_markdown_section_editing(self, sample_resume: ResumeData):
        """Test editing individual sections via markdown."""
        # Get skills section
        skills_md = MarkdownConverter.get_section_markdown(sample_resume, "skills")
        assert "## Skills" in skills_md
        assert "Python" in skills_md

        # Get experience section
        exp_md = MarkdownConverter.get_section_markdown(sample_resume, "experience")
        assert "## Work Experience" in exp_md
        assert "TechCorp Inc." in exp_md

        print("\n=== Skills Section ===")
        print(skills_md)
        print("\n=== Experience Section ===")
        print(exp_md[:300])

    def test_docx_conversion(self, sample_resume: ResumeData, temp_output_dir: Path):
        """Test ResumeData to DOCX conversion."""
        output_path = temp_output_dir / "test_resume.docx"

        # Convert to DOCX
        docx_bytes = DocxConverter.resume_to_docx(sample_resume, output_path)

        # Verify file was created
        assert output_path.exists()
        assert output_path.stat().st_size > 0
        assert len(docx_bytes) > 0

        print(f"\n=== DOCX Output ===")
        print(f"File: {output_path}")
        print(f"Size: {output_path.stat().st_size} bytes")

    def test_markdown_to_docx(self, sample_resume: ResumeData, temp_output_dir: Path):
        """Test Markdown to DOCX conversion."""
        # First convert to markdown
        markdown = MarkdownConverter.resume_to_markdown(sample_resume)

        # Then convert markdown to DOCX
        output_path = temp_output_dir / "test_from_md.docx"
        docx_bytes = DocxConverter.markdown_to_docx(markdown, output_path)

        assert output_path.exists()
        assert len(docx_bytes) > 0

        print(f"\n=== Markdown → DOCX ===")
        print(f"File: {output_path}")
        print(f"Size: {output_path.stat().st_size} bytes")

    def test_pdf_generation(self, sample_resume: ResumeData, temp_output_dir: Path):
        """Test PDF generation with ReportLab."""
        output_path = temp_output_dir / "test_resume.pdf"

        generator = ATSFriendlyPDFGenerator()
        generator.generate_pdf(
            resume_data=sample_resume,
            optimization_result=OptimizationResult(),
            output_path=output_path,
            applicant_name="John Doe",
            company_name="TechCorp Inc."
        )

        # Verify file was created
        assert output_path.exists()
        assert output_path.stat().st_size > 0

        print(f"\n=== PDF Output ===")
        print(f"File: {output_path}")
        print(f"Size: {output_path.stat().st_size} bytes")

    def test_full_export_pipeline(self, sample_resume: ResumeData, temp_output_dir: Path):
        """Test the complete export pipeline: Resume → MD → DOCX → PDF."""
        print("\n=== Full Export Pipeline ===")

        # Step 1: Convert to Markdown
        markdown = MarkdownConverter.resume_to_markdown(sample_resume)
        md_path = temp_output_dir / "pipeline_resume.md"
        md_path.write_text(markdown, encoding='utf-8')
        print(f"1. Markdown: {md_path} ({md_path.stat().st_size} bytes)")

        # Step 2: Convert to DOCX
        docx_path = temp_output_dir / "pipeline_resume.docx"
        DocxConverter.resume_to_docx(sample_resume, docx_path)
        print(f"2. DOCX: {docx_path} ({docx_path.stat().st_size} bytes)")

        # Step 3: Convert to PDF
        pdf_path = temp_output_dir / "pipeline_resume.pdf"
        generator = ATSFriendlyPDFGenerator()
        generator.generate_pdf(
            resume_data=sample_resume,
            optimization_result=OptimizationResult(),
            output_path=pdf_path,
            applicant_name="John Doe",
            company_name="TechCorp Inc."
        )
        print(f"3. PDF: {pdf_path} ({pdf_path.stat().st_size} bytes)")

        # Verify all files exist
        assert md_path.exists()
        assert docx_path.exists()
        assert pdf_path.exists()


# ============================================================================
# END-TO-END TESTS
# ============================================================================

class TestEndToEnd:
    """End-to-end integration tests covering all stages."""

    @pytest.mark.skipif(
        not (check_ollama_available() or os.getenv("GOOGLE_API_KEY")),
        reason="Requires Ollama or GOOGLE_API_KEY"
    )
    def test_full_workflow(
        self,
        test_pdf_path: Path,
        sample_job_description: str,
        temp_output_dir: Path
    ):
        """Test complete workflow: Parse → Analyze → Optimize → Export."""
        print("\n" + "="*60)
        print("FULL WORKFLOW TEST")
        print("="*60)

        # STAGE 1: Parse Resume
        print("\n--- Stage 1: Resume Parsing ---")
        if check_ollama_available():
            client = OllamaClient(model="llama3.1:8b", timeout=180)
            parser = OllamaResumeParser(ollama_client=client)
            print("Using: Ollama Parser")
        else:
            parser = SpacyResumeParser()
            print("Using: SpaCy Parser")

        resume_data = parser.parse(test_pdf_path)
        print(f"Parsed: {resume_data.contact_info.name or 'Unknown'}")
        print(f"Skills found: {len(resume_data.skills)}")
        print(f"Experience entries: {len(resume_data.experience)}")

        # STAGE 2: Analyze Job
        print("\n--- Stage 2: Job Analysis ---")
        job_analyzer = JobDescriptionAnalyzer()
        job_data = job_analyzer.analyze(sample_job_description, company_name="TechCorp Inc.")
        print(f"Job: {job_data.title or 'Unknown'}")
        print(f"Required skills: {len(job_data.required_skills)}")
        print(f"Keywords: {len(job_data.keywords)}")

        # STAGE 3: ATS Optimization (if API available)
        optimization_result = None
        if os.getenv("GOOGLE_API_KEY"):
            print("\n--- Stage 3: ATS Optimization ---")
            optimizer = ATSOptimizer()
            optimization_result = optimizer.optimize(
                resume_data=resume_data,
                job_data=job_data,
                applicant_name=resume_data.contact_info.name or "Test Applicant",
                company_name="TechCorp Inc."
            )
            print(f"Original Score: {optimization_result.original_score:.1f}")
            print(f"Optimized Score: {optimization_result.optimized_score:.1f}")
            print(f"Improvement: {optimization_result.optimized_score - optimization_result.original_score:+.1f}")

            # Use optimized resume for export
            final_resume = optimization_result.optimized_resume
        else:
            print("\n--- Stage 3: Skipped (no API key) ---")
            final_resume = resume_data
            optimization_result = OptimizationResult()

        # STAGE 4: Export
        print("\n--- Stage 4: Export ---")

        # Markdown
        md_content = MarkdownConverter.resume_to_markdown(final_resume)
        md_path = temp_output_dir / "final_resume.md"
        md_path.write_text(md_content, encoding='utf-8')
        print(f"Markdown: {md_path.name} ({len(md_content)} chars)")

        # DOCX
        docx_path = temp_output_dir / "final_resume.docx"
        DocxConverter.resume_to_docx(final_resume, docx_path)
        print(f"DOCX: {docx_path.name} ({docx_path.stat().st_size} bytes)")

        # PDF
        pdf_path = temp_output_dir / "final_resume.pdf"
        generator = ATSFriendlyPDFGenerator()
        generator.generate_pdf(
            resume_data=final_resume,
            optimization_result=optimization_result,
            output_path=pdf_path,
            applicant_name=final_resume.contact_info.name or "Test Applicant",
            company_name="TechCorp Inc."
        )
        print(f"PDF: {pdf_path.name} ({pdf_path.stat().st_size} bytes)")

        print("\n" + "="*60)
        print("WORKFLOW COMPLETE")
        print(f"Output directory: {temp_output_dir}")
        print("="*60)

        # Verify all outputs
        assert md_path.exists()
        assert docx_path.exists()
        assert pdf_path.exists()


# ============================================================================
# OLLAMA-SPECIFIC TESTS
# ============================================================================

class TestOllamaIntegration:
    """Specific tests for Ollama integration."""

    @pytest.mark.skipif(
        not check_ollama_available(),
        reason="Ollama not running"
    )
    def test_ollama_client_connection(self):
        """Test basic Ollama client connectivity."""
        client = OllamaClient()

        # Check if available
        assert client.is_available()

        # List models
        models = client.list_models()
        print(f"\nAvailable Ollama models: {models}")
        assert len(models) > 0

    @pytest.mark.skipif(
        not check_ollama_available(),
        reason="Ollama not running"
    )
    def test_ollama_simple_invoke(self):
        """Test simple Ollama invocation."""
        client = OllamaClient(model="llama3.1:8b", timeout=60)

        response = client.invoke(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say 'Hello, World!' and nothing else.",
            temperature=0.1
        )

        print(f"\nOllama response: {response}")
        assert len(response) > 0

    @pytest.mark.skipif(
        not check_ollama_available(),
        reason="Ollama not running"
    )
    def test_ollama_json_extraction(self):
        """Test Ollama JSON extraction capability."""
        client = OllamaClient(model="llama3.1:8b", timeout=60)

        result = client.invoke_json(
            system_prompt="Return only valid JSON with name and age fields.",
            user_prompt='Extract info: "John is 30 years old"',
            temperature=0.1
        )

        print(f"\nOllama JSON result: {result}")
        # Should be able to parse some JSON
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
