# Architecture Decisions

| # | Date | Decision | Alternatives | Reason |
|---|------|----------|--------------|--------|
| 1 | 2026-03-25 | Split parser into HTML core + optional live browser runner | Keep a single 900-line script | Makes parsing testable without launching a browser |
| 2 | 2026-03-25 | Keep Tkinter desktop UI | Rewrite as web app | Stays close to the original UX while improving layout and safety |
| 3 | 2026-03-25 | Make SeleniumBase an optional live dependency | Keep SeleniumBase in the base install | Parsing saved HTML and tests should still work in limited environments |
| 4 | 2026-03-25 | Add package entry points for CLI execution | Rely on repo-local `sys.path` hacks or docs-only fixes | Makes installed usage predictable and fixes broken module invocation from repo root |
