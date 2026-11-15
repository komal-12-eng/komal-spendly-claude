# Spec: Login and Logout

## Overview
Let registered users sign in and out of Spendly. Step 2 created accounts and sent
users to `/login` with an "Account created" flash, but the login form currently
POSTs to a GET-only route (405) and `/logout` returns a placeholder string. This step
adds the `POST /login` handler: it looks up the user by email, checks the password
with werkzeug, and stores the user in Flask's signed-cookie `session`. It also makes
`/logout` clear the session, and makes the navbar in `base.html` reflect logged-in
vs logged-out state. Sessions are the foundation for every later step: profile
(Step 4) and all expense routes (Steps 7–9) need to know who the current user is.

## Depends on
- Step 1: Database setup (`get_db()`, the `users` table)
- Step 2: Registration (`create_user()`, `app.secret_key`, flash rendering in `login.html`, `.auth-success` style)

## Routes
- `GET /login` renders the sign-in form. If the user is already logged in, it redirects to `/` instead. Public.
- `POST /login` validates credentials. On success it sets the session and redirects to `/`. On failure it re-renders `login.html` with `error` and the submitted email. Public.
- `GET /logout` clears the session, flashes "You've been signed out.", and redirects to `/login`. Requires login, but works harmlessly when logged out.
- `GET /register` / `POST /register` (existing): if the user is already logged in, redirect to `/` instead.

Change `@app.route("/login")` to `@app.route("/login", methods=["GET", "POST"])`.
Keep the function names `login`, `logout` and `register`, because templates reference them via `url_for`.

## Database changes
No database changes. `users` already has `id`, `name`, `email`, `password_hash`.

Add one helper to `database/db.py`:
- `get_user_by_email(email)` runs `SELECT id, name, email, password_hash FROM users WHERE email = ?` and returns the `sqlite3.Row` or `None`. It always closes the connection.

## Templates
- **Create:** none
- **Modify:**
  - `templates/base.html`: make the navbar conditional on `session.user_id`.
    - Logged in: show the user's name (`session.user_name`) and a "Sign out" link to `url_for('logout')`.
    - Logged out: keep the current "Sign in" / "Get started" links.
  - `templates/login.html`: repopulate the email input with `value="{{ email or '' }}"` after a failed attempt, and never repopulate the password. Flash rendering from Step 2 stays as is.

## Files to change
- `app.py`: import `session` and `check_password_hash`, import `get_user_by_email`, implement `login()` POST and `logout()`, and add the logged-in redirect to `login()` and `register()`
- `database/db.py`: add `get_user_by_email()`
- `templates/base.html`: conditional navbar
- `templates/login.html`: sticky email value
- `static/css/style.css`: add a `.nav-user` style for the name shown in the navbar, using existing CSS variables

## Files to create
- `.claude/specs/03-login-and-logout.md` (this file)

## New dependencies
No new dependencies. Flask's `session` and `werkzeug.security.check_password_hash` are already available.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only, never string formatting in SQL
- Passwords hashed with werkzeug. Verify them with `check_password_hash`, and never compare plaintext or log passwords.
- Use CSS variables, and never hardcode hex values
- All templates extend `base.html`
- Keep all styling in `static/css/style.css`
- Normalise the login email the same way registration does: `.strip().lower()`
- Use one generic error for both an unknown email and a wrong password, "Invalid email or password.", so the form doesn't reveal which emails are registered
- Blank email or password shows "Email and password are required."
- On successful login, call `session.clear()` **before** setting keys, to prevent session fixation. Then set `session["user_id"]` and `session["user_name"]`.
- Store only `user_id` and `user_name` in the session, never the password hash or email
- `logout()` uses `session.clear()` and the redirect/flash pattern
- On failure, return the re-rendered form (HTTP 200). On success, redirect, and never render directly from a POST.
- Don't add a `login_required` decorator yet. Protecting `/profile` and the expense routes belongs to their own steps.

## Definition of done
- [ ] Signing in as `demo@spendly.com` / `demo123` redirects to `/` and the navbar shows "Demo User" and "Sign out"
- [ ] Signing in with ` DEMO@Spendly.com ` (mixed case and spaces) also works
- [ ] A wrong password shows "Invalid email or password.", the email stays filled in, and the password is cleared
- [ ] An unregistered email shows the same "Invalid email or password." message
- [ ] Submitting blank fields (with browser validation bypassed) shows "Email and password are required."
- [ ] A newly registered account (Step 2 flow) can sign in immediately afterwards
- [ ] Clicking "Sign out" redirects to `/login` with a green "You've been signed out." message, and the navbar shows "Sign in" / "Get started" again
- [ ] While logged in, visiting `/login` or `/register` redirects to `/`
- [ ] Visiting `/logout` while logged out redirects to `/login` without an error
- [ ] The session cookie doesn't contain the password hash or email
- [ ] App starts without errors with `venv/Scripts/python.exe app.py`
