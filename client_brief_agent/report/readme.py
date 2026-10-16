"""fills the results block in README.md from docs/data.json, so the readme can never quote a stale number."""
import json
import re

from client_brief_agent import config

README = config.ROOT / "README.md"
START, END = "<!-- results:start -->", "<!-- results:end -->"


def _int(v):
    return f"{int(v):,}"


def _pct(v):
    return f"{100 * v:.1f}%"


def _dec(v):
    return f"{v:.3f}"


def _lift(row, metric):
    return f"{row[f'lift_{metric}']:+.3f} [{row[f'lift_{metric}_lo']:+.3f}, {row[f'lift_{metric}_hi']:+.3f}]"


def facts_lines(d):
    f, seg = d["data_facts"], d["segmentation"]
    return [
        f"- **Data:** {_int(f['raw_rows'])} monthly rows for {_int(f['raw_clients'])} clients over "
        f"{f['raw_months']} months; I sample {_int(f['sample_clients'])} clients with seed {d['meta']['seed']}.",
        f"- **Segments:** k = {seg['k']}, adjusted Rand index against a Gaussian mixture {seg['ari_gmm']:.3f}.",
        f"- **Products modelled:** {f['n_products_modelled']} of {f['n_products_raw']}; the rest have too few take ups.",
    ]


def metrics_table(d):
    labels = {p["product"]: p["label"] for p in d["propensity"]["products"]}
    rows = sorted(d["propensity"]["metrics"], key=lambda r: -r["lgbm_pr_auc"])
    lines = ["| Product | Take ups in test | PR AUC logistic | PR AUC LightGBM | PR AUC lift [95% CI] | ROC AUC LightGBM |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {labels.get(r['product'], r['product'])} | {_int(r['n_test_pos'])} | {_dec(r['logreg_pr_auc'])} "
                     f"| {_dec(r['lgbm_pr_auc'])} | {_lift(r, 'pr_auc')} | {_dec(r['lgbm_roc_auc'])} |")
    return lines


def guardrail_lines(d):
    g, r = d["guardrail"]["at_default"], d["reviews"]
    lines = [f"- **At the default threshold of {_pct(g['threshold'])}:** {_int(g['n_suggestions'])} suggestions "
             f"for {_int(g['n_clients_with_any'])} clients; the guardrail held back {_int(g['n_blocked'])}."]
    if "n_in_progress" in g:
        lines.append(f"- **Likely already in progress** (salary, pension or payroll already arriving): "
                     f"{_int(g['n_in_progress'])}, shown separately and not as suggestions.")
    lines.append(f"- **Reviews (synthetic):** {_int(r['n_due_within_window'])} clients ({_pct(r['share_due'])}) have a "
                 f"periodic review due within {r['window_days']} days, {_int(r['n_overdue'])} of them overdue; "
                 f"{_int(r['n_meetings_covering_review'])} clients with a suggestion could cover a due review in the same meeting.")
    return lines


def results_block(d):
    return "\n".join(facts_lines(d) + ["", "Test month, clients who did not hold the product yet:", ""]
                     + metrics_table(d) + [""] + guardrail_lines(d))


def update(data_path=config.DOCS_DIR / "data.json", readme=README):
    d = json.loads(data_path.read_text(encoding="utf-8"))
    text = readme.read_text(encoding="utf-8")
    block = f"{START}\n{results_block(d)}\n{END}"
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    readme.write_text(new, encoding="utf-8")
    return new
