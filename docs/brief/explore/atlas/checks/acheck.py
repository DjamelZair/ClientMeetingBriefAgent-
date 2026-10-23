# usage: acheck.py [shots]
# adapted from the scratchpad checks (bhelp.py, vfit.py, vinteract.py, shoot2.py) for the atlas page.
# one short lived server and one browser: all 40 clients at 1440x900 render real data with no console errors,
# 390 has no horizontal scroll for any client, the logic works (bar, answer, link, replay, follow up),
# and with "shots" it writes the screenshots into ../shots/
import sys
from playwright.sync_api import sync_playwright
from ahelp import serve, open_page, show, SHOTS, MOUNTS

EMPTY = """(ids) => ids.filter(id => { const e = document.getElementById(id); return !e || e.getAttribute("aria-busy") === "true" || !e.textContent.trim() || e.querySelector(".v-sk"); })"""
res = []
def ok(c, what): res.append(("pass  " if c else "FAIL  ") + what)

with serve() as base, sync_playwright() as p:
    b = p.chromium.launch()
    pg, errs = open_page(b, base, 1440, 900)
    n = pg.evaluate("window.__brief.count")
    bad = []
    for i in range(n):
        show(pg, i)
        e = pg.evaluate(EMPTY, MOUNTS)
        if e: bad.append(f"client {i+1:02d}: empty {e}")
        if pg.evaluate("document.scrollingElement.scrollWidth > innerWidth + 0.5"): bad.append(f"client {i+1:02d}: hscroll at 1440")
        figs = pg.evaluate("[...document.querySelectorAll('.at-fig .n')].map(x => x.textContent)")
        if len(figs) != 5 or any(f.strip() in ("", "undefined", "NaN", "null") for f in figs): bad.append(f"client {i+1:02d}: figures {figs}")
    ok(not bad, f"1440x900: {n} clients render real data, five figures each" + ("" if not bad else f" {bad[:6]}"))
    # what sits above the fold for client 10
    show(pg, 9); pg.evaluate("scrollTo(0, 0)"); pg.wait_for_timeout(200)
    fold = pg.evaluate("""() => [1,2,3,4,5].map(n => { const r = document.getElementById('part-' + n).getBoundingClientRect(); return [n, Math.round(r.top + scrollY), Math.round(r.bottom + scrollY)]; })""")
    print("client 10 parts top/bottom at 1440x900:", fold)
    # logic
    R = "() => Object.fromEntries([...document.querySelectorAll('[data-renders]')].map(e => [e.id, +e.dataset.renders]))"
    a = pg.evaluate(R); pg.click('[data-act="bar"][data-t="0.3"]'); pg.wait_for_timeout(500); c = pg.evaluate(R)
    ch = sorted(k for k in c if a.get(k) != c[k])
    ok("discuss" in ch and "timeline" not in ch and "review" not in ch, f"bar rerenders only {ch}")
    ok(pg.evaluate("document.querySelector('[data-act=bar][data-t=\"0.3\"]').getAttribute('aria-pressed')") == "true", "bar pressed state")
    pg.click('[data-act="bar"][data-t="0.1"]'); pg.wait_for_timeout(400)
    pg.click('[data-act="answer"][data-q="0"][data-a="0"]'); pg.wait_for_timeout(500)
    ok(pg.evaluate("!document.getElementById('v-out0').hidden && document.getElementById('v-out0').textContent.includes('Then')"), "answer opens the then branch")
    ok(pg.evaluate("document.querySelector('.at-tree.is-on') !== null"), "answered tree marked")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
    ok(pg.evaluate("document.querySelectorAll('.at-ans[aria-pressed=true]').length") == 0, "Escape clears the answer")
    # an answer that changes the brief, on any client
    moved = pg.evaluate("""() => { const F = V.state.F; for (let i = 0; i < F.count; i++){ const v = F.view(i);
        for (let q = 0; q < v.questions.length; q++) for (let a = 0; a < v.questions[q].answers.length; a++){ const o = v.questions[q].answers[a].outcome || {}; if (o.changes_brief) return [i, q, a]; } } return null; }""")
    if moved:
        show(pg, moved[0]); before = pg.evaluate("document.getElementById('discuss').textContent + document.getElementById('held').textContent + document.getElementById('aside').textContent")
        pg.click(f'[data-act="answer"][data-q="{moved[1]}"][data-a="{moved[2]}"]'); pg.wait_for_timeout(600)
        after = pg.evaluate("document.getElementById('discuss').textContent + document.getElementById('held').textContent + document.getElementById('aside').textContent")
        ok(before != after, f"answer branch changes the brief (client {moved[0]+1:02d}, q{moved[1]} a{moved[2]})")
        fu = pg.evaluate("document.querySelector('.v-fu-a') ? document.querySelector('.v-fu-a').textContent : ''")
        ok("if the client says" in fu, "follow up draft follows the answer")
        pg.keyboard.press("Escape")
    else: ok(False, "no answer that changes the brief found")
    show(pg, 9)
    pg.click('#v-step-3 .v-step-btn'); pg.wait_for_timeout(700)
    ok(pg.evaluate("document.getElementById('part-3').hasAttribute('data-on') && document.getElementById('v-step-3').hasAttribute('data-linked')"), "step 3 pinned: node and part 3 linked")
    ok(pg.evaluate("document.querySelectorAll('[data-lit=\"1\"]').length") > 0, "things step 3 made are lit")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
    pg.evaluate("scrollTo(0, 0)"); pg.wait_for_timeout(200)
    pg.hover('#part-4'); pg.wait_for_timeout(200)
    ok(pg.evaluate("document.getElementById('v-step-4').hasAttribute('data-hover')"), "hover on part 4 lights node 4")
    pg.mouse.move(2, 2)
    pg.click('[data-act="replay"]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("V.state.replaying && document.querySelectorAll('.at-fig[data-ready=\"0\"]').length > 0"), "replay hides figures until their step is done")
    pg.wait_for_timeout(1500)
    ok(pg.evaluate("!V.state.replaying && document.querySelectorAll('.at-node[data-s=done]').length === 5 && document.querySelectorAll('[data-ready=\"0\"]').length === 0"), "replay ends with every step done")
    pg.click('[data-act="next"]'); pg.wait_for_timeout(1500)
    ok(pg.evaluate("V.state.v.index") == 10, "next goes to client 11")
    pg.click('[data-act="prev"]'); pg.wait_for_timeout(1500)
    ok(pg.evaluate("V.state.v.index") == 9, "prev goes back to client 10")
    pg.click('[data-act="fu"]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("!document.getElementById('v-fu-body').hidden"), "follow up draft opens")
    ok(not errs, f"no console errors at 1440 {errs[:3]}")
    if "shots" in sys.argv:
        pg.click('[data-act="fu"]')
        SHOTS.mkdir(exist_ok=True)
        for c in (4, 10, 11):
            show(pg, c - 1); pg.evaluate("scrollTo(0, 0)"); pg.mouse.move(0, 0); pg.wait_for_timeout(400)
            pg.screenshot(path=str(SHOTS / f"desktop_client{c:02d}.png"))
        show(pg, 9); pg.evaluate("scrollTo(0, 0)"); pg.wait_for_timeout(300)
        pg.screenshot(path=str(SHOTS / "desktop_client10_full.png"), full_page=True)
    pg.close()
    # phone
    pg, errs = open_page(b, base, 390, 844)
    hs = []
    for i in range(n):
        show(pg, i)
        if pg.evaluate("document.scrollingElement.scrollWidth > innerWidth + 0.5"): hs.append(i + 1)
    ok(not hs, f"390: no horizontal scroll for any client {hs}")
    ok(not errs, f"no console errors at 390 {errs[:3]}")
    if "shots" in sys.argv:
        show(pg, 9); pg.evaluate("scrollTo(0, 0)"); pg.wait_for_timeout(300)
        pg.screenshot(path=str(SHOTS / "phone_client10.png"), full_page=True)
    pg.close(); b.close()

print("\n".join(res))
sys.exit(0 if all(r.startswith("pass") for r in res) else 1)
