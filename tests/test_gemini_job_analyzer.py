"""
Tests for GeminiJobAnalyzer.

Note: These tests require a valid GOOGLE_API_KEY environment variable.
Some tests are marked as integration tests and may be skipped in CI/CD.
"""

import pytest
from unittest.mock import Mock, patch
import json

from resume_optimizer.core.job_analyzer.gemini_analyzer import GeminiJobAnalyzer
from resume_optimizer.core.models import JobDescriptionData
from resume_optimizer.utils.exceptions import ParsingError


# Sample job description for testing
SAMPLE_JOB_TEXT = """
Senior Software Engineer - Backend
TechCorp Inc.

Location: San Francisco, CA (Remote options available)

We are seeking a Senior Software Engineer with 5+ years of experience in Python
and backend development. Must have experience with Django, PostgreSQL, and AWS.

Required Skills:
- Python, Django, PostgreSQL
- REST API development
- Docker, AWS

Preferred Skills:
- Kubernetes
- GraphQL
- React

Education: Bachelor's degree in Computer Science or related field.
"""


# Sample Gemini API response
SAMPLE_GEMINI_RESPONSE = {
    "title": "Senior Software Engineer - Backend",
    "company": "TechCorp Inc.",
    "location": "San Francisco, CA (Remote options available)",
    "description": "Backend engineering role focused on Python development with Django and AWS.",
    "required_skills": ["Python", "Django", "PostgreSQL", "REST API", "Docker", "AWS"],
    "preferred_skills": ["Kubernetes", "GraphQL", "React"],
    "experience_level": "5+ years",
    "education_requirements": ["Bachelor's degree in Computer Science or related field"],
    "keywords": ["Python", "Django", "PostgreSQL", "AWS", "REST API", "Docker", "backend", "senior"]
}


class TestGeminiJobAnalyzerUnit:
    """Unit tests for GeminiJobAnalyzer (mocked API calls)."""

    def test_initialization(self):
        """Test analyzer initialization."""
        with patch('resume_optimizer.core.job_analyzer.gemini_analyzer.GeminiClient'):
            analyzer = GeminiJobAnalyzer(
                model="gemini-2.5-flash-lite",
                temperature=0.2,
                enable_cache=True
            )
            assert analyzer is not None

    def test_analyze_success(self):
        """Test successful job description analysis."""
        with patch('resume_optimizer.core.job_analyzer.gemini_analyzer.GeminiClient') as mock_client:
            # Mock the Gemini client response
            mock_instance = Mock()
            mock_instance.invoke.return_value = json.dumps(SAMPLE_GEMINI_RESPONSE)
            mock_client.return_value = mock_instance

            analyzer = GeminiJobAnalyzer()
            result = analyzer.analyze(SAMPLE_JOB_TEXT, company_name="TechCorp Inc.")

            # Verify return type
            assert isinstance(result, JobDescriptionData)

            # Verify extracted data
            assert result.title == "Senior Software Engineer - Backend"
            assert result.company == "TechCorp Inc."
            assert result.location == "San Francisco, CA (Remote options available)"
            assert "Python" in result.required_skills
            assert "Kubernetes" in result.preferred_skills
            assert result.experience_level == "5+ years"
            assert len(result.education_requirements) > 0
            assert len(result.keywords) > 0
            assert result.raw_text == SAMPLE_JOB_TEXT

    def test_analyze_with_invalid_json(self):
        """Test handling of invalid JSON response from Gemini."""
        with patch('resume_optimizer.core.job_analyzer.gemini_analyzer.GeminiClient') as mock_client:
            # Mock invalid JSON response
            mock_instance = Mock()
            mock_instance.invoke.return_value = "This is not valid JSON"
            mock_client.return_value = mock_instance

            analyzer = GeminiJobAnalyzer()

            with pytest.raises(ParsingError):
                analyzer.analyze(SAMPLE_JOB_TEXT)

    def test_analyze_with_api_error(self):
        """Test handling of API errors."""
        with patch('resume_optimizer.core.job_analyzer.gemini_analyzer.GeminiClient') as mock_client:
            # Mock API error
            mock_instance = Mock()
            mock_instance.invoke.side_effect = Exception("API Error")
            mock_client.return_value = mock_instance

            analyzer = GeminiJobAnalyzer()

            with pytest.raises(ParsingError):
                analyzer.analyze(SAMPLE_JOB_TEXT)

    def test_convert_to_job_data(self):
        """Test conversion from parsed JSON to JobDescriptionData."""
        with patch('resume_optimizer.core.job_analyzer.gemini_analyzer.GeminiClient'):
            analyzer = GeminiJobAnalyzer()

            job_data = analyzer._convert_to_job_data(
                SAMPLE_GEMINI_RESPONSE,
                SAMPLE_JOB_TEXT
            )

            assert isinstance(job_data, JobDescriptionData)
            assert job_data.title == SAMPLE_GEMINI_RESPONSE["title"]
            assert job_data.company == SAMPLE_GEMINI_RESPONSE["company"]
            assert job_data.required_skills == SAMPLE_GEMINI_RESPONSE["required_skills"]
            assert job_data.raw_text == SAMPLE_JOB_TEXT

    def test_clear_cache(self):
        """Test cache clearing functionality."""
        with patch('resume_optimizer.core.job_analyzer.gemini_analyzer.GeminiClient') as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            analyzer = GeminiJobAnalyzer(enable_cache=True)
            analyzer.clear_cache()

            mock_instance.clear_cache.assert_called_once()

    def test_get_cache_stats(self):
        """Test cache statistics retrieval."""
        with patch('resume_optimizer.core.job_analyzer.gemini_analyzer.GeminiClient') as mock_client:
            mock_instance = Mock()
            mock_instance.get_cache_stats.return_value = {
                "cache_enabled": True,
                "hits": 5,
                "misses": 2
            }
            mock_client.return_value = mock_instance

            analyzer = GeminiJobAnalyzer(enable_cache=True)
            stats = analyzer.get_cache_stats()

            assert stats["cache_enabled"] is True
            assert "hits" in stats
            assert "misses" in stats


@pytest.mark.integration
class TestGeminiJobAnalyzerIntegration:
    """Integration tests for GeminiJobAnalyzer (requires API key)."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for integration tests."""
        import os
        if not os.getenv("GOOGLE_API_KEY"):
            pytest.skip("GOOGLE_API_KEY not set")

        return GeminiJobAnalyzer(
            model="gemini-2.5-flash-lite",
            enable_cache=True
        )

    def test_analyze_real_api(self, analyzer):
        """Test with real Gemini API (requires API key)."""
        result = analyzer.analyze(SAMPLE_JOB_TEXT)

        # Verify we got a valid response
        assert isinstance(result, JobDescriptionData)
        assert result.title is not None
        assert len(result.required_skills) > 0
        assert result.raw_text == SAMPLE_JOB_TEXT

    def test_cache_functionality(self, analyzer):
        """Test that caching works with real API."""
        # First call
        result1 = analyzer.analyze(SAMPLE_JOB_TEXT)

        # Get stats before second call
        stats1 = analyzer.get_cache_stats()

        # Second call (should use cache)
        result2 = analyzer.analyze(SAMPLE_JOB_TEXT)

        # Get stats after second call
        stats2 = analyzer.get_cache_stats()

        # Verify cache was used
        assert result1.title == result2.title
        assert stats2["hits"] > stats1["hits"]


class TestAPICompatibility:
    """Test API compatibility with JobDescriptionAnalyzer."""

    def test_same_method_signature(self):
        """Verify analyze() has the same signature as original analyzer."""
        from inspect import signature
        from resume_optimizer.core.job_analyzer import JobDescriptionAnalyzer

        with patch('resume_optimizer.core.job_analyzer.gemini_analyzer.GeminiClient'):
            gemini_analyzer = GeminiJobAnalyzer()
            original_analyzer = JobDescriptionAnalyzer()

            gemini_sig = signature(gemini_analyzer.analyze)
            original_sig = signature(original_analyzer.analyze)

            # Both should accept job_text and company_name
            assert 'job_text' in gemini_sig.parameters
            assert 'company_name' in gemini_sig.parameters
            assert 'job_text' in original_sig.parameters
            assert 'company_name' in original_sig.parameters

    def test_same_return_type(self):
        """Verify both analyzers return JobDescriptionData."""
        with patch('resume_optimizer.core.job_analyzer.gemini_analyzer.GeminiClient') as mock_client:
            mock_instance = Mock()
            mock_instance.invoke.return_value = json.dumps(SAMPLE_GEMINI_RESPONSE)
            mock_client.return_value = mock_instance

            analyzer = GeminiJobAnalyzer()
            result = analyzer.analyze(SAMPLE_JOB_TEXT)

            assert isinstance(result, JobDescriptionData)

    def test_drop_in_replacement(self):
        """Test that GeminiJobAnalyzer can be used as drop-in replacement."""
        with patch('resume_optimizer.core.job_analyzer.gemini_analyzer.GeminiClient') as mock_client:
            mock_instance = Mock()
            mock_instance.invoke.return_value = json.dumps(SAMPLE_GEMINI_RESPONSE)
            mock_client.return_value = mock_instance

            # This should work exactly like JobDescriptionAnalyzer
            analyzer = GeminiJobAnalyzer()
            result = analyzer.analyze(SAMPLE_JOB_TEXT, company_name="TechCorp")

            # Verify we can access all expected fields
            assert hasattr(result, 'title')
            assert hasattr(result, 'company')
            assert hasattr(result, 'location')
            assert hasattr(result, 'description')
            assert hasattr(result, 'required_skills')
            assert hasattr(result, 'preferred_skills')
            assert hasattr(result, 'experience_level')
            assert hasattr(result, 'education_requirements')
            assert hasattr(result, 'keywords')
            assert hasattr(result, 'raw_text')
