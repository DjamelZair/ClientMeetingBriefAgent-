"""figures for segmentation, propensity and explanations."""
import numpy as np
import matplotlib.pyplot as plt

from client_brief_agent import config
from client_brief_agent.report import style


def pretty(feature):
    if feature.startswith("held_"):
        code = feature[5:]
        return "holds " + config.PRODUCT_LABELS.get(code, code).lower()
    return feature.replace("_", " ")


def label(product):
    return config.PRODUCT_LABELS.get(product, product)


def silhouette_by_k(seg):
    ks = sorted(seg["silhouette"])
    fig, ax = plt.subplots(figsize=(6, 3.4))
    ax.plot(ks, [seg["silhouette"][k] for k in ks], marker="o", color=style.BLUE)
    ax.scatter([seg["k"]], [seg["silhouette"][seg["k"]]], s=90, color=style.FLAG, zorder=3, label=f"chosen k = {seg['k']}")
    ax.set(xlabel="number of clusters k", ylabel="silhouette (sampled)", title="Silhouette by k")
    ax.set_xticks(ks)
    ax.legend()
    return style.save(fig, "segment_silhouette")


def elbow(seg):
    ks = sorted(seg["inertia"])
    fig, ax = plt.subplots(figsize=(6, 3.4))
    ax.plot(ks, [seg["inertia"][k] for k in ks], marker="o", color=style.BLUE)
    ax.axvline(seg["elbow_k"], color=style.SLATE, ls=":", label=f"elbow k = {seg['elbow_k']}")
    ax.axvline(seg["k"], color=style.FLAG, ls="--", label=f"chosen k = {seg['k']}")
    ax.set(xlabel="number of clusters k", ylabel="inertia", title="Elbow check")
    ax.set_xticks(ks)
    ax.legend()
    return style.save(fig, "segment_elbow")


def cluster_pca(seg):
    pts = seg["pca_2d"]
    fig, ax = plt.subplots(figsize=(6.5, 5))
    for c in sorted(pts["cluster"].unique()):
        sub = pts[pts["cluster"] == c]
        ax.scatter(sub["x"], sub["y"], s=6, alpha=0.6, color=style.CLUSTER_COLOURS[c % 10],
                   label=f"{c}: {seg['names'][c]}")
    ax.set(xlabel="principal component 1", ylabel="principal component 2", title="Clusters in two dimensions")
    ax.legend(markerscale=3, fontsize=8, loc="best")
    return style.save(fig, "segment_pca")


def cluster_heatmap(seg):
    z = seg["zprofiles"]
    fig, ax = plt.subplots(figsize=(1 + 0.55 * z.shape[1], 1 + 0.5 * z.shape[0]))
    lim = max(1.0, float(np.nanmax(np.abs(z.to_numpy()))))
    im = ax.imshow(z.to_numpy(), cmap="RdBu_r", vmin=-lim, vmax=lim, aspect="auto")
    ax.set_xticks(range(z.shape[1]), [pretty(f) for f in z.columns], rotation=60, ha="right")
    ax.set_yticks(range(z.shape[0]), [f"{c}: {seg['names'][c]}" for c in z.index])
    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            ax.text(j, i, f"{z.iat[i, j]:.1f}", ha="center", va="center", fontsize=7, color=style.INK)
    ax.grid(False)
    ax.set_title("Cluster profiles (z score against all clients)")
    fig.colorbar(im, ax=ax, shrink=0.8)
    return style.save(fig, "segment_profiles")


def _auc_panel(ax, table, metric, title):
    y = np.arange(len(table))
    for off, model, colour, name in [(-0.18, "logreg", style.SLATE, "logistic regression"),
                                     (0.18, "lgbm", style.BLUE, "LightGBM")]:
        mid = table[f"{model}_{metric}"]
        err = [mid - table[f"{model}_{metric}_lo"], table[f"{model}_{metric}_hi"] - mid]
        ax.errorbar(mid, y + off, xerr=err, fmt="o", color=colour, ms=4, capsize=2, label=name)
    if metric == "pr_auc":
        ax.scatter(table["base_rate"], y, marker="|", s=80, color=style.FLAG, label="base rate")
    ax.set_yticks(y, [label(p) for p in table.index])
    ax.invert_yaxis()
    ax.set(title=title, xlabel=metric.replace("_", " ").upper())


def auc_comparison(table):
    t = table.sort_values("lgbm_pr_auc", ascending=False)
    fig, axes = plt.subplots(1, 2, figsize=(11, 0.45 * len(t) + 1.8), sharey=True)
    _auc_panel(axes[0], t, "roc_auc", "ROC AUC on the test month")
    _auc_panel(axes[1], t, "pr_auc", "PR AUC on the test month")
    axes[1].set_xscale("log")
    axes[1].legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8)
    return style.save(fig, "propensity_auc")


def calibration_grid(calib, table, model="lgbm"):
    products = list(table.sort_values("lgbm_pr_auc", ascending=False).index)
    cols = 4
    rows = int(np.ceil(len(products) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(3 * cols, 2.8 * rows), squeeze=False)
    for ax, p in zip(axes.flat, products):
        pts = calib[(calib["product"] == p) & (calib["model"] == model)]
        top = max(pts["mean_pred"].max(), pts["observed"].max()) * 1.1
        ax.plot([0, top], [0, top], color=style.RULE, lw=1)
        ax.plot(pts["mean_pred"], pts["observed"], marker="o", ms=3, color=style.BLUE)
        b = table.loc[p]
        ax.set_title(f"{label(p)}\nbrier {b['lgbm_brier']:.4f}", fontsize=9)
        ax.set_xlabel("predicted", fontsize=8)
        ax.set_ylabel("observed", fontsize=8)
    for ax in list(axes.flat)[len(products):]:
        ax.axis("off")
    fig.suptitle("LightGBM on the test month: predicted against observed (10 quantile bins)", color=style.BLUE,
                 fontweight="bold", x=0.01, ha="left")
    fig.tight_layout()
    return style.save(fig, "propensity_calibration")


def global_importance_fig(importance, products, top_n=10):
    fig, axes = plt.subplots(1, len(products), figsize=(4.2 * len(products), 0.32 * top_n + 1.5), squeeze=False)
    for ax, p in zip(axes[0], products):
        imp = importance[importance["product"] == p].nlargest(top_n, "mean_abs_shap")
        ax.barh([pretty(f) for f in imp["feature"]][::-1], imp["mean_abs_shap"].to_numpy()[::-1], color=style.BLUE)
        ax.set(title=label(p), xlabel="mean |SHAP| (log odds)")
    fig.tight_layout()
    return style.save(fig, "shap_global")


def make_all(seg=None, table=None, calib=None, importance=None, shap_products=None):
    style.apply()
    paths = {}
    if seg is not None:
        paths.update(segment_silhouette=silhouette_by_k(seg), segment_elbow=elbow(seg),
                     segment_pca=cluster_pca(seg), segment_profiles=cluster_heatmap(seg))
    if table is not None:
        paths["propensity_auc"] = auc_comparison(table)
        if calib is not None:
            paths["propensity_calibration"] = calibration_grid(calib, table)
    if importance is not None:
        if shap_products is None:
            shap_products = list(table.nlargest(3, "n_test_pos").index) if table is not None else \
                sorted(importance["product"].unique())[:3]
        paths["shap_global"] = global_importance_fig(importance, shap_products)
    return paths
