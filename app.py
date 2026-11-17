import os
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


def _is_valid_email(email):
    local, sep, domain = email.partition("@")
    if not sep or not local:
        return False
    dot = domain.find(".")
    return 0 < dot < len(domain) - 1


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    error = None
    if not name or not email or not password:
        error = "All fields are required."
    elif not _is_valid_email(email):
        error = "Please enter a valid email address."
    elif len(password) < 8:
        error = "Password must be at least 8 characters."

    if error is None:
        try:
            create_user(name, email, password)
        except sqlite3.IntegrityError:
            error = "An account with that email already exists."

    if error:
        return render_template("register.html", error=error, name=name, email=email)

    flash("Account created — please sign in.", "success")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    error = None
    user = None
    if not email or not password:
        error = "Email and password are required."
    else:
        user = get_user_by_email(email)
        if user is None or not check_password_hash(user["password_hash"], password):
            error = "Invalid email or password."

    if error:
        return render_template("login.html", error=error, email=email)

    session.clear()
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return redirect(url_for("landing"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You've been signed out.", "success")
    return redirect(url_for("login"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.template_filter("inr")
def inr(amount):
    return f"₹{amount:,.2f}"


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        flash("Please sign in to view your profile.", "error")
        return redirect(url_for("login"))

    # Step 4: hardcoded data to validate the UI. Real queries arrive in Step 5.
    user = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "initials": "DU",
        "member_since": "November 2026",
    }

    transactions = [
        {"date": "2026-11-22", "description": "Groceries", "category": "Food", "amount": 220.00},
        {"date": "2026-11-18", "description": "Gift", "category": "Other", "amount": 500.00},
        {"date": "2026-11-14", "description": "Headphones", "category": "Shopping", "amount": 2999.00},
        {"date": "2026-11-11", "description": "Movie tickets", "category": "Entertainment", "amount": 350.00},
        {"date": "2026-11-08", "description": "Pharmacy", "category": "Health", "amount": 1500.00},
        {"date": "2026-11-05", "description": "Electricity bill", "category": "Bills", "amount": 800.00},
        {"date": "2026-11-03", "description": "Monthly metro pass", "category": "Transport", "amount": 1200.00},
        {"date": "2026-11-01", "description": "Lunch with team", "category": "Food", "amount": 450.00},
    ]

    total = sum(t["amount"] for t in transactions)
    totals_by_category = {}
    for t in transactions:
        totals_by_category[t["category"]] = totals_by_category.get(t["category"], 0) + t["amount"]

    categories = [
        {
            "name": name,
            "slug": name.lower(),
            "total": amount,
            "percent": round(amount / total * 100) if total else 0,
        }
        for name, amount in sorted(totals_by_category.items(), key=lambda kv: kv[1], reverse=True)
    ]

    stats = {
        "total": total,
        "count": len(transactions),
        "top_category": categories[0]["name"] if categories else "—",
    }

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
