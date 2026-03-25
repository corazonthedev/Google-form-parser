# Audit Report

## High-risk issues found in the original repository
1. Single 900+ line script with global state and mixed responsibilities.
2. Password collection in UI with no clear separation between config, parsing, and logging.
3. No automated tests, no coverage target, no CI workflow.
4. Fragile parsing logic tied to hard-coded selectors and repeated branches.
5. Windows-only output path assumptions (`FORMS\\`) and inconsistent path handling.
6. Batch parsing loop marked broken in the original README.
7. Difficult to debug because HTML parsing, Selenium control, file writing, and UI all lived in one class.

## What was changed
- Rebuilt the project as a small package under `src/google_form_parser`.
- Added a testable HTML parser core and fixture-based tests.
- Added a workflow layer for reading `page*.html` files and writing JSON outputs.
- Replaced the old UI with a cleaner Tkinter app that still feels close to the original desktop flow.
- Added optional live parsing with lazy SeleniumBase import.
- Added project hygiene files: `pyproject.toml`, `requirements-dev.txt`, `.env.example`, CI workflow, ADR, and CONTRIBUTING guide.

## Validation performed
- `pytest --cov=src --cov-report=term-missing`
- `python -m compileall src tests main.py`
- CLI smoke test for saved HTML parsing

## Remaining known limits
- Google can change Form DOM structure at any time, so live Selenium behavior still needs a machine-level smoke test after dependency install.
- File upload questions can be detected but are not auto-submitted.
- Conditional branching that depends on user answers can still require form-specific live handling.
