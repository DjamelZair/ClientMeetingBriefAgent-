"""run_brief: the five parts, the tool log, and the rule that fit beats score."""
import json

import numpy as np

import pytest

from client_brief_agent import config
from client_brief_agent.agent import run, tools
from test_tools import make_ctx

TOOL_NAMES = {"get_profile", "get_segment", "get_recent_changes", "get_propensities",
              "check_suitability", "check_linked", "check_care", "check_review_due", "draft_questions"}


@pytest.fixture(scope="module")
def ctx():
    return make_ctx()


@pytest.fixture(scope="module")
def briefs(ctx):
    return {cid: run.run_brief(ctx, cid) for cid in ctx.snapshot.index}


def test_brief_shape(briefs):
    b = briefs[101]
    assert set(b) == {"client_id", "meeting_date", "threshold", "next_step", "who", "might_help",
                      "in_progress", "not_to_offer", "waiting_for_review", "due_anyway", "questions",
                      "question_cards", "holdings", "ranked", "care", "follow_up", "note", "tool_log"}
    assert b["who"]["cluster_name"] == "Settled everyday savers"
    assert 2 <= len(b["questions"]) <= config.MAX_QUESTIONS
    json.dumps(b)


def test_tool_log_shape(briefs):
    for b in briefs.values():
        log = b["tool_log"]
        assert [e["step"] for e in log] == list(range(1, len(log) + 1))
        for e in log:
            assert set(e) == {"step", "tool", "args", "summary"}
            assert e["tool"] in TOOL_NAMES and isinstance(e["summary"], str) and e["summary"]
        assert log[0]["tool"] == "get_profile" and log[-1]["tool"] == "draft_questions"
        json.dumps(log)


def test_every_candidate_is_checked(briefs, ctx):
    b = briefs[102]
    checked = [e["args"]["product"] for e in b["tool_log"] if e["tool"] == "check_suitability"]
    assert checked == ["credit_card", "term_deposit", "investment_fund"]


def test_blocked_never_suggested(briefs, ctx):
    for cid, b in briefs.items():
        shown = {m["product"] for m in b["might_help"]}
        for m in b["might_help"]:
            assert tools.check_suitability(ctx, cid, m["product"])["allowed"]
            assert m["probability"] >= b["threshold"]
        assert not shown & {x["product"] for x in b["not_to_offer"]}
        probs = [m["probability"] for m in b["might_help"]]
        assert probs == sorted(probs, reverse=True)


def test_specific_cases(briefs):
    assert [m["product"] for m in briefs[101]["might_help"]] == ["credit_card", "investment_fund", "pension_plan"]
    assert briefs[101]["might_help"][0]["score_display"] == "35%"
    assert briefs[101]["might_help"][0]["band"]["n"] == 20
    assert briefs[101]["might_help"][0]["reasons"] == ["already pays bills by direct debit", "aged 40"]
    assert briefs[101]["due_anyway"]["due"] is True

    b102 = briefs[102]
    assert [m["product"] for m in b102["might_help"]] == ["term_deposit"]
    blocked = {x["product"]: x for x in b102["not_to_offer"]}
    assert blocked["credit_card"]["rules"] == ["credit_activity_drop"]
    assert blocked["investment_fund"]["rules"] == ["investment_no_risk_profile"]

    assert [m["product"] for m in briefs[103]["might_help"]] == ["online_account"]
    # overdue review, vulnerable and cautious: nothing is suggested. term deposit is held back only
    # by the review, so it is counted rather than listed
    b104 = briefs[104]
    assert b104["might_help"] == [] and b104["next_step"] == run.NEXT_STEP_OVERDUE
    assert [x["product"] for x in b104["not_to_offer"]] == ["credit_card", "investment_account"]
    assert b104["waiting_for_review"] == 1
    assert briefs[101]["next_step"] is None and briefs[101]["waiting_for_review"] == 0
    assert briefs[105]["might_help"] == []
    assert briefs[107]["might_help"] == [] and briefs[107]["not_to_offer"] == []


def test_threshold_moves_the_cut(ctx):
    b = run.run_brief(ctx, 101, threshold=0.3)
    assert [m["product"] for m in b["might_help"]] == ["credit_card"]


def test_due_anyway_is_labelled_synthetic(briefs):
    for b in briefs.values():
        assert b["due_anyway"]["synthetic"] is True and "synthetic" in b["due_anyway"]["note"]
    assert "overdue" in briefs[104]["due_anyway"]["sentence"]
    assert briefs[108]["due_anyway"]["sentence"] == "No periodic review date is on file."


def test_markdown(briefs):
    for b in briefs.values():
        md = run.render_markdown(b)
        for h in ["## 1. Who this client is", "## 2. What might help", "## 3. What not to offer",
                  "## 4. Due anyway", "## 5. Questions to open with"]:
            assert h in md
        assert not tools.has_dash(md)
        assert " sell" not in md.lower() and "target" not in md.lower()
    assert "1 June 2016" in run.render_markdown(briefs[101])


def test_missing_raw_age_says_not_recorded():
    c = make_ctx()
    c.snapshot["age_raw"] = c.snapshot["age"]
    c.snapshot.loc[101, "age_raw"] = np.nan
    md = run.render_markdown(run.run_brief(c, 101))
    assert "Age not recorded" in md and "aged 40" not in md.split("## 2.")[0]
    assert "sex" not in md.lower() and "birth" not in md.lower()


def test_overdue_and_due_soon_read_differently(briefs):
    assert "is overdue" in briefs[104]["due_anyway"]["sentence"]
    assert "is due on" in briefs[101]["due_anyway"]["sentence"]


def test_linked_products_are_in_progress_not_suggested(briefs):
    b = briefs[108]
    assert [m["product"] for m in b["might_help"]] == ["online_account"]
    assert [m["product"] for m in b["in_progress"]] == ["payroll_account", "pension_deposit"]
    assert b["in_progress"][0]["score_display"] == "above 50%"
    assert b["in_progress"][0]["sentence"].startswith("The client already has")
    md = run.render_markdown(b)
    assert "Likely already in progress:" in md
    assert "- **Payroll account**, scores above 50%." in md
    assert "60%" not in md


def test_score_lines_use_bands(briefs):
    md = run.render_markdown(briefs[108])
    assert ("- **Online account**, scores above 50%. In the test month, 75% of the 270 clients "
            "scoring between 50% and 100% took it up. The score leans on:") in md
    md101 = run.render_markdown(briefs[101])
    assert "**Credit card**, scores 35%. Too few clients scored in this range" in md101


def test_overdue_next_step_in_sections_2_and_4(briefs):
    md = run.render_markdown(briefs[104])
    sec2 = md.split("## 2.")[1].split("## 3.")[0]
    sec3 = md.split("## 3.")[1].split("## 4.")[0]
    sec4 = md.split("## 4.")[1].split("## 5.")[0]
    assert sec2.split("\n", 1)[1].strip().startswith("**Next step:** Complete the periodic review first")
    assert "Next step" in sec4
    assert "New products wait until the review is done (1 would otherwise score above the threshold)." in sec3
    assert "Term deposit" not in sec3 and "review is overdue" not in sec3


def test_ref_replaces_client_id(ctx):
    b = run.run_brief(ctx, 102, ref="Client 07")
    assert "client_id" not in b and b["client_ref"] == "Client 07"
    assert all(e["args"]["client"] == "Client 07" for e in b["tool_log"] if e["tool"] != "draft_questions")
    md = run.render_markdown(b)
    assert md.startswith("# Meeting brief: Client 07") and "102" not in md


def test_zero_tenure_reads_as_new():
    from client_brief_agent.wording import tenure_phrase
    assert tenure_phrase(0) == "joined this month"
    assert tenure_phrase(1) == "with the bank for 1 month"
    assert tenure_phrase(30) == "with the bank for 2 years"
    assert tenure_phrase(float("nan")) is None


def test_holdings_cover_every_product_once(briefs):
    for b in briefs.values():
        codes = [p["product"] for c in b["holdings"] for p in c["products"] if p["product"]]
        assert sorted(codes) == sorted(config.PRODUCT_COLUMNS.values())
        held = set(b["who"]["profile"]["held"])
        states = {p["product"]: p["state"] for c in b["holdings"] for p in c["products"] if p["product"]}
        assert {p for p, s in states.items() if s == "held"} == held
        assert {m["product"] for m in b["might_help"]} == {p for p, s in states.items() if s == "suggested"}
        insurance = next(c for c in b["holdings"] if c["category"] == "Insurance")
        assert insurance["products"][0]["state"] == "not_in_data"


def test_question_cards_match_the_question_texts(briefs):
    for b in briefs.values():
        assert b["questions"] == [c["text"] for c in b["question_cards"]]
        for c in b["question_cards"]:
            assert c["why"] and all(a["outcome_line"] for a in c["answers"])


def test_money_flows_are_marked_and_same_signals_shown_once(briefs):
    for b in briefs.values():
        shown = [m["product"] for m in b["might_help"]]
        for m in b["might_help"]:
            assert m["kind"] == ("flow" if m["product"] in config.MONEY_FLOWS else "product")
        for p, partner in config.SAME_SIGNAL.items():
            assert not (p in shown and partner in shown)


def test_mismatch_is_said_plainly():
    assert run._mismatch({"n_products": 1}, 3.9) == ("Grouped with clients who hold 3.9 products on average, "
                                                    "but holds 1 product now.")
    assert run._mismatch({"n_products": 3}, 3.9) is None
    assert run._mismatch({"n_products": 1}, None) is None
