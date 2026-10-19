"""export: docs/data.json for the page, one markdown brief per showcase client, and the agent tables.

everything here is deterministic: same inputs, same bytes out. no timestamps.
"""
import json

import numpy as np
import pandas as pd

from client_brief_agent import config
from client_brief_agent.agent import branches, run, steps, suitability, tools

SOURCE = "Santander Product Recommendation data (public, anonymised, Kaggle)"
SYNTHETIC_NOTE = ("KYC risk class, review dates, risk profile and vulnerability are synthetic, "
                  "generated for this prototype independently of the real data.")


def to_plain(obj):
    """plain python types only, floats rounded to 4 dp, keys as strings."""
    if isinstance(obj, dict):
        return {str(k): to_plain(v) for k, v in obj.items()}
    if isinstance(obj, pd.DataFrame):
        return to_plain(obj.to_dict(orient="records"))
    if isinstance(obj, pd.Series):
        return to_plain(obj.to_dict())
    if isinstance(obj, (list, tuple, set, np.ndarray)):
        items = sorted(obj) if isinstance(obj, set) else obj
        return [to_plain(v) for v in items]
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    if isinstance(obj, (int, np.integer)):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        return None if np.isnan(obj) else round(float(obj), 4)
    if isinstance(obj, pd.Timestamp):
        return obj.strftime("%Y-%m-%d")
    if obj is None or obj is pd.NaT:
        return None
    return obj if isinstance(obj, str) else str(obj)


# guardrail curve, vectorised over the whole brief population

def population(ctx):
    """scored brief clients, minus the deceased: no meeting would be prepared for them."""
    dead = ctx.facts["deceased"].reindex(ctx.scores.index).fillna(False).astype(bool)
    return ctx.scores.index[~dead.to_numpy()]


def n_excluded_deceased(ctx):
    return int(len(ctx.scores.index) - len(population(ctx)))


def _count_ge(sorted_values, thresholds):
    return len(sorted_values) - np.searchsorted(sorted_values, thresholds, side="left")


def _sorted_scores(scores, mask):
    vals = scores[mask & ~np.isnan(scores)]
    return np.sort(vals)


def guardrail_curve(ctx, thresholds=None):
    """per threshold: suggestions shown (capped as in the brief), in progress, blocked, clients covered.

    n_blocked counts every blocked product above the threshold, review_overdue included; the brief
    lists at most config.MAX_BLOCKED_SHOWN and folds review only blocks into one line.
    n_in_progress: allowed linked income products for clients who already hold one of the group.
    """
    if thresholds is None:
        thresholds = config.GUARDRAIL_THRESHOLDS
    thresholds = np.asarray(thresholds, dtype=float)
    products = list(ctx.scores.columns)
    pop = population(ctx)
    facts = ctx.facts.reindex(pop)
    S = ctx.scores.loc[pop].to_numpy(dtype=float)
    B = suitability.blocked_mask(facts, products).to_numpy()
    L = tools.in_progress_mask(ctx.snapshot, products, pop).to_numpy()

    allowed = np.where(~B & ~L & ~np.isnan(S), S, -np.inf)
    top = -np.sort(-allowed, axis=1)[:, :config.MAX_SUGGESTIONS]
    curve = pd.DataFrame({"threshold": thresholds})
    curve["n_suggestions"] = sum(_count_ge(np.sort(top[:, k]), thresholds) for k in range(top.shape[1]))
    curve["n_allowed_pairs"] = _count_ge(_sorted_scores(S, ~B & ~L), thresholds)
    curve["n_in_progress"] = _count_ge(_sorted_scores(S, ~B & L), thresholds)
    curve["n_blocked"] = _count_ge(_sorted_scores(S, B), thresholds)
    curve["n_clients_with_any"] = _count_ge(np.sort(top[:, 0]), thresholds)
    blocked_best = np.where(B & ~np.isnan(S), S, -np.inf).max(axis=1) if len(products) else np.array([])
    curve["n_clients_with_blocked"] = _count_ge(np.sort(blocked_best), thresholds)
    curve["n_clients"] = len(S)

    by_rule = {r: np.zeros(len(thresholds), dtype=int) for r in suitability.RULE_NAMES}
    for j, p in enumerate(products):
        fired = suitability.rule_matrix(facts, p).to_numpy()
        for i, r in enumerate(suitability.RULE_NAMES):
            if fired[:, i].any():
                by_rule[r] += _count_ge(_sorted_scores(S[:, j], fired[:, i]), thresholds)
    rules = pd.DataFrame(by_rule)
    rules.insert(0, "threshold", thresholds)
    return curve, rules


# reviews due, from the synthetic layer

def review_days(ctx):
    syn = ctx.synthetic.reindex(population(ctx))
    days = (pd.to_datetime(syn["next_kyc_review"]) - pd.Timestamp(ctx.meeting_date)).dt.days
    return pd.DataFrame({"days_until": days, "risk_class": syn["kyc_risk_class"].astype(object)})


def review_summary(ctx, suggest_mask=None):
    rd = review_days(ctx)
    due = rd["days_until"] <= config.REVIEW_WINDOW_DAYS
    overdue = rd["days_until"] < 0
    table = (pd.DataFrame({"risk_class": rd["risk_class"], "due": due, "overdue": overdue})
             .groupby("risk_class").agg(n=("due", "size"), n_due=("due", "sum"),
                                         n_overdue=("overdue", "sum")).reset_index())
    out = {"window_days": config.REVIEW_WINDOW_DAYS, "n_clients": int(len(rd)),
           "n_due_within_window": int(due.sum()), "share_due": float(due.mean()) if len(rd) else 0.0,
           "n_overdue": int(overdue.sum()), "by_risk_class": table, "synthetic": True}
    if suggest_mask is not None:
        # meetings that would cover a review as well as a suggestion
        out["n_meetings_covering_review"] = int((due & suggest_mask.reindex(rd.index, fill_value=False)).sum())
    return out, table


# showcase selection

def _client_stats(ctx, threshold):
    products = list(ctx.scores.columns)
    facts = ctx.facts.reindex(ctx.scores.index)
    S = ctx.scores.to_numpy(dtype=float)
    B = suitability.blocked_mask(facts, products).to_numpy()
    L = tools.in_progress_mask(ctx.snapshot, products, ctx.scores.index).to_numpy()
    above = ~np.isnan(S) & (S >= threshold)
    stats = pd.DataFrame(index=ctx.scores.index)
    stats["top_allowed"] = np.where(above & ~B & ~L, S, -np.inf).max(axis=1)
    stats["top_any"] = np.where(above, S, -np.inf).max(axis=1)
    stats["n_suggest"] = (above & ~B & ~L).sum(axis=1)
    stats["top_in_progress"] = np.where(above & ~B & L, S, -np.inf).max(axis=1)
    stats["cluster"] = ctx.segments["labels"].reindex(stats.index)
    rd = review_days(ctx).reindex(stats.index)
    stats["review_due"] = (rd["days_until"] <= config.REVIEW_WINDOW_DAYS).to_numpy()
    stats["review_overdue"] = (rd["days_until"] < 0).to_numpy()
    stats["deceased"] = facts["deceased"].to_numpy()
    fired = [suitability.rule_matrix(facts, p).to_numpy() for p in products]
    for i, r in enumerate(suitability.RULE_NAMES):
        best = np.full(len(S), -np.inf)
        for j in range(len(products)):
            best = np.maximum(best, np.where(fired[j][:, i] & above[:, j], S[:, j], -np.inf))
        stats[f"rule_{r}"] = best
    for f in ["flag_new_products", "flag_dropped_products", "flag_activity_drop", "flag_moved",
              "flag_new_client", "flag_segment_change"]:
        if f in ctx.snapshot:
            stats[f] = ctx.snapshot[f].reindex(stats.index).fillna(0).to_numpy() > 0.5
    return stats.sort_index()


def _best(stats, mask, key, taken):
    pool = stats.loc[mask & ~stats.index.isin(list(taken)), key]
    pool = pool[np.isfinite(pool)]
    # idxmax returns the first maximum, and the index is sorted, so ties go to the lowest id
    return None if pool.empty else pool.idxmax()


def choose_showcase(ctx, threshold=config.DEFAULT_THRESHOLD, n=config.N_SHOWCASE, seed=config.SEED):
    """deterministic: every cluster, every rule that fires, review due cases, change flags, then fill."""
    stats = _client_stats(ctx, threshold)
    # no meeting would be prepared for a deceased client, so they never appear here
    stats = stats[~stats["deceased"] & stats["cluster"].notna()]
    picks = {}
    has = stats["n_suggest"] > 0

    def take(cid, why):
        if cid is not None and len(picks) < n:
            picks.setdefault(cid, []).append(why)

    def cover(mask, key, why, want=1):
        # a client already picked can cover a case too, then i only add what is missing
        already = [c for c in picks if mask.get(c, False)][:want]
        for c in already:
            picks[c].append(why)
        for _ in range(want - len(already)):
            take(_best(stats, mask, key, picks), why)

    for c in sorted(stats["cluster"].unique()):
        cover((stats["cluster"] == c) & has, "top_allowed", f"cluster {int(c)} example")
    for r in suitability.RULE_NAMES:
        cover(stats[f"rule_{r}"] > -np.inf, f"rule_{r}", f"shows rule {r}")
    cover(stats["review_due"] & ~stats["review_overdue"] & has, "top_allowed", "review due soon", want=3)
    cover(stats["review_overdue"], "top_any", "review overdue", want=2)
    cover(stats["top_in_progress"] > -np.inf, "top_in_progress", "linked product in progress", want=2)
    for f in [c for c in stats.columns if c.startswith("flag_")]:
        cover(stats[f] & has, "top_allowed", f"recent change {f[5:]}")
    quiet = stats.index[~has & ~stats.index.isin(list(picks))]
    if len(quiet):
        take(quiet[np.random.default_rng(seed).integers(len(quiet))], "nothing above the threshold")
    rest = stats.index[has & ~stats.index.isin(list(picks))].to_numpy()
    k = min(n - len(picks), len(rest))
    for cid in np.sort(np.random.default_rng(seed).choice(rest, size=k, replace=False)) if k > 0 else []:
        take(cid, "random fill")
    return [(int(cid), why) for cid, why in picks.items()]


# data.json sections

PROFILE_COLUMNS = ["age", "tenure_months", "n_products", "active", "log_income"]


def _cluster_profile(seg, c):
    prof = seg.get("profiles")
    if prof is None or c not in prof.index:
        return {}
    cols = [col for col in PROFILE_COLUMNS if col in prof.columns]
    return {col: round(float(prof.loc[c, col]), 2) for col in cols}


def _points(seg):
    pts = seg.get("pca_2d")
    if pts is None:
        return []
    # only coordinates and cluster go out, never the client id the sample row came from
    pts = pts.head(config.MAX_PCA_POINTS)
    return [{"x": round(float(x), 3), "y": round(float(y), 3), "cluster": int(c)}
            for x, y, c in zip(pts["x"], pts["y"], pts["cluster"])]


def segmentation_section(seg):
    sizes = pd.Series(seg.get("sizes", seg["labels"].value_counts())).sort_index()
    total = float(sizes.sum())
    clusters = [{"cluster": int(c), "name": seg["names"][c], "description": seg["descriptions"][c],
                 "size": int(sizes[c]), "share": float(sizes[c]) / total,
                 "profile": _cluster_profile(seg, c)} for c in sizes.index]
    return {"k": seg.get("k"), "silhouette": seg.get("silhouette"), "inertia": seg.get("inertia"),
            "ari_gmm": seg.get("ari_gmm"), "elbow_k": seg.get("elbow_k"), "tie_margin": config.SILHOUETTE_TIE,
            "k_range": [min(config.SEGMENT_K_RANGE), max(config.SEGMENT_K_RANGE)],
            "clusters": clusters, "points": _points(seg)}


def _importance_top5(imp):
    if imp is None:
        return None
    if isinstance(imp, pd.DataFrame) and "mean_abs_shap" in imp.columns and "importance" not in imp.columns:
        imp = imp.rename(columns={"mean_abs_shap": "importance"})
    if isinstance(imp, pd.DataFrame) and {"product", "feature", "importance"} <= set(imp.columns):
        return {p: g.nlargest(5, "importance")[["feature", "importance"]]
                for p, g in imp.groupby("product", sort=True)}
    if isinstance(imp, dict):
        return {p: pd.Series(s).nlargest(5).rename_axis("feature").reset_index(name="importance")
                for p, s in sorted(imp.items())}
    return imp


def propensity_section(ctx, extras):
    return {"products": [{"product": p, "label": config.PRODUCT_LABELS.get(p, p)} for p in ctx.scores.columns],
            "metrics": extras.get("metrics"), "calibration": extras.get("calibration"),
            "importance_top5": _importance_top5(extras.get("importance"))}


def meta_section(ctx, extras):
    meta = {"source": SOURCE, "code_url": config.CODE_URL, "sample_size": config.N_CLIENTS, "brief_population": int(len(ctx.scores)),
            "seed": config.SEED,
            "months": {"train_targets": config.TRAIN_TARGETS, "val_target": config.VAL_TARGET,
                       "test_target": config.TEST_TARGET, "brief_target": config.BRIEF_TARGET},
            "meeting_date": ctx.meeting_date, "default_threshold": config.DEFAULT_THRESHOLD,
            "review_window_days": config.REVIEW_WINDOW_DAYS, "synthetic_note": SYNTHETIC_NOTE}
    meta["n_excluded_deceased"] = n_excluded_deceased(ctx)
    meta["curve_population"] = int(len(population(ctx)))
    meta["agent_steps"] = steps.step_specs(k=ctx.segments.get("k"),
                                           n_features=extras.get("data_facts", {}).get("n_model_features"))
    meta["novelty"] = steps.NOVELTY
    meta["product_categories"] = [{"category": c, "products": ps} for c, ps in config.PRODUCT_CATEGORIES]
    meta["state_words"] = run.STATE_WORDS
    meta["money_flows"] = sorted(config.MONEY_FLOWS)
    meta["not_held"] = branches.NOT_HELD
    meta.update(extras.get("meta", {}))
    return meta


def tuning_section():
    """the saved search with every trial, or a plain statement that none has been run."""
    from client_brief_agent.models import tune
    saved = tune.load()
    if saved is None or not tune.TRIALS_PATH.exists():
        return {"run": False, "default_params": dict(config.LGBM_PARAMS)}
    trials = pd.read_csv(tune.TRIALS_PATH)
    saved = dict(saved, run=True,
                 trials={p: g.drop(columns="product").to_dict("records") for p, g in trials.groupby("product")})
    return saved


def limits_section(extras):
    """the limits, with the numbers taken from the run, never typed in."""
    facts = extras.get("data_facts", {})
    metrics = extras.get("metrics")
    out = [{"title": "Linked products and leakage",
            "text": ("Salary paid in, pension paid in and the payroll account tend to arrive together (salary and pension "
                     "start in the same month for almost every client, so the brief shows them as one signal), so part of what "
                     "those models learn is that one follows the other. The brief marks them as likely already in "
                     "progress instead of suggesting them, and keeps them in the metrics. Features only use history "
                     "up to the month before the target month, so the label never leaks into them.")},
           {"title": "The KYC layer is synthetic",
            "text": ("Review dates, risk class, risk profile and vulnerability are made up with a fixed seed, "
                     "independently of the real data. The rules and review intervals are illustrative.")}]
    if facts:
        out.append({"title": "Spanish retail data, " + facts.get("first_month", "") + " to " + facts.get("last_month", ""),
                    "text": ("The patterns come from one Spanish bank's anonymised clients in that period. They may not "
                             "hold for other markets, products or years, and the score says nothing about intent.")})
    if metrics is not None and len(metrics):
        m = metrics.set_index("product") if "product" in metrics else metrics
        if "plus_account" in m.index:
            r = m.loc["plus_account"]
            out.append({"title": "The plus account sample is small",
                        "text": (f"Only {int(r['n_test_pos'])} take ups in the test month. The lift over the baseline has a "
                                 f"95% interval from {r['lift_pr_auc_lo']:+.3f} to {r['lift_pr_auc_hi']:+.3f}, so it is "
                                 "not clearly better than logistic regression for this product.")})
    out.append({"title": "One test month",
                "text": f"Every metric comes from {config.TEST_TARGET} alone; another month could look different."})
    out.append({"title": "No learning from advisors yet",
                "text": (f"When an advisor records a decline, the brief does not raise that product again for "
                         f"{config.DECLINE_COOLDOWN_DAYS} days. There are no real advisors here, so the log is empty "
                         "and nothing is learned from it. With real logs, declines could become a feature or a "
                         "negative label for the models; I do not fake that with made up records.")})
    out.append({"title": "Care signals are limited",
                "text": ("The care check reads only the synthetic vulnerability flag and a drop in activity. The "
                         "data has no debts, arrears or spending, so it cannot spot over borrowing; an advisor "
                         "still has to ask.")})
    return out


def model_card_section(extras):
    return {"tuning": tuning_section(), "fairness": extras.get("fairness"), "limits": limits_section(extras)}


def rule_coverage(ctx):
    """per rule, honestly: which scored products it can touch and how many clients meet its condition.

    a rule that covers no scored product (the investment rules, when no investment product is
    modelled) still shows up here, with zero blocks.
    """
    facts = ctx.facts.reindex(population(ctx))
    out = []
    for r in suitability.RULES:
        covered = [p for p in ctx.scores.columns if r.applies(p)]
        cond = np.asarray(r.condition(facts), dtype=bool)
        out.append({"rule": r.name, "reason": r.reason, "scored_products_covered": covered,
                    "n_clients_condition_true": int(cond.sum())})
    return out


def guardrail_section(curve, rules, coverage):
    at = curve.loc[np.isclose(curve["threshold"], config.DEFAULT_THRESHOLD)].iloc[0]
    rule_at = rules.loc[np.isclose(rules["threshold"], config.DEFAULT_THRESHOLD)].iloc[0]
    blocked = [{"rule": r, "reason": suitability.RULE_REASONS[r], "n": int(rule_at[r])}
               for r in suitability.RULE_NAMES]
    return {"default_threshold": config.DEFAULT_THRESHOLD, "max_suggestions": config.MAX_SUGGESTIONS,
            "rules": coverage,
            "curve": curve, "blocked_by_rule": rules,
            "at_default": {k: (float(v) if k == "threshold" else int(v)) for k, v in at.items()},
            "blocked_by_rule_at_default": blocked}


def build_showcase(ctx, picks, threshold):
    """the page is public: each client gets a ref in showcase order, the real id never goes out."""
    out = []
    for i, (cid, why) in enumerate(picks, 1):
        ref, slug = f"Client {i:02d}", f"client_{i:02d}"
        brief = run.run_brief(ctx, cid, threshold, ref=ref)
        out.append({"client_ref": ref, "picked_for": why, "brief": brief,
                    "markdown": run.render_markdown(brief), "markdown_path": f"briefs/{slug}.md"})
    return out


def write_tables(curve, rules, review_table):
    config.TABLE_DIR.mkdir(parents=True, exist_ok=True)
    curve.round(4).to_csv(config.TABLE_DIR / "guardrail_curve.csv", index=False)
    rules.round(4).to_csv(config.TABLE_DIR / "guardrail_blocked_by_rule.csv", index=False)
    review_table.to_csv(config.TABLE_DIR / "reviews_due.csv", index=False)


def write_briefs(showcase):
    config.BRIEF_DIR.mkdir(parents=True, exist_ok=True)
    # old briefs may be named by real client id, so they all go before i write the new ones
    for old in config.BRIEF_DIR.glob("*.md"):
        old.unlink()
    for s in showcase:
        name = s["markdown_path"].split("/")[-1]
        (config.BRIEF_DIR / name).write_text(s["markdown"], encoding="utf-8")


def build_data(ctx, extras=None, make_figures=True):
    """extras: data_facts, metrics, calibration, importance, figures, meta (all optional)."""
    extras = extras or {}
    threshold = config.DEFAULT_THRESHOLD
    curve, rules = guardrail_curve(ctx)
    stats = _client_stats(ctx, threshold)
    reviews, review_table = review_summary(ctx, suggest_mask=stats["n_suggest"] > 0)
    picks = choose_showcase(ctx, threshold)
    showcase = build_showcase(ctx, picks, threshold)
    figures = dict(extras.get("figures", {}))
    if make_figures:
        from client_brief_agent.report import figures_agent
        figures.update(figures_agent.make_all(curve, rules, review_days(ctx)))
    data = {"meta": meta_section(ctx, extras), "data_facts": extras.get("data_facts", {}),
            "segmentation": segmentation_section(ctx.segments),
            "propensity": propensity_section(ctx, extras),
            "guardrail": guardrail_section(curve, rules, rule_coverage(ctx)), "reviews": reviews,
            "showcase": showcase, "figures": figures, "model_card": model_card_section(extras)}
    return to_plain(data), (curve, rules, review_table, showcase)


def write_all(ctx, extras=None, make_figures=True):
    data, (curve, rules, review_table, showcase) = build_data(ctx, extras, make_figures)
    write_tables(curve, rules, review_table)
    write_briefs(showcase)
    config.DOCS_DIR.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=1, ensure_ascii=False)
    (config.DOCS_DIR / "data.json").write_text(text + "\n", encoding="utf-8")
    return data
