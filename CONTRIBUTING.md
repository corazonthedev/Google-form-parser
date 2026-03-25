# Contributing

## Setup
1. Create a virtual environment.
2. Install the package in editable mode.
3. Install dev dependencies.
4. Run `pytest --cov=src --cov-report=term-missing` before opening a PR.

Example:
```bash
python -m pip install -e .
python -m pip install -e .[dev]
```

## Branching strategy
- `feature/<name>` for new work
- `fix/<name>` for bug fixes
- `docs/<name>` for documentation only

## Commit format
Use small, descriptive commits. Example:
`feat: add html fixture coverage for grid questions`

## Quality gates
- `pytest --cov=src --cov-report=term-missing`
- `python -m compileall src tests`
- `ruff check src tests`
