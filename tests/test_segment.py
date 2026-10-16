"""segmentation on a synthetic frame with three planted groups."""
import numpy as np
import pandas as pd
import pytest

from client_brief_agent.models import segment

FEATURES = ["age", "log_income", "tenure_months", "n_products", "active",
            "segment_student", "segment_top", "held_direct_debit"]


def planted(n_per=600, seed=0):
    rng = np.random.default_rng(seed)
    groups = [
        dict(age=22, log_income=10.0, tenure_months=10, n_products=1, active=0.2, segment_student=0.95,
             segment_top=0.0, held_direct_debit=0.05),
        dict(age=45, log_income=11.0, tenure_months=90, n_products=2, active=0.6, segment_student=0.0,
             segment_top=0.05, held_direct_debit=0.4),
        dict(age=62, log_income=12.0, tenure_months=200, n_products=4, active=0.95, segment_student=0.0,
             segment_top=0.9, held_direct_debit=0.9),
    ]
    parts = []
    for g in groups:
        d = {}
        for f, m in g.items():
            if f in ("active", "segment_student", "segment_top", "held_direct_debit"):
                d[f] = (rng.random(n_per) < m).astype("float32")
            else:
                d[f] = (m + rng.normal(0, 0.08 * abs(m) + 0.1, n_per)).astype("float32")
        parts.append(pd.DataFrame(d))
    df = pd.concat(parts, ignore_index=True)
    df.loc[::50, "log_income"] = np.nan
    df.index = pd.Index(np.arange(10_000, 10_000 + len(df)), name="client_id")
    return df


@pytest.fixture(scope="module")
def seg():
    return segment.fit_segments(planted(), features=FEATURES)


def test_finds_planted_groups(seg):
    assert seg["k"] == 3
    assert set(seg["silhouette"]) == set(range(2, 11))
    assert seg["ari_gmm"] > 0.8


def test_outputs_shape(seg):
    df = planted()
    assert seg["labels"].index.equals(df.index)
    assert sum(seg["sizes"].values()) == len(df)
    assert list(seg["profiles"].columns) == FEATURES
    assert set(seg["pca_2d"].columns) == {"client_id", "x", "y", "cluster"}
    assert len(seg["pca_2d"]) <= 3000


def test_descriptions_follow_numbers(seg):
    prof = seg["profiles"]
    young = int(prof["age"].idxmin())
    old = int(prof["age"].idxmax())
    assert "student" in seg["descriptions"][young].lower() or "younger" in seg["descriptions"][young].lower()
    # the quoted average age must be the real cluster mean
    if "average age" in seg["descriptions"][old]:
        assert f"{prof.loc[old, 'age']:.0f}" in seg["descriptions"][old]
    assert len(set(seg["names"].values())) == seg["k"]
    for name in seg["names"].values():
        assert 2 <= len(name.split()) <= 4


def test_choose_k_rule():
    sil = {2: 0.50, 3: 0.495, 4: 0.30, 5: 0.25}
    inertia = {2: 100.0, 3: 40.0, 4: 35.0, 5: 33.0}
    k, elbow = segment.choose_k(sil, inertia, tie=0.01)
    assert elbow == 3 and k == 3
    k, _ = segment.choose_k(sil, inertia, tie=0.0)
    assert k == 2


def test_no_dashes(seg):
    text = " ".join(seg["descriptions"].values()) + " ".join(seg["names"].values())
    assert "\u2014" not in text and "\u2013" not in text


def test_excluded_features_dropped():
    assert segment.segment_features(FEATURES + ["sex_male", "foreign_birth"]) == FEATURES
