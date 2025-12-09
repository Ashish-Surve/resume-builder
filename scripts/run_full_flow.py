"""Run full parse -> optimize -> PDF flow with optional Gemini caching disabled.

Usage examples:
  # Run using Spacy-only (no external Gemini):
  python3 scripts/run_full_flow.py --parser spacy --input data/input/resumes/example.pdf

  # Run using Gemini (requires GOOGLE_API_KEY in env/.env), disable cache:
  python3 scripts/run_full_flow.py --parser gemini --no-cache --input data/input/resumes/example.pdf

This script mirrors the cells in `notebook/ai_integration_test/0_ai_integration_test.ipynb`
but in a single runnable .py file and gives explicit control over caching.
"""

import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

from resume_optimizer.core.resume_parser import ResumeParserFactory
from resume_optimizer.core.ai_integration.gemini_client import GeminiClient
from resume_optimizer.core.ats_optimizer.optimizer import ATSOptimizer
from resume_optimizer.core.pdf_generator.generator import PDFGeneratorFactory


def main():
    parser = argparse.ArgumentParser(description="Run parse -> optimize -> generate PDF flow")
    parser.add_argument('--parser', choices=['gemini', 'spacy'], default='gemini', help='Which parser to use')
    parser.add_argument('--no-cache', action='store_true', help='Disable Gemini response cache')
    parser.add_argument('--input', type=str, required=True, help='Input resume file path')
    parser.add_argument('--output', type=str, default='output/pdfs/generated_from_flow.pdf', help='Output PDF path')
    parser.add_argument('--company', type=str, default='TargetCompany', help='Company name used for optimization')
    parser.add_argument('--applicant', type=str, default=None, help='Applicant name to use in PDF header')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return

    # Configure Gemini client
    gemini_api_key = os.getenv('GOOGLE_API_KEY')
    gc = None
    if args.parser == 'gemini':
        # If no API key, warn and fall back to spacy
        if not gemini_api_key:
            print("GOOGLE_API_KEY not found in environment; falling back to spacy parser")
            parser_type = 'spacy'
        else:
            # Create GeminiClient with caching controlled by flag
            gc = GeminiClient(api_key=gemini_api_key, enable_cache=not args.no_cache)
            # If user requested no-cache, clear any existing cache to avoid stale responses
            if args.no_cache and gc.cache_manager:
                gc.clear_cache()
            parser_type = 'gemini'
    else:
        parser_type = 'spacy'

    # Create parser
    resume_parser = ResumeParserFactory.create_parser(parser_type=parser_type, gemini_client=gc)

    # Parse resume
    print(f"Parsing resume: {input_path}")
    resume_data = resume_parser.parse(input_path)
    print("Parsed summary (first 200 chars):", (resume_data.summary or '')[:200])
    print("Parsed skills:", resume_data.skills)

    # Run ATS optimizer (will use Gemini internally if api_key provided)
    print("Running ATS optimization...")
    optimizer = ATSOptimizer(gemini_api_key=gemini_api_key if gc is not None else None)
    result = optimizer.optimize(resume_data=resume_data, job_data=None, applicant_name=(args.applicant or resume_data.contact_info.name or 'Applicant'), company_name=args.company)

    optimized = result.optimized_resume
    print("Optimized summary (first 200 chars):", (optimized.summary or '')[:200])
    print("Optimized skills:", optimized.skills)

    # Ensure output directory exists
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate PDF
    gen = PDFGeneratorFactory().create_generator()
    gen.generate_pdf(optimized, result, out_path, applicant_name=(args.applicant or resume_data.contact_info.name or 'Applicant'), company_name=args.company)
    print(f"PDF written to: {out_path.resolve()}")


if __name__ == '__main__':
    main()
