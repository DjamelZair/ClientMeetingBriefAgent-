"""questions with a reason and answer branches, as plain rules.

every question the agent drafts says why it is asked (the exact signal from the data) and offers two or
three likely answers. each answer carries a small list of effects, and apply() works out what the brief
would then suggest, hold back or note. no model decides a branch: the effects are written out here so a
reviewer can read every one of them.

effects:
  ("pause", reason)          every suggestion moves to held back with this reason
  ("hold_credit", reason)    credit suggestions move to held back with this reason
  ("remove_top", reason)     the top suggestion is dropped from the brief, the reason goes in the notes
  ("review", text)           an action for the periodic review
  ("note", text)             a note for the advisor
"""
from client_brief_agent import config
from client_brief_agent.agent import follow_up

KIND_REVIEW, KIND_CHANGE, KIND_TOPIC, KIND_OPEN = "Periodic review", "Recent change", "Top suggestion", "Open"
KIND_CARE = "Care first"
CARE_QUESTION = "How are you managing with your money at the moment?"

# questions about the client's situation, not a product pitch
CHANGE_QUESTIONS = {
    "review_due": "Has anything changed in your work, income or home since we last updated your details?",
    "flag_activity_drop": "You use your account less than you used to. Has something changed in how you manage your money?",
    "flag_moved": "You moved recently. Is everything at your new address set up the way you need it?",
    "flag_new_client": "How have your first months with us gone, and is anything not set up yet?",
    "flag_dropped_products": "Some of your products with us were closed recently. How are those needs covered now?",
    "flag_new_products": "You started using something new with us recently. How is it working for you?",
    "flag_segment_change": "Your situation with us has changed recently. Do your accounts still fit how you live now?",
}

TOPIC_QUESTIONS = {
    "current_account": "How do you handle your everyday payments at the moment?",
    "particular_account": "How do you handle your everyday payments at the moment?",
    "online_account": "How do you prefer to do your banking: in a branch, online or on your phone?",
    "credit_card": "How do you usually pay for larger purchases?",
    "direct_debit": "How do you keep track of your regular bills?",
    "salary_deposit": "How do you prefer to handle your income and regular payments?",
    "payroll_account": "How do you prefer to handle your income and regular payments?",
    "pension_deposit": "How is your pension income arranged at the moment?",
    "tax_account": "How do you handle tax payments and official charges?",
    "term_deposit": "Is there money you would like to set aside for a fixed period?",
    "investment_fund": "How do you think about saving for the longer term?",
    "investment_account": "How do you think about saving for the longer term?",
    "pension_plan": "How are you preparing for retirement?",
    "plus_account": "How do you like to keep money you are not spending right away?",
    "particular_plus_account": "How do you like to keep money you are not spending right away?",
    "mortgage": "Are there any plans around your home coming up?",
    "personal_loan": "Are there any larger costs coming up that you are planning for?",
}

# what "not held here" means in words, so the reason names the real signal
NOT_HELD = {
    "salary_deposit": "This client's salary is not paid into this bank.",
    "payroll_account": "This client's salary is not paid into this bank.",
    "pension_deposit": "This client has no pension paid into this bank.",
    "direct_debit": "This client has no direct debits set up here.",
    "online_account": "This client has no online account here yet.",
    "credit_card": "This client has no credit card with this bank.",
}

OPEN_QUESTIONS = ["What matters most to you financially over the next year?",
                  "Is there anything about your banking you would like to make simpler?"]

NO_CHANGE = []
# recording a decline feeds the one rule in feedback.py, so the next brief does not raise it again too soon
DECLINE_NOTE = f"Record it as declined: the brief will not raise {{top}} again for {config.DECLINE_COOLDOWN_DAYS} days."

ANSWERS = {
    # the care question comes before anything else; an answer about money troubles stops every suggestion
    "care": [
        ("Things are tight", [("pause", "Money is tight, so offer support rather than new products."),
                              ("note", "Explain where help is available and agree a follow up.")]),
        ("Would rather not say", [("pause", "The client did not want to talk about money, so no product push in this meeting."),
                                  ("note", "Leave the door open and mention where help is available.")]),
        ("Managing fine", [("note", "Record that the client says they are managing.")]),
    ],
    "review_due": [
        ("My income changed", [("hold_credit", "Income needs updating in the review first."),
                               ("review", "Update income in the periodic review.")]),
        ("I moved home", [("review", "Update the address in the periodic review.")]),
        ("Nothing has changed", [("review", "Confirm the details and complete the review in this meeting.")]),
    ],
    "flag_dropped_products": [
        ("Moved to another bank", [("pause", "Products moved to another bank, so no product push in this meeting."),
                                   ("note", "Ask what made them move and record it for the advisor.")]),
        ("No longer needed", NO_CHANGE),
        ("Something went wrong", [("pause", "Resolve the complaint before suggesting anything."),
                                  ("note", "Log the complaint and agree a follow up.")]),
    ],
    "flag_activity_drop": [
        ("I bank elsewhere now", [("pause", "Day to day banking moved elsewhere, so no product push."),
                                  ("note", "Record where the client banks now.")]),
        ("Money is tighter", [("pause", "Money is tight, so offer support rather than new products."),
                              ("note", "Check for signs of financial difficulty and explain where help is available.")]),
        ("Nothing in particular", NO_CHANGE),
    ],
    "flag_moved": [
        ("Details still need updating", [("review", "Update the address and any regular payments.")]),
        ("All set", NO_CHANGE),
    ],
    "flag_new_client": [
        ("Something is missing", [("note", "Find out what is missing and set it up before anything new.")]),
        ("All going well", NO_CHANGE),
    ],
    "flag_new_products": [
        ("It works well", NO_CHANGE),
        ("Having trouble with it", [("pause", "Sort out the new product first, no further suggestions now."),
                                    ("note", "Help with the set up.")]),
    ],
    "flag_segment_change": [
        ("My work or studies changed", [("hold_credit", "Work and income need updating first."),
                                        ("review", "Update work and income details.")]),
        ("Nothing has changed", NO_CHANGE),
    ],
    "topic": [
        ("Open to talking about it", [("note", "Discuss {top} if the client wants to.")]),
        ("Already arranged elsewhere", [("remove_top", "{top} is arranged at another bank."),
                                        ("note", "Record where it is arranged and do not raise {top} again in this meeting."),
                                        ("note", DECLINE_NOTE)]),
        ("Not a priority now", [("remove_top", "{top} is not a priority for the client now."),
                                ("note", DECLINE_NOTE)]),
    ],
    "open": [
        ("Raises something specific", [("note", "Record what the client raises; the brief has no data on it.")]),
        ("Nothing in particular", NO_CHANGE),
    ],
}


def _review_why(facts):
    days = facts.get("review_days")
    if days is None:
        return "Periodic review due (synthetic date)."
    if days < 0:
        return f"Periodic review overdue by {-days} day{'' if days == -1 else 's'} (synthetic date)."
    return f"Periodic review due in {days} day{'' if days == 1 else 's'} (synthetic date)."


def _topic_why(top):
    # the kind label already says "top suggestion", so the reason only names the product and the evidence
    sentence = top["band_sentence"]
    if "took it up" in sentence:
        why = sentence.replace("took it up", f"took up {top['label'].lower()}")
    else:
        why = f"{top['label']}: {sentence[:1].lower() + sentence[1:]}"
    extra = NOT_HELD.get(top["product"])
    return f"{why} {extra}" if extra else why


def pick(facts):
    """the questions in priority order: due review, recent changes, top suggestion, then open questions.
    returns (key, kind, text, why) tuples; at most config.MAX_QUESTIONS, at least two."""
    picked = []
    if facts.get("care"):
        picked.append(("care", KIND_CARE, CARE_QUESTION, " ".join(facts.get("care_signals", []))))
    if facts.get("review_due"):
        picked.append(("review_due", KIND_REVIEW, CHANGE_QUESTIONS["review_due"], _review_why(facts)))
    changes = facts.get("changes", {})
    for key in CHANGE_QUESTIONS:
        # the care question already covers an activity drop, so i do not ask about it twice
        if key == "flag_activity_drop" and facts.get("care"):
            continue
        if key in facts.get("change_flags", []) and len(picked) < 2:
            picked.append((key, KIND_CHANGE, CHANGE_QUESTIONS[key], changes.get(key, "")))
    top = facts.get("top")
    if top and len(picked) < config.MAX_QUESTIONS and top["product"] in TOPIC_QUESTIONS:
        picked.append(("topic", KIND_TOPIC, TOPIC_QUESTIONS[top["product"]], _topic_why(top)))
    for text in OPEN_QUESTIONS:
        if len(picked) >= 2:
            break
        picked.append(("open", KIND_OPEN, text,
                       "No due review, recent change or suggestion to start from, so an open question."))
    return picked[:config.MAX_QUESTIONS]


def apply(effects, brief_now, top_label=None):
    """what the brief becomes after one answer. brief_now: {"suggest": [labels], "credit": [labels],
    "held_back": [{"label", "reason"}]}. returns the new suggest, held back, notes and review actions."""
    suggest = list(brief_now["suggest"])
    held = [dict(h) for h in brief_now["held_back"]]
    notes, review = [], []
    for op, text in effects:
        text = text.replace("{top}", top_label or "the top suggestion")
        if op == "pause":
            held += [{"label": s, "reason": text} for s in suggest]
            suggest = []
        elif op == "hold_credit":
            moving = [s for s in suggest if s in brief_now.get("credit", [])]
            held += [{"label": s, "reason": text} for s in moving]
            suggest = [s for s in suggest if s not in moving]
        elif op == "remove_top":
            if top_label in suggest:
                suggest.remove(top_label)
                notes.append(text)
        elif op == "review":
            review.append(text)
        elif op == "note":
            notes.append(text)
        else:
            raise ValueError(f"unknown effect {op}")
    changed = suggest != brief_now["suggest"] or len(held) != len(brief_now["held_back"])
    return {"suggest": suggest, "held_back": held, "notes": notes, "review": review, "changes_brief": changed}


def outcome_line(result):
    """one plain sentence for the page and the markdown."""
    if not result["changes_brief"] and not result["notes"] and not result["review"]:
        return "No change to the brief."
    bits = []
    if result["changes_brief"]:
        # "still on the brief" covers offers and things worth asking about alike, so a money flow is never "suggested"
        left = result["suggest"]
        bits.append(("Still on the brief: " + (left[0] if len(left) == 1 else ", ".join(left[:-1]) + " and " + left[-1]) + ".")
                    if left else "Nothing new is raised.")
    bits += result["review"] + result["notes"]
    return " ".join(bits)


def follow_up_for(facts, result=None):
    """the follow up draft as the brief stands, or as it would stand after one answer."""
    now = facts.get("brief_now", {})
    suggest = result["suggest"] if result else now.get("suggest", [])
    flows = set(now.get("flows", []))
    held = [h["label"] for h in (result["held_back"] if result else now.get("held_back", []))]
    return follow_up.draft(facts.get("meeting", "the day of the meeting"),
                           products=[s for s in suggest if s not in flows],
                           flows=[s for s in suggest if s in flows],
                           review=bool(facts.get("review_due")) or bool(result and result["review"]),
                           # with any sign of difficulty the draft offers help and names no product
                           support=bool(facts.get("care")),
                           held_back=held)


def cards(facts, texts=None):
    """the question cards: text, kind, why, and every answer with what the brief would then do.
    texts lets a rephrased wording replace the template text without touching the rules."""
    brief_now = facts.get("brief_now", {"suggest": [], "credit": [], "held_back": []})
    top_label = facts["top"]["label"] if facts.get("top") else None
    out = []
    for i, (key, kind, text, why) in enumerate(pick(facts)):
        answers = []
        for label, effects in ANSWERS[key]:
            result = apply(effects, brief_now, top_label)
            answers.append({"answer": label, "effects": [list(e) for e in effects],
                            "outcome": result, "outcome_line": outcome_line(result),
                            "follow_up": follow_up_for(facts, result)})
        out.append({"key": key, "kind": kind, "text": texts[i] if texts else text, "why": why, "answers": answers})
    return out
