"""export: the vectorised guardrail curve must match what run_brief does, and the output must be clean."""
import json

import numpy as np
import pandas as pd
import pytest

from client_brief_agent import config
from client_brief_agent.agent import run, suitability
from client_brief_agent.agent.tools import has_dash
from client_brief_agent.report import export
from test_tools import make_bands, make_ctx


@pytest.fixture(scope="module")
def ctx():
    return make_ctx()


@pytest.fixture
def out_dirs(tmp_path, monkeypatch):
    for name in ["FIG_DIR", "TABLE_DIR", "BRIEF_DIR", "DOCS_DIR"]:
        monkeypatch.setattr(config, name, tmp_path / name.lower())
    monkeypatch.setattr(config, "DOCS_FIG_DIR", config.DOCS_DIR / "figures")
    return tmp_path


def _uncapped_blocked(brief):
    return sum(1 for e in brief["tool_log"] if e["tool"] == "check_suitability" and not e["summary"].endswith(": allowed"))


@pytest.mark.parametrize("t", [0.01, 0.05, 0.1, 0.12, 0.2, 0.3, 0.5, 0.6])
def test_curve_matches_run_brief(ctx, t):
    curve, rules = export.guardrail_curve(ctx, [t])
    pop = export.population(ctx)
    assert 105 not in pop
    briefs = [run.run_brief(ctx, cid, t) for cid in pop]
    row = curve.iloc[0]
    assert row["n_suggestions"] == sum(len(b["might_help"]) for b in briefs)
    assert row["n_blocked"] == sum(_uncapped_blocked(b) for b in briefs)
    assert row["n_clients_with_any"] == sum(1 for b in briefs if b["might_help"])
    assert row["n_in_progress"] == sum(len(b["in_progress"]) for b in briefs)
    # blocked by rule: count every (client, product, rule) that fired above the threshold
    expected = {r: 0 for r in suitability.RULE_NAMES}
    for cid in pop:
        for item in run.tools.get_propensities(ctx, cid, top_n=None):
            if item["probability"] >= t:
                for f in run.tools.check_suitability(ctx, cid, item["product"])["rules_fired"]:
                    expected[f["rule"]] += 1
    assert {r: int(rules.iloc[0][r]) for r in suitability.RULE_NAMES} == expected


def test_curve_is_monotone(ctx):
    curve, _ = export.guardrail_curve(ctx)
    assert len(curve) == 60 and curve["threshold"].iloc[0] == 0.01 and curve["threshold"].iloc[-1] == 0.6
    for col in ["n_suggestions", "n_blocked", "n_clients_with_any", "n_allowed_pairs"]:
        assert (np.diff(curve[col].to_numpy()) <= 0).all()


def test_review_summary(ctx):
    summary, table = export.review_summary(ctx)
    # 101 (30 days), 104 (overdue), 106 (exactly 90 days) are due; 108 has no synthetic row
    assert summary["n_due_within_window"] == 3 and summary["n_overdue"] == 1
    assert summary["n_clients"] == 7 and table["n"].sum() == 6  # 105 is deceased, so left out


def test_showcase_choice(ctx):
    picks = export.choose_showcase(ctx)
    ids = [cid for cid, _ in picks]
    assert ids == [cid for cid, _ in export.choose_showcase(ctx)]
    assert 105 not in ids  # deceased
    assert len(ids) == len(set(ids))
    clusters = {int(ctx.segments["labels"][cid]) for cid in ids}
    assert clusters == {0, 1, 2}
    why = [w for _, ws in picks for w in ws]
    assert any(w.startswith("shows rule") for w in why) and "review due soon" in why
    assert "review overdue" in why and "linked product in progress" in why
    briefs = [run.run_brief(ctx, cid) for cid in ids]
    assert any(b["not_to_offer"] for b in briefs) and any(b["due_anyway"]["due"] for b in briefs)
    assert any(b["in_progress"] for b in briefs) and any(b["next_step"] for b in briefs)


def test_showcase_respects_n(ctx):
    assert len(export.choose_showcase(ctx, n=2)) == 2


def test_to_plain():
    out = export.to_plain({1: np.float32(0.123456), "b": [np.int64(3), np.nan, pd.Timestamp("2016-06-01")],
                           "c": np.bool_(True), "d": pd.DataFrame({"x": [1.234567]})})
    assert out == {"1": 0.1235, "b": [3, None, "2016-06-01"], "c": True, "d": [{"x": 1.2346}]}


def _with_page_bits(c):
    c.segments["pca_2d"] = pd.DataFrame({"client_id": [101, 102, 103], "x": [1.23456, 0.1, 0.2],
                                         "y": [-0.5, 0.3, 0.4], "cluster": [0, 0, 2]})
    c.segments["profiles"] = pd.DataFrame({"age": [41.2345, 60.0, 25.0], "n_products": [2.0, 3.0, 1.0],
                                           "held_credit_card": [0.1, 0.2, 0.3]}, index=[0, 1, 2])
    return c


def _remapped_ctx():
    """same fake clients under long ids, so a leak is easy to spot in the text."""
    c = _with_page_bits(make_ctx())
    m = {cid: 7_000_000 + cid * 13 for cid in c.snapshot.index}
    snap = c.snapshot.rename(index=m)
    snap.loc[:, "income"] = snap["income"]
    return run.tools.Context(snapshot=snap, segments=dict(c.segments, labels=c.segments["labels"].rename(index=m)),
                             scores=c.scores.rename(index=m), reasons=lambda cid, p: ["aged 40"],
                             synthetic=c.synthetic.rename(index=m), bands=c.bands), list(m.values())


def _extras():
    metrics = pd.DataFrame({"product": ["credit_card", "credit_card"], "model": ["lgbm", "logreg"],
                            "roc_auc": [0.81234567, 0.7712], "pr_auc": [0.1, 0.08]})
    imp = pd.DataFrame({"product": ["credit_card"] * 6, "feature": list("abcdef"),
                        "importance": [0.6, 0.5, 0.4, 0.3, 0.2, 0.1]})
    return {"metrics": metrics, "importance": imp, "data_facts": {"n_rows": 100},
            "calibration": {"quantile": pd.DataFrame({"product": ["credit_card"], "mean_pred": [0.1]}),
                            "bands": make_bands()}}


def test_write_all(out_dirs):
    ctx = _with_page_bits(make_ctx())
    data = export.write_all(ctx, _extras())
    assert set(data) == {"meta", "data_facts", "segmentation", "propensity", "guardrail", "reviews",
                         "showcase", "figures"}
    assert "generated_at" not in json.dumps(data)
    assert data["segmentation"]["k"] == 3 and len(data["segmentation"]["clusters"]) == 3
    assert data["propensity"]["metrics"][0]["roc_auc"] == 0.8123
    assert len(data["propensity"]["importance_top5"]["credit_card"]) == 5
    assert len(data["guardrail"]["curve"]) == 60
    assert data["guardrail"]["at_default"]["threshold"] == config.DEFAULT_THRESHOLD
    assert isinstance(data["guardrail"]["at_default"]["n_suggestions"], int)
    assert "n_meetings_covering_review" in data["reviews"]
    assert data["meta"]["n_excluded_deceased"] == 1 and data["meta"]["curve_population"] == 7
    cov = {r["rule"]: r for r in data["guardrail"]["rules"]}
    assert set(cov) == set(suitability.RULE_NAMES)
    assert cov["investment_account_cautious"]["scored_products_covered"] == ["investment_account"]
    zero = {r["rule"]: r["n"] for r in data["guardrail"]["blocked_by_rule_at_default"]}
    assert set(zero) == set(suitability.RULE_NAMES) and zero["deceased"] == 0
    refs = [s["client_ref"] for s in data["showcase"]]
    assert refs == [f"Client {i:02d}" for i in range(1, len(refs) + 1)]
    for i, s in enumerate(data["showcase"], 1):
        assert s["markdown_path"] == f"briefs/client_{i:02d}.md"
        assert (config.BRIEF_DIR / f"client_{i:02d}.md").exists()
        assert s["brief"]["tool_log"] and "client_id" not in s["brief"]
    assert data["meta"]["code_url"] == config.CODE_URL
    assert "n_in_progress" in data["guardrail"]["curve"][0]
    seg = data["segmentation"]
    assert seg["points"][0] == {"x": 1.235, "y": -0.5, "cluster": 0} and len(seg["points"]) == 3
    assert seg["clusters"][0]["profile"] == {"age": 41.23, "n_products": 2.0}
    assert data["propensity"]["calibration"]["bands"][0]["product"] == "current_account"
    for name, path in data["figures"].items():
        assert (config.DOCS_DIR / path).exists(), name
    for t in ["guardrail_curve.csv", "guardrail_blocked_by_rule.csv", "reviews_due.csv"]:
        assert (config.TABLE_DIR / t).exists()


def test_export_is_deterministic(ctx, out_dirs):
    export.write_all(ctx, _extras(), make_figures=False)
    first = (config.DOCS_DIR / "data.json").read_bytes()
    export.write_all(ctx, _extras(), make_figures=False)
    assert (config.DOCS_DIR / "data.json").read_bytes() == first


def test_no_dashes_in_exported_text(ctx, out_dirs):
    export.write_all(ctx, _extras(), make_figures=False)
    files = [config.DOCS_DIR / "data.json"] + sorted(config.BRIEF_DIR.glob("*.md"))
    assert len(files) > 1
    for f in files:
        text = f.read_text(encoding="utf-8")
        assert not has_dash(text), f.name
        assert " sell" not in text.lower(), f.name


def test_no_real_client_id_leaves(out_dirs):
    c, ids = _remapped_ctx()
    (config.BRIEF_DIR).mkdir(parents=True, exist_ok=True)
    (config.BRIEF_DIR / f"{ids[0]}.md").write_text("old brief\n")
    export.write_all(c, _extras(), make_figures=False)
    text = (config.DOCS_DIR / "data.json").read_text()
    text += "".join(f.read_text() for f in config.BRIEF_DIR.glob("*.md"))
    names = [f.name for f in config.BRIEF_DIR.glob("*.md")]
    assert all(n.startswith("client_") for n in names)
    for cid in ids:
        assert str(cid) not in text, cid


def test_importance_accepts_mean_abs_shap():
    imp = pd.DataFrame({"product": ["a"] * 6, "feature": list("uvwxyz"), "mean_abs_shap": [6, 5, 4, 3, 2, 1.0]})
    top = export.to_plain(export._importance_top5(imp))
    assert list(top) == ["a"] and len(top["a"]) == 5 and top["a"][0] == {"feature": "u", "importance": 6.0}
