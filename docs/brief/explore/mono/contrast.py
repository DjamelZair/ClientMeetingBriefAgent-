"""reads the colour tokens in the :root block of mono.css and checks the wcag contrast ratio of every text and
background pair the page uses. text needs 4.5:1, marks that are not text (glyphs, meter segments, the signal rule,
the timeline axis, focus rings) need 3:1. it also fails when a raw colour turns up outside the token block,
in mono.css or index.html. exit code 1 when anything fails.

    python docs/brief/explore/mono/contrast.py
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
CSS = (HERE / "mono.css").read_text()
HTML = (HERE / "index.html").read_text()

# each pair: foreground token, background token, kind ("text" or "ui"), where it is used
PAIRS = [
    ("ink", "panel", "text", "body text, card titles, stat values"),
    ("ink", "frame", "text", "sidebar step names, breadcrumb"),
    ("ink", "sunk", "text", "item names, wells, the follow up text"),
    ("ink", "lit-bg", "text", "text in a part lit by its step"),
    ("ink", "signal-tint", "text", "item name inside a held back card"),
    ("ink-2", "panel", "text", "secondary text on a card"),
    ("ink-2", "frame", "text", "top bar links"),
    ("ink-2", "sunk", "text", "evidence lines, segmented control labels"),
    ("ink-2", "lit-bg", "text", "secondary text in a lit part"),
    ("ink-2", "signal-tint", "text", "reasons inside a held back card"),
    ("ink-3", "panel", "text", "labels and captions on a card"),
    ("ink-3", "frame", "text", "sidebar part names, crumb"),
    ("ink-3", "sunk", "text", "part titles on the board floor, meter labels"),
    ("ink-3", "lit-bg", "text", "quiet text in a lit part"),
    ("on-ink", "ink", "text", "black pills: the active view, the bar, the pinned step, step numbers"),
    ("on-ink", "ink-2", "text", "black button on hover"),
    ("on-ink", "signal-text", "text", "number of a step that held something back, held back icon square"),
    ("signal-text", "panel", "text", "held back value, rule names, the held back status word"),
    ("signal-text", "signal-tint", "text", "rule names and status inside a held back card or pill"),
    ("signal-text", "frame", "text", "held back count in the sidebar"),
    ("signal", "panel", "ui", "held back rule, glyph and timeline dot on a card"),
    ("signal", "signal-tint", "ui", "held back rule on its tinted card"),
    ("signal", "sunk", "ui", "held back segment in the agent meter"),
    ("slate", "panel", "ui", "timeline axis, info glyph, band chart base"),
    ("ink", "line-2", "ui", "filled against empty meter segments"),
    ("ink-3", "panel", "ui", "progress and not in data glyphs"),
    ("focus", "panel", "ui", "focus ring on a card"),
    ("focus", "frame", "ui", "focus ring in the sidebar"),
    ("focus", "canvas", "ui", "focus ring at the window edge"),
]


def tokens(css):
    root = re.search(r":root\s*\{(.*?)\n\}", css, re.S).group(1)
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9A-Fa-f]{6})\b", root)), root


def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def main():
    T, root = tokens(CSS)
    fails = 0
    print("mono contrast check")
    for fg, bg, kind, where in PAIRS:
        need = 4.5 if kind == "text" else 3.0
        r = ratio(T[fg], T[bg])
        ok = r >= need
        fails += not ok
        print(f"  {'pass' if ok else 'FAIL'}  {r:5.2f} (needs {need})  {fg} {T[fg]} on {bg} {T[bg]}  {where}")
    # raw colours outside the token block
    rest = CSS.replace(root, "")
    for name, text in (("mono.css outside :root", rest), ("index.html", HTML)):
        raw = re.findall(r"#[0-9A-Fa-f]{3,8}\b|rgba?\(", text)
        if raw:
            fails += 1
            print(f"  FAIL  raw colour in {name}: {raw[:5]}")
    print(f"{len(PAIRS)} pairs, {fails} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
