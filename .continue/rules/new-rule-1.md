---
name: Architecture Rules
globs: ["src/resume_optimizer/**/*"]
alwaysApply: true
description: Enforce layered architecture and module boundaries within the src package.

---

Architecture and Boundaries
Respect layers:

UI: streamlit_ui depends on core and config only.

Core: resume_parser, job_analyzer, ai_integration, ats_optimizer, pdf_generator depend on core.models, utils, config.

Utils: no imports upward; only standard lib and third-party libs.

Config: no imports from core or UI.

No cross-module imports that violate boundaries (e.g., ats_optimizer importing streamlit_ui is forbidden).

Public data flows through dataclasses in core/models.py. Avoid ad-hoc dicts at module boundaries.

Each submodule exposes a factory when multiple strategies exist (e.g., ResumeParserFactory, PDFGeneratorFactory).

Side effects (network calls, file IO) must be isolated and injected; core algorithms accept data objects and return data objects.