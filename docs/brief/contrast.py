"""reads the four scheme blocks in tokens.css, computes the wcag contrast ratio for every text and background
pair the shared components use, and writes the report to contrast.txt next to this file.

    python docs/variants/contrast.py

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
]


def blocks(css):
    out = {}
    for m in re.finditer(r'((?::root,\s*)?\[data-scheme="(S\d)"\])\s*\{(.*?)\}', css, re.S):
        out[m.group(2)] = dict(re.findall(r"--([a-z0-9-]+):\s*([^;]+);", m.group(3)))
    return out


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


def main():
    schemes = blocks(CSS)
    lines, fails = [], 0
    names = {"S1": "teal and cherry", "S2": "calm banking light", "S3": "dark slate", "S4": "warm paper"}
    lines.append("WCAG contrast report for docs/variants/tokens.css, written by contrast.py")
    lines.append("text needs 4.5:1, non text marks need 3:1\n")
    for sid in sorted(schemes):
        tok = schemes[sid]
        lines.append(f"{sid}, {names.get(sid, '')}")
        worst = None
        for fg, bg, kind, where in PAIRS:
            r = ratio(tok[fg], tok[bg])
            need = 4.5 if kind == "text" else 3.0
            ok = r >= need
            fails += not ok
            worst = r if worst is None or r - need < worst - need else worst
            lines.append(f"  {'pass' if ok else 'FAIL'}  {r:5.2f}  {kind:4}  {fg} on {bg}: {where}")
        lines.append("")
    lines.append(f"{len(PAIRS) * len(schemes)} pairs checked, {fails} failing")
    (HERE / "contrast.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(l for l in lines if "FAIL" in l) or "no failures")
    print(lines[-1])
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
