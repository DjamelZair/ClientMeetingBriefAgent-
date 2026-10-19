"""the fairness audit: groups in plain words, rates per group, and flags that are mechanical."""
import numpy as np
import pandas as pd

from client_brief_agent import config
from client_brief_agent.report import fairness
from test_tools import make_ctx


def test_audit_groups_are_plain_words():
    frame = pd.DataFrame({"age_raw": [16, 30, 50, 70, np.nan], "sex_male": [1, 0, 1, 0, 0],
                          "income_missing": [1, 0, 0, 0, 1], "segment_student": [1, 0, 0, 0, 0],
                          "segment_top": [0, 0, 1, 0, 0], "segment_individual": [0, 1, 0, 1, 0]})
    g = fairness.audit_groups(frame)
    assert list(g["age_band"]) == ["under 25", "25 to 44", "45 to 64", "65 and over", "age not recorded"]
    assert list(g["segment"]) == ["Student", "Individual", "Top tier", "Individual", "not recorded"]
    assert g["sex"].iloc[0].startswith("V") and g["income_missing"].iloc[0] == "no income recorded"


def test_rates_add_up_and_flags_are_mechanical():
    ctx = make_ctx()
    ctx.snapshot["sex_male"] = (ctx.snapshot.index % 2).astype(float)
    overall, rows = fairness.rate_table(ctx)
    out = fairness.brief_outcomes(ctx)
    assert np.isclose(overall["suggestion_rate"], out["suggested"].mean())
    for attr in fairness.ATTRIBUTES:
        part = [r for r in rows if r["attribute"] == attr]
        assert sum(r["n_clients"] for r in part) == len(out)
        for r in part:
            lo, hi = config.FAIRNESS_RATE_RATIO
            flagged = r["suggestion_ratio"] is not None and not lo <= r["suggestion_ratio"] <= hi
            assert flagged == any(f.startswith("Suggestion rate") for f in r["flags"])


def test_deceased_clients_are_not_audited():
    ctx = make_ctx()
    dead = ctx.facts.index[ctx.facts["deceased"] == 1]
    assert not set(dead) & set(fairness.brief_outcomes(ctx).index)
