"""reads the four scheme blocks and the three design system blocks in tokens.css, computes the wcag contrast
ratio for every text and background pair the page uses, in every scheme and under every design system,
and writes the report to review/contrast.txt.

    python docs/brief/contrast.py

a design system block never sets a colour; it only points its role tokens (card-bg, item-bg, the tab colours)
at scheme tokens. so the scheme pairs are checked once per scheme, and the role pairs once per scheme and ds.
it also fails when a raw colour turns up outside the scheme blocks: in tokens.css, in index.html or in variants.js.

text pairs need 4.5:1 (aa, normal text). marks that are not text (glyphs, the chart bar for this client,
focus rings, the timeline meeting dot) need 3:1. exit code 1 when anything fails.
"""
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
CSS = (HERE / "tokens.css").read_text()

# each pair: foreground token, background token, kind ("text" or "ui"), where it is used
PAIRS = [
    ("ink", "bg", "text", "body text on the page"),
    ("ink", "surface", "text", "body text on a card"),
    ("ink", "surface-2", "text", "text in chips, items and review"),
    ("ink-2", "surface", "text", "secondary text on a card"),
    ("ink-2", "surface-2", "text", "secondary text in items"),
    ("ink-2", "bg", "text", "secondary text on the page"),
    ("ink-3", "surface", "text", "quiet text on a card"),
    ("ink-3", "surface-2", "text", "chip labels, quiet text in items"),
    ("ink-3", "bg", "text", "footer text"),
    ("accent-text", "surface", "text", "links and the segment badge on a card"),
    ("accent-text", "accent-soft", "text", "segment badge, done status"),
    ("on-accent", "accent", "text", "pressed buttons, done step numbers"),
    ("alarm-text", "surface", "text", "held back rule names"),
    ("alarm-text", "alarm-soft", "text", "overdue chip and review, held back status"),
    ("alarm-text", "st-heldback-bg", "text", "rule names inside a held back item"),
    ("surface", "alarm", "text", "number of a step that held something back"),
    ("st-held", "st-held-bg", "text", "wallet: held"),
    ("st-discuss", "st-discuss-bg", "text", "wallet: worth discussing"),
    ("st-progress", "st-progress-bg", "text", "wallet: likely in progress, review due chip"),
    ("st-heldback", "st-heldback-bg", "text", "wallet: held back"),
    ("st-none", "st-none-bg", "text", "wallet: not in data"),
    ("ink", "st-discuss-bg", "text", "item names in worth discussing"),
    ("ink-2", "st-discuss-bg", "text", "evidence lines in worth discussing"),
    ("ink", "st-heldback-bg", "text", "item names in held back"),
    ("ink-2", "st-heldback-bg", "text", "reasons in held back"),
    ("ink-3", "st-none-bg", "text", "not in data product names"),
    ("ink", "st-held-bg", "text", "held product names"),
    ("ink", "st-progress-bg", "text", "in progress product names"),
    ("ink", "lit-bg", "text", "text inside a linked part"),
    ("ink-2", "lit-bg", "text", "secondary text inside a linked part"),
    ("ink", "accent-soft", "text", "answer outcome text"),
    ("care-ink", "care-bg", "text", "care line and care chip"),
    ("care-ink", "surface", "text", "care question kind"),
    ("avatar-ink", "avatar-bg", "text", "monogram avatar"),
    ("ink-2", "surface-2", "text", "not raised items"),
    ("surface", "lit-line", "text", "pressed step marker number"),
    ("ink-3", "lit-bg", "text", "quiet text inside a linked part"),
    ("st-held", "surface", "ui", "held glyph on a card"),
    ("st-discuss", "surface", "ui", "discuss glyph on a card"),
    ("st-progress", "surface", "ui", "in progress glyph on a card"),
    ("st-heldback", "surface", "ui", "held back glyph on a card"),
    ("st-none", "surface", "ui", "not in data glyph on a card"),
    ("chart-me", "surface-2", "ui", "this client's bar in the band chart"),
    ("chart-me", "st-discuss-bg", "ui", "this client's bar inside a discuss item"),
    ("chart-rule", "st-discuss-bg", "ui", "the dashed bar line"),
    ("focus", "surface", "ui", "focus ring on a card"),
    ("focus", "bg", "ui", "focus ring on the page"),
    ("mark", "surface", "ui", "meeting dot on the timeline"),
    ("alarm", "surface", "ui", "overdue dot on the timeline"),
    ("lit-line", "surface", "ui", "outline of a linked part"),
    ("accent", "surface", "ui", "pressed scheme and step markers"),
    # the redesign: state words now sit on the card itself, without a tinted row behind them
    ("st-held", "surface", "text", "wallet: held, as a word on the card"),
    ("st-discuss", "surface", "text", "wallet: worth discussing, as a word on the card"),
    ("st-progress", "surface", "text", "review due status word in the summary"),
    ("st-heldback", "surface", "text", "held back count, status word and part title"),
    ("st-none", "surface", "text", "wallet: not in data, as a word on the card"),
    ("care-ink", "bg", "text", "care fact under the client name"),
    ("ink-2", "surface", "text", "header links"),
    ("ink-3", "bg", "text", "a waiting status on the rail"),
    # round 2
    ("accent", "bg", "ui", "focus ring and pressed markers on the page"),
    ("ink-2", "bg", "text", "the context line under the header"),
    ("ink", "surface-2", "text", "a hovered tab or switch"),
    ("st-held", "surface-2", "ui", "has it glyph in the wallet group"),
    ("st-heldback", "st-heldback-bg", "ui", "held back glyph on a tinted wallet row"),
    ("ink", "st-heldback-bg", "text", "product name on a held back wallet row"),
    ("st-heldback", "bg", "ui", "held back top rule seen against the page"),
]

# role tokens a design system points at scheme tokens; each pair is checked under every ds in every scheme
DS_PAIRS = [
    ("ink", "card-bg", "text", "text in a part or a summary card"),
    ("ink-2", "card-bg", "text", "secondary text in a part"),
    ("ink-3", "card-bg", "text", "labels and quiet text in a part"),
    ("accent-text", "card-bg", "text", "links in a part"),
    ("st-held", "card-bg", "text", "wallet word: held"),
    ("st-discuss", "card-bg", "text", "wallet word: worth discussing"),
    ("st-progress", "card-bg", "text", "summary word: review due"),
    ("st-heldback", "card-bg", "text", "summary and wallet word: held back"),
    ("st-none", "card-bg", "text", "wallet word: not in data"),
    ("care-ink", "care-bg", "text", "care line inside a part"),
    ("ink", "item-bg", "text", "item names and the review line"),
    ("ink-2", "item-bg", "text", "item evidence and review detail"),
    ("ink-3", "item-bg", "text", "synthetic date note in the review line"),
    ("st-progress", "item-bg", "text", "review due inside the review line"),
    ("tab-on-ink", "tab-on-bg", "text", "selected tab: ds, scheme and bar"),
    ("tab-off-ink", "tab-off-bg", "text", "unselected tab: ds, scheme and bar"),
    ("tab-on-line", "tab-on-bg", "ui", "underline of a selected tab"),
    ("st-heldback", "card-bg", "ui", "top rule of what not to offer and the held back card"),
    ("lit-line", "card-bg", "ui", "ring of a lit part"),
    ("st-heldback", "card-bg", "ui", "held back glyph in a part"),
    # round 2
    ("tab-off-ink", "bg", "text", "unselected tab where its own fill is transparent"),
    ("ink-3", "item-bg", "text", "quiet text in the wallet group"),
    ("st-held", "item-bg", "text", "has it word in the wallet group"),
    ("st-none", "card-bg", "ui", "not in data glyph in the wallet row"),
]


def blocks(css, attr="scheme"):
    out = {}
    pat = r'((?::root,\s*)?\[data-scheme="(S\d)"\])\s*\{(.*?)\}' if attr == "scheme" else r'\[data-ds="([a-z]+)"\]\s*\{(.*?)\}'
    for m in re.finditer(pat, css, re.S):
        body = m.group(3) if attr == "scheme" else m.group(2)
        out[m.group(2) if attr == "scheme" else m.group(1)] = dict(re.findall(r"--([a-z0-9-]+):\s*([^;]+);", body))
    return out


RAW = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:oklch|rgba?|hsla?)\(")


def raw_colours():
    """every colour outside the scheme blocks must be a token. returns the offending lines"""
    found = []
    scheme_free = re.sub(r'(?::root,\s*)?\[data-scheme="S\d"\]\s*\{.*?\}', "", CSS, flags=re.S)
    for no, line in enumerate(scheme_free.splitlines(), 1):
        if RAW.search(re.sub(r"/\*.*?\*/", "", line)):
            found.append(f"tokens.css: {line.strip()[:90]}")
    page = (HERE / "index.html").read_text()
    for st in re.findall(r"<style>(.*?)</style>", page, re.S):
        for line in st.splitlines():
            if RAW.search(re.sub(r"/\*.*?\*/", "", line)):
                found.append(f"index.html: {line.strip()[:90]}")
    # the components build markup in strings, so a literal colour there would pass every other check
    js = re.sub(r"/\*.*?\*/", "", (HERE / "variants.js").read_text(), flags=re.S)
    for line in js.splitlines():
        if RAW.search(re.sub(r"//.*$", "", line)):
            found.append(f"variants.js: {line.strip()[:90]}")
    return found


def resolve(value, tok):
    """a ds role token points at a scheme token through var(); transparent means there is nothing to check"""
    v = value.strip()
    m = re.fullmatch(r"var\(--([a-z0-9-]+)\)", v)
    if m:
        return tok[m.group(1)]
    return None if v == "transparent" else v


def srgb_from_oklch(l, c, h):
    a, b = c * math.cos(math.radians(h)), c * math.sin(math.radians(h))
    l_ = l + 0.3963377774 * a + 0.2158037573 * b
    m_ = l - 0.1055613458 * a - 0.0638541728 * b
    s_ = l - 0.0894841775 * a - 1.2914855480 * b
    l3, m3, s3 = l_ ** 3, m_ ** 3, s_ ** 3
    r = 4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3
    g = -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3
    bl = -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3
    return [min(1.0, max(0.0, x)) for x in (r, g, bl)]  # linear rgb, clipped to the gamut


def linear(value):
    v = value.strip()
    if v.startswith("#"):
        h = v[1:]
        rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in rgb]
    m = re.match(r"oklch\(\s*([\d.]+)%\s+([\d.]+)\s+([\d.]+)", v)
    if m:
        return srgb_from_oklch(float(m.group(1)) / 100, float(m.group(2)), float(m.group(3)))
    raise ValueError("cannot read colour " + v)


def ratio(fg, bg):
    lum = lambda rgb: 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    a, b = sorted((lum(linear(fg)), lum(linear(bg))), reverse=True)
    return (a + 0.05) / (b + 0.05)


def check(pairs, tok, lines):
    fails = n = 0
    for fg, bg, kind, where in pairs:
        f, b = tok.get(fg), tok.get(bg)
        if f is None or b is None:
            continue  # a transparent role has nothing to measure
        r = ratio(f, b)
        need = 4.5 if kind == "text" else 3.0
        ok = r >= need
        fails += not ok
        n += 1
        lines.append(f"  {'pass' if ok else 'FAIL'}  {r:5.2f}  {kind:4}  {fg} on {bg}: {where}")
    return n, fails


def main():
    schemes, layers = blocks(CSS), blocks(CSS, "ds")
    lines, fails, total = [], 0, 0
    names = {"S1": "teal and cherry", "S2": "calm banking light", "S3": "dark slate", "S4": "warm paper"}
    lines.append("WCAG contrast report for docs/brief/tokens.css, written by contrast.py")
    lines.append("text needs 4.5:1, non text marks need 3:1\n")
    for sid in sorted(schemes):
        tok = schemes[sid]
        lines.append(f"{sid}, {names.get(sid, '')}")
        n, f = check(PAIRS, tok, lines)
        total += n; fails += f
        lines.append("")
        for did in sorted(layers):
            roles = {k: resolve(v, tok) for k, v in layers[did].items() if "var(--" in v or v.strip() == "transparent"}
            lines.append(f"{sid} with ds={did}")
            n, f = check(DS_PAIRS, {**tok, **roles}, lines)
            total += n; fails += f
            lines.append("")
    raw = raw_colours()
    lines.append(f"raw colours outside the scheme blocks: {len(raw)}")
    lines.extend("  FAIL  " + r for r in raw)
    fails += len(raw)
    lines.append("")
    lines.append(f"{total} pairs checked over {len(schemes)} schemes and {len(layers)} ds layers, {fails} failing")
    (HERE / "review").mkdir(exist_ok=True)
    (HERE / "review" / "contrast.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(l for l in lines if "FAIL" in l) or "no failures")
    print(lines[-1])
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
