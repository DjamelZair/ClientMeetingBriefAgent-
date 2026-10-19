"""the advisor log and the one rule that reads it: a recent decline holds a product back."""
from client_brief_agent import config
from client_brief_agent.agent import feedback, run, tools
from test_tools import make_ctx


def test_empty_log_changes_nothing(tmp_path):
    log = feedback.load(tmp_path / "missing.csv")
    assert len(log) == 0 and not feedback.declined(log, 102, "credit_card", config.MEETING_DATE)


def test_recent_decline_holds_the_product_back_until_the_cooldown_passes():
    ctx = make_ctx()
    before = run.run_brief(ctx, 102)
    product = before["might_help"][0]["product"]
    ctx.advisor_log = feedback.record(feedback.empty(), 102, product, "Not a priority now", "2016-04-01")
    verdict = tools.check_suitability(ctx, 102, product)
    assert not verdict["allowed"] and verdict["rules_fired"][-1]["rule"] == "declined_recently"
    after = run.run_brief(ctx, 102)
    assert product not in [m["product"] for m in after["might_help"]]
    # a decline older than the cooldown no longer counts
    ctx.advisor_log = feedback.record(feedback.empty(), 102, product, "Not a priority now", "2015-01-01")
    assert tools.check_suitability(ctx, 102, product)["allowed"]
    ctx.advisor_log = None


def test_only_decline_answers_count():
    log = feedback.record(feedback.empty(), 7, "credit_card", "Open to talking about it", "2016-05-01")
    assert not feedback.declined(log, 7, "credit_card", config.MEETING_DATE)
