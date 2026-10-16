"""figures for the data layer: product uptake, change flags, the synthetic review dates."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from client_brief_agent import config
from client_brief_agent.data import synthetic
from client_brief_agent.features import build
from client_brief_agent.report import style


def change_flag_table(brief):
    share = brief[build.CHANGE_FLAGS].mean()
    table = pd.DataFrame({"flag": share.index, "n_clients": brief[build.CHANGE_FLAGS].sum().astype(int).values,
                          "share": share.values})
    config.TABLE_DIR.mkdir(parents=True, exist_ok=True)
    table.round(6).to_csv(config.TABLE_DIR / "change_flag_prevalence.csv", index=False)
    return table


def fig_product_uptake(table):
    t = table.sort_values("test_positives")
    fig, ax = plt.subplots(figsize=(7.5, 6))
    colours = [style.BLUE if m else style.SLATE for m in t["modelled"]]
    # log scale, otherwise direct debit hides the rare products completely
    ax.barh(t["label"], t["test_positives"].clip(lower=0.8), color=colours)
    ax.set_xscale("log")
    ax.axvline(config.MIN_TEST_POSITIVES, color=style.FLAG, lw=1.2, ls=":")
    ax.text(config.MIN_TEST_POSITIVES * 1.1, 0, f"min {config.MIN_TEST_POSITIVES} test take ups",
            color=style.FLAG, fontsize=8, va="bottom")
    ax.set_xlabel(f"take ups in the test month ({config.TEST_TARGET}), log scale")
    ax.set_title("Product take ups in the sample (blue = modelled)")
    ax.grid(axis="y", visible=False)
    return style.save(fig, "product_uptake")


def fig_change_flags(table):
    t = table.sort_values("share")
    labels = [f.replace("flag_", "").replace("_", " ") for f in t["flag"]]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.barh(labels, t["share"] * 100, color=style.BLUE)
    for y, (s, n) in enumerate(zip(t["share"], t["n_clients"])):
        ax.text(s * 100, y, f"  {s * 100:.1f}% ({n:,})", va="center", fontsize=8, color=style.INK_SOFT)
    ax.set_xlabel(f"share of brief clients (history up to {build.shift_month(config.BRIEF_TARGET, -1)}), %")
    ax.set_title("Recent change flags")
    ax.set_xlim(0, t["share"].max() * 130)
    ax.grid(axis="y", visible=False)
    return style.save(fig, "change_flag_prevalence")


def fig_synthetic_layer(layer):
    meeting = pd.Timestamp(config.MEETING_DATE)
    days = (layer["next_kyc_review"] - meeting).dt.days
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw={"width_ratios": [2, 1]})
    bins = np.arange(days.min() // 30 * 30, days.max() + 30, 30)
    ax1.hist(days, bins=bins, color=style.BLUE_SOFT)
    ax1.axvspan(days.min(), config.REVIEW_WINDOW_DAYS, color=style.FLAG, alpha=0.15, zorder=0)
    ax1.axvline(0, color=style.FLAG, lw=1)
    ax1.set_xlabel(f"days from meeting ({config.MEETING_DATE}) to next review")
    ax1.set_ylabel("clients")
    ax1.set_title("Synthetic review dates (shaded = due or overdue)")
    classes = list(config.KYC_CLASS_PROBS)
    due = [(days[layer["kyc_risk_class"] == c] <= config.REVIEW_WINDOW_DAYS).mean() * 100 for c in classes]
    ax2.bar(classes, due, color=[style.BLUE, style.AMBER, style.FLAG])
    ax2.set_ylabel(f"% due within {config.REVIEW_WINDOW_DAYS} days")
    ax2.set_title("Due soon, by risk class")
    ax2.grid(axis="x", visible=False)
    return style.save(fig, "synthetic_review_due")


def make_all(frames=None, layer=None):
    """writes the data tables and the three figures, returns the figure paths."""
    style.apply()
    frames = frames if frames is not None else build.get_training_frames()
    if layer is None:
        layer = synthetic.make_synthetic_layer(frames["brief"].index.to_numpy())
    synthetic.write_summary(layer)
    return {
        "product_uptake": fig_product_uptake(build.write_product_uptake(frames)),
        "change_flag_prevalence": fig_change_flags(change_flag_table(frames["brief"])),
        "synthetic_review_due": fig_synthetic_layer(layer),
    }
