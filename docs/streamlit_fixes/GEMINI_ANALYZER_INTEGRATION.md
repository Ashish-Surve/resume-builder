# Gemini Job Analyzer - Integration Guide

## Overview

The new `GeminiJobAnalyzer` is a drop-in replacement for the existing `JobDescriptionAnalyzer` that uses Google's Gemini AI for superior job description analysis.

## Key Benefits

✅ **Same API** - Works with your existing pipeline without modifications
✅ **Single API Call** - Complete analysis in one request (vs multiple NLP operations)
✅ **Better Accuracy** - AI-powered context understanding
✅ **Built-in Caching** - Automatic caching to reduce API costs
✅ **Smart Rate Limiting** - Automatically handles API rate limits

## Quick Start

### 1. Set up API Key

```bash
export GOOGLE_API_KEY='your-google-api-key'
```

Get your API key from: https://makersuite.google.com/app/apikey

### 2. Use in Your Pipeline

Simply replace the analyzer class name:

```python
# Before:
from resume_optimizer.core.job_analyzer import JobDescriptionAnalyzer
analyzer = JobDescriptionAnalyzer()

# After:
from resume_optimizer.core.job_analyzer import GeminiJobAnalyzer
analyzer = GeminiJobAnalyzer()

# Everything else stays the same!
job_data = analyzer.analyze(job_description_text, company_name="Company")
```

## Usage Examples

### Example 1: Basic Usage

```python
from resume_optimizer.core.job_analyzer import GeminiJobAnalyzer

# Initialize with default settings (recommended)
analyzer = GeminiJobAnalyzer()

# Analyze a job description
job_data = analyzer.analyze(job_posting_text)

# Access extracted information
print(f"Title: {job_data.title}")
print(f"Required Skills: {job_data.required_skills}")
print(f"Keywords: {job_data.keywords}")
```

### Example 2: Full Pipeline Integration

```python
from resume_optimizer.core.job_analyzer import GeminiJobAnalyzer
from resume_optimizer.core.resume_parser import ResumeParser
from resume_optimizer.core.ats_optimizer import ATSOptimizer

# Step 1: Analyze job description with Gemini
job_analyzer = GeminiJobAnalyzer()
job_data = job_analyzer.analyze(job_posting_text)

# Step 2: Parse resume (existing code)
resume_parser = ResumeParser()
resume_data = resume_parser.parse(resume_file_path)

# Step 3: Optimize resume (existing code)
ats_optimizer = ATSOptimizer()
result = ats_optimizer.optimize(
    resume_data=resume_data,
    job_data=job_data  # JobDescriptionData from Gemini!
)
```

### Example 3: Advanced Configuration

```python
from resume_optimizer.core.job_analyzer import GeminiJobAnalyzer

# Configure for your needs
analyzer = GeminiJobAnalyzer(
    model="gemini-1.5-flash",  # Fastest, best rate limits (15 RPM)
    temperature=0.2,            # Low = consistent results
    enable_cache=True           # Cache responses (recommended)
)

# Analyze multiple job descriptions
for job_text in job_descriptions:
    job_data = analyzer.analyze(job_text)
    # Rate limiting is handled automatically!
    process_job(job_data)

# Check cache stats
stats = analyzer.get_cache_stats()
print(f"Cache hits: {stats['hits']}, misses: {stats['misses']}")
```

## Configuration Options

### Model Selection

| Model | Rate Limit | Best For |
|-------|------------|----------|
| `gemini-1.5-flash` | 15 RPM | **Recommended** - Fast, high throughput |
| `gemini-2.0-flash` | 10 RPM | Better reasoning, moderate speed |
| `gemini-2.5-flash` | 2 RPM | Most powerful, very limited |

```python
# Recommended for most use cases
analyzer = GeminiJobAnalyzer(model="gemini-1.5-flash")
```

### Temperature

- **0.0-0.3**: More deterministic, consistent results (recommended)
- **0.4-0.7**: Balanced creativity and consistency
- **0.8-1.0**: More creative, less consistent

```python
# For consistent, reliable extraction
analyzer = GeminiJobAnalyzer(temperature=0.2)
```

### Caching

Enable caching to avoid redundant API calls:

```python
# Enable caching (recommended)
analyzer = GeminiJobAnalyzer(enable_cache=True)

# First call - hits API
result1 = analyzer.analyze(job_text)

# Second call with same text - instant from cache!
result2 = analyzer.analyze(job_text)
```

## Migration Checklist

- [ ] Get Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- [ ] Set `GOOGLE_API_KEY` environment variable
- [ ] Update imports: `GeminiJobAnalyzer` instead of `JobDescriptionAnalyzer`
- [ ] Test with a sample job description
- [ ] Monitor API usage and cache stats
- [ ] Update any documentation referencing the analyzer

## Testing

### Run Unit Tests (No API Key Required)

```bash
pytest tests/test_gemini_job_analyzer.py -v
```

### Run Integration Tests (Requires API Key)

```bash
export GOOGLE_API_KEY='your-key'
pytest tests/test_gemini_job_analyzer.py -v -m integration
```

### Try the Example Script

```bash
export GOOGLE_API_KEY='your-key'
python examples/gemini_job_analyzer_example.py
```

## Comparison: Before vs After

### Before (Original Analyzer)

```python
from resume_optimizer.core.job_analyzer import JobDescriptionAnalyzer

analyzer = JobDescriptionAnalyzer()
job_data = analyzer.analyze(job_text)

# Uses:
# - spaCy for NER
# - TF-IDF for keywords
# - Regex patterns for extraction
# - Local processing (no API)
```

### After (Gemini Analyzer)

```python
from resume_optimizer.core.job_analyzer import GeminiJobAnalyzer

analyzer = GeminiJobAnalyzer()
job_data = analyzer.analyze(job_text)

# Uses:
# - Gemini AI for intelligent extraction
# - Single API call
# - Context-aware understanding
# - Built-in caching and rate limiting
```

**Result**: Same `job_data` object, better accuracy!

## API Reference

### JobDescriptionData Fields

Both analyzers return the same `JobDescriptionData` object:

```python
JobDescriptionData(
    title: str,                        # Job title
    company: str,                      # Company name
    location: str,                     # Job location
    description: str,                  # Clean description
    required_skills: List[str],        # Must-have skills
    preferred_skills: List[str],       # Nice-to-have skills
    experience_level: str,             # Required experience
    education_requirements: List[str], # Education requirements
    keywords: List[str],               # ATS keywords (15-20)
    raw_text: str,                     # Original text
    created_at: datetime               # Timestamp
)
```

## Performance & Costs

### API Usage

- **Free Tier**: 1,500 requests per day
- **Rate Limits**:
  - `gemini-1.5-flash`: 15 requests/minute
  - `gemini-2.0-flash`: 10 requests/minute

### Speed

- **First call**: ~1-2 seconds (API call)
- **Cached call**: Instant (< 10ms)
- **Rate limited call**: Auto-waits and retries

### Cost Optimization

1. **Enable caching** - Reuse results for duplicate job descriptions
2. **Use `gemini-1.5-flash`** - Best rate limits and speed
3. **Batch processing** - Analyzer handles rate limiting automatically

## Troubleshooting

### Issue: "API key not found"

**Solution**: Set your API key

```bash
export GOOGLE_API_KEY='your-api-key-here'
```

### Issue: Rate limit errors

**Solution**: The analyzer automatically waits and retries. For very high volumes, consider using a slower model or adding delays between batches.

### Issue: JSON parsing errors

**Solution**: This is rare but can happen. The analyzer includes error logging. Check logs for details. The error is wrapped in `ParsingError`.

### Issue: Cache not working

**Solution**: Verify caching is enabled:

```python
analyzer = GeminiJobAnalyzer(enable_cache=True)
print(analyzer.get_cache_stats())  # Should show cache_enabled: True
```

## Best Practices

1. ✅ **Always enable caching** for production use
2. ✅ **Use `gemini-1.5-flash`** for best performance
3. ✅ **Set temperature to 0.2** for consistent results
4. ✅ **Wrap in try-except** to handle errors gracefully
5. ✅ **Monitor cache stats** to optimize usage
6. ✅ **Keep API key secure** (use environment variables)

## Support

For issues or questions:
- Check the [full documentation](docs/gemini_job_analyzer.md)
- Run the [example script](examples/gemini_job_analyzer_example.py)
- Review the [test cases](tests/test_gemini_job_analyzer.py)

## Next Steps

1. Set up your API key
2. Try the example script
3. Replace your analyzer in one place
4. Test thoroughly
5. Roll out to production
6. Monitor API usage and cache performance

Happy analyzing! 🚀
