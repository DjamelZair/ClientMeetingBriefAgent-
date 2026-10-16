"""monthly snapshots: features from history up to T-1, labels from T.

nothing at or after the target month touches a feature. the only thing T is used for is the label,
and to keep clients who are still around at T (otherwise the label is meaningless).
"""
import numpy as np
import pandas as pd

from client_brief_agent import config

PRODUCT_CODES = list(config.PRODUCT_COLUMNS.values())
WINDOW = 6  # months of history i look back over for adds, drops, moves
SEGMENTS = ["top", "individual", "student"]
CHANNEL_COLUMNS = [f"channel_{c.lower()}" for c in config.CHANNEL_FEATURES]
HELD_COLUMNS = [f"held_{c}" for c in PRODUCT_CODES]
LABEL_COLUMNS = [f"label_{c}" for c in PRODUCT_CODES]

CHANGE_FLAGS = ["flag_new_products", "flag_dropped_products", "flag_activity_drop",
                "flag_moved", "flag_new_client", "flag_segment_change"]
FEATURE_COLUMNS = (["age", "income", "log_income", "income_missing", "tenure_months"]
                   + [f"segment_{s}" for s in SEGMENTS]
                   + ["active", "primary", "employee", "foreign_birth", "sex_male"]
                   + CHANNEL_COLUMNS + ["province"] + HELD_COLUMNS
                   + ["n_products", "adds_3m", "drops_3m", "adds_6m", "drops_6m",
                      "months_observed", "active_3m_ago"]
                   + CHANGE_FLAGS)
# compact profile for clustering, the held_* picked are the common everyday products
SEGMENT_FEATURES = (["age", "log_income", "tenure_months", "n_products", "active"]
                    + [f"segment_{s}" for s in SEGMENTS]
                    + ["held_current_account", "held_particular_account", "held_online_account",
                       "held_direct_debit", "held_payroll_account", "held_credit_card"]
                    + ["adds_6m", "drops_6m"])
# raw values with NaN kept, for anything that shows a number to a person
RAW_COLUMNS = ["age_raw", "income_raw", "tenure_raw"]
SPLITS = {"val": config.VAL_TARGET, "test": config.TEST_TARGET, "brief": config.BRIEF_TARGET}


def shift_month(month, k):
    return str(pd.Period(month, "M") + k)


def snapshot_path(name):
    return config.INTERIM_DIR / f"snap_{name}.parquet"


def top_channels(panel, month=config.CHANNEL_REFERENCE_MONTH, n=len(config.CHANNEL_FEATURES)):
    """recomputes the channel list in config, only as a check."""
    ch = panel.loc[panel["month"] == month, "channel"].astype(object)
    return list(ch[ch != "other"].value_counts().index[:n])


def _month_frames(hist, clients, months):
    # one frame per month, aligned on the same clients; absent clients are NaN rows
    cols = PRODUCT_CODES + ["province", "segment", "active"]
    out = {}
    for m in months:
        sub = hist.loc[hist["month"] == m, ["client_id"] + cols].set_index("client_id")
        out[m] = sub.reindex(clients)
    return out


def _history_features(frames, months):
    held = np.stack([frames[m][PRODUCT_CODES].to_numpy(dtype=np.float32) for m in months])
    step = held[1:] - held[:-1]  # NaN wherever the client is missing in either month
    adds, drops = (step == 1), (step == -1)
    prov = pd.DataFrame({m: frames[m]["province"] for m in months})
    seg = pd.DataFrame({m: frames[m]["segment"].astype(object).map(
        {s: i for i, s in enumerate(SEGMENTS)}).astype(float) for m in months})
    three_ago = frames[months[-4]]["active"]
    now = frames[months[-1]]["active"]
    return pd.DataFrame({
        "adds_3m": adds[-3:].sum(axis=(0, 2)), "drops_3m": drops[-3:].sum(axis=(0, 2)),
        "adds_6m": adds.sum(axis=(0, 2)), "drops_6m": drops.sum(axis=(0, 2)),
        "active_3m_ago": three_ago.fillna(0).to_numpy(),
        "flag_activity_drop": ((three_ago == 1) & (now == 0)).to_numpy(),
        "flag_moved": (prov.max(axis=1) != prov.min(axis=1)).to_numpy(),
        "flag_segment_change": (seg.max(axis=1) != seg.min(axis=1)).to_numpy(),
    }, index=frames[months[-1]].index)


def _profile_features(base):
    # medians come from the same T-1 month, so imputation never looks forward
    income = base["income"].fillna(base["income"].median())
    feats = pd.DataFrame(index=base.index)
    feats["age"] = base["age"].fillna(base["age"].median())
    feats["income"] = income
    feats["log_income"] = np.log1p(income)
    feats["income_missing"] = base["income"].isna()
    feats["tenure_months"] = base["tenure_months"].fillna(base["tenure_months"].median())
    for s in SEGMENTS:
        feats[f"segment_{s}"] = base["segment"] == s
    for col in ["active", "primary", "employee", "foreign_birth"]:
        feats[col] = base[col]
    # santander codes sex as H and V; i read V as varon (male), the dataset does not document it
    feats["sex_male"] = base["sex"] == "V"
    channel = base["channel"].astype(object)
    for code, col in zip(config.CHANNEL_FEATURES, CHANNEL_COLUMNS):
        feats[col] = channel == code
    feats["province"] = base["province"].fillna(-1)
    for code in PRODUCT_CODES:
        feats[f"held_{code}"] = base[code]
    feats["n_products"] = base[PRODUCT_CODES].sum(axis=1)
    return feats


def _labels(panel, target_month, base):
    cur = panel.loc[panel["month"] == target_month, ["client_id"] + PRODUCT_CODES]
    cur = cur.set_index("client_id").reindex(base.index)
    taken = (cur.to_numpy() == 1) & (base[PRODUCT_CODES].to_numpy() == 0)
    return pd.DataFrame(taken.astype(np.int8), index=base.index, columns=LABEL_COLUMNS)


def build_snapshot(panel, target_month):
    """features at target_month from months <= target_month - 1; labels only if the month is in the data."""
    last = shift_month(target_month, -1)
    hist = panel[panel["month"] <= last]
    base = hist[hist["month"] == last].set_index("client_id")
    has_label = (panel["month"] == target_month).any()
    if has_label:
        base = base[base.index.isin(panel.loc[panel["month"] == target_month, "client_id"])]
    base = base.sort_index()
    months = [shift_month(last, -k) for k in range(WINDOW, -1, -1)]
    frames = _month_frames(hist, base.index, months)
    feats = _profile_features(base).join(_history_features(frames, months))
    feats["months_observed"] = hist.groupby("client_id").size().reindex(base.index)
    feats["flag_new_products"] = feats["adds_3m"] > 0
    feats["flag_dropped_products"] = feats["drops_3m"] > 0
    feats["flag_new_client"] = base["tenure_months"] <= 6
    feats = feats[FEATURE_COLUMNS].astype(np.float32)
    feats[CHANGE_FLAGS] = feats[CHANGE_FLAGS].astype(np.int8)
    feats["age_raw"] = base["age"]
    feats["income_raw"] = base["income"]
    feats["tenure_raw"] = base["tenure_months"]
    feats["target_month"] = target_month
    feats["deceased"] = base["deceased"].astype(np.int8)
    if has_label:
        feats = feats.join(_labels(panel, target_month, base))
    feats.index.name = "client_id"
    return feats


def build_training_frames(panel, cache=True):
    """train stacks the config train targets; val, test and brief are single months."""
    check = top_channels(panel)
    if check and check != config.CHANNEL_FEATURES:
        print(f"note: top channels at {config.CHANNEL_REFERENCE_MONTH} are now {check}")
    frames = {"train": pd.concat([build_snapshot(panel, t) for t in config.TRAIN_TARGETS])}
    for name, target in SPLITS.items():
        frames[name] = build_snapshot(panel, target)
    if cache:
        config.INTERIM_DIR.mkdir(parents=True, exist_ok=True)
        for name, frame in frames.items():
            frame.to_parquet(snapshot_path(name))
    return frames


def get_training_frames(panel=None, force=False):
    """load the cached snapshots, or build them (loading the panel if needed)."""
    names = ["train", *SPLITS]
    if not force and all(snapshot_path(n).exists() for n in names):
        return {n: pd.read_parquet(snapshot_path(n)) for n in names}
    if panel is None:
        from client_brief_agent.data.load import get_panel
        panel = get_panel()
    return build_training_frames(panel)


def product_uptake(frames):
    """positives per split, and base rate among clients who did not hold the product at T-1."""
    rows = []
    for code in PRODUCT_CODES:
        row = {"product": code, "label": config.PRODUCT_LABELS[code]}
        for split in ["train", "val", "test"]:
            f = frames[split]
            eligible = f[f"held_{code}"] == 0
            pos = int(f.loc[eligible, f"label_{code}"].sum())
            row[f"{split}_eligible"] = int(eligible.sum())
            row[f"{split}_positives"] = pos
            row[f"{split}_base_rate"] = pos / max(int(eligible.sum()), 1)
        row["modelled"] = (row["test_positives"] >= config.MIN_TEST_POSITIVES
                           and row["train_positives"] >= config.MIN_TRAIN_POSITIVES)
        rows.append(row)
    return pd.DataFrame(rows)


def modelled_products(frames):
    table = product_uptake(frames)
    return table.loc[table["modelled"], "product"].tolist()


def write_product_uptake(frames):
    table = product_uptake(frames)
    config.TABLE_DIR.mkdir(parents=True, exist_ok=True)
    table.round(6).to_csv(config.TABLE_DIR / "product_uptake.csv", index=False)
    return table
