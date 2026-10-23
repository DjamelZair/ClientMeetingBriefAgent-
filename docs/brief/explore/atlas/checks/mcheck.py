# the model page check: at 1440x900 and 390 in all three palettes, no console errors, no horizontal scroll, nothing
# clipped, no en or em dash, the links between the brief and this page resolve; then it takes the screenshots.
# run it through the flock lock:  flock <lock> python checks/mcheck.py [noshots]
import sys
from PIL import Image
from ahelp import serve, SHOTS
from playwright.sync_api import sync_playwright

PAGE = "model.html"
CLIP = """() => {
  const out = [];
  const name = e => (e.id ? "#" + e.id : e.className && e.className.baseVal === undefined ? "." + String(e.className).split(" ")[0] : e.tagName.toLowerCase());
  document.querySelectorAll("body *").forEach(e => {
    if (e.closest("[hidden]") || e.offsetParent === null && getComputedStyle(e).position !== "fixed") return;
    if (e.closest(".v-sr, .v-skip, svg, .pl")) return;
    const cs = getComputedStyle(e);
    if (cs.overflowX !== "visible" || cs.overflowY !== "visible") {
      if (e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1) out.push("clipped " + name(e));
    }
    if (!e.children.length && e.textContent.trim()) {
      const box = e.closest(".mp-sec, .mp-mast, .at-node, .top, .foot"); if (!box) return;
      const r = e.getBoundingClientRect(), b = box.getBoundingClientRect();
      if (r.right > b.right + 1 || r.left < b.left - 1) out.push("past its box: " + name(e) + " '" + e.textContent.trim().slice(0, 30) + "'");
    }
  });
  /* a table or chart wider than the column that holds it */
  document.querySelectorAll(".mp-t, .mp-chart svg").forEach(t => {
    const r = t.getBoundingClientRect(), b = t.parentNode.getBoundingClientRect();
    if (r.right > b.right + 1 || r.width > b.width + 1) out.push("wider than its column: " + name(t) + " in " + name(t.parentNode));
  });
  /* svg text running past its own chart */
  document.querySelectorAll(".mp-chart svg").forEach(s => {
    const b = s.getBoundingClientRect();
    s.querySelectorAll("text").forEach(t => { const r = t.getBoundingClientRect(); if (r.right > b.right + 2 || r.left < b.left - 2) out.push("svg text past its chart: '" + t.textContent.slice(0, 30) + "' in " + s.parentNode.id); });
  });
  if (document.scrollingElement.scrollWidth > innerWidth + 0.5) out.push("horizontal scroll " + document.scrollingElement.scrollWidth);
  if (/[\\u2013\\u2014]/.test(document.body.innerText)) out.push("en or em dash in the text");
  return [...new Set(out)];
}"""

def open_model(b, base, w, h, pal="fabric"):
    pg = b.new_page(viewport={"width": w, "height": h})
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{base}/{PAGE}?pal={pal}")
    pg.wait_for_function("window.__model && window.__model.ready", timeout=15000)
    pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(800)
    return pg, errs

bad = []
shots = not (len(sys.argv) > 1 and sys.argv[1] == "noshots")
with serve() as base, sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in ((1440, 900), (390, 844)):
        for pal in ("fabric", "calm", "graphite"):
            pg, errs = open_model(b, base, w, h, pal)
            for x in pg.evaluate(CLIP): bad.append(f"{w} {pal}: {x}")
            if errs: bad.append(f"{w} {pal}: console {errs[:3]}")
            if shots and w == 1440:
                pg.screenshot(path=str(SHOTS / f"_model_{pal}.png"))
            if pal == "fabric":
                if shots and w == 1440:
                    pg.screenshot(path=str(SHOTS / "model_desktop.png"))
                    pg.screenshot(path=str(SHOTS / "model_desktop_full.png"), full_page=True)
                if shots and w == 390:
                    pg.screenshot(path=str(SHOTS / "model_phone.png"), full_page=True)
                # the metric switch redraws the heat table, which must still fit
                pg.click('#heat [data-m="pr"]'); pg.wait_for_timeout(150)
                for x in pg.evaluate(CLIP): bad.append(f"{w} pr heat: {x}")
                pg.click('#heat [data-m="roc"]'); pg.wait_for_timeout(150)
            pg.close()
    # links: the brief to this page, and back
    pg, errs = open_model(b, base, 1440, 900)
    for href in pg.evaluate("[...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => h.startsWith(location.origin))"):
        st = pg.request.get(href.split("#")[0]).status
        if st != 200: bad.append(f"model link {href}: {st}")
    pg.close()
    q = b.new_page(viewport={"width": 1440, "height": 900})
    q.goto(f"{base}/brief/explore/atlas/index.html")
    q.wait_for_function("window.__brief", timeout=15000); q.wait_for_timeout(800)
    links = q.evaluate("[...document.querySelectorAll('a')].filter(a => /model\\.html/.test(a.getAttribute('href'))).map(a => a.href)")
    if not links: bad.append("atlas: no link to model.html")
    for href in links:
        st = q.request.get(href).status
        if st != 200 or not href.endswith("/model.html"): bad.append(f"atlas link {href}: {st}")
    q.close(); b.close()

if shots:
    ims = [Image.open(SHOTS / f"_model_{p}.png") for p in ("fabric", "calm", "graphite")]
    W = sum(i.width for i in ims) + 40
    out = Image.new("RGB", (W, ims[0].height), (255, 255, 255))
    x = 0
    for i in ims: out.paste(i, (x, 0)); x += i.width + 20
    from PIL import ImageDraw, ImageFont
    try: fnt = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
    except OSError: fnt = ImageFont.load_default()
    top = Image.new("RGB", (W, ims[0].height + 70), (255, 255, 255)); top.paste(out, (0, 70)); out = top
    d = ImageDraw.Draw(out)
    for k, name in enumerate(("Fabric (default)", "Calm", "Graphite")): d.text((k * (ims[0].width + 20) + 20, 14), name, fill=(30, 40, 60), font=fnt)
    out = out.resize((W // 2, out.height // 2), Image.LANCZOS)
    out.save(SHOTS / "model_palettes.png")
    for p in ("fabric", "calm", "graphite"): (SHOTS / f"_model_{p}.png").unlink()
print(f"model check: {len(bad)} problems")
for x in bad[:60]: print("  " + x)
sys.exit(1 if bad else 0)
