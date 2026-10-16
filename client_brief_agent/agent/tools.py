"""the tools the brief agent calls. plain functions over one shared Context.

each tool reads, it never writes. run.py calls them in order and logs every call.
"""
import json
import os
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

from client_brief_agent import config
from client_brief_agent.agent import suitability

# written as escapes so no dash character sits in the source itself
EM_DASH, EN_DASH = "\u2014", "\u2013"


def has_dash(text):
    return EM_DASH in text or EN_DASH in text


SEGMENT_WORDS = {"segment_top": "top tier", "segment_individual": "individual",
                 "segment_student": "student"}

# change flag -> plain sentence. counts come from the snapshot, never made up
CHANGE_SENTENCES = {
    "flag_new_products": "Took up {adds_text} in the last three months.",
    "flag_dropped_products": "Closed {drops_text} in the last three months.",
    "flag_activity_drop": "Was active three months ago and is not active now.",
    "flag_moved": "Moved to a different province in the last six months.",
    "flag_new_client": "Joined the bank in the last six months ({joined_text}).",
    "flag_segment_change": "Client segment changed in the last six months.",
}

# conversation starters, in the order i want them considered
QUESTION_TEMPLATES = {
    "review_due": ("Before we look ahead, has anything changed in your work, income or home "
                   "that we should update in your details?"),
    "flag_activity_drop": ("You seem to use your account a little less lately. Is there anything "
                           "about how you bank with us that is not working well for you?"),
    "flag_moved": ("You have moved recently. Is there anything we can help you settle, such as "
                   "addresses or regular payments?"),
    "flag_new_client": ("How have your first months with us gone, and is there anything you "
                        "expected that is not set up yet?"),
    "flag_dropped_products": ("You closed a product with us recently. Was there a reason we "
                              "should know about?"),
    "flag_new_products": ("You started using something new with us recently. How is it working "
                          "for you so far?"),
    "flag_segment_change": ("Your situation with us has changed a little recently. Are your "
                            "current accounts still a good fit for how you live now?"),
}

# what a product is about, so a question can open the topic without naming a sale
PRODUCT_TOPICS = {
    "current_account": "your everyday money",
    "online_account": "banking online or on your phone",
    "credit_card": "paying for larger purchases and spreading costs",
    "direct_debit": "keeping on top of regular bills",
    "salary_deposit": "where your salary is paid",
    "pension_deposit": "where your pension is paid",
    "payroll_account": "where your salary is paid",
    "tax_account": "paying taxes and official charges",
    "term_deposit": "money you would like to set aside for a fixed period",
    "investment_fund": "longer term saving",
    "investment_account": "investing",
    "pension_plan": "saving for retirement",
    "plus_account": "how your savings are kept",
    "particular_account": "your everyday money",
    "particular_plus_account": "how your savings are kept",
    "mortgage": "your plans for a home",
    "personal_loan": "any larger costs coming up",
}
FALLBACK_QUESTIONS = [
    "What matters most to you financially over the next year?",
    "Is there anything about your banking you would like to make simpler?",
]


@dataclass
class Context:
    """everything the tools need, built once by the integrator.

    snapshot: brief snapshot indexed by client_id (features, held_*, flags, deceased).
    segments: fit_segments() result (labels, names, descriptions, ...).
    scores: client x product lightgbm take up probability, NaN where already held.
    reasons: callable (client_id, product) -> list of plain reason strings.
    synthetic: synthetic kyc layer indexed by client_id.
    bands: optional calibration bands (product, band, lo, hi, observed, n, positives), test month.
    """
    snapshot: pd.DataFrame
    segments: dict
    scores: pd.DataFrame
    reasons: Callable[[int, str], list]
    synthetic: pd.DataFrame
    meeting_date: str = config.MEETING_DATE
    bands: pd.DataFrame = None
    facts: pd.DataFrame = field(init=False, repr=False)

    def __post_init__(self):
        self.facts = suitability.client_facts(self.snapshot, self.synthetic, self.meeting_date)


def label(product):
    return config.PRODUCT_LABELS.get(product, product.replace("_", " ").capitalize())


def _num(value):
    return None if value is None or pd.isna(value) else float(value)


def _shown(row, raw, fallback):
    """values shown to a person come from the raw column, never the imputed feature."""
    return _num(row.get(raw)) if raw in row.index else _num(row.get(fallback))


def _rounded_income(row):
    # the page is public, so income is only ever shown to the nearest thousand
    if row.get("income_missing", 0) > 0.5:
        return None
    v = _shown(row, "income_raw", "income")
    return None if v is None else float(round(v / config.INCOME_ROUNDING) * config.INCOME_ROUNDING)


def get_profile(ctx, cid):
    # sex and place of birth are never part of the profile
    row = ctx.snapshot.loc[cid]
    held = [c[len("held_"):] for c in ctx.snapshot.columns
            if c.startswith("held_") and row[c] > 0.5]
    segment = next((w for c, w in SEGMENT_WORDS.items() if c in row and row[c] > 0.5), None)
    return {
        "age": _shown(row, "age_raw", "age"),
        "income": _rounded_income(row),
        "tenure_months": _shown(row, "tenure_raw", "tenure_months"),
        "segment": segment,
        "active": bool(row.get("active", 0) > 0.5),
        "n_products": int(row.get("n_products", len(held))),
        "held": held,
    }


def get_segment(ctx, cid):
    cluster = int(ctx.segments["labels"].loc[cid])
    return {"cluster": cluster,
            "name": ctx.segments["names"][cluster],
            "description": ctx.segments["descriptions"][cluster]}


def _fmt_count(value):
    v = _num(value)
    return "some" if v is None else str(int(round(v)))


def _plural(value, noun):
    n = _fmt_count(value)
    return f"{n} {noun}" if n == "1" else f"{n} {noun}s"


def _joined_text(tenure):
    if tenure is None or pd.isna(tenure):
        return "date not recorded"
    if round(float(tenure)) == 0:
        return "this month"
    return f"{_plural(tenure, 'month')} ago"


def get_recent_changes(ctx, cid):
    row = ctx.snapshot.loc[cid]
    tenure = _shown(row, "tenure_raw", "tenure_months")
    fields = {"joined_text": _joined_text(tenure),
              "adds_text": _plural(row.get("adds_3m"), "new product"),
              "drops_text": _plural(row.get("drops_3m"), "product")}
    flags = [f for f in CHANGE_SENTENCES if f in row and row[f] > 0.5]
    return {"flags": flags, "sentences": [CHANGE_SENTENCES[f].format(**fields) for f in flags]}


def get_propensities(ctx, cid, top_n=5):
    """products not yet held, highest score first. top_n=None returns all."""
    row = ctx.scores.loc[cid].dropna()
    # ties broken by product code so the order is stable
    items = sorted(row.items(), key=lambda kv: (-float(kv[1]), kv[0]))
    if top_n is not None:
        items = items[:top_n]
    return [{"product": p, "label": label(p), "probability": float(v)} for p, v in items]


def check_suitability(ctx, cid, product):
    return suitability.check(suitability.facts_row(ctx.facts, cid), product)


def check_review_due(ctx, cid, meeting_date=None):
    meeting = pd.Timestamp(meeting_date or ctx.meeting_date)
    if cid not in ctx.synthetic.index:
        return {"due": False, "status": "unknown", "next_review": None, "days_until": None, "risk_class": None,
                "synthetic": True}
    row = ctx.synthetic.loc[cid]
    nxt = pd.Timestamp(row["next_kyc_review"])
    days = int((nxt - meeting).days)
    status = "overdue" if days < 0 else ("due_soon" if days <= config.REVIEW_WINDOW_DAYS else "not_due")
    return {"due": days <= config.REVIEW_WINDOW_DAYS, "status": status, "next_review": nxt.strftime("%Y-%m-%d"),
            "days_until": days, "risk_class": str(row["kyc_risk_class"]), "synthetic": True}


# score display and calibration bands

def score_display(p):
    return "above 50%" if p >= config.SCORE_DISPLAY_CAP else f"{round(p * 100)}%"


def _band_edges(p):
    edges = config.BAND_EDGES
    i = min(max(int(np.searchsorted(edges, p, side="right")) - 1, 0), len(edges) - 2)
    return i, edges[i], edges[i + 1]


def score_band(ctx, product, p):
    """the test month band that contains p; real counts from the bands table, never filled in."""
    i, lo, hi = _band_edges(p)
    band = {"lo": lo, "hi": hi, "n": 0, "positives": 0, "observed": None, "enough": False}
    if ctx.bands is not None:
        rows = ctx.bands[(ctx.bands["product"] == product) & (ctx.bands["band"] == i)]
        if len(rows):
            r = rows.iloc[0]
            band.update(n=int(r["n"]), positives=int(r["positives"]), observed=float(r["observed"]))
            band["enough"] = band["n"] >= config.MIN_BAND_CLIENTS
    return band


def band_sentence(band):
    if not band["enough"]:
        return "Too few clients scored in this range in the test month to check the score."
    return (f"In the test month, {round(band['observed'] * 100)}% of the {band['n']:,} clients "
            f"scoring between {round(band['lo'] * 100)}% and {round(band['hi'] * 100)}% took it up.")


def describe_score(ctx, item):
    band = score_band(ctx, item["product"], item["probability"])
    return dict(item, score_display=score_display(item["probability"]), band=band,
                band_sentence=band_sentence(band))


# linked income products

# the sentence names what the client actually has, a payroll account alone is not "salary already paid in"
LINKED_PHRASES = {"payroll_account": "a payroll account", "salary_deposit": "salary paid in",
                  "pension_deposit": "pension paid in"}


def in_progress_sentence(row):
    held = [LINKED_PHRASES.get(p, p) for p in sorted(config.LINKED_INCOME_PRODUCTS)
            if f"held_{p}" in row and row[f"held_{p}"] > 0.5]
    have = held[0] if len(held) == 1 else ", ".join(held[:-1]) + " and " + held[-1]
    return f"The client already has {have}, so this is likely already in progress rather than something to suggest."


def _holds_linked(frame_or_row):
    cols = [f"held_{p}" for p in sorted(config.LINKED_INCOME_PRODUCTS)]
    vals = [frame_or_row[c] if c in frame_or_row else 0 for c in cols]
    return np.logical_or.reduce([np.asarray(v, dtype=float) > 0.5 for v in vals])


def check_linked(ctx, cid, product):
    """is this product part of a group the client already has income flowing through?"""
    row = ctx.snapshot.loc[cid]
    linked = product in config.LINKED_INCOME_PRODUCTS and bool(_holds_linked(row))
    return {"in_progress": linked, "sentence": in_progress_sentence(row) if linked else None}


def in_progress_mask(snapshot, products, index=None):
    """clients x products, True where check_linked says in progress. vectorised twin."""
    snap = snapshot if index is None else snapshot.reindex(index)
    holds = _holds_linked(snap)
    return pd.DataFrame({p: holds & (p in config.LINKED_INCOME_PRODUCTS) for p in products},
                        index=snap.index)


def template_questions(facts):
    """two or three open questions, picked by rule from the facts."""
    keys = (["review_due"] if facts.get("review_due") else []) + list(facts.get("change_flags", []))
    picked = [QUESTION_TEMPLATES[k] for k in QUESTION_TEMPLATES if k in keys][:2]
    for product in facts.get("might_help", []):
        if len(picked) >= config.MAX_QUESTIONS:
            break
        topic = PRODUCT_TOPICS.get(product)
        q = f"What are your thoughts on {topic} at the moment?" if topic else None
        if q and q not in picked:
            picked.append(q)
            break
    for q in FALLBACK_QUESTIONS:
        if len(picked) >= 2:
            break
        picked.append(q)
    return picked[:config.MAX_QUESTIONS]


def _claude_available():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return True


def _claude_rephrase(facts, drafts):
    """optional: let claude smooth the wording. it only sees structured facts and my drafts."""
    import anthropic
    client = anthropic.Anthropic()
    system = ("You rephrase conversation starters for a bank advisor. Use only the facts given; "
              "never add facts, numbers or products. Keep the same number of questions, open and "
              "calm, British spelling, no dashes. Do not sell. Return one question per line.")
    msg = client.messages.create(
        model=config.CLAUDE_MODEL, max_tokens=400, system=system,
        messages=[{"role": "user", "content": json.dumps({"facts": facts, "drafts": drafts})}])
    lines = [ln.strip() for ln in msg.content[0].text.splitlines() if ln.strip()]
    lines = [ln.replace(EM_DASH, ", ").replace(EN_DASH, ", ") for ln in lines]
    return lines if len(lines) == len(drafts) else drafts


def draft_questions(ctx, facts, use_claude=None):
    drafts = template_questions(facts)
    if use_claude is None:
        use_claude = _claude_available()
    if not use_claude:
        return drafts
    try:
        return _claude_rephrase(facts, drafts)
    except Exception:
        # any failure falls back to the templates, the brief must still be ready
        return drafts
