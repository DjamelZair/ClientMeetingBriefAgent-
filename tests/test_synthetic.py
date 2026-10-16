"""the synthetic compliance layer must be reproducible and internally consistent."""
import numpy as np
import pandas as pd

from client_brief_agent import config
from client_brief_agent.data import synthetic

IDS = np.arange(1000, 21000, dtype=np.int64)


def test_two_calls_give_identical_frames():
    a = synthetic.make_synthetic_layer(IDS)
    b = synthetic.make_synthetic_layer(IDS)
    pd.testing.assert_frame_equal(a, b)


def test_input_order_does_not_matter():
    a = synthetic.make_synthetic_layer(IDS)
    b = synthetic.make_synthetic_layer(IDS[::-1])
    pd.testing.assert_frame_equal(a, b)


def test_different_seed_changes_draws():
    a = synthetic.make_synthetic_layer(IDS, seed=1)
    b = synthetic.make_synthetic_layer(IDS, seed=2)
    assert not a["kyc_risk_class"].equals(b["kyc_risk_class"])


def test_layer_is_consistent():
    layer = synthetic.make_synthetic_layer(IDS)
    assert layer.index.name == "client_id" and len(layer) == len(IDS)
    assert set(layer["kyc_risk_class"]) <= {"low", "medium", "high"}
    years = layer["kyc_risk_class"].map(config.KYC_INTERVAL_YEARS)
    for y in years.unique():
        m = years == y
        expected = layer.loc[m, "last_kyc_review"] + pd.DateOffset(years=int(y))
        assert (layer.loc[m, "next_kyc_review"] == expected).all()
    assert (layer["last_kyc_review"] <= pd.Timestamp(config.MEETING_DATE)).all()
    done = layer["risk_profile_done"]
    assert layer.loc[~done, "risk_appetite"].isna().all() and layer.loc[~done, "risk_profile_date"].isna().all()
    assert layer.loc[done, "risk_appetite"].isin(["cautious", "balanced", "adventurous"]).all()
    assert layer["synthetic"].all()
    # shares near the configured probabilities on 20k draws
    assert abs((layer["kyc_risk_class"] == "low").mean() - 0.70) < 0.02
    assert abs(layer["vulnerable"].mean() - config.VULNERABLE_PROB) < 0.01


def test_summary_has_the_review_window_metric():
    summary = synthetic.summarise_layer(synthetic.make_synthetic_layer(IDS))
    row = summary.set_index("metric").loc[f"share_review_due_within_{config.REVIEW_WINDOW_DAYS}d", "value"]
    assert 0 < row < 0.5
