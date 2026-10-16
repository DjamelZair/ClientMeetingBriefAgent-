"""figures for the agent part: guardrail curve, blocked by rule, reviews due."""
import matplotlib.pyplot as plt
import numpy as np

from client_brief_agent import config
from client_brief_agent.agent import suitability
from client_brief_agent.report import style


def guardrail_curve(curve):
    style.apply()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(curve["threshold"], curve["n_suggestions"], color=style.BLUE, lw=2, label="suggestions shown")
    ax.plot(curve["threshold"], curve["n_clients_with_any"], color=style.BLUE_SOFT, lw=2,
            label="clients with at least one suggestion")
    ax.plot(curve["threshold"], curve["n_blocked"], color=style.FLAG, lw=2, label="held back by a rule")
    if "n_in_progress" in curve:
        ax.plot(curve["threshold"], curve["n_in_progress"], color=style.AMBER, lw=1.5, ls="--",
                label="likely already in progress")
    ax.axvline(config.DEFAULT_THRESHOLD, color=style.SLATE, ls=":", lw=1)
    ax.text(config.DEFAULT_THRESHOLD, ax.get_ylim()[1] * 0.95, " default", color=style.SLATE, va="top")
    ax.set_xlabel("score threshold")
    ax.set_ylabel("count over the brief population")
    ax.set_title("What the brief would show at each threshold")
    ax.legend()
    return style.save(fig, "guardrail_curve")


def blocked_by_rule(rules, threshold=config.DEFAULT_THRESHOLD):
    style.apply()
    row = rules.loc[np.isclose(rules["threshold"], threshold)].iloc[0]
    counts = row[suitability.RULE_NAMES].astype(int).sort_values()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(counts.index, counts.values, color=style.FLAG)
    ax.set_xlabel(f"products held back at threshold {threshold:.2f}")
    ax.set_title("Which suitability rule held a product back")
    ax.grid(axis="y", visible=False)
    return style.save(fig, "guardrail_blocked_by_rule")


def reviews_due(review_days):
    style.apply()
    days = review_days["days_until"].dropna().clip(-365, 3 * 365)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(days, bins=60, color=style.BLUE_SOFT)
    ax.axvspan(days.min() if len(days) else -365, config.REVIEW_WINDOW_DAYS, color=style.FLAG, alpha=0.12,
               label=f"due within {config.REVIEW_WINDOW_DAYS} days or overdue")
    ax.axvline(0, color=style.SLATE, ls=":", lw=1)
    ax.set_xlabel("days from the meeting to the next periodic review (synthetic)")
    ax.set_ylabel("clients")
    ax.set_title("Periodic reviews around the meeting date")
    ax.legend()
    return style.save(fig, "reviews_due")


def make_all(curve, rules, review_days):
    return {"guardrail_curve": guardrail_curve(curve),
            "guardrail_blocked_by_rule": blocked_by_rule(rules),
            "reviews_due": reviews_due(review_days)}
