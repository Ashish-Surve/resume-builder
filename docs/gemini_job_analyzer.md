# Gemini Job Analyzer

A Gemini AI-powered job description analyzer that provides intelligent, context-aware analysis in a single API call while maintaining full API compatibility with the original `JobDescriptionAnalyzer`.

## Overview

The `GeminiJobAnalyzer` uses Google's Gemini AI models to analyze job descriptions with superior accuracy and understanding compared to traditional NLP approaches. It's designed as a drop-in replacement for the existing `JobDescriptionAnalyzer`.

## Features

✅ **Single API Call** - Complete analysis in one Gemini request
✅ **Intelligent Extraction** - AI-powered understanding of context and nuances
✅ **API Compatible** - Same interface as `JobDescriptionAnalyzer`
✅ **Built-in Caching** - Automatic response caching to reduce costs
✅ **Rate Limiting** - Smart rate limiting based on model limits
✅ **Cost Efficient** - Uses free tier with optimized model selection

## Installation

The analyzer is included in the resume-optimizer package. Make sure you have the required dependencies:

```bash
pip install langchain-google-genai pydantic
```

You'll also need a Google API key. Get one from [Google AI Studio](https://makersuite.google.com/app/apikey).

## Quick Start

### Basic Usage

```python
from resume_optimizer.core.job_analyzer import GeminiJobAnalyzer

# Initialize the analyzer
analyzer = GeminiJobAnalyzer()

# Analyze a job description
job_text = """
Senior Python Developer - Remote
...your job description text...
"""

result = analyzer.analyze(job_text, company_name="TechCorp")

# Access structured data
print(f"Title: {result.title}")
print(f"Required Skills: {result.required_skills}")
print(f"Keywords: {result.keywords}")
```

### Drop-in Replacement

Replace your existing analyzer with zero code changes:

```python
# Before:
from resume_optimizer.core.job_analyzer import JobDescriptionAnalyzer
analyzer = JobDescriptionAnalyzer()

# After (just change the class name!):
from resume_optimizer.core.job_analyzer import GeminiJobAnalyzer
analyzer = GeminiJobAnalyzer()

# Everything else works the same!
job_data = analyzer.analyze(job_text, company_name="Company")
```

## Configuration

### API Key Setup

Set your Google API key as an environment variable:

```bash
export GOOGLE_API_KEY='your-api-key-here'
```

Or pass it directly:

```python
analyzer = GeminiJobAnalyzer(api_key="your-api-key-here")
```

### Model Selection

Choose the best model for your needs:

```python
# Fastest with best rate limits (recommended, 15 RPM)
analyzer = GeminiJobAnalyzer(model="gemini-1.5-flash")

# Better reasoning (10 RPM)
analyzer = GeminiJobAnalyzer(model="gemini-2.0-flash")

# More powerful but limited (2 RPM, not recommended for high volume)
analyzer = GeminiJobAnalyzer(model="gemini-2.5-flash")
```

### Advanced Configuration

```python
analyzer = GeminiJobAnalyzer(
    api_key="your-api-key",           # API key (optional, uses env var)
    model="gemini-1.5-flash",         # Model name
    temperature=0.2,                   # Lower = more deterministic
    enable_cache=True,                 # Enable caching (recommended)
    cache_ttl_hours=24                 # Cache expiration time
)
```

## API Reference

### `GeminiJobAnalyzer`

#### `__init__(api_key=None, model="gemini-1.5-flash", temperature=0.2, enable_cache=True)`

Initialize the analyzer.

**Parameters:**
- `api_key` (str, optional): Google API key. Defaults to `GOOGLE_API_KEY` env var.
- `model` (str): Gemini model name. Default: `"gemini-1.5-flash"`.
- `temperature` (float): Generation temperature (0.0-1.0). Default: `0.2`.
- `enable_cache` (bool): Enable response caching. Default: `True`.

#### `analyze(job_text: str, company_name: Optional[str] = None) -> JobDescriptionData`

Analyze a job description and extract structured information.

**Parameters:**
- `job_text` (str): Raw job description text.
- `company_name` (str, optional): Company name if not in job text.

**Returns:**
- `JobDescriptionData`: Structured job information with the following fields:
  - `title`: Job title
  - `company`: Company name
  - `location`: Job location
  - `description`: Clean job description summary
  - `required_skills`: List of required skills
  - `preferred_skills`: List of preferred/nice-to-have skills
  - `experience_level`: Required experience level
  - `education_requirements`: Education requirements
  - `keywords`: ATS keywords (15-20 items)
  - `raw_text`: Original job posting text

**Raises:**
- `ParsingError`: If analysis fails

#### `clear_cache()`

Clear the cached responses.

#### `get_cache_stats() -> dict`

Get cache statistics including hits, misses, and size.

## Examples

### Example 1: Basic Analysis

```python
from resume_optimizer.core.job_analyzer import GeminiJobAnalyzer

analyzer = GeminiJobAnalyzer()

job_description = """
Senior Data Scientist
Google - Mountain View, CA

We're looking for a Senior Data Scientist with 5+ years of experience
in machine learning and statistical analysis...
"""

result = analyzer.analyze(job_description)

print(f"Job Title: {result.title}")
print(f"Location: {result.location}")
print(f"Required Skills: {', '.join(result.required_skills)}")
```

### Example 2: Integrating into Existing Pipeline

```python
from resume_optimizer.core.job_analyzer import GeminiJobAnalyzer
from resume_optimizer.core.ats_optimizer import ATSOptimizer

# Step 1: Analyze job description
job_analyzer = GeminiJobAnalyzer()
job_data = job_analyzer.analyze(job_posting_text)

# Step 2: Use in your existing pipeline
ats_optimizer = ATSOptimizer()
optimized_resume = ats_optimizer.optimize(
    resume_data=resume,
    job_data=job_data  # Same JobDescriptionData structure!
)
```

### Example 3: Comparing Analyzers

```python
from resume_optimizer.core.job_analyzer import (
    JobDescriptionAnalyzer,
    GeminiJobAnalyzer
)

# Original analyzer (spaCy + TF-IDF)
original = JobDescriptionAnalyzer()
result1 = original.analyze(job_text)

# Gemini analyzer (AI-powered)
gemini = GeminiJobAnalyzer()
result2 = gemini.analyze(job_text)

# Compare results
print("Original extracted skills:", len(result1.required_skills))
print("Gemini extracted skills:", len(result2.required_skills))
```

### Example 4: Using Cache

```python
analyzer = GeminiJobAnalyzer(enable_cache=True)

# First call - hits the API
result1 = analyzer.analyze(job_text)

# Second call with same text - uses cache (instant!)
result2 = analyzer.analyze(job_text)

# Check cache stats
stats = analyzer.get_cache_stats()
print(f"Cache hits: {stats['hits']}")
print(f"Cache misses: {stats['misses']}")

# Clear cache if needed
analyzer.clear_cache()
```

## Comparison: Original vs Gemini Analyzer

| Feature | JobDescriptionAnalyzer | GeminiJobAnalyzer |
|---------|------------------------|-------------------|
| **Method** | spaCy + TF-IDF | Gemini AI |
| **API Calls** | N/A (local processing) | 1 per analysis |
| **Accuracy** | Good for common patterns | Excellent with context understanding |
| **Speed** | Very fast (local) | Fast (~1-2 seconds per call) |
| **Setup** | Requires spaCy model download | Requires API key |
| **Cost** | Free (local) | Free tier (1500 requests/day) |
| **Skills Extraction** | Keyword matching | Context-aware AI extraction |
| **Understanding** | Pattern-based | Semantic understanding |
| **Maintenance** | Requires skill keyword updates | Always up-to-date with AI |

## Best Practices

### 1. Enable Caching

Always enable caching to avoid redundant API calls:

```python
analyzer = GeminiJobAnalyzer(enable_cache=True)
```

### 2. Use Appropriate Model

For most use cases, use `gemini-1.5-flash` for the best balance:

```python
analyzer = GeminiJobAnalyzer(model="gemini-1.5-flash")  # 15 RPM
```

### 3. Handle Rate Limits

The analyzer automatically handles rate limiting, but be aware of model limits:

- `gemini-1.5-flash`: 15 requests/minute (recommended)
- `gemini-2.0-flash`: 10 requests/minute
- `gemini-2.5-flash`: 2 requests/minute (very limited)

### 4. Error Handling

Always wrap analyzer calls in try-except:

```python
from resume_optimizer.utils.exceptions import ParsingError

try:
    result = analyzer.analyze(job_text)
except ParsingError as e:
    print(f"Analysis failed: {e}")
    # Fall back to original analyzer or handle error
```

### 5. Batch Processing

For multiple job descriptions, the rate limiter handles timing automatically:

```python
analyzer = GeminiJobAnalyzer(model="gemini-1.5-flash")  # 15 RPM

for job_text in job_descriptions:
    # Automatically rate-limited
    result = analyzer.analyze(job_text)
    process_result(result)
```

## Troubleshooting

### "API key not found" Error

Make sure your Google API key is set:

```bash
export GOOGLE_API_KEY='your-api-key-here'
```

Or pass it directly:

```python
analyzer = GeminiJobAnalyzer(api_key="your-key")
```

### Rate Limit Errors

If you hit rate limits, the analyzer will automatically wait. To reduce rate:

```python
# Use a slower model with lower limits
analyzer = GeminiJobAnalyzer(model="gemini-2.5-flash")  # 2 RPM
```

### JSON Parsing Errors

If Gemini returns invalid JSON, check your input and try again. The analyzer includes error handling and logging.

### Cache Not Working

Ensure caching is enabled:

```python
analyzer = GeminiJobAnalyzer(enable_cache=True)
stats = analyzer.get_cache_stats()
print(stats)  # Should show cache_enabled: True
```

## Migration Guide

### From JobDescriptionAnalyzer to GeminiJobAnalyzer

**Step 1:** Update imports

```python
# Before
from resume_optimizer.core.job_analyzer import JobDescriptionAnalyzer

# After
from resume_optimizer.core.job_analyzer import GeminiJobAnalyzer
```

**Step 2:** Update initialization

```python
# Before
analyzer = JobDescriptionAnalyzer()

# After
analyzer = GeminiJobAnalyzer()  # Uses env var GOOGLE_API_KEY
```

**Step 3:** That's it! The API is identical:

```python
# Same method signature
result = analyzer.analyze(job_text, company_name="Company")

# Same return type (JobDescriptionData)
print(result.title)
print(result.required_skills)
```

## Performance Tips

1. **Enable caching** for repeated analyses of the same job descriptions
2. **Use `gemini-1.5-flash`** for best rate limits and speed
3. **Set appropriate temperature** (0.2 for consistent results)
4. **Monitor cache stats** to optimize API usage
5. **Batch process** job descriptions to maximize throughput

## License

Part of the Resume Optimizer project. See main project license.

## Support

For issues, questions, or contributions, please refer to the main project repository.
