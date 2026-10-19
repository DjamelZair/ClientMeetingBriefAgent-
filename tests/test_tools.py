"""tools over a small hand made context. no imports from the data or model modules."""
import numpy as np
import pandas as pd
import pytest

from client_brief_agent import config
from client_brief_agent.agent import branches, tools

PRODUCTS = ["current_account", "online_account", "credit_card", "direct_debit", "term_deposit",
            "investment_fund", "investment_account", "pension_plan", "personal_loan",
            "salary_deposit", "pension_deposit", "payroll_account"]
FLAGS = ["flag_new_products", "flag_dropped_products", "flag_activity_drop", "flag_moved",
         "flag_new_client", "flag_segment_change"]


def _client(age, income, tenure, held, segment="individual", active=1, flags=(), deceased=0,
            adds=0, drops=0, province=28):
    row = {"age": age, "income": income, "income_missing": float(np.isnan(income)),
           "tenure_months": tenure, "active": active, "province": province,
           "adds_3m": adds, "drops_3m": drops, "deceased": deceased}
    for s in ["top", "individual", "student"]:
        row[f"segment_{s}"] = float(s == segment)
    for p in PRODUCTS:
        row[f"held_{p}"] = float(p in held)
    row["n_products"] = len(held)
    for f in FLAGS:
        row[f] = int(f in flags)
    return row


def make_ctx():
    nan = np.nan
    snap = pd.DataFrame.from_dict({
        101: _client(40, 30000.0, 52, ["current_account", "direct_debit"]),
        102: _client(55, 22000.0, 120, ["current_account"], active=0, flags=["flag_activity_drop"]),
        103: _client(16, 8000.0, 30, ["current_account"], segment="student"),
        104: _client(70, 15000.0, 200, ["current_account", "direct_debit"], segment="top"),
        105: _client(81, 12000.0, 300, ["current_account"], deceased=1),
        106: _client(29, nan, 3, ["current_account"], flags=["flag_new_client", "flag_moved", "flag_new_products"],
                     adds=1),
        107: _client(45, 41000.0, 80, ["current_account", "online_account"], flags=["flag_dropped_products"],
                     drops=2),
        108: _client(33, 27000.0, 40, ["current_account", "salary_deposit"], flags=["flag_segment_change"]),
    }, orient="index")
    snap.index.name = "client_id"

    scores = pd.DataFrame(np.nan, index=snap.index, columns=PRODUCTS)
    scores.loc[101, ["credit_card", "investment_fund", "term_deposit", "pension_plan"]] = [0.35, 0.2, 0.05, 0.12]
    scores.loc[102, ["credit_card", "investment_fund", "term_deposit"]] = [0.4, 0.15, 0.2]
    scores.loc[103, ["online_account", "credit_card", "term_deposit"]] = [0.3, 0.25, 0.15]
    scores.loc[104, ["credit_card", "investment_account", "term_deposit"]] = [0.5, 0.3, 0.12]
    scores.loc[105, ["online_account", "term_deposit"]] = [0.6, 0.3]
    scores.loc[106, ["personal_loan", "online_account", "credit_card"]] = [0.22, 0.11, 0.04]
    scores.loc[107, ["credit_card", "term_deposit"]] = [0.03, 0.02]
    scores.loc[108, ["investment_fund", "online_account", "payroll_account", "pension_deposit"]] = [0.3, 0.5, 0.6, 0.2]

    meeting = pd.Timestamp(config.MEETING_DATE)
    syn = pd.DataFrame.from_dict({
        101: ("low", meeting + pd.Timedelta(days=30), True, "balanced", False),
        102: ("medium", meeting + pd.Timedelta(days=400), False, None, False),
        103: ("low", meeting + pd.Timedelta(days=900), False, None, False),
        104: ("high", meeting - pd.Timedelta(days=20), True, "cautious", True),
        105: ("low", meeting + pd.Timedelta(days=500), False, None, False),
        106: ("medium", meeting + pd.Timedelta(days=90), True, "adventurous", False),
        107: ("low", meeting + pd.Timedelta(days=91), True, "balanced", False),
    }, orient="index", columns=["kyc_risk_class", "next_kyc_review", "risk_profile_done",
                                "risk_appetite", "vulnerable"])
    syn["last_kyc_review"] = syn["next_kyc_review"] - pd.Timedelta(days=365)
    syn["risk_profile_date"] = pd.NaT
    syn["synthetic"] = True
    # 108 is left out of the synthetic layer on purpose

    segments = {"k": 3, "labels": pd.Series({101: 0, 102: 0, 103: 2, 104: 1, 105: 1, 106: 2, 107: 1, 108: 2}),
                "names": {0: "Settled everyday savers", 1: "Long standing clients", 2: "Young starters"},
                "descriptions": {0: "middle aged, a few everyday products, mostly active",
                                 1: "older, long tenure, more products than average",
                                 2: "younger, short tenure, few products"},
                "silhouette": {2: 0.31, 3: 0.35}, "inertia": {2: 900.0, 3: 700.0}, "ari_gmm": 0.62}

    def reasons(cid, product):
        row = snap.loc[cid]
        out = [f"aged {int(row['age'])}"]
        if row["held_direct_debit"] > 0.5:
            out.insert(0, "already pays bills by direct debit")
        return out

    return tools.Context(snapshot=snap, segments=segments, scores=scores, reasons=reasons, synthetic=syn,
                         bands=make_bands())


def make_bands():
    """hand made bands table in the shape of calibration_bands.csv. term_deposit has no band 4 row."""
    edges = config.BAND_EDGES
    rows = []
    for p in PRODUCTS:
        for b in range(len(edges) - 1):
            if p == "term_deposit" and b == 4:
                continue
            n = 20 if b == 6 else 200 + 10 * b
            pos = int(n * (edges[b] + edges[b + 1]) / 2)
            rows.append({"product": p, "band": b, "lo": edges[b], "hi": edges[b + 1],
                         "mean_pred": (edges[b] + edges[b + 1]) / 2, "observed": pos / n,
                         "n": n, "positives": pos})
    return pd.DataFrame(rows)


@pytest.fixture
def ctx():
    return make_ctx()


def test_profile(ctx):
    p = tools.get_profile(ctx, 101)
    assert p["age"] == 40 and p["income"] == 30000 and p["n_products"] == 2
    assert p["held"] == ["current_account", "direct_debit"] and p["segment"] == "individual"
    assert tools.get_profile(ctx, 106)["income"] is None


def test_segment(ctx):
    s = tools.get_segment(ctx, 103)
    assert s == {"cluster": 2, "name": "Young starters", "description": "younger, short tenure, few products",
                 "typical_products": None}


def test_recent_changes(ctx):
    assert tools.get_recent_changes(ctx, 101) == {"flags": [], "sentences": []}
    ch = tools.get_recent_changes(ctx, 106)
    assert ch["flags"] == ["flag_new_products", "flag_moved", "flag_new_client"]
    assert "Took up 1 new product in the last three months." in ch["sentences"]
    assert any("3 months ago" in s for s in ch["sentences"])
    assert tools.get_recent_changes(ctx, 107)["sentences"] == ["Closed 2 products in the last three months."]


def test_propensities_sorted_and_skip_held(ctx):
    r = tools.get_propensities(ctx, 101, top_n=None)
    assert [x["product"] for x in r] == ["credit_card", "investment_fund", "pension_plan", "term_deposit"]
    assert all(x["product"] != "current_account" for x in r)
    assert len(tools.get_propensities(ctx, 101, top_n=2)) == 2
    assert r[0]["label"] == "Credit card"


def test_review_due(ctx):
    assert tools.check_review_due(ctx, 101)["due"] is True
    assert tools.check_review_due(ctx, 101)["days_until"] == 30
    assert tools.check_review_due(ctx, 106)["due"] is True  # exactly on the window edge
    assert tools.check_review_due(ctx, 107)["due"] is False  # one day past it
    over = tools.check_review_due(ctx, 104)
    assert over["due"] is True and over["days_until"] == -20 and over["risk_class"] == "high"
    assert tools.check_review_due(ctx, 108) == {"due": False, "status": "unknown", "next_review": None, "days_until": None,
                                                 "risk_class": None, "synthetic": True}
    # a different meeting date moves the answer
    assert tools.check_review_due(ctx, 107, "2016-06-02")["due"] is True


def test_suitability_tool(ctx):
    assert tools.check_suitability(ctx, 101, "credit_card")["allowed"] is True
    r = tools.check_suitability(ctx, 102, "credit_card")
    assert not r["allowed"] and r["rules_fired"][0]["rule"] == "credit_activity_drop"


def test_questions_templates(ctx, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    facts = {"review_due": True, "review_days": 34, "change_flags": ["flag_moved"],
             "changes": {"flag_moved": "Moved to a different province in the last six months."},
             "might_help": ["pension_plan"]}
    q = tools.draft_questions(ctx, facts)
    assert [c["key"] for c in q] == ["review_due", "flag_moved", "topic"]
    assert q[0]["kind"] == "Periodic review" and q[0]["why"] == "Periodic review due in 34 days (synthetic date)."
    assert q[1]["why"] == "Moved to a different province in the last six months."
    assert "retirement" in q[2]["text"]
    assert q == tools.draft_questions(ctx, facts)
    quiet = tools.draft_questions(ctx, {"review_due": False, "change_flags": [], "might_help": []})
    assert [c["text"] for c in quiet] == branches.OPEN_QUESTIONS
    for c in q + quiet:
        assert c["text"].endswith("?") and c["why"] and 2 <= len(c["answers"]) <= 3


def test_questions_fall_back_without_package(ctx, monkeypatch):
    # the key alone is not enough, the package must import too, and it is not installed here
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setattr(tools, "_claude_available", lambda: False)
    facts = {"review_due": False, "change_flags": [], "might_help": ["credit_card"]}
    assert tools.draft_questions(ctx, facts) == tools.template_questions(facts)


def test_questions_fall_back_on_error(ctx, monkeypatch):
    def boom(*a):
        raise RuntimeError("no network")
    monkeypatch.setattr(tools, "_claude_rephrase", boom)
    facts = {"review_due": True, "change_flags": [], "might_help": []}
    assert tools.draft_questions(ctx, facts, use_claude=True) == tools.template_questions(facts)


def test_claude_only_changes_wording(ctx, monkeypatch):
    monkeypatch.setattr(tools, "_claude_rephrase", lambda facts, drafts: [d.upper() for d in drafts])
    facts = {"review_due": True, "change_flags": [], "might_help": ["credit_card"]}
    plain, smooth = tools.template_questions(facts), tools.draft_questions(ctx, facts, use_claude=True)
    assert [c["text"].upper() for c in plain] == [c["text"] for c in smooth]
    assert [c["answers"] for c in plain] == [c["answers"] for c in smooth]


def test_claude_needs_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert tools._claude_available() is False


def test_template_text_is_clean():
    texts = (list(branches.CHANGE_QUESTIONS.values()) + list(branches.TOPIC_QUESTIONS.values()) + branches.OPEN_QUESTIONS
             + list(tools.CHANGE_SENTENCES.values()) + list(branches.NOT_HELD.values())
             + [a for v in branches.ANSWERS.values() for a, _ in v]
             + [t for v in branches.ANSWERS.values() for _, effects in v for _, t in effects])
    for t in texts:
        assert not tools.has_dash(t)
        assert "sell" not in t.lower() and "target" not in t.lower()


def test_raw_values_are_shown_not_imputed():
    c = make_ctx()
    c.snapshot["age_raw"] = c.snapshot["age"]
    c.snapshot["income_raw"] = c.snapshot["income"]
    c.snapshot["tenure_raw"] = c.snapshot["tenure_months"]
    c.snapshot.loc[101, ["age_raw", "tenure_raw"]] = np.nan
    c.snapshot["sex_male"] = 1.0
    c.snapshot["foreign_birth"] = 1
    p = tools.get_profile(c, 101)
    assert p["age"] is None and p["tenure_months"] is None and p["income"] == 30000
    assert not any(k.startswith("sex") or "birth" in k for k in p)


def test_review_status(ctx):
    assert tools.check_review_due(ctx, 104)["status"] == "overdue"
    assert tools.check_review_due(ctx, 101)["status"] == "due_soon"
    assert tools.check_review_due(ctx, 102)["status"] == "not_due"
    assert tools.check_review_due(ctx, 108)["status"] == "unknown"


def test_score_display_caps_at_50():
    assert tools.score_display(0.234) == "23%"
    assert tools.score_display(0.4949) == "49%"
    assert tools.score_display(0.5) == "above 50%" and tools.score_display(0.97) == "above 50%"


def test_score_band_uses_real_rows(ctx):
    b = tools.score_band(ctx, "credit_card", 0.35)
    assert (b["lo"], b["hi"]) == (0.3, 0.5) and b["n"] == 20 and b["enough"] is False
    assert tools.band_sentence(b) == "Too few clients scored in this range in the test month to check the score."
    top = tools.score_band(ctx, "payroll_account", 0.6)
    assert (top["lo"], top["hi"], top["n"]) == (0.5, 1.0, 270) and top["enough"]
    assert tools.band_sentence(top) == ("In the test month, 75% of the 270 clients scoring between "
                                        "50% and 100% took it up.")
    assert tools.score_band(ctx, "payroll_account", 1.0)["hi"] == 1.0
    assert tools.score_band(ctx, "credit_card", 0.10)["lo"] == 0.10
    # a band missing from the table is never filled in
    gap = tools.score_band(ctx, "term_deposit", 0.15)
    assert gap["n"] == 0 and gap["observed"] is None and not gap["enough"]


def test_no_bands_means_not_enough(ctx):
    c = make_ctx()
    c.bands = None
    assert tools.score_band(c, "credit_card", 0.35)["enough"] is False


def test_linked_products(ctx):
    assert tools.check_linked(ctx, 108, "payroll_account")["in_progress"] is True
    assert tools.check_linked(ctx, 108, "online_account")["in_progress"] is False
    assert tools.check_linked(ctx, 101, "payroll_account")["in_progress"] is False


def test_linked_mask_agrees_with_per_client():
    c = make_ctx()
    rng = np.random.default_rng(3)
    for p in config.LINKED_INCOME_PRODUCTS:
        c.snapshot[f"held_{p}"] = (rng.random(len(c.snapshot)) < 0.4).astype(float)
    mask = tools.in_progress_mask(c.snapshot, PRODUCTS)
    for cid in c.snapshot.index:
        for p in PRODUCTS:
            assert mask.loc[cid, p] == tools.check_linked(c, cid, p)["in_progress"]


def test_income_is_rounded_and_province_hidden(ctx):
    c = make_ctx()
    c.snapshot.loc[101, "income"] = 78_412.5
    p = tools.get_profile(c, 101)
    assert p["income"] == 78_000 and "province" not in p and "client_id" not in p


def test_in_progress_sentence_names_what_is_held():
    import pandas as pd
    from client_brief_agent.agent.tools import in_progress_sentence
    row = pd.Series({"held_payroll_account": 1, "held_salary_deposit": 0, "held_pension_deposit": 0})
    assert in_progress_sentence(row).startswith("The client already has a payroll account,")
    row = pd.Series({"held_payroll_account": 0, "held_salary_deposit": 1, "held_pension_deposit": 1})
    assert "pension paid in and salary paid in" in in_progress_sentence(row)
