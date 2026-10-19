"""the follow up draft: a template that can only say what the brief says."""
from client_brief_agent.agent import branches, follow_up


def test_never_names_a_held_back_product():
    text = follow_up.draft("1 June 2016", products=["Credit card", "Current account"], held_back=["Credit card"])
    assert "credit card" not in text.lower() and "current account" in text


def test_support_names_no_product():
    text = follow_up.draft("1 June 2016", products=["Current account"], flows=["Salary paid into the account"],
                           support=True)
    assert "current account" not in text and "salary" not in text and "here to help" in text


def test_every_answer_has_a_draft_without_internal_notes():
    facts = {"review_due": True, "review_days": 30, "change_flags": ["flag_dropped_products"],
             "changes": {"flag_dropped_products": "Closed 2 products in the last three months."},
             "might_help": ["current_account"], "top": None, "meeting": "1 June 2016",
             "brief_now": {"suggest": ["Current account"], "flows": [], "credit": [], "held_back": []}}
    for card in branches.cards(facts):
        for a in card["answers"]:
            assert a["follow_up"].startswith("Hello,")
            for note in a["outcome"]["notes"]:
                assert note not in a["follow_up"]
            if not a["outcome"]["suggest"]:
                assert "current account" not in a["follow_up"]
