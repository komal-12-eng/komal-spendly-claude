from datetime import date

from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
)

SEED_TOTAL = 8019.00
SEED_PCTS = {
    "Shopping": 38, "Health": 19, "Transport": 15, "Bills": 10,
    "Food": 8, "Other": 6, "Entertainment": 4,
}


# ----------------------------- unit tests ----------------------------- #

def test_get_user_by_id_valid(demo_user_id):
    user = get_user_by_id(demo_user_id)
    assert user["name"] == "Demo User"
    assert user["email"] == "demo@spendly.com"
    assert user["member_since"] == date.today().strftime("%B %Y")


def test_get_user_by_id_missing():
    assert get_user_by_id(999_999) is None


def test_summary_stats_with_expenses(demo_user_id):
    s = get_summary_stats(demo_user_id)
    assert s["total_spent"] == SEED_TOTAL
    assert s["transaction_count"] == 8
    assert s["top_category"] == "Shopping"


def test_summary_stats_no_expenses(empty_user_id):
    assert get_summary_stats(empty_user_id) == {
        "total_spent": 0, "transaction_count": 0, "top_category": "—",
    }


def test_recent_transactions_newest_first(demo_user_id):
    txns = get_recent_transactions(demo_user_id)
    assert len(txns) == 8
    dates = [t["date"] for t in txns]
    assert dates == sorted(dates, reverse=True)
    for t in txns:
        assert set(t) >= {"date", "description", "category", "amount"}


def test_recent_transactions_limit(demo_user_id):
    assert len(get_recent_transactions(demo_user_id, limit=3)) == 3


def test_recent_transactions_no_expenses(empty_user_id):
    assert get_recent_transactions(empty_user_id) == []


def test_category_breakdown_with_expenses(demo_user_id):
    cats = get_category_breakdown(demo_user_id)
    amounts = [c["amount"] for c in cats]
    assert amounts == sorted(amounts, reverse=True)
    assert all(isinstance(c["pct"], int) for c in cats)
    assert sum(c["pct"] for c in cats) == 100
    assert {c["name"]: c["pct"] for c in cats} == SEED_PCTS


def test_category_breakdown_no_expenses(empty_user_id):
    assert get_category_breakdown(empty_user_id) == []


# ----------------------------- route tests ---------------------------- #

def test_profile_requires_login(client):
    resp = client.get("/profile")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_profile_demo_user(client, login, demo_user_id):
    login(demo_user_id, "Demo User")
    resp = client.get("/profile")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Demo User" in html
    assert "demo@spendly.com" in html
    assert "₹" in html
    assert "₹8,019.00" in html
    assert "Shopping" in html
    assert html.count('class="txn-date"') == 8
    for name in SEED_PCTS:
        assert f"cat-bar-{name.lower()}" in html
    # newest-first: the latest seeded date appears before the earliest
    txns = get_recent_transactions(demo_user_id)
    assert html.index(txns[0]["date"]) < html.index(txns[-1]["date"])


def test_profile_empty_user(client, login, empty_user_id):
    login(empty_user_id, "Empty Person")
    resp = client.get("/profile")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Empty Person" in html
    assert "₹0.00" in html
    assert 'class="txn-date"' not in html
    assert "cat-bar-" not in html


def test_profile_stale_session_redirects(client, login):
    login(999_999)
    resp = client.get("/profile")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]
