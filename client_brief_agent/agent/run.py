"""run_brief: call the tools in a fixed order, log every call, assemble the five parts.

the agent only prepares. the advisor reads the brief and decides what, if anything, to raise.
"""
import pandas as pd

from client_brief_agent import config
from client_brief_agent.agent import tools
from client_brief_agent.wording import tenure_phrase

NOTE = ("Prepared to support the conversation. Scores are estimates, not instructions; "
        "the advisor decides what to discuss.")
SYNTHETIC_NOTE = "Review dates come from a synthetic layer made for this prototype, not real records."


NEXT_STEP_OVERDUE = "Complete the periodic review first, then discuss new products."
IN_PROGRESS_LABEL = "Likely already in progress"


class ToolLog:
    """every call is logged. with a ref, the log shows the ref and never the real client id."""

    def __init__(self, ref=None):
        self.entries = []
        self.ref = ref

    def call(self, name, fn, ctx, summarise, **args):
        result = fn(ctx, **args)
        plain_args = {}
        for k, v in args.items():
            if k == "cid":
                plain_args["client"] = self.ref if self.ref is not None else int(v)
            else:
                plain_args[k] = v
        self.entries.append({"step": len(self.entries) + 1, "tool": name,
                             "args": plain_args, "summary": summarise(result)})
        return result


def pct(p):
    return f"{round(p * 100)}%"


def nice_date(iso):
    d = pd.Timestamp(iso)
    return f"{d.day} {d.strftime('%B %Y')}"


def _n(count, noun):
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def _summ_profile(r):
    age = "age not recorded" if r["age"] is None else f"aged {int(r['age'])}"
    held = "no products held" if r["n_products"] == 0 else f"{_n(r['n_products'], 'product')} held"
    return f"{age}, {held}"


def _summ_propensities(r):
    if not r:
        return "no products left to score"
    top = r[0]
    return f"{_n(len(r), 'product')} scored, highest {top['label']} ({tools.score_display(top['probability'])})"


def _summ_suitability(r):
    return "allowed" if r["allowed"] else "blocked by " + ", ".join(x["rule"] for x in r["rules_fired"])


def _summ_review(r):
    if r["next_review"] is None:
        return "no review date on file"
    state = r["status"].replace("_", " ")
    return f"{state}, next review {r['next_review']} ({r['days_until']} days)"


def _who(log, ctx, cid):
    profile = log.call("get_profile", tools.get_profile, ctx, _summ_profile, cid=cid)
    seg = log.call("get_segment", tools.get_segment, ctx,
                   lambda r: f"cluster {r['cluster']}, {r['name']}", cid=cid)
    changes = log.call("get_recent_changes", tools.get_recent_changes, ctx,
                       lambda r: _n(len(r["flags"]), "change flag") if r["flags"] else "no change flags",
                       cid=cid)
    return {"cluster": seg["cluster"], "cluster_name": seg["name"],
            "cluster_description": seg["description"], "profile": profile,
            "change_flags": changes["flags"], "changes": changes["sentences"]}


def _only_review(entry):
    return entry["rules"] == ["review_overdue"]


def _screen(log, ctx, cid, threshold):
    """every product above the threshold goes through suitability, then the linked product check."""
    scored = log.call("get_propensities", tools.get_propensities, ctx, _summ_propensities,
                      cid=cid, top_n=None)
    might, blocked, in_progress = [], [], []
    for item in (s for s in scored if s["probability"] >= threshold):
        verdict = log.call("check_suitability", tools.check_suitability, ctx,
                           lambda r, p=item["label"]: f"{p}: {_summ_suitability(r)}",
                           cid=cid, product=item["product"])
        entry = tools.describe_score(ctx, item)
        if not verdict["allowed"]:
            entry["rules"] = [x["rule"] for x in verdict["rules_fired"]]
            entry["reasons"] = [x["reason"] for x in verdict["rules_fired"]]
            blocked.append(entry)
            continue
        if item["product"] in config.LINKED_INCOME_PRODUCTS:
            linked = log.call("check_linked", tools.check_linked, ctx,
                              lambda r, p=item["label"]: f"{p}: {'in progress' if r['in_progress'] else 'not linked'}",
                              cid=cid, product=item["product"])
            if linked["in_progress"]:
                in_progress.append(dict(entry, sentence=linked["sentence"]))
                continue
        might.append(entry)
    might = might[:config.MAX_SUGGESTIONS]
    for entry in might:
        entry["reasons"] = list(ctx.reasons(cid, entry["product"]))
    # products held back only by the overdue review are counted, not listed one by one
    waiting = sum(1 for b in blocked if _only_review(b))
    listed = [b for b in blocked if not _only_review(b)][:config.MAX_BLOCKED_SHOWN]
    return might, in_progress, listed, waiting


def _due(log, ctx, cid):
    r = log.call("check_review_due", tools.check_review_due, ctx, _summ_review,
                 cid=cid, meeting_date=ctx.meeting_date)
    if r["next_review"] is None:
        sentence = "No periodic review date is on file."
    elif r["days_until"] < 0:
        sentence = (f"The periodic client review (KYC/CDD) was due on {nice_date(r['next_review'])}, "
                    f"{-r['days_until']} days before the meeting, and is overdue.")
    elif r["due"]:
        sentence = (f"The periodic client review (KYC/CDD) is due on {nice_date(r['next_review'])}, "
                    f"{r['days_until']} days after the meeting.")
    else:
        sentence = (f"No periodic review is due within {config.REVIEW_WINDOW_DAYS} days; "
                    f"the next one is on {nice_date(r['next_review'])}.")
    return dict(r, sentence=sentence, note=SYNTHETIC_NOTE)


def run_brief(ctx, cid, threshold=config.DEFAULT_THRESHOLD, ref=None):
    """ref, when given, replaces the client id everywhere in the output (public showcase)."""
    log = ToolLog(ref)
    who = _who(log, ctx, cid)
    might, in_progress, blocked, waiting = _screen(log, ctx, cid, threshold)
    due = _due(log, ctx, cid)
    overdue = due["status"] == "overdue"
    facts = {"review_due": due["due"], "change_flags": who["change_flags"],
             "might_help": [m["product"] for m in might]}
    questions = log.call("draft_questions", tools.draft_questions, ctx,
                         lambda r: f"{_n(len(r), 'question')} drafted", facts=facts)
    brief = {"client_ref": ref} if ref is not None else {"client_id": int(cid)}
    brief.update({"meeting_date": ctx.meeting_date, "threshold": float(threshold),
                  "next_step": NEXT_STEP_OVERDUE if overdue else None,
                  "who": who, "might_help": might, "in_progress": in_progress,
                  "not_to_offer": blocked, "waiting_for_review": waiting, "due_anyway": due,
                  "questions": questions, "note": NOTE, "tool_log": log.entries})
    return brief


def _md_who(who):
    lines = ["## 1. Who this client is", "",
             f"**{who['cluster_name']}** (cluster {who['cluster']}): {who['cluster_description'].rstrip('.')}.", ""]
    p = who["profile"]
    bits = ["age not recorded" if p["age"] is None else f"aged {int(p['age'])}",
            tenure_phrase(p["tenure_months"]) or "tenure not recorded",
            "income not recorded" if p["income"] is None else f"recorded income about {p['income']:,.0f}"]
    if p["segment"]:
        bits.append(f"{p['segment']} segment")
    n = p["n_products"]
    bits.append("holds no products" if n == 0 else f"holds {n} product" + ("" if n == 1 else "s"))
    held = ", ".join(tools.label(h) for h in p["held"])
    first = bits[0][0].upper() + bits[0][1:]
    lines.append(", ".join([first] + bits[1:]) + (f": {held}." if held else "."))
    lines += ["", "Recent changes:"] + ([f"- {s}" for s in who["changes"]] or
                                        ["- No notable changes in the last six months."])
    return lines


def _md_might(brief):
    lines = ["## 2. What might help", ""]
    if brief["next_step"]:
        lines += [f"**Next step:** {brief['next_step']}", ""]
    if not brief["might_help"] and brief["in_progress"]:
        lines.append(f"Nothing new to suggest above {pct(brief['threshold'])}.")
    elif not brief["might_help"] and not brief["next_step"]:
        lines.append(f"Nothing scores above {pct(brief['threshold'])} after the suitability check.")
    for m in brief["might_help"]:
        # shap says what the score leans on, not why the client would want it, so i word it that way
        why = "; ".join(r.rstrip(".") for r in m["reasons"]) or "no single feature stands out"
        lines.append(f"- **{m['label']}**, scores {m['score_display']}. {m['band_sentence']} "
                     f"The score leans on: {why}.")
    if brief["in_progress"]:
        lines += ["", f"{IN_PROGRESS_LABEL}:"]
        lines += [f"- **{m['label']}**, scores {m['score_display']}. {m['sentence']}"
                  for m in brief["in_progress"]]
    while lines[-1] == "":
        lines.pop()
    return lines


def _md_not(brief):
    lines = ["## 3. What not to offer", ""]
    for b in brief["not_to_offer"]:
        # the overdue review is said once, below, rather than on every line
        reasons = [text for rule, text in zip(b["rules"], b["reasons"])
                   if not (brief["next_step"] and rule == "review_overdue")]
        lines.append(f"- **{b['label']}** (scores {b['score_display']}) is held back. " + " ".join(reasons))
    if brief["waiting_for_review"]:
        lines.append(f"New products wait until the review is done ({brief['waiting_for_review']} would "
                     "otherwise score above the threshold).")
    if len(lines) == 2:
        lines.append("No high scoring product was held back by the suitability check.")
    return lines


def render_markdown(brief):
    due = brief["due_anyway"]
    who_ref = brief.get("client_ref") or f"client {brief['client_id']}"
    lines = [f"# Meeting brief: {who_ref}", "",
             f"Meeting on {nice_date(brief['meeting_date'])}. {brief['note']}", ""]
    lines += _md_who(brief["who"]) + [""] + _md_might(brief) + [""] + _md_not(brief) + [""]
    lines += ["## 4. Due anyway", "", due["sentence"], ""]
    if brief["next_step"]:
        lines += [f"**Next step:** {brief['next_step']}", ""]
    lines += [f"*{due['note']}*", ""]
    lines += ["## 5. Questions to open with", ""]
    lines += [f"{i}. {q}" for i, q in enumerate(brief["questions"], 1)] + [""]
    lines += ["## How this brief was prepared", ""]
    lines += [f"{e['step']}. `{e['tool']}`: {e['summary']}" for e in brief["tool_log"]]
    return "\n".join(lines) + "\n"
