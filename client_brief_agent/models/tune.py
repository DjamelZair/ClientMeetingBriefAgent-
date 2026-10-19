"""hyperparameter search for the lightgbm models, on the validation month only.

optuna's tpe sampler with a fixed seed. trial 0 is always my current default setting, so the search is
compared against what i had, on the same rows. each trial trains on a fixed random share of the training
rows (config.TUNING_TRAIN_ROWS) to keep it affordable here, stops early on the validation month and is
scored by validation pr auc. the test month is never touched. a product only switches to its tuned
setting when that beat the default on validation; the final model is then refitted on all training rows
by propensity.train_all, which reads the saved choice.

    python -m client_brief_agent.models.tune
"""
import json
import time

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from client_brief_agent import config
from client_brief_agent.models.propensity import eligible, model_features

TRIALS_PATH = config.TABLE_DIR / "tuning_trials.csv"
SEARCHED = ["learning_rate", "num_leaves", "min_child_samples", "subsample", "colsample_bytree", "reg_lambda"]


def _space(trial):
    return {"learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            "num_leaves": trial.suggest_int("num_leaves", 15, 255, log=True),
            "min_child_samples": trial.suggest_int("min_child_samples", 20, 2000, log=True),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.4, 1.0),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 30.0, log=True)}


def full_params(searched):
    """the searched values on top of the fixed ones (number of trees, bagging every round)."""
    return dict(config.LGBM_PARAMS, **searched)


def _sample(X, y, n, seed):
    if len(y) <= n:
        return X, y
    idx = np.sort(np.random.default_rng(seed).choice(len(y), size=n, replace=False))
    return X.iloc[idx], y[idx]


def tune_product(frames, product, features=None, n_trials=config.TUNING_TRIALS, seed=config.SEED):
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    features = model_features(features)
    X_tr, y_tr = eligible(frames["train"], product, features)
    X_tr, y_tr = _sample(X_tr, y_tr, config.TUNING_TRAIN_ROWS, seed)
    X_va, y_va = eligible(frames["val"], product, features)

    def objective(trial):
        params = full_params(_space(trial))
        model = lgb.LGBMClassifier(**params, n_jobs=config.N_JOBS, random_state=seed, verbose=-1)
        model.fit(X_tr, y_tr, eval_set=[(X_va, y_va)], eval_metric="binary_logloss",
                  callbacks=[lgb.early_stopping(config.EARLY_STOPPING_ROUNDS, verbose=False)])
        trial.set_user_attr("best_iteration", int(model.best_iteration_))
        p = model.predict_proba(X_va, num_iteration=model.best_iteration_)[:, 1]
        return float(average_precision_score(y_va, p))

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=seed))
    # trial 0 is the setting i used before the search
    study.enqueue_trial({k: config.LGBM_PARAMS[k] for k in SEARCHED})
    t0 = time.time()
    study.optimize(objective, n_trials=n_trials)
    trials = pd.DataFrame([{"product": product, "trial": t.number, "val_pr_auc": t.value,
                            "best_iteration": t.user_attrs.get("best_iteration"), **t.params}
                           for t in study.trials])
    default, best = study.trials[0], study.best_trial
    use_tuned = best.number != 0 and best.value > default.value
    choice = {"product": product, "n_trials": len(study.trials), "train_rows_per_trial": int(len(y_tr)),
              "val_pr_auc_default": float(default.value), "val_pr_auc_best": float(best.value),
              "best_trial": int(best.number), "chosen": "tuned" if use_tuned else "default",
              "params": {k: (best.params if use_tuned else default.params)[k] for k in SEARCHED},
              "seconds": round(time.time() - t0, 1)}
    return choice, trials


def tune_all(frames, products, n_trials=config.TUNING_TRIALS, seed=config.SEED, verbose=True):
    choices, tables = {}, []
    for product in products:
        choice, trials = tune_product(frames, product, n_trials=n_trials, seed=seed)
        choices[product] = choice
        tables.append(trials)
        if verbose:
            print(f"{product}: default {choice['val_pr_auc_default']:.4f} best {choice['val_pr_auc_best']:.4f} "
                  f"-> {choice['chosen']} ({choice['seconds']}s)", flush=True)
    save(choices, pd.concat(tables, ignore_index=True), n_trials, seed)
    return choices


def save(choices, trials, n_trials, seed):
    config.TABLE_DIR.mkdir(parents=True, exist_ok=True)
    trials.round(5).to_csv(TRIALS_PATH, index=False)
    out = {"method": "optuna tpe", "seed": seed, "n_trials": n_trials, "objective": "validation pr auc",
           "validation_month": config.VAL_TARGET, "train_rows_per_trial": config.TUNING_TRAIN_ROWS,
           "searched": SEARCHED, "fixed": {k: v for k, v in config.LGBM_PARAMS.items() if k not in SEARCHED},
           "products": choices}
    config.TUNED_PARAMS_PATH.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")


def load():
    """the saved search, or None when no search has been run yet."""
    if not config.TUNED_PARAMS_PATH.exists():
        return None
    return json.loads(config.TUNED_PARAMS_PATH.read_text(encoding="utf-8"))


def params_for(product):
    """the lightgbm setting train_all uses: the tuned one when the search chose it, otherwise my default."""
    saved = load()
    choice = (saved or {}).get("products", {}).get(product)
    if choice and choice["chosen"] == "tuned":
        return full_params(choice["params"]), "tuned"
    return dict(config.LGBM_PARAMS), "default"


if __name__ == "__main__":
    from client_brief_agent.features import build
    frames = build.get_training_frames()
    tune_all(frames, build.modelled_products(frames))
