"""per product take up models: lightgbm as the main model, logistic regression as the honest baseline.

i tried isotonic calibration on the validation month. it did not improve brier, it cost pr auc on every product
and it pushed some brief scores to exactly 1.0, which an advisor would read as certain. plain lightgbm trained
on log loss was already close to calibrated, so the score is plain lightgbm and isotonic stays only as a comparison.
"""
import time

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from client_brief_agent import config

MODELS = ("lgbm", "lgbm_isotonic", "logreg")
# fixed probability bands, so the calibration check covers the range where suggestions actually happen
CALIBRATION_EDGES = [0.0, 0.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.50, 1.0]


def model_features(features=None):
    """the model never sees sex or place of birth, even when a caller passes them in (config.EXCLUDED_FEATURES)."""
    if features is None:
        from client_brief_agent.features.build import FEATURE_COLUMNS
        features = FEATURE_COLUMNS
    return [f for f in features if f not in config.EXCLUDED_FEATURES]


def eligible(frame, product, features):
    """only clients who do not hold the product yet can take it up, so only they are trained and tested on.
    deceased clients are dropped too. the train index repeats client ids across months, so i only use masks."""
    keep = frame[f"held_{product}"] == 0
    if "deceased" in frame:
        keep &= frame["deceased"] != 1
    rows = frame[keep]
    X = rows[features].astype("float32")
    y = rows[f"label_{product}"].astype("int8").to_numpy() if f"label_{product}" in rows else None
    return X, y


def fit_lgbm(X_tr, y_tr, X_va, y_va, seed=config.SEED, params=None):
    model = lgb.LGBMClassifier(**(params or config.LGBM_PARAMS), n_jobs=config.N_JOBS, random_state=seed, verbose=-1)
    model.fit(X_tr, y_tr, eval_set=[(X_va, y_va)], eval_metric="binary_logloss",
              callbacks=[lgb.early_stopping(config.EARLY_STOPPING_ROUNDS, verbose=False)])
    return model


def fit_logreg(X_tr, y_tr, seed=config.SEED):
    # median fill because income and tenure have gaps; no class weights so the scores stay probabilities
    model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                          LogisticRegression(max_iter=2000, class_weight=None, random_state=seed))
    return model.fit(X_tr, y_tr)


def fit_isotonic(p_val, y_val):
    return IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0).fit(p_val, y_val)


def lgbm_proba(bundle, X, calibrated=False):
    p = bundle["lgbm"].predict_proba(X, num_iteration=bundle["lgbm"].best_iteration_)[:, 1]
    return bundle["isotonic"].predict(p) if calibrated else p


def evaluate(y, p):
    return {"roc_auc": float(roc_auc_score(y, p)), "pr_auc": float(average_precision_score(y, p)),
            "brier": float(brier_score_loss(y, p))}


def bootstrap_ci(y, preds, n=config.N_BOOTSTRAP, seed=config.SEED):
    """paired bootstrap: every resample scores all models on the same rows, so the lift ci is fair."""
    rng = np.random.default_rng(seed)
    draws = {f"{m}_{s}": [] for m in preds for s in ("roc_auc", "pr_auc")}
    draws.update({"lift_roc_auc": [], "lift_pr_auc": []})
    for _ in range(n):
        idx = rng.integers(0, len(y), len(y))
        yb = y[idx]
        if yb.min() == yb.max():
            continue
        cur = {}
        for m, p in preds.items():
            cur[m] = (roc_auc_score(yb, p[idx]), average_precision_score(yb, p[idx]))
            draws[f"{m}_roc_auc"].append(cur[m][0])
            draws[f"{m}_pr_auc"].append(cur[m][1])
        draws["lift_roc_auc"].append(cur["lgbm"][0] - cur["logreg"][0])
        draws["lift_pr_auc"].append(cur["lgbm"][1] - cur["logreg"][1])
    out = {}
    for key, vals in draws.items():
        out[f"{key}_lo"], out[f"{key}_hi"] = (float(v) for v in np.percentile(vals, [2.5, 97.5]))
    return out


def calibration_points(y, p, bins=10):
    """10 quantile bins of predicted probability; isotonic ties can merge bins, so there may be fewer."""
    df = pd.DataFrame({"y": y, "p": p})
    df["bin"] = pd.qcut(df["p"].rank(method="first"), bins, labels=False)
    pts = df.groupby("bin").agg(mean_pred=("p", "mean"), observed=("y", "mean"), n=("y", "size"))
    return pts.reset_index()


def calibration_bands(y, p, edges=CALIBRATION_EDGES):
    """observed take up inside fixed score bands; empty bands are dropped."""
    df = pd.DataFrame({"y": y, "p": p})
    df["band"] = pd.cut(df["p"], edges, include_lowest=True, labels=False)
    pts = df.groupby("band").agg(mean_pred=("p", "mean"), observed=("y", "mean"), n=("y", "size"),
                                 positives=("y", "sum")).reset_index()
    pts["lo"] = [edges[int(b)] for b in pts["band"]]
    pts["hi"] = [edges[int(b) + 1] for b in pts["band"]]
    return pts


def train_product(frames, product, features, seed=config.SEED):
    t0 = time.time()
    X_tr, y_tr = eligible(frames["train"], product, features)
    X_va, y_va = eligible(frames["val"], product, features)
    X_te, y_te = eligible(frames["test"], product, features)

    # the tuned setting when the validation search chose it (models/tune.py), otherwise my default
    from client_brief_agent.models.tune import params_for
    params, source = params_for(product)
    bundle = {"product": product, "features": features, "params": params, "params_source": source}
    bundle["lgbm"] = fit_lgbm(X_tr, y_tr, X_va, y_va, seed, params)
    bundle["logreg"] = fit_logreg(X_tr, y_tr, seed)
    # isotonic sees validation only; the test month stays untouched until scoring
    bundle["isotonic"] = fit_isotonic(lgbm_proba(bundle, X_va, calibrated=False), y_va)

    preds = {"lgbm": lgbm_proba(bundle, X_te), "lgbm_isotonic": lgbm_proba(bundle, X_te, calibrated=True),
             "logreg": bundle["logreg"].predict_proba(X_te)[:, 1]}
    row = {"product": product, "n_train": int(len(y_tr)), "n_train_pos": int(y_tr.sum()),
           "n_test": int(len(y_te)), "n_test_pos": int(y_te.sum()), "base_rate": float(y_te.mean()),
           "lgbm_best_iteration": int(bundle["lgbm"].best_iteration_), "params_source": source}
    for m, p in preds.items():
        row.update({f"{m}_{k}": v for k, v in evaluate(y_te, p).items()})
    # the isotonic version gets no ci of its own: it is only the comparison i rejected
    row.update(bootstrap_ci(y_te, {"lgbm": preds["lgbm"], "logreg": preds["logreg"]}, seed=seed))
    row["lift_roc_auc"] = row["lgbm_roc_auc"] - row["logreg_roc_auc"]
    row["lift_pr_auc"] = row["lgbm_pr_auc"] - row["logreg_pr_auc"]
    row["seconds"] = round(time.time() - t0, 1)
    calib = pd.concat([calibration_points(y_te, preds["lgbm"]).assign(model="lgbm"),
                       calibration_points(y_te, preds["lgbm_isotonic"]).assign(model="lgbm_isotonic"),
                       calibration_points(y_te, preds["logreg"]).assign(model="logreg")])
    bands = calibration_bands(y_te, preds["lgbm"]).assign(product=product)
    return bundle, row, calib.assign(product=product), bands


def train_all(frames, products, features=None, save=True, seed=config.SEED, verbose=True):
    features = model_features(features)
    models, rows, calibs, bands = {}, [], [], []
    for product in products:
        bundle, row, calib, band = train_product(frames, product, features, seed)
        bands.append(band)
        models[product] = bundle
        rows.append(row)
        calibs.append(calib)
        if verbose:
            print(f"{product}: lgbm pr {row['lgbm_pr_auc']:.4f} logreg pr {row['logreg_pr_auc']:.4f} "
                  f"lift {row['lift_pr_auc']:+.4f} ({row['seconds']}s)", flush=True)
        if save:
            save_model(bundle)
    return {"models": models, "metrics": rows, "calibration": pd.concat(calibs, ignore_index=True),
            "calibration_bands": pd.concat(bands, ignore_index=True),
            "features": features}


def save_model(bundle):
    config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, config.MODEL_DIR / f"{bundle['product']}.joblib")


def load_models(products):
    return {p: joblib.load(config.MODEL_DIR / f"{p}.joblib") for p in products}


def score(models, snapshot):
    """lightgbm take up probability per client and product; NaN where the client already holds it or is deceased."""
    out = {}
    for product, bundle in models.items():
        p = lgbm_proba(bundle, snapshot[bundle["features"]].astype("float32"))
        skip = snapshot[f"held_{product}"].to_numpy() == 1
        if "deceased" in snapshot:
            skip |= snapshot["deceased"].to_numpy() == 1
        out[product] = np.where(skip, np.nan, p)
    return pd.DataFrame(out, index=snapshot.index).astype("float32")


def metrics_table(result):
    return pd.DataFrame(result["metrics"]).set_index("product")


def write_tables(result, out_dir=None):
    out = out_dir or config.TABLE_DIR
    out.mkdir(parents=True, exist_ok=True)
    table = metrics_table(result)
    table.round(4).to_csv(out / "propensity_metrics.csv")
    result["calibration"].round(5).to_csv(out / "calibration_points.csv", index=False)
    result["calibration_bands"].round(5).to_csv(out / "calibration_bands.csv", index=False)
    return table
