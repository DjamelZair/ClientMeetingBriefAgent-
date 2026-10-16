"""builds notebooks/walkthrough.ipynb, runs it and exports docs/notebook.html.

the notebook holds no logic of its own: every cell imports a pipeline module and calls it, so the walkthrough
can never disagree with main.py. it needs the caches from a previous `python main.py`.

    python -m client_brief_agent.report.notebook
"""
import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor

from client_brief_agent import config

NB_DIR = config.ROOT / "notebooks"
NB_PATH = NB_DIR / "walkthrough.ipynb"
HTML_PATH = config.DOCS_DIR / "notebook.html"

CELLS = [
    ("md", """# Client meeting brief agent: a walkthrough

This notebook walks through the pipeline behind the [interactive page](analysis.html), one module at a time.
There is no logic in here; every cell imports a module from `client_brief_agent/` and calls it, so what you see is
exactly what `python main.py` does. It reads the cached snapshots and models from the last full run.

Client profiles and product holdings are real public data (Kaggle Santander Product Recommendation). KYC review
dates, risk profiles and vulnerability flags are **synthetic**, made up for this prototype."""),
    ("code", """import sys
sys.path.insert(0, "..")  # the notebook lives in notebooks/, the package one level up

import pandas as pd
from IPython.display import Image, Markdown, display

from client_brief_agent import config
from client_brief_agent.features import build
from client_brief_agent.data import synthetic
from client_brief_agent.models import segment, propensity, explain
from client_brief_agent.agent import tools, run
from client_brief_agent.report import export

pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 160)"""),
    ("md", """## 1. The snapshots

For a target month T, every feature comes from history up to T minus 1 and the label is "took the product up in T".
Training stacks the target months up to March 2016, validation is April, test is May. The brief looks ahead to June
2016, which the data does not contain, so it has no labels."""),
    ("code", """frames = build.get_training_frames()
pd.DataFrame({name: {"rows": len(f), "columns": f.shape[1]} for name, f in frames.items()}).T"""),
    ("md", """A product only gets a model when the sample has enough take ups to learn from and test on. Most of the rare ones
(investment funds, pension plans, loans) do not make it, which matters later for the guardrail."""),
    ("code", """uptake = build.product_uptake(frames)
uptake[["label", "train_positives", "val_positives", "test_positives", "modelled"]]"""),
    ("code", """display(Image(str(config.FIG_DIR / "product_uptake.png"), width=640))"""),
    ("md", """## 2. The synthetic layer

No public dataset has review dates or risk profiles, so I draw them with a fixed seed, independently of the real
data. Nothing in the models reads these fields; only the guardrail and the brief do."""),
    ("code", """layer = synthetic.make_synthetic_layer(frames["brief"].index.to_numpy())
layer.drop(columns=["synthetic"]).describe(include="all").T[["count", "unique", "top", "freq"]]"""),
    ("md", """## 3. Grouping clients

k means for k from 2 to 10 on standardised features, chosen by silhouette with the elbow as a tie breaker, then a
Gaussian mixture with the same k to see whether a different method finds the same groups."""),
    ("code", """seg = segment.fit_segments(frames["brief"])
print(f"chosen k = {seg['k']}, adjusted Rand index against the Gaussian mixture = {seg['ari_gmm']:.3f}")
pd.DataFrame({"silhouette": seg["silhouette"], "inertia": seg["inertia"]}).round(4)"""),
    ("code", """pd.DataFrame({"name": seg["names"], "size": seg["sizes"], "description": seg["descriptions"]})"""),
    ("code", """display(Image(str(config.FIG_DIR / "segment_pca.png"), width=560))"""),
    ("md", """## 4. Propensity: LightGBM against a logistic regression baseline

One model per product, trained only on clients who did not hold it yet. The table is the test month with paired
bootstrap intervals for the lift."""),
    ("code", """products = build.modelled_products(frames)
models = propensity.load_models(products)
metrics = pd.read_csv(config.TABLE_DIR / "propensity_metrics.csv", index_col="product")
metrics[["n_test_pos", "logreg_pr_auc", "lgbm_pr_auc", "lift_pr_auc", "lift_pr_auc_lo", "lift_pr_auc_hi",
         "lgbm_roc_auc", "lgbm_brier", "lgbm_isotonic_brier"]].round(4)"""),
    ("md", """I tried isotonic calibration on the validation month (the `lgbm_isotonic` columns) and dropped it. The brief shows
each score next to what happened to clients in the same score band in the test month instead:"""),
    ("code", """bands = pd.read_csv(config.TABLE_DIR / "calibration_bands.csv")
bands[bands["lo"] >= 0.10][["product", "lo", "hi", "mean_pred", "observed", "n"]].round(3)"""),
    ("code", """display(Image(str(config.FIG_DIR / "propensity_calibration.png"), width=760))"""),
    ("md", """## 5. What a score leans on

SHAP contributions for LightGBM, turned into short phrases with the client's own recorded values. They describe what
moved the score, not why a client would want the product."""),
    ("code", """display(Image(str(config.FIG_DIR / "shap_global.png"), width=760))"""),
    ("md", """## 6. The agent

The agent is a fixed sequence of small tool calls, each one logged: profile, segment, recent changes, propensities,
a suitability check per product, a linked products check, the review date and the questions. Here is the brief
for the first showcase client. The page shows clients by a reference only, so I do the same here."""),
    ("code", """brief = frames["brief"]
ctx = tools.Context(snapshot=brief, segments=seg, scores=propensity.score(models, brief),
                    reasons=explain.reasons_provider(models, brief), synthetic=layer, bands=bands)
picks = export.choose_showcase(ctx)
first_id, picked_for = picks[0]
example = run.run_brief(ctx, first_id, ref="Client 01")
print("picked because:", ", ".join(picked_for))
display(Markdown(run.render_markdown(example)))"""),
    ("md", """## 7. The guardrail across every client

The same rules, vectorised over all clients, for a range of thresholds. A high score never overrides fit."""),
    ("code", """curve, rules = export.guardrail_curve(ctx)
curve[curve["threshold"].isin([0.05, 0.10, 0.20, 0.30, 0.50])]"""),
    ("code", """display(Image(str(config.FIG_DIR / "guardrail_curve.png"), width=640))"""),
    ("md", """That is the whole pipeline. The page reads all of this from `docs/data.json`, which `python main.py` writes."""),
]


def build_notebook():
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_markdown_cell(src) if kind == "md" else nbformat.v4.new_code_cell(src)
                for kind, src in CELLS]
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    return nb


def run_and_export(timeout=900):
    NB_DIR.mkdir(parents=True, exist_ok=True)
    nb = build_notebook()
    ExecutePreprocessor(timeout=timeout, kernel_name="python3").preprocess(nb, {"metadata": {"path": str(NB_DIR)}})
    nbformat.write(nb, NB_PATH)
    html, _ = HTMLExporter(template_name="lab").from_notebook_node(nb)
    HTML_PATH.write_text(html, encoding="utf-8")
    return NB_PATH, HTML_PATH


if __name__ == "__main__":
    print(run_and_export())
