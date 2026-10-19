"""fairness and ethics check: who gets suggestions, who gets held back, and does the model rank as well for them.

the groups are only used here, to audit the output; sex is never a model feature (config.EXCLUDED_FEATURES).
suggestion and held back rates are measured on the clients the agent briefs, at the default threshold.
ranking quality is measured on the test month, because only that month has labels. pr auc depends on how
common take up is in a group, so the flag for ranking uses roc auc, which does not; pr auc is reported too.

flags are mechanical, so nothing is hidden or judged by eye:
  a rate below 0.8 or above 1.25 times the overall rate (config.FAIRNESS_RATE_RATIO)
  a roc auc more than 0.05 below the overall roc auc for a product (config.FAIRNESS_AUC_GAP)
where a rule targets the group on purpose (the under 18 rules, the missing income rule), the flag says so.
"""
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from client_brief_agent import config
from client_brief_agent.agent import suitability, tools
from client_brief_agent.models.propensity import eligible, lgbm_proba

ATTRIBUTES = {"sex": "Sex as recorded", "age_band": "Age band", "income_missing": "Income recorded",
              "segment": "Client segment"}
# the dataset codes sex as H and V and does not document them; i read V as male, as in features.build
SEX_WORDS = {True: "V (read as male)", False: "Coded H, or not recorded (read as female)"}
SEGMENT_WORDS = {"segment_top": "Top tier", "segment_individual": "Individual", "segment_student": "Student"}
# rules that hold a group back on purpose, so a high held back rate there is expected
BY_DESIGN = {"age_band": {"under_18_basic_only", "credit_under_18"}, "income_missing": {"credit_income_missing"}}


def audit_groups(frame):
    """one column per audit attribute, plain words for every value."""
    age = frame["age_raw"] if "age_raw" in frame else frame["age"]
    band = pd.Series("age not recorded", index=frame.index)
    for lo, hi, name in config.AGE_BANDS:
        band[(age >= lo) & (age < hi)] = name
    seg = pd.Series("not recorded", index=frame.index)
    for col, name in SEGMENT_WORDS.items():
        if col in frame:
            seg[frame[col] > 0.5] = name
    return pd.DataFrame({
        "sex": (frame["sex_male"] > 0.5).map(SEX_WORDS),
        "age_band": band,
        "income_missing": np.where(frame["income_missing"] > 0.5, "no income recorded", "income recorded"),
        "segment": seg,
    }, index=frame.index)


def brief_outcomes(ctx, threshold=config.DEFAULT_THRESHOLD):
    """per briefed client: any suggestion, any product held back, and which rules held something back."""
    products = list(ctx.scores.columns)
    facts = ctx.facts.reindex(ctx.scores.index)
    S = ctx.scores.to_numpy(dtype=float)
    above = ~np.isnan(S) & (S >= threshold)
    B = suitability.blocked_mask(facts, products).to_numpy()
    L = tools.in_progress_mask(ctx.snapshot, products, ctx.scores.index).to_numpy()
    out = pd.DataFrame({"suggested": (above & ~B & ~L).any(axis=1), "held_back": (above & B).any(axis=1)},
                       index=ctx.scores.index)
    fired = [suitability.rule_matrix(facts, p).to_numpy() for p in products]
    for i, r in enumerate(suitability.RULE_NAMES):
        out[f"rule_{r}"] = np.logical_or.reduce([fired[j][:, i] & above[:, j] for j in range(len(products))])
    # deceased clients are not briefed, they would only add held back noise
    return out[facts["deceased"].to_numpy() == 0]


def _ratio(v, overall):
    return float(v / overall) if overall else None


def rate_table(ctx, threshold=config.DEFAULT_THRESHOLD):
    out = brief_outcomes(ctx, threshold)
    groups = audit_groups(ctx.snapshot.reindex(out.index))
    overall = {"suggestion_rate": float(out["suggested"].mean()), "held_back_rate": float(out["held_back"].mean())}
    lo, hi = config.FAIRNESS_RATE_RATIO
    rows = []
    for attr in ATTRIBUTES:
        for value, idx in groups.groupby(attr).groups.items():
            part = out.loc[idx]
            row = {"attribute": attr, "attribute_words": ATTRIBUTES[attr], "group": value, "n_clients": int(len(part)),
                   "suggestion_rate": float(part["suggested"].mean()), "held_back_rate": float(part["held_back"].mean())}
            row["suggestion_ratio"] = _ratio(row["suggestion_rate"], overall["suggestion_rate"])
            row["held_back_ratio"] = _ratio(row["held_back_rate"], overall["held_back_rate"])
            rules = {r: int(part[f"rule_{r}"].sum()) for r in suitability.RULE_NAMES}
            top_rule = max(rules, key=rules.get) if any(rules.values()) else None
            flags = []
            for key, words in (("suggestion_ratio", "Suggestion rate"), ("held_back_ratio", "Held back rate")):
                r = row[key]
                if r is not None and not lo <= r <= hi:
                    text = f"{words} is {r:.2f} times the overall rate."
                    if key == "held_back_ratio" and top_rule in BY_DESIGN.get(attr, set()):
                        text += f" Mostly the {top_rule.replace('_', ' ')} rule, which targets this group on purpose."
                    flags.append(text)
            row["top_rule"] = top_rule
            row["flags"] = flags
            rows.append(row)
    return overall, rows


def auc_table(models, test):
    """ranking quality per group and product on the test month; empty where a group has too few take ups."""
    groups = audit_groups(test)
    rows = []
    for product, bundle in models.items():
        X, y = eligible(test, product, bundle["features"])
        p = lgbm_proba(bundle, X)
        g = groups.loc[X.index]
        overall_roc = float(roc_auc_score(y, p))
        for attr in ATTRIBUTES:
            for value in sorted(g[attr].unique()):
                m = (g[attr] == value).to_numpy()
                pos = int(y[m].sum())
                row = {"product": product, "attribute": attr, "group": value, "n": int(m.sum()), "positives": pos,
                       "base_rate": float(y[m].mean()) if m.any() else None, "pr_auc": None, "roc_auc": None,
                       "roc_gap": None, "flag": None}
                if pos >= config.FAIRNESS_MIN_POSITIVES and pos < m.sum():
                    row["pr_auc"] = float(average_precision_score(y[m], p[m]))
                    row["roc_auc"] = float(roc_auc_score(y[m], p[m]))
                    row["roc_gap"] = row["roc_auc"] - overall_roc
                    if row["roc_gap"] < -config.FAIRNESS_AUC_GAP:
                        row["flag"] = (f"ROC AUC {row['roc_auc']:.3f} against {overall_roc:.3f} overall: "
                                       "the model ranks take up less well for this group.")
                rows.append(row)
    return rows


def audit(ctx, models, test, threshold=config.DEFAULT_THRESHOLD):
    overall, rates = rate_table(ctx, threshold)
    aucs = auc_table(models, test)
    return {"threshold": threshold, "overall": overall, "rates": rates, "auc": aucs,
            "min_positives": config.FAIRNESS_MIN_POSITIVES, "rate_ratio": list(config.FAIRNESS_RATE_RATIO),
            "auc_gap": config.FAIRNESS_AUC_GAP,
            "n_flags": sum(len(r["flags"]) for r in rates) + sum(1 for a in aucs if a["flag"]),
            "note": ("Groups are used only to audit the output. Sex is not a model feature. Rates are measured on "
                     "the briefed clients; ranking quality on the test month, where labels exist.")}
