#!/usr/bin/env python3
"""
Example script demonstrating the GeminiJobAnalyzer usage.

This script shows how to use the new Gemini-based job analyzer
which maintains API compatibility with the original JobDescriptionAnalyzer.
"""

import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from resume_optimizer.core.job_analyzer import GeminiJobAnalyzer, JobDescriptionAnalyzer


# Sample job description
SAMPLE_JOB_DESCRIPTION = """
Senior Python Developer - Remote

TechCorp Inc. is seeking an experienced Senior Python Developer to join our growing team.

Location: San Francisco, CA (Remote options available)

Job Description:
We are looking for a talented Senior Python Developer to help build and maintain our cloud-based data processing platform. You'll work with a team of engineers to design scalable APIs, optimize database performance, and implement new features.

Required Skills and Qualifications:
- 5+ years of professional Python development experience
- Strong experience with Django or Flask frameworks
- Proficiency in PostgreSQL and SQL optimization
- Experience with REST API design and implementation
- Strong knowledge of Docker and containerization
- Experience with AWS services (EC2, S3, Lambda, RDS)
- Solid understanding of Git and CI/CD pipelines
- Bachelor's degree in Computer Science or related field

Preferred Skills:
- Experience with Kubernetes and orchestration
- Knowledge of React or Vue.js for full-stack development
- Familiarity with GraphQL
- Machine Learning experience with TensorFlow or PyTorch
- Experience with microservices architecture

Responsibilities:
- Design and develop scalable backend services
- Optimize database queries and improve application performance
- Write clean, maintainable, and well-tested code
- Mentor junior developers and conduct code reviews
- Collaborate with product and design teams
- Participate in agile ceremonies and sprint planning

What We Offer:
- Competitive salary ($120k-$160k based on experience)
- Comprehensive health benefits
- 401(k) matching
- Flexible remote work options
- Professional development budget
- Collaborative and inclusive culture
"""


def compare_analyzers():
    """Compare the original and Gemini analyzers side by side."""

    print("=" * 80)
    print("COMPARING JOB DESCRIPTION ANALYZERS")
    print("=" * 80)
    print()

    # Initialize both analyzers
    print("Initializing analyzers...")
    try:
        original_analyzer = JobDescriptionAnalyzer()
        print("✓ Original analyzer initialized (uses spaCy + TF-IDF)")
    except Exception as e:
        print(f"✗ Original analyzer failed to initialize: {e}")
        original_analyzer = None

    try:
        gemini_analyzer = GeminiJobAnalyzer(
            model="gemini-2.5-flash-lite",  # Fast model, most cost-effective
            enable_cache=True
        )
        print("✓ Gemini analyzer initialized (uses Gemini AI)")
    except Exception as e:
        print(f"✗ Gemini analyzer failed to initialize: {e}")
        print("  Make sure GOOGLE_API_KEY environment variable is set")
        gemini_analyzer = None

    print()
    print("-" * 80)
    print()

    # Analyze with original analyzer
    if original_analyzer:
        print("ORIGINAL ANALYZER RESULTS:")
        print("-" * 40)
        try:
            original_result = original_analyzer.analyze(
                SAMPLE_JOB_DESCRIPTION,
                company_name="TechCorp Inc."
            )
            print_job_data(original_result)
        except Exception as e:
            print(f"Error: {e}")
        print()

    # Analyze with Gemini analyzer
    if gemini_analyzer:
        print("GEMINI ANALYZER RESULTS:")
        print("-" * 40)
        try:
            gemini_result = gemini_analyzer.analyze(
                SAMPLE_JOB_DESCRIPTION,
                company_name="TechCorp Inc."
            )
            print_job_data(gemini_result)

            # Show cache stats
            print()
            cache_stats = gemini_analyzer.get_cache_stats()
            print(f"Cache stats: {cache_stats}")

        except Exception as e:
            print(f"Error: {e}")
        print()


def simple_gemini_example():
    """Simple example showing basic usage of GeminiJobAnalyzer."""

    print("=" * 80)
    print("SIMPLE GEMINI ANALYZER EXAMPLE")
    print("=" * 80)
    print()

    # Initialize analyzer
    analyzer = GeminiJobAnalyzer(
        model="gemini-2.5-flash-lite",  # Fast, cost-effective model
        temperature=0.2,                 # Low temperature for consistent results
        enable_cache=True                # Cache responses to save API calls
    )

    # Analyze job description
    print("Analyzing job description with Gemini...")
    result = analyzer.analyze(SAMPLE_JOB_DESCRIPTION)

    print()
    print_job_data(result)

    # The analyzer maintains the same API as JobDescriptionAnalyzer
    # So you can use it as a drop-in replacement in your existing pipeline!
    print()
    print("✓ Analysis complete! You can use this analyzer in your existing pipeline.")


def print_job_data(job_data):
    """Pretty print job description data."""

    print(f"Title: {job_data.title or 'N/A'}")
    print(f"Company: {job_data.company or 'N/A'}")
    print(f"Location: {job_data.location or 'N/A'}")
    print(f"Experience Level: {job_data.experience_level or 'N/A'}")
    print()

    print(f"Description: {job_data.description[:150]}..." if len(job_data.description) > 150 else f"Description: {job_data.description}")
    print()

    print(f"Required Skills ({len(job_data.required_skills)}):")
    for skill in job_data.required_skills[:10]:  # Show first 10
        print(f"  - {skill}")
    if len(job_data.required_skills) > 10:
        print(f"  ... and {len(job_data.required_skills) - 10} more")
    print()

    print(f"Preferred Skills ({len(job_data.preferred_skills)}):")
    for skill in job_data.preferred_skills[:10]:
        print(f"  - {skill}")
    if len(job_data.preferred_skills) > 10:
        print(f"  ... and {len(job_data.preferred_skills) - 10} more")
    print()

    print(f"Education Requirements ({len(job_data.education_requirements)}):")
    for edu in job_data.education_requirements:
        print(f"  - {edu}")
    print()

    print(f"Keywords ({len(job_data.keywords)}):")
    print(f"  {', '.join(job_data.keywords[:15])}")
    if len(job_data.keywords) > 15:
        print(f"  ... and {len(job_data.keywords) - 15} more")


def integration_example():
    """Show how to integrate into existing pipeline."""

    print("=" * 80)
    print("INTEGRATION EXAMPLE")
    print("=" * 80)
    print()

    print("The GeminiJobAnalyzer is a drop-in replacement for JobDescriptionAnalyzer!")
    print()
    print("Example integration code:")
    print("-" * 40)
    print("""
# Original code:
from resume_optimizer.core.job_analyzer import JobDescriptionAnalyzer

analyzer = JobDescriptionAnalyzer()
job_data = analyzer.analyze(job_text, company_name="TechCorp")

# New code (just change the class name!):
from resume_optimizer.core.job_analyzer import GeminiJobAnalyzer

analyzer = GeminiJobAnalyzer()  # ← Only change needed!
job_data = analyzer.analyze(job_text, company_name="TechCorp")

# The rest of your pipeline works exactly the same!
# Both analyzers return the same JobDescriptionData structure.
""")
    print("-" * 40)
    print()
    print("Benefits of using GeminiJobAnalyzer:")
    print("  ✓ More accurate skill extraction using AI")
    print("  ✓ Better understanding of context and nuances")
    print("  ✓ Single API call (vs multiple NLP operations)")
    print("  ✓ Built-in caching to reduce costs")
    print("  ✓ Automatic rate limiting")
    print("  ✓ Same API - works with existing code!")
    print()


def main():
    """Main function to run examples."""

    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("WARNING: GOOGLE_API_KEY environment variable not set.")
        print("The Gemini analyzer examples will not work without an API key.")
        print()
        print("To set your API key:")
        print("  export GOOGLE_API_KEY='your-api-key-here'")
        print()
        return

    # Run examples
    choice = input("Choose example:\n"
                   "1. Simple Gemini example\n"
                   "2. Compare analyzers\n"
                   "3. Integration example\n"
                   "Choice (1-3): ").strip()

    print()

    if choice == "1":
        simple_gemini_example()
    elif choice == "2":
        compare_analyzers()
    elif choice == "3":
        integration_example()
    else:
        print("Invalid choice. Running simple example by default.")
        simple_gemini_example()


if __name__ == "__main__":
    main()
