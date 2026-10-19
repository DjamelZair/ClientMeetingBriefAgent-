"""the answer branches are plain rules: each answer changes the brief in a way i can read and test."""
from client_brief_agent import config
from client_brief_agent.agent import branches

NOW = {"suggest": ["Salary paid in", "Credit card"], "credit": ["Credit card"],
       "held_back": [{"label": "Personal loan", "reason": "No income is recorded."}]}


def facts(**kw):
    base = {"review_due": False, "review_days": 200, "change_flags": [], "changes": {}, "might_help": [],
            "top": None, "brief_now": NOW}
    base.update(kw)
    return base


def test_no_change_is_said_plainly():
    r = branches.apply([], NOW)
    assert r["suggest"] == NOW["suggest"] and not r["changes_brief"]
    assert branches.outcome_line(r) == "No change to the brief."


def test_pause_moves_every_suggestion_to_held_back():
    r = branches.apply([("pause", "Moved to another bank.")], NOW)
    assert r["suggest"] == [] and r["changes_brief"]
    assert [h["label"] for h in r["held_back"]] == ["Personal loan", "Salary paid in", "Credit card"]
    assert branches.outcome_line(r).startswith("Nothing new is raised.")


def test_hold_credit_only_touches_credit():
    r = branches.apply([("hold_credit", "Income needs updating first.")], NOW)
    assert r["suggest"] == ["Salary paid in"]
    assert r["held_back"][-1] == {"label": "Credit card", "reason": "Income needs updating first."}


def test_remove_top_names_the_product():
    r = branches.apply([("remove_top", "{top} is arranged at another bank.")], NOW, top_label="Salary paid in")
    assert r["suggest"] == ["Credit card"] and r["notes"] == ["Salary paid in is arranged at another bank."]


def test_review_question_comes_first_and_says_why():
    cards = branches.cards(facts(review_due=True, review_days=-35))
    assert cards[0]["key"] == "review_due" and cards[0]["kind"] == "Periodic review"
    assert cards[0]["why"] == "Periodic review overdue by 35 days (synthetic date)."


def test_moved_to_another_bank_stops_the_product_push():
    f = facts(change_flags=["flag_dropped_products"],
              changes={"flag_dropped_products": "Closed 5 products in the last three months."})
    card = branches.cards(f)[0]
    assert card["why"] == "Closed 5 products in the last three months."
    moved = next(a for a in card["answers"] if a["answer"] == "Moved to another bank")
    assert moved["outcome"]["suggest"] == [] and moved["outcome"]["notes"]
    unneeded = next(a for a in card["answers"] if a["answer"] == "No longer needed")
    assert unneeded["outcome_line"] == "No change to the brief."


def test_topic_question_is_about_the_situation_and_names_the_signal():
    top = {"product": "salary_deposit", "label": "Salary paid in",
           "band_sentence": "In the test month, 56% of the 338 clients scoring between 50% and 100% took it up."}
    card = [c for c in branches.cards(facts(top=top)) if c["key"] == "topic"][0]
    assert card["text"] == "How do you prefer to handle your income and regular payments?"
    assert card["why"] == ("In the test month, 56% of the 338 clients scoring between 50% and 100% took up salary paid in. "
                           "This client's salary is not paid into this bank.")
    elsewhere = next(a for a in card["answers"] if a["answer"] == "Already arranged elsewhere")
    assert "Salary paid in" not in elsewhere["outcome"]["suggest"]


def test_every_answer_set_has_two_or_three_answers_and_known_effects():
    for key, answers in branches.ANSWERS.items():
        assert 2 <= len(answers) <= 3, key
        for _, effects in answers:
            for op, text in effects:
                assert op in {"pause", "hold_credit", "remove_top", "review", "note"} and text.endswith(".")


def test_never_more_than_the_limit():
    f = facts(review_due=True, change_flags=["flag_moved", "flag_new_client", "flag_activity_drop"],
              top={"product": "credit_card", "label": "Credit card", "band_sentence": "x."})
    assert len(branches.cards(f)) == config.MAX_QUESTIONS


def test_care_question_comes_first_and_tight_money_stops_every_suggestion():
    f = facts(care=True, care_signals=["Account activity dropped in the last three months."],
              change_flags=["flag_activity_drop"],
              changes={"flag_activity_drop": "Account activity dropped in the last three months."})
    cards = branches.cards(f)
    assert cards[0]["key"] == "care" and cards[0]["kind"] == branches.KIND_CARE
    assert cards[0]["why"] == "Account activity dropped in the last three months."
    # the activity drop is covered by the care question, so it is not asked again
    assert "flag_activity_drop" not in [c["key"] for c in cards]
    tight = next(a for a in cards[0]["answers"] if a["answer"] == "Things are tight")
    assert tight["outcome"]["suggest"] == [] and tight["outcome"]["changes_brief"]


def test_no_care_question_without_a_signal():
    assert "care" not in [c["key"] for c in branches.cards(facts())]
