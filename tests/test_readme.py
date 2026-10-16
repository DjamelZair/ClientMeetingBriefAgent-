"""the readme block is generated, so it only needs to stay well formed and dash free."""
from client_brief_agent.agent.tools import has_dash
from client_brief_agent.report import readme


def test_update_replaces_only_the_block(tmp_path):
    data = tmp_path / "data.json"
    data.write_text('{"meta": {"seed": 42}, "data_facts": {"raw_rows": 10, "raw_clients": 2, "raw_months": 3,'
                    ' "sample_clients": 2, "n_products_modelled": 1, "n_products_raw": 2},'
                    ' "segmentation": {"k": 2, "ari_gmm": 0.5},'
                    ' "propensity": {"products": [{"product": "a", "label": "A"}], "metrics": [{"product": "a",'
                    ' "n_test_pos": 5, "logreg_pr_auc": 0.1, "lgbm_pr_auc": 0.2, "lift_pr_auc": 0.1,'
                    ' "lift_pr_auc_lo": 0.05, "lift_pr_auc_hi": 0.15, "lgbm_roc_auc": 0.9}]},'
                    ' "guardrail": {"at_default": {"threshold": 0.1, "n_suggestions": 3, "n_clients_with_any": 2,'
                    ' "n_blocked": 1, "n_in_progress": 1}},'
                    ' "reviews": {"n_due_within_window": 1, "share_due": 0.5, "window_days": 90, "n_overdue": 0,'
                    ' "n_meetings_covering_review": 1}}')
    md = tmp_path / "README.md"
    md.write_text(f"before\n{readme.START}\nold\n{readme.END}\nafter\n")
    out = readme.update(data, md)
    assert out.startswith("before\n") and out.endswith("after\n")
    assert "\nold\n" not in out and "| A | 5 |" in out
    assert not has_dash(out)
