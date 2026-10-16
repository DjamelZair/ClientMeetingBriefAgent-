"""client segments with k-means, plus the rules that turn a cluster profile into words."""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

from client_brief_agent import config


def segment_features(features=None):
    """same exclusion as the models: no sex or place of birth in the clusters (config.EXCLUDED_FEATURES)."""
    if features is None:
        from client_brief_agent.features.build import SEGMENT_FEATURES
        features = SEGMENT_FEATURES
    return [f for f in features if f not in config.EXCLUDED_FEATURES]


def standardise(snapshot, features):
    """median fill then z-score. k-means cannot take NaN and income is often missing."""
    raw = snapshot[features].astype("float32")
    medians = raw.median()
    filled = raw.fillna(medians)
    scaler = StandardScaler().fit(filled)
    z = scaler.transform(filled).astype("float32")
    return z, filled


def elbow_k(ks, inertia):
    """the k furthest from the straight line between the first and last point of the inertia curve."""
    x = np.asarray(ks, dtype=float)
    y = np.asarray([inertia[k] for k in ks], dtype=float)
    xn = (x - x.min()) / (x.max() - x.min())
    yn = (y - y.min()) / (y.max() - y.min() + 1e-12)
    # line from (0, 1) to (1, 0) in normalised space, so distance is proportional to 1 - xn - yn
    dist = np.abs(1.0 - xn - yn)
    return int(x[int(np.argmax(dist))])


def choose_k(silhouette, inertia, tie=config.SILHOUETTE_TIE):
    """my rule: take the highest silhouette. if other k are within `tie` of it, they count as tied
    and i take the one closest to the elbow of the inertia curve (ties again go to the higher silhouette).
    so silhouette decides and the elbow only breaks near ties."""
    ks = sorted(silhouette)
    best = max(silhouette.values())
    candidates = [k for k in ks if silhouette[k] >= best - tie]
    elbow = elbow_k(ks, inertia)
    chosen = min(candidates, key=lambda k: (abs(k - elbow), -silhouette[k]))
    return chosen, elbow


def scan_k(z_sub, ks, seed=config.SEED):
    """k-means for every k on the selection subsample, silhouette on a further sample."""
    silhouette, inertia = {}, {}
    n_sil = min(config.SILHOUETTE_SAMPLE, len(z_sub))
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(z_sub)
        inertia[k] = float(km.inertia_)
        silhouette[k] = float(silhouette_score(z_sub, km.labels_, sample_size=n_sil, random_state=seed))
    return silhouette, inertia


def gmm_agreement(z_sub, km_labels_sub, k, seed=config.SEED):
    """a gaussian mixture with the same k, to see whether the partition survives a different method."""
    gmm = GaussianMixture(n_components=k, covariance_type="full", reg_covar=1e-3, random_state=seed)
    gmm_labels = gmm.fit(z_sub).predict(z_sub)
    return float(adjusted_rand_score(km_labels_sub, gmm_labels))


def pca_sample(z, labels, index, n=config.PCA_PLOT_SAMPLE, seed=config.SEED):
    pca = PCA(n_components=2, random_state=seed).fit(z)
    rng = np.random.default_rng(seed)
    pick = rng.choice(len(z), size=min(n, len(z)), replace=False)
    xy = pca.transform(z[pick])
    return pd.DataFrame({"client_id": np.asarray(index)[pick], "x": xy[:, 0], "y": xy[:, 1],
                         "cluster": labels[pick]})


# ---------- descriptions by rule ----------

def _label(code):
    return config.PRODUCT_LABELS.get(code, code.replace("_", " ")).lower()


def a_or_an(noun):
    return ("an " if noun[:1] in "aeiou" else "a ") + noun


def _income_value(feature, mean):
    return float(np.expm1(mean)) if feature == "log_income" else float(mean)


def _window(feature):
    return {"3m": "in the last three months", "6m": "in the last six months"}.get(feature.rsplit("_", 1)[-1], "")


def _term(feature, z, mean):
    """one feature of one cluster -> (tag for the name, phrase for the description), or None to skip.
    `mean` is the cluster mean in raw units, so the phrase quotes a real number."""
    hi = z > 0
    pct = f"{100 * mean:.0f}%"
    if feature == "age":
        return ("older" if hi else "younger", f"{'older' if hi else 'younger'} (average age {mean:.0f})")
    if feature in ("income", "log_income"):
        val = _income_value(feature, mean)
        word = "higher income" if hi else "lower income"
        return (word, f"{word} (typical income {val:,.0f})")
    if feature == "tenure_months":
        years = mean / 12
        return ("long standing" if hi else "new",
                f"{'long standing' if hi else 'newer'} clients (about {years:.0f} years with the bank)"
                if years >= 1 else f"newer clients (about {mean:.0f} months with the bank)")
    if feature == "n_products":
        return ("multi product" if hi else "single product",
                f"{'many' if hi else 'few'} products ({mean:.1f} on average)")
    if feature in ("active", "active_3m_ago"):
        return ("active" if hi else "inactive", f"mostly {'active' if hi else 'inactive'} ({pct} active)")
    if feature == "sex_male":
        return ("male" if hi else "female", f"mostly {'men' if hi else 'women'} ({pct} men)")
    if feature.startswith("segment_") and hi:
        seg = feature[len("segment_"):]
        names = {"student": ("students", "mostly students"), "top": ("premium", "premium segment"),
                 "individual": ("everyday", "everyday individual segment")}
        tag, text = names.get(seg, (seg, f"mostly {seg} segment"))
        return (tag, f"{text} ({pct})")
    if feature.startswith("held_"):
        code = feature[len("held_"):]
        if hi:
            return (f"{_label(code)} holders", f"often hold {a_or_an(_label(code))} ({pct})")
        return None if mean > 0.5 else (f"no {_label(code)}", f"rarely hold {a_or_an(_label(code))} ({pct})")
    if feature.startswith("adds_") and hi:
        return ("growing", f"recently adding products (about {mean:.1f} on average {_window(feature)})")
    if feature.startswith("drops_") and hi:
        return ("shrinking", f"recently closing products (about {mean:.1f} on average {_window(feature)})")
    if feature.startswith("channel_") and hi:
        return (None, f"mostly joined via channel {feature[8:]} ({pct})")
    if feature.startswith("flag_") and hi:
        return (None, f"{feature[5:].replace('_', ' ')} flag common ({pct})")
    return None


NOUN_TAGS = ("students", "holders")


def _make_name(tags, max_words=4):
    words = []
    for tag in tags:
        if tag is None:
            continue
        has_noun = any(w.endswith(NOUN_TAGS) for w in words + [tag])
        extra = 0 if has_noun else 1
        if len(" ".join(words + [tag]).split()) + extra <= max_words:
            words.append(tag)
        if len(words) == 2:
            break
    if not words:
        return "Typical clients"
    # nouns go last so "students older" reads "older students"
    words.sort(key=lambda w: w.endswith(NOUN_TAGS))
    name = " ".join(words)
    if not name.endswith(NOUN_TAGS):
        name += " clients"
    return name[0].upper() + name[1:]


def describe_clusters(profiles, zprof, threshold=config.SEGMENT_Z_THRESHOLD, top_n=3):
    """for every cluster, rank features by |z| and keep the ones that pass the threshold and have a rule."""
    descriptions, names = {}, {}
    for c in zprof.index:
        order = zprof.loc[c].abs().sort_values(ascending=False).index
        terms = []
        for f in order:
            if abs(zprof.loc[c, f]) < threshold:
                break
            t = _term(f, zprof.loc[c, f], profiles.loc[c, f])
            if t is not None:
                terms.append(t)
        phrases = [p for _, p in terms[:top_n]]
        text = ", ".join(phrases) if phrases else "close to the average client on every feature"
        descriptions[int(c)] = text[0].upper() + text[1:]
        names[int(c)] = _make_name([t for t, _ in terms])
    return descriptions, _unique(names)


def _unique(names):
    seen, out = {}, {}
    for c, n in names.items():
        seen[n] = seen.get(n, 0) + 1
        out[c] = n if seen[n] == 1 else f"{n} {seen[n]}"
    return out


def cluster_profiles(filled, labels):
    profiles = filled.groupby(labels).mean()
    zprof = (profiles - filled.mean()) / filled.std(ddof=0).replace(0, np.nan)
    return profiles, zprof.fillna(0.0)


# ---------- main entry ----------

def fit_segments(snapshot, features=None, seed=config.SEED):
    features = segment_features(features)
    z, filled = standardise(snapshot, features)
    rng = np.random.default_rng(seed)
    n_sub = min(config.SEGMENT_SELECTION_SAMPLE, len(z))
    sub = np.sort(rng.choice(len(z), size=n_sub, replace=False))
    ks = [k for k in config.SEGMENT_K_RANGE if k < n_sub]
    silhouette, inertia = scan_k(z[sub], ks, seed)
    k, elbow = choose_k(silhouette, inertia)

    final = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(z)
    labels = final.labels_.astype(int)
    ari = gmm_agreement(z[sub], labels[sub], k, seed)

    filled.index = snapshot.index
    lab = pd.Series(labels, index=snapshot.index, name="cluster")
    profiles, zprof = cluster_profiles(filled, lab)
    descriptions, names = describe_clusters(profiles, zprof)
    return {
        "k": int(k), "elbow_k": int(elbow), "features": features, "labels": lab,
        "silhouette": silhouette, "inertia": inertia, "ari_gmm": ari,
        "profiles": profiles, "zprofiles": zprof,
        "sizes": lab.value_counts().sort_index().astype(int).to_dict(),
        "descriptions": descriptions, "names": names,
        "pca_2d": pca_sample(z, labels, snapshot.index, seed=seed),
    }


def write_tables(seg, out_dir=None):
    out = out_dir or config.TABLE_DIR
    out.mkdir(parents=True, exist_ok=True)
    sel = pd.DataFrame({"k": list(seg["silhouette"]),
                        "silhouette": list(seg["silhouette"].values()),
                        "inertia": [seg["inertia"][k] for k in seg["silhouette"]]})
    sel["chosen"] = sel["k"] == seg["k"]
    sel.to_csv(out / "segment_selection.csv", index=False)
    total = sum(seg["sizes"].values())
    summary = pd.DataFrame([{"cluster": c, "name": seg["names"][c], "size": n, "share": n / total,
                             "description": seg["descriptions"][c]} for c, n in seg["sizes"].items()])
    summary.to_csv(out / "segment_summary.csv", index=False)
    seg["profiles"].round(4).to_csv(out / "segment_profiles.csv", index_label="cluster")
    seg["zprofiles"].round(4).to_csv(out / "segment_zprofiles.csv", index_label="cluster")
    return summary
