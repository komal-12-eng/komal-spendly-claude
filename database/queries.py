"""Read-only query helpers for the profile page. No Flask imports."""

from datetime import datetime

from database.db import get_db


def get_user_by_id(user_id):
    """Return {"name", "email", "member_since"} for the user, or None."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    created = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
    return {
        "name": row["name"],
        "email": row["email"],
        "member_since": created.strftime("%B %Y"),
    }


# === SECTION: TRANSACTIONS ===
def get_recent_transactions(user_id, limit=10):
    """Return the user's most recent expenses, newest first, as a list of dicts
    with keys date, description, category, amount (empty list if none)."""
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT date, description, category, amount FROM expenses "
            "WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [
            {
                "date": row["date"],
                "description": row["description"],
                "category": row["category"],
                "amount": row["amount"],
            }
            for row in rows
        ]
    finally:
        conn.close()
# === END SECTION: TRANSACTIONS ===


# === SECTION: SUMMARY STATS ===
def get_summary_stats(user_id):
    """Return total spent, transaction count and top category for a user.

    With no expenses, returns zeros and "—" as the top category.
    """
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total "
            "FROM expenses WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        top = conn.execute(
            "SELECT category FROM expenses WHERE user_id = ? "
            "GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        return {
            "total_spent": row["total"],
            "transaction_count": row["count"],
            "top_category": top["category"] if top else "—",
        }
    finally:
        conn.close()
# === END SECTION: SUMMARY STATS ===


# === SECTION: CATEGORY BREAKDOWN ===
def get_category_breakdown(user_id):
    """Return per-category spending totals for a user, largest first.

    Each item is {"name": str, "amount": float, "pct": int}. Percentages are
    rounded and the remainder is added to the largest category so they sum
    to exactly 100. Returns [] when the user has no expenses.
    """
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT category, SUM(amount) AS total FROM expenses "
            "WHERE user_id = ? GROUP BY category ORDER BY total DESC, category",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()

    grand_total = sum(row["total"] for row in rows)
    if not rows or not grand_total:
        return []

    breakdown = [
        {
            "name": row["category"],
            "amount": row["total"],
            "pct": int(round(row["total"] / grand_total * 100)),
        }
        for row in rows
    ]
    breakdown[0]["pct"] += 100 - sum(item["pct"] for item in breakdown)
    return breakdown
# === END SECTION: CATEGORY BREAKDOWN ===
