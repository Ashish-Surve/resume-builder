---
name: Config & Secrets
globs: ["src/resume_optimizer/config//*", "/*.env", "**/.env.example"]
alwaysApply: true
description: Configuration and secrets handling guidelines.
---



Configuration & Secrets
Read secrets only from environment variables or .env via python-dotenv; never hardcode API keys.

Support both PPLX_API_KEY (Perplexity) and GOOGLE_API_KEY (Gemini).

Provide .env.example updates when adding new settings; include safe defaults.

Validate config on app start and fail fast with clear error messages.

Do not log secrets; redact values in logs and errors.