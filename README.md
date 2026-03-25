<div align="center">

# Google Form Parser

**A cleaner, testable Google Form → JSON parser with a desktop UI, CLI, and optional live browser mode.**

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Tests](https://img.shields.io/badge/tests-7%20passed-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-90.77%25-brightgreen)
![License](https://img.shields.io/badge/license-MIT-black)

</div>

## Overview

This project parses Google Forms into structured JSON.

It keeps the original desktop-oriented workflow, but rebuilds the internals around a proper parser core, a cleaner architecture, and a developer workflow that is easier to test, maintain, and extend.

Instead of relying on a single large script, the project now separates:

- **HTML parsing**
- **workflow / export logic**
- **desktop UI**
- **CLI entry points**
- **optional live browser automation**

The result is a repo that is much easier to run, debug, review, and ship.

---

## Why this version is better

### Better engineering
- modular `src/` layout instead of a 900+ line monolith
- parser core covered by tests
- explicit packaging with `pyproject.toml`
- optional dependencies for live browser mode
- cleaner import paths and CLI entry points

### Better UX
- desktop app stays close to the original flow
- separate tabs for **Live URL** and **Saved HTML**
- output directory selection
- clearer status feedback
- safer handling of optional sign-in inputs

### Better delivery
- JSON export is more structured and easier to consume
- repo includes test, lint, and contribution setup
- architecture and audit notes are documented in `docs/`

---

## Core features

- Parse saved Google Form HTML files into structured JSON
- Parse live forms through an optional SeleniumBase adapter
- Preserve page and section boundaries
- Extract:
  - form title
  - source URL when available
  - page titles and descriptions
  - question text
  - question type
  - required state
  - answer options
  - rows / columns for matrix-style questions
  - validation hints when present
- Export output into a predictable folder structure
- Run from either:
  - **desktop UI**
  - **CLI**

---

## Project structure

```text
Google-form-parser-main/
├── src/google_form_parser/
│   ├── __init__.py
│   ├── __main__.py
│   ├── app.py           # Tkinter desktop app
│   ├── cli.py           # CLI entry point
│   ├── html_parser.py   # HTML -> structured form model
│   ├── live_runner.py   # optional SeleniumBase live mode
│   ├── models.py        # dataclasses / domain models
│   ├── rich_text.py     # rich text extraction helpers
│   └── workflow.py      # export and file-system workflow
├── tests/
├── docs/
├── main.py              # desktop launcher
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Installation

### 1) Create a virtual environment

```bash
python -m venv .venv
```

**Windows**
```bash
.venv\Scripts\activate
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

### 2) Install the package

Base install:

```bash
python -m pip install -e .
```

Developer install:

```bash
python -m pip install -e .[dev]
```

Live browser mode:

```bash
python -m pip install -e .[live]
```

Everything together:

```bash
python -m pip install -e .[dev,live]
```

---

## Usage

### Desktop app

Launch the desktop interface:

```bash
python main.py
```

The UI supports two parsing modes:

### Live URL mode
Use this when you want to open a real Google Form URL and parse it through browser automation.

Typical flow:
1. open the **Live URL** tab
2. paste the Google Form link
3. optionally enter sign-in details if the form requires authentication
4. choose an output directory
5. start parsing

### Saved HTML mode
Use this when you already saved the form pages as HTML files.

Typical flow:
1. open the **Saved HTML** tab
2. select the folder containing `page*.html`
3. choose an output directory
4. start parsing

---

### CLI usage

After editable install or package install:

```bash
google-form-parser --html-folder ./sample_form --output-dir ./FORMS
```

Alternative module form:

```bash
python -m google_form_parser --html-folder ./sample_form --output-dir ./FORMS
```

Expected input:
- a folder containing saved Google Form HTML pages
- page files named like `page1.html`, `page2.html`, etc.

Expected output:

```text
FORMS/<slugified-form-title>/parsed_form.json
```

---

## Output shape

The exported JSON contains structured data for downstream tooling.

Typical top-level fields include:

```json
{
  "title": "Example Form",
  "source_url": "https://...",
  "pages": [
    {
      "title": "Section 1",
      "description": "Intro text",
      "questions": [
        {
          "type": "multiple_choice",
          "title": "Your role?",
          "required": true,
          "options": ["Designer", "Developer", "PM"]
        }
      ]
    }
  ]
}
```

The exact shape depends on what exists in the form DOM.

---

## Development

### Run tests

```bash
pytest --cov=src --cov-report=term-missing
```

Current local result for this repo state:
- **7 tests passed**
- **90.77% total coverage**

### Run lint

```bash
python -m ruff check src tests
```

### Verify compilation

```bash
python -m compileall src tests main.py
```

---

## Notes on live parsing

Live parsing is intentionally isolated as an optional adapter.

That matters because Google Forms can change DOM structure without warning.

Important notes:
- live mode depends on **SeleniumBase**
- private forms may require Google authentication
- browser behavior should be smoke-tested on the target machine
- passwords are **not** written to disk by this app

If your primary goal is reliability, **Saved HTML mode** is the safer and more deterministic path.

---

## Documentation

Additional project notes are included here:

- `docs/ADR.md` — architecture decisions
- `docs/AUDIT_REPORT.md` — audit and refactor notes
- `CONTRIBUTING.md` — local workflow and contribution guide

---

## Contributing

If you want to improve the parser:

1. create a branch
2. add or update tests first when changing parser behavior
3. keep UI changes aligned with the existing desktop flow
4. prefer parser-core changes over brittle UI-specific hacks
5. run tests and lint before pushing

---

## Limitations

- Google may change form markup at any time
- live browser mode is more fragile than saved HTML parsing
- some advanced widgets may require future parser updates
- authenticated/private forms depend on the target machine and browser environment

---

## Disclaimer

This project is an independent parser utility and is **not affiliated with or endorsed by Google**.

