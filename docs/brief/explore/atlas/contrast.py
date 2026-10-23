"""reads the three palette blocks in atlas.css, computes the wcag contrast ratio for every text and mark pair the atlas page
uses, and prints the report. modelled on docs/brief/contrast.py.

    python docs/brief/explore/atlas/contrast.py

text pairs need 4.5:1 (aa, normal text); large text (24px and up) and marks that are not text need 3:1.
it also fails when a raw colour turns up outside the token block, in atlas.css or index.html. exit code 1 on any failure.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
CSS = (HERE / "atlas.css").read_text()

# foreground token, background token, kind ("text", "large" or "ui"), where it is used
PAIRS = [
    ("ink", "paper", "text", "body text on the page"),
    ("ink", "paper-2", "text", "question roots, outcome, draft"),
    ("ink", "stone", "text", "has it product names"),
    ("ink-2", "paper", "text", "secondary text"),
    ("ink-2", "paper-2", "text", "why asked, care reasons"),
    ("ink-2", "stone", "text", "has it category names"),
    ("ink-3", "paper", "text", "quiet text, figure sub lines, footer"),
    ("ink-3", "paper-2", "text", "draft note"),
    ("ink-3", "focus-wash", "text", "quiet text in a linked part"),
    ("ink-2", "focus-wash", "text", "figure labels when the step is pinned"),
    ("prime", "paper", "text", "headline, figures, buttons"),
    ("prime", "stone-2", "text", "button hover"),
    ("prime", "focus-wash", "text", "figures when the step is pinned"),
    ("prime", "focus", "text", "step name in the focus pill"),
    ("on-prime", "prime", "text", "pressed buttons, done nodes, part markers"),
    ("on-prime", "hold", "text", "node and marker of a step that held something back"),
    ("second-ink", "paper", "text", "links, segment, question kind, has it"),
    ("second-ink", "paper-2", "text", "question kind in a root"),
    ("second-ink", "stone", "text", "has it glyph and word"),
    ("second", "paper", "large", "lead word of the headline, 40px"),
    ("prime", "paper-2", "text", "part titles on a raised paper"),
    ("hold", "paper-2", "text", "held back in an outcome"),
    ("hold", "stone", "text", "held back figure in a pinned step"),
    ("second", "paper", "ui", "timeline span, draft rule"),
    ("hold", "paper", "text", "held back figure, status, overdue"),
    ("hold", "hold-wash", "text", "held back item names and rules"),
    ("ink-2", "hold-wash", "text", "held back reasons"),
    ("ink", "hold-wash", "text", "held back product rows"),
    ("ink-3", "hold-wash", "text", "category under a held back row"),
    ("mist-ink", "paper", "ui", "tree connectors, axis, not in data glyph"),
    ("mist-ink", "paper-2", "ui", "connectors next to a root"),
    ("prime", "paper", "ui", "node rings, focus ring, chosen branch"),
    ("prime", "stone", "ui", "this client's band in the chart"),
    ("ink-2", "paper", "ui", "likely in progress glyph"),
]


PALETTES = ["fabric", "calm", "graphite"]


def blocks(css):
    """the raw blocks: fabric sits on ':root, [data-pal="fabric"]', the others on their own [data-pal] selector,
    and the derived roles on ':root, [data-pal]'"""
    out, spans = {}, []
    for m in re.finditer(r"(^|\n)([^{}\n]*)\{([^{}]*)\}", css):
        sel, body = m.group(2).strip(), m.group(3)
        if "--" not in body or ("data-pal" not in sel and sel != ":root"):
            continue
        spans.append(body)
        key = "derived" if sel == ":root, [data-pal]" else "base" if sel == ":root" else next((p for p in PALETTES if f'"{p}"' in sel), None)
        if key:
            out.setdefault(key, {}).update(dict(re.findall(r"--([a-z0-9-]+):\s*([^;]+);", body)))
    return out, spans


def tokens(css, pal):
    B, _ = blocks(css)
    raw = dict(B.get("base", {}))
    raw.update(B[pal]); raw.update(B.get("derived", {}))
    def res(v, seen=0):
        v = v.strip()
        m = re.fullmatch(r"var\(--([a-z0-9-]+)\)", v)
        return res(raw[m.group(1)], seen + 1) if m and seen < 8 else v
    return {k: res(v) for k, v in raw.items()}


def lum(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    a, b = lum(a), lum(b)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def main():
    fails = 0
    for pal in PALETTES:
        T = tokens(CSS, pal)
        print(f"\n{pal}\n{'pair':44} {'ratio':>6}  need  where")
        for fg, bg, kind, where in PAIRS:
            r = ratio(T[fg], T[bg])
            need = 4.5 if kind == "text" else 3.0
            ok = r >= need
            fails += not ok
            print(f"{fg + ' on ' + bg:44} {r:6.2f}  {need:>4}  {'ok  ' if ok else 'FAIL'} {where}")
    # every colour lives in a token block
    rest = CSS
    for body in blocks(CSS)[1]:
        rest = rest.replace(body, "")
    rest += (HERE / "index.html").read_text()
    raw = re.findall(r"#[0-9a-fA-F]{3,8}\b(?![\w-])", re.sub(r"<!--.*?-->|/\*.*?\*/", "", rest, flags=re.S))
    raw = [x for x in raw if not re.fullmatch(r"#(report|part|v|find|ident|add|ace|bad|bed|dad|fade|face)", x)]
    if raw:
        fails += 1
        print("FAIL raw colours outside the token blocks:", sorted(set(raw)))
    print(f"\n{len(PAIRS)} pairs in {len(PALETTES)} palettes, {fails} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
