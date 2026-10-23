# shared helpers for the atlas checks: a short lived static server on docs and a page opener that records console errors
import contextlib, functools, http.server, socketserver, sys, threading
from pathlib import Path
from playwright.sync_api import sync_playwright

DOCS = "/home/djameldino/ClientMeetingBriefAgent/docs"
PAGE = "brief/explore/atlas/index.html"
SHOTS = Path(__file__).resolve().parent.parent / "shots"
MOUNTS = ["ident", "headline", "hbar", "agent-h", "stepper", "group", "timeline", "wallet", "discuss", "held", "review",
          "questions", "sl1", "sl2", "sl3", "sl4", "sl5"]

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

@contextlib.contextmanager
def serve():
    with socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Q, directory=DOCS)) as h:
        threading.Thread(target=h.serve_forever, daemon=True).start()
        try: yield f"http://127.0.0.1:{h.server_address[1]}"
        finally: h.shutdown()

def open_page(b, base, w, h, reduce=False, q=""):
    pg = b.new_page(viewport={"width": w, "height": h}, reduced_motion="reduce" if reduce else "no-preference")
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{base}/{PAGE}{q}")
    pg.wait_for_function("window.__brief && document.querySelectorAll('[aria-busy=true]').length === 0", timeout=15000)
    pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(1500)
    return pg, errs

def show(pg, i):
    pg.evaluate(f"window.__brief.show({i}, false)"); pg.wait_for_timeout(150)

