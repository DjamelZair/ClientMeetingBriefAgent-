"""why a model scored a client the way it did, in numbers and then in plain words."""
import warnings

import numpy as np
import pandas as pd
import shap

from client_brief_agent import config
from client_brief_agent.wording import tenure_phrase


def lgbm_contributions(model, X):
    """shap TreeExplainer in raw margin (log odds) space. rows sum to the margin minus the expected value.
    early stopping keeps the extra rounds in the booster, so i limit shap to the iteration predict uses."""
    best = getattr(model, "best_iteration_", None) or None
    with warnings.catch_warnings():
        # shap warns that binary lightgbm now returns a list; i take the positive class below
        warnings.simplefilter("ignore", UserWarning)
        vals = shap.TreeExplainer(model).shap_values(X, tree_limit=best)
    if isinstance(vals, list):
        vals = vals[-1]
    vals = np.asarray(vals)
    if vals.ndim == 3:
        vals = vals[:, :, -1]
    return pd.DataFrame(vals, index=X.index, columns=X.columns)


def logreg_contributions(model, X):
    """exact for a linear model: coef_j * z_j, where z_j is the standardised value. the scaler was fitted
    on the training rows, so each term is the shift in log odds relative to an average training client."""
    imputer, scaler, lr = model.named_steps.values()
    z = scaler.transform(imputer.transform(X))
    return pd.DataFrame(z * lr.coef_[0], index=X.index, columns=X.columns)


# ---------- plain words ----------

def _plural(n, word):
    return f"{n:.0f} {word}" if round(n) == 1 else f"{n:.0f} {word}s"


def _when_one(text):
    return lambda v: text if v >= 0.5 else None


def _tenure(v):
    return tenure_phrase(v)


def _count(verb, window):
    return lambda v: f"{verb} {_plural(v, 'product')} in the last {window}" if v >= 1 else None


HELD_PHRASES = {
    "direct_debit": "already pays bills by direct debit",
    "salary_deposit": "already has a salary paid in",
    "pension_deposit": "already has a pension paid in",
}

FEATURE_PHRASES = {
    "age": lambda v: f"aged {v:.0f}",
    "income": lambda v: f"recorded income of about {round(v, -3):,.0f}",
    "log_income": lambda v: f"recorded income of about {round(float(np.expm1(v)), -3):,.0f}",
    "income_missing": _when_one("no income on record"),
    "tenure_months": _tenure,
    "segment_top": _when_one("in the premium segment"),
    "segment_individual": _when_one("in the everyday individual segment"),
    "segment_student": _when_one("in the student segment"),
    "active": lambda v: "an active client" if v >= 0.5 else "not currently active",
    "active_3m_ago": _when_one("was active three months ago"),
    "primary": _when_one("a primary client"),
    "employee": _when_one("a staff member"),
    "foreign_birth": _when_one("born abroad"),
    "n_products": lambda v: f"holds {_plural(v, 'product')}",
    "adds_3m": _count("added", "three months"),
    "adds_6m": _count("added", "six months"),
    "drops_3m": _count("closed", "three months"),
    "drops_6m": _count("closed", "six months"),
    "flag_new_products": _when_one("took up a new product in the last three months"),
    "flag_dropped_products": _when_one("closed a product in the last three months"),
    "flag_activity_drop": _when_one("has become less active in the last three months"),
    "flag_moved": _when_one("moved to a different province in the last six months"),
    "flag_new_client": _when_one("joined in the last six months"),
    "flag_segment_change": _when_one("changed customer segment in the last six months"),
}
for _code, _label in config.PRODUCT_LABELS.items():
    _noun = _label.lower()
    _default = f"already holds {'an' if _noun[0] in 'aeiou' else 'a'} {_noun}"
    FEATURE_PHRASES[f"held_{_code}"] = _when_one(HELD_PHRASES.get(_code, _default))
# sex, province, sign up channel and months observed get no phrase on purpose: they are not a reason
# an advisor should say out loud, so they never show up as one


def phrase(feature, value):
    fn = FEATURE_PHRASES.get(feature)
    if fn is None or value is None or pd.isna(value):
        return None
    return fn(float(value))


# features that say the same thing over different windows; only the strongest one gets a phrase,
# otherwise a brief reads "closed 1 product in three months; closed 1 product in six months"
TOPICS = {
    "adds_3m": "adds", "adds_6m": "adds", "flag_new_products": "adds",
    "drops_3m": "drops", "drops_6m": "drops", "flag_dropped_products": "drops",
    "active": "active", "active_3m_ago": "active", "flag_activity_drop": "active",
}


def plain_reasons(contribs_row, feature_values_row, top_n=3):
    """the strongest positive contributors that have a phrase, worded with the client's own values."""
    pos = contribs_row[contribs_row > 0].sort_values(ascending=False)
    reasons, topics = [], set()
    for feature in pos.index:
        topic = TOPICS.get(feature, feature)
        if topic in topics:
            continue
        text = phrase(feature, feature_values_row.get(feature))
        if text:
            text = text.rstrip(". ")
            if text not in reasons:
                reasons.append(text)
                topics.add(topic)
        if len(reasons) == top_n:
            break
    return reasons


# the snapshot fills gaps in age, income and tenure with medians for the model; the advisor must see
# the recorded value, so the phrase reads the raw column and is skipped when that is missing
RAW_DISPLAY = {"age": "age_raw", "income": "income_raw", "tenure_months": "tenure_raw", "log_income": "income_raw"}


def display_values(rows, features):
    vals = rows[features].astype("float64").copy()
    for feature, raw in RAW_DISPLAY.items():
        if feature in vals and raw in rows:
            vals[feature] = rows[raw].astype("float64")
            if feature == "log_income":
                vals[feature] = np.log1p(vals[feature])
    return vals


def client_reasons(bundle, rows, top_n=3, model="lgbm"):
    """reasons for each row of a snapshot slice (unique client ids), for one bundle from propensity.train_all."""
    X = rows[bundle["features"]].astype("float32")
    contribs = lgbm_contributions(bundle["lgbm"], X) if model == "lgbm" else logreg_contributions(bundle["logreg"], X)
    shown = display_values(rows, bundle["features"])
    return {cid: plain_reasons(contribs.loc[cid], shown.loc[cid], top_n) for cid in X.index}


# ---------- global importance ----------

def global_importance(models, frame, n=config.SHAP_SAMPLE, seed=config.SEED):
    """mean |shap| per feature, on a seeded sample of eligible test rows."""
    rows = []
    for product, bundle in models.items():
        elig = frame[frame[f"held_{product}"] == 0]
        sample = elig.sample(n=min(n, len(elig)), random_state=seed)[bundle["features"]].astype("float32")
        imp = lgbm_contributions(bundle["lgbm"], sample).abs().mean()
        rows.append(pd.DataFrame({"product": product, "feature": imp.index, "mean_abs_shap": imp.values}))
    out = pd.concat(rows, ignore_index=True)
    return out.sort_values(["product", "mean_abs_shap"], ascending=[True, False]).reset_index(drop=True)


def write_importance(importance, out_dir=None):
    out = out_dir or config.TABLE_DIR
    out.mkdir(parents=True, exist_ok=True)
    importance.round(6).to_csv(out / "global_importance.csv", index=False)
    return importance


def reasons_provider(models, snapshot, top_n=3):
    """the agent asks for reasons one client and product at a time, and only for products it will show,
    so i compute shap lazily and remember the answer instead of explaining all 200k clients up front."""
    cache = {}

    def reasons(cid, product):
        key = (cid, product)
        if key not in cache:
            if product not in models:
                cache[key] = []
            else:
                cache[key] = client_reasons(models[product], snapshot.loc[[cid]], top_n)[cid]
        return cache[key]

    return reasons
