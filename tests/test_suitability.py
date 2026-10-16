"""suitability rules, and the per client check against the vectorised mask."""
import numpy as np
import pandas as pd
import pytest

from client_brief_agent import config
from client_brief_agent.agent import suitability as su
from client_brief_agent.agent.tools import has_dash

ALL_PRODUCTS = list(config.PRODUCT_LABELS)
CLEAN = {"age": 40.0, "income_missing": False, "flag_activity_drop": False, "deceased": False,
         "vulnerable": False, "risk_profile_done": True, "risk_appetite": "balanced", "review_overdue": False}


def fired(facts, product):
    return [r["rule"] for r in su.check(facts, product)["rules_fired"]]


def test_clean_adult_can_get_anything():
    for p in ALL_PRODUCTS:
        assert su.check(CLEAN, p) == {"allowed": True, "rules_fired": []}


@pytest.mark.parametrize("change, product, rule", [
    ({"deceased": True}, "online_account", "deceased"),
    ({"age": 16.0}, "term_deposit", "under_18_basic_only"),
    ({"age": 16.0}, "credit_card", "credit_under_18"),
    ({"flag_activity_drop": True}, "personal_loan", "credit_activity_drop"),
    ({"vulnerable": True}, "mortgage", "credit_vulnerable"),
    ({"income_missing": True}, "credit_card", "credit_income_missing"),
    ({"risk_profile_done": False, "risk_appetite": None}, "pension_plan", "investment_no_risk_profile"),
    ({"risk_appetite": "cautious"}, "investment_account", "investment_account_cautious"),
    ({"vulnerable": True}, "investment_fund", "investment_vulnerable"),
    ({"review_overdue": True}, "current_account", "review_overdue"),
])
def test_each_rule_fires(change, product, rule):
    facts = dict(CLEAN, **change)
    r = su.check(facts, product)
    assert r["allowed"] is False and rule in fired(facts, product)
    assert all(x["reason"] == su.RULE_REASONS[x["rule"]] for x in r["rules_fired"])


def test_rules_stay_in_their_lane():
    assert su.check(dict(CLEAN, flag_activity_drop=True), "term_deposit")["allowed"]
    assert su.check(dict(CLEAN, income_missing=True), "investment_fund")["allowed"]
    assert su.check(dict(CLEAN, risk_appetite="cautious"), "investment_fund")["allowed"]
    assert su.check(dict(CLEAN, risk_profile_done=False), "credit_card")["allowed"]
    # vulnerable blocks credit and investment, not everyday accounts
    assert su.check(dict(CLEAN, vulnerable=True), "online_account")["allowed"]


def test_under_18_only_basic_accounts():
    minor = dict(CLEAN, age=15.0)
    for p in ALL_PRODUCTS:
        assert su.check(minor, p)["allowed"] == (p in config.BASIC_PRODUCTS)
    assert set(fired(minor, "credit_card")) == {"under_18_basic_only", "credit_under_18"}


def test_unknown_age_is_not_treated_as_minor():
    assert su.check(dict(CLEAN, age=np.nan), "term_deposit")["allowed"]


def _random_facts(n=600, seed=0):
    rng = np.random.default_rng(seed)
    age = rng.integers(10, 90, n).astype(float)
    age[rng.random(n) < 0.05] = np.nan
    done = rng.random(n) < 0.6
    appetite = np.where(done, rng.choice(["cautious", "balanced", "adventurous"], n), None)
    return pd.DataFrame({
        "age": age, "income_missing": rng.random(n) < 0.2, "flag_activity_drop": rng.random(n) < 0.15,
        "deceased": rng.random(n) < 0.03, "vulnerable": rng.random(n) < 0.1, "risk_profile_done": done,
        "risk_appetite": pd.Series(appetite, dtype=object), "review_overdue": rng.random(n) < 0.1,
    }, index=pd.Index(np.arange(1000, 1000 + n), name="client_id"))


def test_vectorised_mask_agrees_with_per_client_check():
    facts = _random_facts()
    mask = su.blocked_mask(facts, ALL_PRODUCTS)
    for cid in facts.index:
        row = su.facts_row(facts, cid)
        for p in ALL_PRODUCTS:
            assert mask.loc[cid, p] == (not su.check(row, p)["allowed"]), (cid, p)


def test_rule_matrix_agrees_rule_by_rule():
    facts = _random_facts(200, seed=1)
    for p in ALL_PRODUCTS:
        m = su.rule_matrix(facts, p)
        for cid in facts.index:
            assert set(m.columns[m.loc[cid]]) == set(fired(su.facts_row(facts, cid), p))


def test_client_facts_from_snapshot_and_synthetic():
    snap = pd.DataFrame({"age": [30.0, 17.0, 50.0], "income": [1.0, np.nan, 2.0],
                         "income_missing": [0.0, 1.0, 0.0], "flag_activity_drop": [0, 0, 1],
                         "deceased": [0, 0, 0]}, index=[1, 2, 3])
    syn = pd.DataFrame({"vulnerable": [True, False], "risk_profile_done": [True, False],
                        "risk_appetite": ["cautious", None],
                        "next_kyc_review": pd.to_datetime(["2016-05-01", "2017-01-01"])}, index=[1, 2])
    f = su.client_facts(snap, syn, "2016-06-01")
    assert f.loc[1, "review_overdue"] and not f.loc[2, "review_overdue"]
    assert f.loc[1, "risk_appetite"] == "cautious" and f.loc[2, "risk_appetite"] is None
    assert f.loc[2, "income_missing"] and f.loc[3, "flag_activity_drop"]
    # client 3 has no synthetic row: no risk profile, not vulnerable, nothing overdue
    assert not f.loc[3, "risk_profile_done"] and not f.loc[3, "vulnerable"] and not f.loc[3, "review_overdue"]
    assert list(f.columns) == su.FACT_COLUMNS


def test_reason_text_is_plain():
    assert len(su.RULES) == len(set(su.RULE_NAMES))
    for r in su.RULES:
        assert not has_dash(r.reason)
        assert "sell" not in r.reason.lower() and "target" not in r.reason.lower()
        assert r.reason.endswith(".")
