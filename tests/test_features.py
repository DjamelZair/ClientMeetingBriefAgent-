"""snapshot tests on a hand built panel: no leakage, correct labels, correct history counts."""
import numpy as np
import pandas as pd
import pytest

from client_brief_agent import config
from client_brief_agent.features import build

MONTHS = [f"2015-{m:02d}" for m in range(1, 10)]
CODES = build.PRODUCT_CODES


def make_panel():
    rows = []
    for cid in [1, 2, 3, 4]:
        for i, m in enumerate(MONTHS):
            if cid == 3 and m == "2015-09":
                continue  # client 3 leaves before the last month
            if cid == 4 and i < 7:
                continue  # client 4 joins in 2015-08
            row = {"month": m, "client_id": cid, "age": 30.0 + cid, "income": np.nan if cid == 2 else 40000.0,
                   "tenure_months": 3.0 if cid == 4 else 20.0 + i, "joined": "2014-01-01",
                   "segment": "student" if (cid == 2 and i < 5) else "individual",
                   "province": 8.0 if (cid == 1 and i >= 6) else 28.0, "channel": "KHE" if cid != 2 else "KAT",
                   "active": 0 if (cid == 1 and i >= 7) else 1, "rel_type": "A", "sex": "V" if cid % 2 else "H",
                   "employee": 0, "foreign_birth": 0, "deceased": 0, "primary": 1}
            for c in CODES:
                row[c] = 0
            row["current_account"] = 1
            # client 1 takes a credit card in 2015-07 and direct debit in 2015-09
            row["credit_card"] = int(cid == 1 and i >= 6)
            row["direct_debit"] = int(cid == 1 and m == "2015-09")
            rows.append(row)
    panel = pd.DataFrame(rows)
    for col in ["segment", "channel", "rel_type", "sex"]:
        panel[col] = panel[col].astype("category")
    for c in CODES + ["active", "employee", "foreign_birth", "deceased", "primary"]:
        panel[c] = panel[c].astype(np.int8)
    return panel


def test_rows_are_clients_present_at_t_minus_1_and_t():
    snap = build.build_snapshot(make_panel(), "2015-09")
    assert sorted(snap.index) == [1, 2, 4]
    brief = build.build_snapshot(make_panel(), "2015-10")
    assert sorted(brief.index) == [1, 2, 4]
    assert not any(c.startswith("label_") for c in brief.columns)


def test_columns_and_types():
    snap = build.build_snapshot(make_panel(), "2015-09")
    assert set(build.FEATURE_COLUMNS) <= set(snap.columns)
    assert set(build.SEGMENT_FEATURES) <= set(build.FEATURE_COLUMNS)
    plain = [c for c in build.FEATURE_COLUMNS if c not in build.CHANGE_FLAGS]
    assert (snap[plain].dtypes == np.float32).all()
    assert (snap[build.CHANGE_FLAGS].dtypes == np.int8).all()
    assert not snap[build.FEATURE_COLUMNS].isna().any().any()
    assert (snap[build.LABEL_COLUMNS].dtypes == np.int8).all()
    assert snap["target_month"].eq("2015-09").all() and "deceased" in snap


def test_no_leakage_from_target_month():
    panel = make_panel()
    before = build.build_snapshot(panel, "2015-09")
    changed = panel.copy()
    at_t = changed["month"] == "2015-09"
    for c in CODES:
        changed.loc[at_t, c] = 1
    changed.loc[at_t, ["age", "income", "tenure_months", "province"]] = [99.0, 1.0, 0.0, 1.0]
    changed.loc[at_t, "active"] = 0
    changed["segment"] = changed["segment"].cat.add_categories(["top"])
    changed.loc[at_t, "segment"] = "top"
    after = build.build_snapshot(changed, "2015-09")
    feats = build.FEATURE_COLUMNS + build.RAW_COLUMNS
    pd.testing.assert_frame_equal(before[feats], after[feats])
    assert not before[build.LABEL_COLUMNS].equals(after[build.LABEL_COLUMNS])


def test_labels_are_new_take_ups_only():
    snap = build.build_snapshot(make_panel(), "2015-09")
    assert snap.loc[1, "label_direct_debit"] == 1
    assert snap.loc[1, "label_credit_card"] == 0  # already held at T-1
    assert snap[build.LABEL_COLUMNS].drop(index=1).sum().sum() == 0


def test_history_counts_and_flags():
    snap = build.build_snapshot(make_panel(), "2015-09")
    c1 = snap.loc[1]
    assert c1["held_credit_card"] == 1 and c1["n_products"] == 2
    assert c1["adds_3m"] == 1 and c1["adds_6m"] == 1 and c1["drops_6m"] == 0
    assert c1["flag_new_products"] == 1 and c1["flag_moved"] == 1
    # active 3 months before 2015-08 (2015-05) and inactive at 2015-08
    assert c1["active_3m_ago"] == 1 and c1["flag_activity_drop"] == 1
    assert c1["months_observed"] == 8 and c1["sex_male"] == 1 and c1["channel_khe"] == 1
    c2 = snap.loc[2]
    assert c2["income_missing"] == 1 and c2["flag_segment_change"] == 1 and c2["channel_kat"] == 1
    assert c2["flag_moved"] == 0
    c4 = snap.loc[4]
    assert c4["flag_new_client"] == 1 and c4["months_observed"] == 1 and c4["adds_6m"] == 0


def test_modelled_products_uses_thresholds(monkeypatch):
    panel = make_panel()
    snap = build.build_snapshot(panel, "2015-09")
    frames = {"train": snap, "val": snap, "test": snap}
    monkeypatch.setattr(config, "MIN_TEST_POSITIVES", 1)
    monkeypatch.setattr(config, "MIN_TRAIN_POSITIVES", 1)
    assert build.modelled_products(frames) == ["direct_debit"]
    monkeypatch.setattr(config, "MIN_TEST_POSITIVES", 2)
    assert build.modelled_products(frames) == []
