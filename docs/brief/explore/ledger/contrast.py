"""reads the colour block at the top of ledger.css and checks every text and mark pair the ledger page uses.
text needs 4.5:1 (aa, normal text), marks that are not text (glyphs, markers, the chart bar for this client) need 3:1.
exit code 1 when anything fails.

    python docs/brief/explore/ledger/contrast.py

the orange #F67E04 is never checked against the paper: it is only used as a fill behind ink text (checked below)
and as a decorative rule beside a part whose title and words already say held back in orange-text.
"""
import re
import sys
from pathlib import Path

CSS = (Path(__file__).parent / "ledger.css").read_text()
block = CSS[CSS.index(":root {"):CSS.index("}", CSS.index(":root {"))]
HEX = r"--([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6});"
BASE = dict(re.findall(HEX, block))
# each palette block only swaps some colours, the rest come from the base block
PALS = {"tokyo": BASE}
pal_blocks = re.findall(r'(\[data-pal="([a-z]+)"\]\s*\{[^}]*\})', CSS)
for whole, name in pal_blocks:
    PALS[name] = {**BASE, **dict(re.findall(HEX, whole))}

PAIRS = [
    ("ink", "paper", "text", "body text on the page"), ("ink", "card", "text", "body text on a card"),
    ("ink", "paper-2", "text", "text in items and the products block"), ("ink", "sand", "text", "rail titles"),
    ("ink-2", "paper", "text", "secondary text on the page"), ("ink-2", "card", "text", "secondary text on a card"),
    ("ink-2", "paper-2", "text", "secondary text in items"), ("ink-2", "sand", "text", "rail captions and labels"),
    ("ink-3", "card", "text", "quiet text on a card"), ("ink-3", "paper", "text", "quiet text on the page"),
    ("ink-3", "paper-2", "text", "quiet text in items"),
    ("teal-deep", "card", "text", "links on a card"), ("teal-deep", "paper", "text", "links on the page"),
    ("teal-deep", "sage-soft", "text", "segment badge, done status"),
    ("on-teal", "teal", "text", "pressed buttons, done step numerals"),
    ("on-orange", "orange", "text", "held back step status and numeral"),
    ("orange-text", "card", "text", "held back title, kpi value, rule names"),
    ("orange-text", "paper", "text", "held back count in the page"), ("orange-text", "sand", "text", "held back count in the rail"),
    ("orange-text", "orange-soft", "text", "rule names inside a held back item"),
    ("ink", "orange-soft", "text", "item names in held back"), ("ink-2", "orange-soft", "text", "reasons in held back"),
    ("st-held", "st-held-bg", "text", "has it"), ("st-held", "card", "text", "has it on a card"),
    ("st-discuss", "st-discuss-bg", "text", "worth discussing"), ("st-discuss", "card", "text", "worth discussing on a card"),
    ("st-progress", "st-progress-bg", "text", "likely in progress"), ("st-progress", "card", "text", "review due word"),
    ("st-heldback", "st-heldback-bg", "text", "held back"), ("st-heldback", "card", "text", "held back on a card"),
    ("st-none", "st-none-bg", "text", "not in data"), ("st-none", "card", "text", "not in data on a card"),
    ("ink", "st-discuss-bg", "text", "item names in worth discussing"), ("ink-2", "st-discuss-bg", "text", "evidence lines"),
    ("care-ink", "care-bg", "text", "care line"), ("care-ink", "card", "text", "care question kind"),
    ("ink", "lit-bg", "text", "text in a linked part"), ("ink-2", "lit-bg", "text", "secondary text in a linked part"),
    ("ink", "sage-soft", "text", "answer outcome"), ("ink-2", "sage-soft", "text", "outcome detail"),
    ("st-held", "card", "ui", "has it glyph"), ("st-discuss", "card", "ui", "discuss glyph"),
    ("st-progress", "card", "ui", "in progress glyph"), ("st-heldback", "card", "ui", "held back glyph"),
    ("st-none", "card", "ui", "not in data glyph"), ("teal", "card", "ui", "this client's group bar, meeting dot, focus ring"),
    ("teal", "paper", "ui", "focus ring and step numeral on the page"), ("lit-line", "card", "ui", "outline of a linked part"),
]

def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

def ratio(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)

fail = 0
for name, T in PALS.items():
    print(f"== {name}")
    for fg, bg, kind, where in PAIRS:
        r = ratio(T[fg], T[bg])
        need = 1.3 if fg == "line-2" else 4.5 if kind == "text" else 3.0
        ok = r >= need
        fail += not ok
        if not ok or "-v" in sys.argv:
            print(f"{'ok  ' if ok else 'FAIL'} {r:5.2f} (needs {need}) {fg} {T[fg]} on {bg} {T[bg]}: {where}")
    print(f"   {len(PAIRS)} pairs, lowest {min(ratio(T[f], T[b]) for f, b, k, w in PAIRS):.2f}")
# no raw colour may sit outside the colour block, in the css or in the page
rest = CSS.replace(block, "")
for whole, name in pal_blocks:
    rest = rest.replace(whole, "")
rest = rest + (Path(__file__).parent / "index.html").read_text()
raw = [m for m in re.findall(r"#[0-9A-Fa-f]{6}\b|oklch\(|\brgb\((?!92 72 48)", rest)]
if raw:
    fail += 1
    print("FAIL raw colours outside the colour block:", raw[:8])
print(f"{len(PALS)} palettes x {len(PAIRS)} pairs, {fail} failing")
sys.exit(1 if fail else 0)
