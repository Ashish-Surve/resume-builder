---
name: Python Style & PEP
globs: ["**/*.py"]
alwaysApply: false
description: Style, typing, and structure guidelines for Python files.

---

Python Style
Follow PEP 8 and use black (line length 88) and isort (profile black).

Use typing annotations everywhere; prefer from future import annotations if Python version allows.

Use dataclasses for plain data; Enums for discrete states (e.g., OptimizationStatus).

Prefer pathlib over os.path; prefer Path objects in APIs.

Raise specific exceptions from utils.exceptions; never raise bare Exception.

Write docstrings in Google or NumPy style; include brief example when helpful.

Keep module-level constants UPPER_SNAKE_CASE; no mutable module-level state.