"""runs the whole thing end to end: raw parquet in, docs/data.json, figures, tables and briefs out.

python main.py            rebuilds everything from the raw files (about ten minutes here)
python main.py --reuse    reuses the cached panel, snapshots and models, handy while editing the page
"""
import argparse
import time

from client_brief_agent import config
from client_brief_agent.agent import tools
from client_brief_agent.data import load, synthetic
from client_brief_agent.features import build
from client_brief_agent.models import explain, propensity, segment
from client_brief_agent.report import export, figures, readme


def step(msg, t0):
    print(f"[{time.time() - t0:6.0f}s] {msg}", flush=True)


def data_facts(frames, products, panel_rows):
    facts = load.raw_facts()
    facts.update({
        "sample_clients": int(len(frames["brief"])),
        "panel_rows": int(panel_rows),
        "train_rows": int(len(frames["train"])), "val_rows": int(len(frames["val"])),
        "test_rows": int(len(frames["test"])),
        "n_products_raw": len(config.PRODUCT_COLUMNS), "n_products_modelled": len(products),
        "modelled_products": products,
        "n_model_features": len(propensity.model_features()),
        "excluded_features": config.EXCLUDED_FEATURES,
        "income_missing_share": float(frames["brief"]["income_missing"].mean()),
    })
    return facts


def main(reuse=False):
    t0 = time.time()
    config.TABLE_DIR.mkdir(parents=True, exist_ok=True)
    panel = load.get_panel(force=not reuse)
    panel_rows = len(panel)
    frames = build.get_training_frames(panel=panel, force=not reuse)
    # the panel is only needed to build the snapshots, i free it before training
    del panel
    products = build.modelled_products(frames)
    step(f"frames ready, modelled products: {products}", t0)

    brief = frames["brief"]
    layer = synthetic.make_synthetic_layer(brief.index.to_numpy())
    seg = segment.fit_segments(brief)
    segment.write_tables(seg)
    step(f"segments: k={seg['k']}, ari vs gmm {seg['ari_gmm']:.4f}", t0)

    if reuse and all((config.MODEL_DIR / f"{p}.joblib").exists() for p in products):
        # metrics come from the last full run's tables in this mode, so i say so loudly
        print("reusing saved models and their metric tables", flush=True)
        import pandas as pd
        models = propensity.load_models(products)
        metrics = pd.read_csv(config.TABLE_DIR / "propensity_metrics.csv", index_col="product")
        calib = pd.read_csv(config.TABLE_DIR / "calibration_points.csv")
        bands = pd.read_csv(config.TABLE_DIR / "calibration_bands.csv")
    else:
        result = propensity.train_all(frames, products)
        metrics = propensity.write_tables(result)
        models, calib, bands = result["models"], result["calibration"], result["calibration_bands"]
    step("propensity models ready", t0)

    importance = explain.write_importance(explain.global_importance(models, frames["test"]))
    fig_paths = figures.make_all(frames, layer, seg, metrics, calib, importance)
    step("figures written", t0)

    ctx = tools.Context(snapshot=brief, segments=seg, scores=propensity.score(models, brief),
                        reasons=explain.reasons_provider(models, brief), synthetic=layer,
                        bands=bands)
    extras = {
        "data_facts": data_facts(frames, products, panel_rows),
        "metrics": metrics.reset_index(),
        "calibration": {"quantile": calib[calib["model"].isin(["lgbm", "logreg"])], "bands": bands},
        "importance": importance,
        "figures": fig_paths,
        # the knobs behind the rules, so the page can quote them instead of hard coding them
        "meta": {"rules": {"min_band_clients": config.MIN_BAND_CLIENTS, "score_display_cap": config.SCORE_DISPLAY_CAP,
                           "min_test_positives": config.MIN_TEST_POSITIVES,
                           "min_train_positives": config.MIN_TRAIN_POSITIVES,
                           "kyc_interval_years": config.KYC_INTERVAL_YEARS},
                 "product_labels": config.PRODUCT_LABELS},
    }
    data = export.write_all(ctx, extras)
    step(f"docs/data.json written, {len(data['showcase'])} showcase briefs in {config.BRIEF_DIR}", t0)
    readme.update()
    step("readme results block refreshed from data.json", t0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse", action="store_true", help="reuse cached panel, snapshots and models")
    main(parser.parse_args().reuse)
