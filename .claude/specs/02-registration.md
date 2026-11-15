# Spec: Registration

## Overview
Make the existing `/register` page functional so a visitor can create a Spendly
account. The form in `templates/register.html` already POSTs name, email and
password to `/register` and renders an `{{ error }}` variable, but the route only
accepts GET. This step adds the POST handler: it validates the input, hashes the
password, inserts a row into `users`, and redirects to the sign-in page with a
success message. It comes right after the database layer (Step 1) and before
login/logout (Step 3), because users have to exist before they can sign in.
Logging the user in automatically after registration is **out of scope**. That
needs sessions, which belong to Step 3.

## Depends on
- Step 1: Database setup (`get_db()`, `init_db()`, and the `users` table with its `UNIQUE` email constraint)

## Routes
- `GET /register` renders the registration form (already exists, unchanged behaviour). Public.
- `POST /register` validates the form, creates the user, then redirects to `/login` with a success flash. If validation fails, it re-renders `register.html` with `error`. Public.

Change `@app.route("/register")` to `@app.route("/register", methods=["GET", "POST"])`.
Keep the function name `register`, because templates reference `url_for('register')`.

## Database changes
No database changes. The `users` table in `database/db.py` already has
`name`, `email` (`NOT NULL UNIQUE`), `password_hash` and `created_at`.

Add one helper to `database/db.py`:
- `create_user(name, email, password)` hashes the password with
  `generate_password_hash`, inserts the user with a parameterised query, commits,
  and returns the new user id. It lets `sqlite3.IntegrityError` propagate when the
  email already exists, and always closes the connection.

## Templates
- **Create:** none
- **Modify:**
  - `templates/register.html`: repopulate the `name` and `email` inputs from the submitted values (`value="{{ name or '' }}"` / `value="{{ email or '' }}"`) after a failed submission. Never repopulate the password. Add `minlength="8"` to the password input.
  - `templates/login.html`: show flashed messages (`get_flashed_messages(with_categories=true)`) above the form inside `.auth-card`, so the "Account created" message appears after the redirect.

## Files to change
- `app.py`: set `app.secret_key` (needed for `flash`), import `request`, `redirect`, `url_for`, `flash`, and `create_user`, and add POST handling to `register()`
- `database/db.py`: add `create_user()`
- `templates/register.html`: sticky name/email values and `minlength`
- `templates/login.html`: render flash messages
- `static/css/style.css`: add an `.auth-success` style next to `.auth-error`, using `--accent` / `--accent-light`

## Files to create
- `.claude/specs/02-registration.md` (this file)

## New dependencies
No new dependencies. Flask's `flash` and `werkzeug.security` are already available.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only, never string formatting in SQL
- Hash passwords with werkzeug (`generate_password_hash`), and never store or log plaintext
- Use CSS variables, and never hardcode hex values
- All templates extend `base.html`
- Keep all styling in `static/css/style.css`; don't create per-page CSS files
- Validate on the server, not only with HTML attributes:
  - Strip whitespace from `name` and `email`; lowercase `email`
  - All three fields are required
  - Email must contain `@` and a `.` after it (simple check, no regex library)
  - Password must be at least 8 characters
- Detect a duplicate email by catching `sqlite3.IntegrityError` from `create_user()`, not by a SELECT-then-INSERT, and show "An account with that email already exists."
- On validation failure, return the re-rendered form (HTTP 200) with `error`, `name` and `email`
- On success, use the redirect/flash pattern (`redirect(url_for('login'))`), and don't render the template directly
- `app.secret_key` reads from the `SECRET_KEY` environment variable and falls back to a dev-only default string
- No changes to the navbar in `base.html` (it stays logged-out until Step 3)

## Definition of done
- [ ] `GET /register` still shows the form
- [ ] Submitting a valid new name/email/password redirects to `/login` and shows a green "Account created" message
- [ ] The new row exists in `users` with a `password_hash` starting with `scrypt:` or `pbkdf2:` (not the plaintext password)
- [ ] Email is stored lowercase and trimmed (registering ` Test@Example.com ` stores `test@example.com`)
- [ ] Registering with `demo@spendly.com` shows "An account with that email already exists." and creates no row
- [ ] Submitting a password shorter than 8 characters shows an error and creates no row
- [ ] Submitting a blank name (only spaces) shows an error and creates no row
- [ ] Submitting an invalid email such as `abc` (with browser validation bypassed) shows an error
- [ ] After an error, name and email stay filled in and the password field is empty
- [ ] Refreshing `/login` after the success redirect doesn't show the flash message again
- [ ] App starts without errors with `venv/Scripts/python.exe app.py`
