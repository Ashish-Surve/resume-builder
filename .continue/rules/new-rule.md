---
name: Project Standards
globs: ["**/*"]
alwaysApply: true
description: Global standards for this repository, applied to all files.
---

Project-wide Standards
Use src-layout packaging with imports rooted at src/resume_optimizer; never use relative path hacks in code or notebooks.

Prefer uv for environment and dependency management; add runtime deps with uv add and dev deps with uv add --group dev.

Follow PEP 8 and type hints; keep functions cohesive and under ~50 lines where practical.

Use dataclasses for immutable models in core/models.py and validate with simple constructors or helper validators.

All modules must expose a stable API via all or data classes; avoid leaking internal helpers.

Keep business logic pure and testable; IO-bound and framework code should call into core classes.

Log via logging, not prints, except in CLI or notebooks explicitly labeled as demos.

Guard all notebook imports with sys.path insertion for ./src when running outside editable installs; prefer uv run jupyter to inherit the project venv.