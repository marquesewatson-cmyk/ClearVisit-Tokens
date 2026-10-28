"""Embed test: the snippet works without JS inside a hostile host page and doesn't leak styles."""
import os, sys
from playwright.sync_api import sync_playwright
R = []
def chk(n, got, want): R.append((n, got == want, got, want))
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1100, "height": 900}, java_script_enabled=False)
    pg.goto("file:///tmp/sq.html")
    cs = lambda s, prop: pg.eval_on_selector(s, f"e=>getComputedStyle(e).{prop}") if False else None
    js = b.new_page(viewport={"width": 1100, "height": 900})  # separate page with JS only for measuring
    js.goto("file:///tmp/sq.html")
    get = lambda s, prop: js.eval_on_selector(s, f"e=>getComputedStyle(e)['{prop}']")
    sel = ".cvx .cv-slot[aria-pressed=true]"
    chk("default: selected slot = blue-600", get(sel, "backgroundColor"), "rgb(0, 106, 190)")
    chk("button height desktop 36px", get(".cvx-admin .cv-btn", "height"), "36px")
    chk("book button height mobile 48px", get(".cvx-phone .cv-btn", "height"), "48px")
    chk("host paragraph untouched", get("#host-p", "textTransform"), "uppercase")
    chk("snippet text not uppercased", get(".cvx .cvx-name", "textTransform"), "none")
    js.click("label[for=cvx-teal]"); js.wait_for_timeout(600)
    chk("teal: selected slot = teal-600", get(sel, "backgroundColor"), "rgb(0, 121, 118)")
    chk("teal: tab indicator = teal-600", get(".cvx .cv-tab[aria-selected=true]", "borderBottomColor"), "rgb(0, 121, 118)")
    js.click("label[for=cvx-dark]"); js.wait_for_timeout(600)
    chk("teal+dark: slot = teal-400", get(sel, "backgroundColor"), "rgb(68, 185, 181)")
    chk("dark: demo text = slate-50", get(".cvx .cvx-name", "color"), "rgb(245, 247, 249)")
    chk("host td background doesn't leak", get(".cvx .cv-table td", "backgroundColor"), "rgba(0, 0, 0, 0)")
    chk("host td side borders don't leak", get(".cvx .cv-table td", "borderLeftWidth"), "0px")
    chk("host table border doesn't leak", get(".cvx .cv-table", "borderTopWidth"), "0px")
    chk("host span line-height doesn't leak", get(".cvx .cvx-meta", "lineHeight") != "38px", True)
    chk("dark: readout visible", js.is_visible(".cvx .s-teal-dark.cvx-ratio"), True)
    chk("light readout hidden in dark", js.is_visible(".cvx .s-teal-light.cvx-ratio"), False)
    js.screenshot(path="/tmp/sq-teal-dark.png", full_page=True)
    # no-JS page: toggles must still work
    pg.click("label[for=cvx-violet]")
    pg.wait_for_timeout(600); chk("no-JS page: violet readout shown", pg.is_visible(".cvx .s-violet-light.cvx-ratio"), True)
    pg.screenshot(path="/tmp/sq-nojs-violet.png", full_page=True)
    m = b.new_page(viewport={"width": 390, "height": 844}); m.goto("file:///tmp/sq.html")
    chk("390px: no horizontal page scroll", m.evaluate("document.documentElement.scrollWidth<=390"), True)
    m.screenshot(path="/tmp/sq-mobile.png", full_page=True)
    b.close()
for n, ok, g, w in R: print("PASS" if ok else "FAIL", n, "" if ok else f"(got {g}, want {w})")
print(f"{sum(r[1] for r in R)}/{len(R)} embed checks passed"); sys.exit(0 if all(r[1] for r in R) else 1)
