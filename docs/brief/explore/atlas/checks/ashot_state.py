# usage: ashot_state.py. one shot of client 10 scrolled to part 5 with an answer chosen and step 3 pinned, for review
import sys
from playwright.sync_api import sync_playwright
from ahelp import serve, open_page, show, SHOTS
with serve() as base, sync_playwright() as p:
    b = p.chromium.launch(); pg, errs = open_page(b, base, 1440, 900)
    show(pg, 0); pg.click('[data-act="answer"][data-q="0"][data-a="1"]'); pg.wait_for_timeout(500)
    pg.evaluate("document.getElementById('part-3').scrollIntoView()"); pg.wait_for_timeout(300)
    pg.click('#v-step-5 .v-step-btn'); pg.wait_for_timeout(900); pg.mouse.move(0, 0); pg.wait_for_timeout(300)
    pg.screenshot(path=str(SHOTS / "desktop_client01_answered.png")); b.close()
print("ok", errs)
