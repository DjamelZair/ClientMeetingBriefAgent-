"""contributions must add up, and reasons only use what the features say."""
import numpy as np
import pandas as pd
import pytest

from client_brief_agent.models import explain, propensity
from test_propensity import FEATURES, frame


@pytest.fixture(scope="module")
def bundle():
    frames = {"train": frame(6000, 1), "val": frame(2000, 2), "test": frame(2000, 3)}
    res = propensity.train_all(frames, ["credit_card"], features=FEATURES, save=False, verbose=False)
    return res["models"]["credit_card"], frames["test"]


def test_shap_adds_to_margin(bundle):
    b, test = bundle
    X = test[FEATURES].iloc[:200]
    c = explain.lgbm_contributions(b["lgbm"], X)
    margin = b["lgbm"].predict_proba(X, raw_score=True, num_iteration=b["lgbm"].best_iteration_)
    base = margin - c.sum(axis=1).to_numpy()
    assert np.allclose(base, base[0], atol=1e-4)


def test_logreg_exact(bundle):
    b, test = bundle
    X = test[FEATURES].iloc[:200]
    c = explain.logreg_contributions(b["logreg"], X)
    logit = b["logreg"].decision_function(X)
    assert np.allclose(c.sum(axis=1) + b["logreg"].named_steps["logisticregression"].intercept_[0], logit)


def test_plain_reasons_positive_only():
    contribs = pd.Series({"age": 0.5, "held_direct_debit": 0.3, "flag_new_client": -0.4, "income": 0.1,
                          "sex_male": 0.9})
    values = pd.Series({"age": 34.0, "held_direct_debit": 1.0, "flag_new_client": 1.0, "income": 52000.0,
                        "sex_male": 1.0})
    r = explain.plain_reasons(contribs, values, top_n=3)
    assert r == ["aged 34", "already pays bills by direct debit", "recorded income of about 52,000"]
    assert not any("six months" in x for x in r)


def test_reasons_skip_absent_facts():
    contribs = pd.Series({"held_credit_card": 0.6, "flag_new_client": 0.5, "income": 0.2})
    values = pd.Series({"held_credit_card": 0.0, "flag_new_client": 1.0, "income": np.nan})
    assert explain.plain_reasons(contribs, values) == ["joined in the last six months"]


def test_global_importance(bundle):
    b, test = bundle
    imp = explain.global_importance({"credit_card": b}, test, n=500)
    assert set(imp["feature"]) == set(FEATURES)
    assert imp["mean_abs_shap"].ge(0).all()
    assert imp.iloc[0]["feature"] in ("active", "age")


def test_phrases_have_no_dashes():
    for f in explain.FEATURE_PHRASES:
        text = explain.phrase(f, 1.0) or ""
        assert "\u2014" not in text and "\u2013" not in text


def test_reasons_use_raw_values(bundle):
    b, test = bundle
    rows = test.iloc[:50].copy()
    rows["age_raw"] = np.nan
    rows["income_raw"] = 12345.0
    reasons = explain.client_reasons(b, rows, top_n=10)
    flat = [r for rs in reasons.values() for r in rs]
    assert not any(r.startswith("aged") for r in flat)
    assert all("12,000" in r for r in flat if r.startswith("recorded income"))


def test_one_phrase_per_topic():
    import pandas as pd
    from client_brief_agent.models import explain
    contribs = pd.Series({"drops_3m": 0.9, "drops_6m": 0.8, "flag_dropped_products": 0.7, "n_products": 0.5})
    values = pd.Series({"drops_3m": 1.0, "drops_6m": 1.0, "flag_dropped_products": 1.0, "n_products": 4.0})
    reasons = explain.plain_reasons(contribs, values, top_n=3)
    assert sum("closed" in r for r in reasons) == 1
    assert not any(r.endswith(".") for r in reasons)
