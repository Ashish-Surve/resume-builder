"""
Generate a UML-style class diagram (DOT/PNG) for key classes in the project.

This file uses the graphviz python package to generate a visual class diagram.
Install dependencies with: pip install graphviz
Graphviz CLI should be installed on your system (mac: brew install graphviz)

Run:
    python scripts/generate_class_diagram.py

It will produce:
 - diagrams/class_diagram.dot
 - diagrams/class_diagram.png
"""
from graphviz import Digraph
from pathlib import Path
import shutil

OUT_DIR = Path('diagrams')
OUT_DIR.mkdir(parents=True, exist_ok=True)

def add_class_node(dot: Digraph, name: str, attrs: list = None, methods: list = None):
    attrs = attrs or []
    methods = methods or []
    # Build the label parts separately to avoid backslash problems inside f-string expressions
    attrs_join = ('\\l'.join(attrs) + '\\l') if attrs else ''
    methods_join = ('\\l'.join(methods) + '\\l') if methods else ''
    label = '{' + name + '|' + attrs_join + '|' + methods_join + '}'
    dot.node(name, label=label, shape='record')

def main():
    dot = Digraph('UML', filename=str(OUT_DIR / 'class_diagram'), format='png')
    dot.attr(rankdir='LR', fontsize='10')

    # Models
    add_class_node(dot, 'ContactInfo', ['name', 'email', 'phone', 'linkedin', 'github'])
    add_class_node(dot, 'Experience', ['company', 'position', 'duration', 'description'])
    add_class_node(dot, 'Education', ['institution', 'degree', 'field', 'graduation_date'])
    add_class_node(dot, 'ResumeData', ['contact_info:ContactInfo', 'skills', 'experience:List[Experience]', 'education:List[Education]'])
    add_class_node(dot, 'JobDescriptionData', ['title', 'company', 'required_skills', 'keywords'])
    add_class_node(dot, 'OptimizationResult', ['original_score', 'optimized_score', 'optimized_resume:ResumeData'])

    # AI Clients
    add_class_node(dot, 'BaseAIClient', ['api_key', 'max_retries', 'timeout'], ['analyze_resume_job_match()', 'optimize_resume_section()'])
    add_class_node(dot, 'GeminiClient', ['model_name', 'rate_limiter', 'cache_manager'], ['invoke()', 'clear_cache()', 'get_cache_stats()'])
    add_class_node(dot, 'PerplexityClient', ['chat'], ['invoke()', 'analyze_resume_job_match()'])

    # Rate Limiting / Cache
    add_class_node(dot, 'RateLimiter', ['calls_per_minute', 'calls_per_day'], ['acquire()', 'wait_if_needed()'])
    add_class_node(dot, 'CacheManager', ['ttl', 'cache_dir'], ['get()', 'set()', 'clear()'])

    # Resume Parsers
    add_class_node(dot, 'BaseResumeParser', [], ['parse(file_path)'])
    add_class_node(dot, 'SpacyResumeParser', ['nlp','text_extractor','contact_extractor','skills_extractor'], ['parse(file_path)'])
    add_class_node(dot, 'GeminiResumeParser', ['gemini_client','text_extractor'], ['parse(file_path)', 'parse_with_gemini()'])
    add_class_node(dot, 'ResumeParserFactory', [], ['create_parser()'])

    # Extractors
    add_class_node(dot, 'TextExtractor', [], ['extract_from_pdf()', 'extract_from_docx()', 'extract_from_txt()'])
    add_class_node(dot, 'ContactInfoExtractor', [], ['extract(text, nlp_doc)'])
    add_class_node(dot, 'SkillsExtractor', [], ['extract(text, nlp_doc)'])
    add_class_node(dot, 'ExperienceExtractor', [], ['extract_from_section(text)'])
    add_class_node(dot, 'EducationExtractor', [], ['extract_from_section(text)'])
    add_class_node(dot, 'SectionExtractor', [], ['extract_sections(text)'])

    # Job Analyzer and ATS Optimizer
    add_class_node(dot, 'JobDescriptionAnalyzer', ['nlp', 'skill_keywords'], ['analyze(job_text)'])
    add_class_node(dot, 'ATSCompatibilityChecker', [], ['check_compatibility()'])
    add_class_node(dot, 'KeywordOptimizer', [], ['optimize_keywords()'])
    add_class_node(dot, 'ResumeScorer', [], ['score_resume()'])
    add_class_node(dot, 'GeminiResumeOptimizer', ['gemini_client'], ['optimize_summary()', 'optimize_all_experiences_batch()'])
    add_class_node(dot, 'ATSOptimizer', ['compatibility_checker', 'keyword_optimizer','scorer','gemini_optimizer'], ['optimize(resume_data, job_data, applicant_name, company_name)'])

    # PDF Generator
    add_class_node(dot, 'ATSFriendlyPDFGenerator', [], ['generate_pdf(resume_data, optimization_result, output_path, applicant_name, company_name)'])
    add_class_node(dot, 'PDFGeneratorFactory', [], ['create_generator()'])

    # Streamlit App and Config
    add_class_node(dot, 'ResumeOptimizerApp', [], ['run()'])
    add_class_node(dot, 'ConfigManager', ['ai', 'app', 'database'], ['get_ai_config()', 'validate_config()'])

    # Relationships (composition / uses) - We use arrows and labels to indicate relationship
    # Parsers composition
    dot.edge('SpacyResumeParser', 'TextExtractor', label='uses', arrowhead='open')
    dot.edge('SpacyResumeParser', 'ContactInfoExtractor', label='uses', arrowhead='open')
    dot.edge('SpacyResumeParser', 'SkillsExtractor', label='uses', arrowhead='open')
    dot.edge('SpacyResumeParser', 'ExperienceExtractor', label='uses', arrowhead='open')
    dot.edge('SpacyResumeParser', 'EducationExtractor', label='uses', arrowhead='open')
    dot.edge('SpacyResumeParser', 'SectionExtractor', label='uses', arrowhead='open')

    dot.edge('GeminiResumeParser', 'TextExtractor', label='uses', arrowhead='open')
    dot.edge('GeminiResumeParser', 'GeminiClient', label='depends on', style='dashed')

    # AI Clients and utilities
    dot.edge('GeminiClient', 'RateLimiter', label='uses', arrowhead='open')
    dot.edge('GeminiClient', 'CacheManager', label='uses', arrowhead='open')
    dot.edge('PerplexityClient', 'BaseAIClient', label='conceptual interface', style='dashed')
    dot.edge('GeminiClient', 'BaseAIClient', label='conceptual interface', style='dashed')

    # ATS optimizer relationships
    dot.edge('ATSOptimizer', 'ATSCompatibilityChecker', label='contains', arrowhead='open')
    dot.edge('ATSOptimizer', 'KeywordOptimizer', label='contains', arrowhead='open')
    dot.edge('ATSOptimizer', 'ResumeScorer', label='contains', arrowhead='open')
    dot.edge('ATSOptimizer', 'GeminiResumeOptimizer', label='contains', arrowhead='open')
    dot.edge('GeminiResumeOptimizer', 'GeminiClient', label='uses', arrowhead='open')

    # Models usage
    dot.edge('ATSOptimizer', 'ResumeData', label='processes', style='dashed')
    dot.edge('ATSOptimizer', 'JobDescriptionData', label='processes', style='dashed')
    dot.edge('JobDescriptionAnalyzer', 'JobDescriptionData', label='produces', style='dashed')
    dot.edge('ResumeParserFactory', 'BaseResumeParser', label='creates', style='dashed')
    dot.edge('ResumeParserFactory', 'SpacyResumeParser', label='creates', style='dashed')
    dot.edge('ResumeParserFactory', 'GeminiResumeParser', label='creates', style='dashed')

    # PDF generator
    dot.edge('ATSFriendlyPDFGenerator', 'ResumeData', label='reads', style='dashed')
    dot.edge('ATSFriendlyPDFGenerator', 'OptimizationResult', label='reads', style='dashed')
    dot.edge('PDFGeneratorFactory', 'ATSFriendlyPDFGenerator', label='creates', style='dashed')

    # App usage
    dot.edge('ResumeOptimizerApp', 'ResumeParserFactory', label='uses', style='dashed')
    dot.edge('ResumeOptimizerApp', 'ATSOptimizer', label='uses', style='dashed')
    dot.edge('ResumeOptimizerApp', 'PDFGeneratorFactory', label='uses', style='dashed')
    dot.edge('ResumeOptimizerApp', 'JobDescriptionAnalyzer', label='uses', style='dashed')
    dot.edge('ResumeOptimizerApp', 'ConfigManager', label='uses', style='dashed')

    # Output
    # If the Graphviz `dot` CLI isn't available, write the DOT file and warn the user
    dot_path = OUT_DIR / 'class_diagram'
    if not shutil.which('dot'):
        print('Graphviz `dot` executable not found on PATH. Writing DOT file and skipping PNG render.')
        with open(str(dot_path), 'w') as f:
            f.write(dot.source)
        print(f'Wrote DOT file to {dot_path}. To render PNG, install Graphviz CLI and run: dot -Tpng {dot_path} -o {dot_path}.png')
    else:
        print('Rendering class diagram to diagrams/class_diagram.png')
        dot.render(cleanup=True)

if __name__ == '__main__':
    main()
