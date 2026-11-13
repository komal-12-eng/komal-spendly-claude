# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Spendly is a Flask personal expense tracker (amounts in ₹). It is a **step-by-step teaching scaffold**: much of the code is intentionally unimplemented and marked "students will implement" / "coming in Step N". Build features incrementally in step order rather than filling in everything at once.

Step map (from placeholders in the code):
- Step 1: `database/db.py`: `get_db()` (SQLite connection with `row_factory` and foreign keys enabled), `init_db()` (`CREATE TABLE IF NOT EXISTS`), `seed_db()` (sample dev data)
- Step 3: `/logout` · Step 4: `/profile` · Step 7: `/expenses/add` · Step 8: `/expenses/<id>/edit` · Step 9: `/expenses/<id>/delete`
- Steps 2, 5 and 6 aren't named in the code (likely register/login logic and an expense list/dashboard).

## Commands

Windows dev environment, with the virtualenv in `venv/` (Python 3.14). The `!` prefix and the Bash tool run Git Bash, so use forward slashes there.

```bash
python -m venv venv                                  # create venv
venv/Scripts/python.exe -m pip install -r requirements.txt
venv/Scripts/python.exe app.py                       # dev server, debug on, http://127.0.0.1:5001 (not 5000)
venv/Scripts/python.exe -m pytest                    # all tests (pytest + pytest-flask)
venv/Scripts/python.exe -m pytest tests/test_x.py::test_name   # single test
```

There are no tests or linter config yet. pytest-flask expects an `app` fixture in `tests/conftest.py`.

## Architecture

- `app.py` holds the single Flask app and all routes (no blueprints or app factory). `app.run(debug=True, port=5001)`.
- `database/` is the data layer. SQLite file `expense_tracker.db` (gitignored, created by `init_db()`). Routes should import from `database.db`.
- `templates/`: every page extends `base.html` and fills `{% block title %}`, `{% block content %}`, and optionally `{% block head %}` / `{% block scripts %}`. The navbar in `base.html` is hard-coded to the logged-out state (Sign in / Get started), so it needs updating once auth/session exists.
- Links use `url_for('<endpoint>')`, so route function names (`landing`, `register`, `login`, ...) are part of the template contract. Don't rename them without updating templates.
- Auth forms (`register.html`: name/email/password; `login.html`: email/password) `POST` to `/register` and `/login` and render an `{{ error }}` variable. Those routes currently accept only GET, so they need `methods=["GET", "POST"]` when auth is implemented.
- `static/css/style.css` contains all styling (DM Serif Display / DM Sans via Google Fonts). `static/js/main.js` is an empty placeholder.
