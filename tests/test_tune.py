"""the search is honest: trial 0 is my default, the test month is never read, and a tuned setting is only
chosen when it beat the default on validation."""
import numpy as np
import pandas as pd
import pytest

from client_brief_agent import config

optuna = pytest.importorskip("optuna")
from client_brief_agent.models import tune  # noqa: E402


def _frame(n, seed):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=n)
    df = pd.DataFrame({"age": rng.normal(40, 10, n), "income": x, "log_income": x, "income_missing": 0.0,
                       "tenure_months": rng.normal(50, 10, n), "held_current_account": 0.0})
    df["label_current_account"] = (rng.random(n) < 1 / (1 + np.exp(-(x * 2 - 3)))).astype(int)
    return df


def test_trial_zero_is_the_default_and_test_is_untouched(monkeypatch):
    monkeypatch.setattr(config, "LGBM_PARAMS", dict(config.LGBM_PARAMS, n_estimators=50))
    frames = {"train": _frame(3000, 1), "val": _frame(1500, 2)}
    feats = ["age", "income", "log_income", "income_missing", "tenure_months"]
    choice, trials = tune.tune_product(frames, "current_account", features=feats, n_trials=4)
    first = trials.iloc[0]
    for k in tune.SEARCHED:
        assert first[k] == pytest.approx(config.LGBM_PARAMS[k])
    assert len(trials) == 4 and "test" not in frames
    if choice["chosen"] == "tuned":
        assert choice["val_pr_auc_best"] > choice["val_pr_auc_default"]
    else:
        assert choice["params"] == {k: config.LGBM_PARAMS[k] for k in tune.SEARCHED}


def test_params_for_falls_back_to_default(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "TUNED_PARAMS_PATH", tmp_path / "none.json")
    params, source = tune.params_for("current_account")
    assert source == "default" and params == config.LGBM_PARAMS
