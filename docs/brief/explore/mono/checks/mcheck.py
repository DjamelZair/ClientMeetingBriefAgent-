# usage: mcheck.py [shots]
# opens the mono page on a short lived local server, walks all clients at 1440x900 and 390x844, works the controls,
# and fails on an empty mount, a console error or a horizontal scroll. with "shots" it also writes the screenshots
import contextlib, functools, http.server, socketserver, sys, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE = Path(__file__).resolve().parent.parent
DOCS = HERE.parent.parent.parent
PAGE = "brief/explore/mono/index.html"
SHOTS = HERE / "shots"

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

@contextlib.contextmanager
def serve():
    with socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(DOCS))) as h:
        threading.Thread(target=h.serve_forever, daemon=True).start()
        try: yield f"http://127.0.0.1:{h.server_address[1]}"
        finally: h.shutdown()

def open_page(b, base, w, h, reduce=False):
    pg = b.new_page(viewport={"width": w, "height": h}, reduced_motion="reduce" if reduce else "no-preference")
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{base}/{PAGE}")
    pg.wait_for_function("window.__brief && document.querySelectorAll('[aria-busy=true]').length === 0", timeout=20000)
    pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(1200)
    return pg, errs

def show(pg, i): pg.evaluate(f"window.__brief.show({i}, false)"); pg.wait_for_timeout(150)

EMPTY = """() => [...document.querySelectorAll('[data-renders], [aria-busy]')].filter(e => e.getAttribute('aria-busy') === 'true' || e.querySelector('.v-sk')).map(e => e.id)"""
HS = "document.scrollingElement.scrollWidth > innerWidth + 0.5"
OVER = """() => { const W = document.documentElement.clientWidth; return [...document.querySelectorAll('.panel *')].filter(e => { const r = e.getBoundingClientRect(); return r.width && r.right > W + 1 && !e.closest('.board[style], .v-sr'); }).slice(0, 3).map(e => e.className || e.tagName); }"""
bad = []
shots = len(sys.argv) > 1 and sys.argv[1] == "shots"
with serve() as base, sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in [(1440, 900), (390, 844)]:
        pg, errs = open_page(b, base, w, h)
        n = pg.evaluate("window.__brief.count")
        for i in range(n):
            show(pg, i)
            e = pg.evaluate(EMPTY)
            if e: bad.append(f"{w}: client {i+1:02d} empty mounts {e}")
            if pg.evaluate(HS): bad.append(f"{w}: client {i+1:02d} horizontal scroll {pg.evaluate(OVER)}")
            # work the controls on every client: bar, each first answer, a step link, the tool log
            pg.click('[data-act="bar"][data-t="0.3"]'); pg.wait_for_timeout(60)
            pg.click('[data-act="bar"][data-t="0.1"]'); pg.wait_for_timeout(60)
            nq = pg.evaluate("document.querySelectorAll('.v-q').length")
            for q in range(nq):
                a = pg.locator(f'[data-act="answer"][data-q="{q}"][data-a="0"]')
                if a.count(): a.click(); pg.wait_for_timeout(60)
            pg.keyboard.press("Escape")
            if w == 1440:
                pg.click('.snav [data-step="3"]'); pg.wait_for_timeout(60); pg.keyboard.press("Escape")
                pg.click('[data-view="log"]'); pg.wait_for_timeout(60)
                if not pg.evaluate("document.querySelectorAll('#log section').length === 5"): bad.append(f"client {i+1:02d}: tool log not five steps")
                pg.click('[data-view="board"]')
            if pg.evaluate(HS): bad.append(f"{w}: client {i+1:02d} horizontal scroll after the controls")
        # replay and the follow up draft once
        pg.click('[data-act="replay"]'); pg.wait_for_timeout(250)
        if not pg.evaluate("document.querySelectorAll('[data-ready=\"0\"]').length"): bad.append(f"{w}: replay did not fade the parts")
        pg.wait_for_timeout(2000)
        if pg.evaluate("document.querySelectorAll('[data-ready=\"0\"]').length"): bad.append(f"{w}: replay left parts hidden")
        fu = pg.locator('[data-act="fu"]')
        if fu.count(): fu.first.click(); pg.wait_for_timeout(100)
        if errs: bad.append(f"{w}: console errors {errs[:4]}")
        print(f"{w}x{h}: {n} clients walked")
        pg.close()
    if shots:
        SHOTS.mkdir(exist_ok=True)
        pg, errs = open_page(b, base, 1440, 900)
        for c in (4, 10, 11):
            show(pg, c - 1); pg.mouse.move(0, 0); pg.wait_for_timeout(300)
            pg.screenshot(path=str(SHOTS / f"desktop_client{c:02d}.png"))
        show(pg, 9); pg.wait_for_timeout(300)
        pg.screenshot(path=str(SHOTS / "desktop_client10_full.png"), full_page=True)
        pg.click('[data-view="log"]'); pg.wait_for_timeout(200)
        pg.screenshot(path=str(SHOTS / "desktop_client10_toollog.png"))
        pg.close()
        pg, errs2 = open_page(b, base, 390, 844)
        show(pg, 9); pg.wait_for_timeout(300)
        pg.screenshot(path=str(SHOTS / "phone_client10.png"), full_page=True)
        pg.close()
        if errs or errs2: bad.append(f"shots: console errors {(errs + errs2)[:3]}")
    b.close()
print(f"mcheck: {len(bad)} problems")
for x in bad: print("  " + x)
sys.exit(1 if bad else 0)
