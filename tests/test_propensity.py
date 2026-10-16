"""propensity training on a synthetic panel where the signal is known."""
import numpy as np
import pandas as pd
import pytest

from client_brief_agent.models import propensity

FEATURES = ["age", "income", "tenure_months", "n_products", "active", "held_direct_debit",
            "held_credit_card", "flag_new_client"]


def frame(n, seed):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "age": rng.uniform(18, 80, n), "income": rng.lognormal(11, 0.5, n),
        "tenure_months": rng.uniform(0, 240, n), "n_products": rng.integers(1, 6, n),
        "active": rng.integers(0, 2, n), "held_direct_debit": rng.integers(0, 2, n),
        "held_credit_card": (rng.random(n) < 0.2).astype(int), "flag_new_client": (rng.random(n) < 0.1).astype(int),
    }).astype("float32")
    df.loc[rng.random(n) < 0.1, "income"] = np.nan
    # an interaction, so a tree has something a linear model misses
    logit = -4 + 1.5 * df["active"] + 1.2 * ((df["age"] > 30) & (df["age"] < 45)) + 0.8 * df["held_direct_debit"]
    df["label_credit_card"] = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype("int8")
    df["label_direct_debit"] = (rng.random(n) < 1 / (1 + np.exp(-(-3 + df["active"])))).astype("int8")
    df.index = pd.Index(np.arange(seed * 100_000, seed * 100_000 + n), name="client_id")
    return df


@pytest.fixture(scope="module")
def frames():
    return {"train": frame(8000, 1), "val": frame(3000, 2), "test": frame(3000, 3), "brief": frame(500, 4)}


@pytest.fixture(scope="module")
def result(frames):
    return propensity.train_all(frames, ["credit_card", "direct_debit"], features=FEATURES, save=False,
                                verbose=False)


def test_metrics_table(result):
    t = propensity.metrics_table(result)
    assert list(t.index) == ["credit_card", "direct_debit"]
    for col in ["lgbm_roc_auc", "logreg_roc_auc", "lgbm_pr_auc", "logreg_pr_auc", "lgbm_isotonic_pr_auc",
                "base_rate", "n_test", "n_test_pos", "lgbm_brier", "lgbm_isotonic_brier",
                "lgbm_pr_auc_lo", "lgbm_pr_auc_hi", "logreg_pr_auc_lo", "lift_pr_auc", "lift_pr_auc_lo"]:
        assert col in t.columns
    row = t.loc["credit_card"]
    assert row["lgbm_pr_auc_lo"] <= row["lgbm_pr_auc"] <= row["lgbm_pr_auc_hi"]
    assert abs(row["lift_pr_auc"] - (row["lgbm_pr_auc"] - row["logreg_pr_auc"])) < 1e-12
    assert row["lgbm_roc_auc"] > 0.6


def test_trains_only_on_non_holders(frames, result):
    test = frames["test"]
    assert result["metrics"][0]["n_test"] == int((test["held_credit_card"] == 0).sum())


def test_calibration_keeps_ranking(result):
    t = propensity.metrics_table(result)
    # isotonic is monotone, so ranking can only move through ties
    assert (t["lgbm_roc_auc"] - t["lgbm_isotonic_roc_auc"]).abs().max() < 0.02
    cal = result["calibration"]
    assert set(cal["model"]) == {"lgbm", "lgbm_isotonic", "logreg"}
    assert cal.groupby(["product", "model"]).size().max() <= 10


def test_score_masks_held(frames, result):
    s = propensity.score(result["models"], frames["brief"])
    held = frames["brief"]["held_credit_card"] == 1
    assert s.loc[held, "credit_card"].isna().all()
    assert s.loc[~held, "credit_card"].between(0, 1).all()


def test_excludes_protected_and_deceased(frames):
    f = {k: v.copy() for k, v in frames.items()}
    for v in f.values():
        v["sex_male"] = 1.0
        v["deceased"] = 0
    f["test"].iloc[:100, f["test"].columns.get_loc("deceased")] = 1
    f["brief"].iloc[:10, f["brief"].columns.get_loc("deceased")] = 1
    res = propensity.train_all(f, ["credit_card"], features=FEATURES + ["sex_male"], save=False, verbose=False)
    assert "sex_male" not in res["features"]
    expected = int(((f["test"]["held_credit_card"] == 0) & (f["test"]["deceased"] == 0)).sum())
    assert res["metrics"][0]["n_test"] == expected
    s = propensity.score(res["models"], f["brief"])
    assert s["credit_card"].iloc[:10].isna().all()


def test_calibration_bands_cover_all_rows(frames, result):
    bands = result["calibration_bands"]
    for p in ["credit_card", "direct_debit"]:
        b = bands[bands["product"] == p]
        assert b["n"].sum() == int((frames["test"][f"held_{p}"] == 0).sum())
        assert (b["lo"] < b["hi"]).all()
