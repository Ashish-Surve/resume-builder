# Gemini API Setup Guide

## Overview
The Resume Builder app supports AI-powered parsing and analysis using Google's Gemini API. This is optional - the app works perfectly fine with the default Spacy parser and Standard analyzer.

## What Requires Gemini API?

### Stage 1: Resume Parsing
- **Gemini Parser**: AI-powered resume parsing with better understanding of complex formats
- **Spacy Parser**: Fast, offline resume parsing (default)

### Stage 2: Job Analysis
- **Gemini Analyzer**: AI-powered job description analysis with deeper understanding
- **Standard Analyzer**: Keyword-based analysis (default)

## Setup Instructions

### 1. Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/)
2. Click "Get API Key" in the left sidebar
3. Click "Create API Key"
4. Copy your API key

### 2. Configure Your .env File

1. Open the `.env` file in the project root
2. Find the line: `GOOGLE_API_KEY=your_google_api_key_here`
3. Replace `your_google_api_key_here` with your actual API key:
   ```
   GOOGLE_API_KEY=AIzaSyB8Mf9inmgx5avo-A6IFDAjRSpjizjFa3s
   ```
4. Save the file

### 3. Restart the Streamlit App

```bash
uv run streamlit run src/resume_optimizer/streamlit_ui/app.py
```

## Usage

Once configured, you'll see the Gemini options available:

- **Stage 1 Parser Selection**:
  - Select "Gemini Parser (AI-powered)" instead of "Spacy Parser"

- **Stage 2 Analyzer Selection**:
  - Select "Gemini Analyzer (AI-powered)" instead of "Standard Analyzer"

If the API key is not configured:
- Gemini options will be **disabled** in the UI
- An error message will appear if you try to use them
- You can still use Spacy and Standard analyzers without any API key

## Security Notes

⚠️ **Important**:
- Never commit your `.env` file to version control
- Keep your API key private and secure
- The `.env` file is already in `.gitignore`

## Rate Limiting

The Gemini client includes automatic rate limiting to stay within Google's free tier limits:
- **gemini-1.5-flash**: 15 requests per minute (recommended)
- **gemini-2.0-flash**: 10 requests per minute
- **gemini-2.5-flash**: 2 requests per minute (very limited)

The app uses `gemini-2.5-flash-lite` by default, which is the fastest and most cost-effective model.

## Troubleshooting

### "Gemini API key not found in .env file"
- Make sure you've added `GOOGLE_API_KEY=your_key` to your `.env` file
- Verify the key is valid and not a placeholder

### API Call Fails with Authentication Error
- Check that your API key is correct
- Make sure the key hasn't been revoked in Google AI Studio

### Rate Limit Exceeded
- The app includes automatic rate limiting and retry logic
- Wait a minute and try again
- Consider using a lower-frequency model

## Fallback Behavior

The app is designed to work without Gemini:
- Stage 1 defaults to **Spacy Parser** (fast, offline)
- Stage 2 defaults to **Standard Analyzer** (keyword matching)
- Both work perfectly well for resume optimization

Use Gemini when you need:
- Better understanding of complex resume formats
- Deeper job description analysis
- AI-powered insights into skill matches

## Costs

Google's Gemini API offers:
- **Free tier**: Up to 1,500 requests per day
- Generous limits for testing and development
- Paid plans available for higher usage

For typical resume optimization (1-5 resumes per session), the free tier is more than sufficient.
