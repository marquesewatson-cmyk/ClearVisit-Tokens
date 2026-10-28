"""Browser test (Playwright/Chromium): computed styles prove the token chain works end to end."""
import json, os, sys
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
vals = lambda f: json.load(open(os.path.join(ROOT, "tokens/primitives/color.tokens.json")))["color"]
C = vals(0)
def rgb(hue, step):
    r, g, b = [round(x * 255) for x in C[hue][step]["$value"]["components"]]
    return f"rgb({r}, {g}, {b})"
checks = []
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page()
    pg.goto("file://" + os.path.join(ROOT, "tests/propagation.html"))
    cs = lambda sel, prop: pg.eval_on_selector(sel, f"e => getComputedStyle(e).{prop}")
    def check(name, got, want):
        checks.append((name, got == want, got, want))
    check("light desktop button bg = blue-600", cs("#b0", "backgroundColor"), rgb("blue", "600"))
    check("desktop button height = 36px", cs("#b0", "height"), "36px")
    check("mobile scope button height = 48px", cs("#b1", "height"), "48px")
    check("dark scope button bg = blue-400", cs("#b2", "backgroundColor"), rgb("blue", "400"))
    check("dark scope focus ring = blue-300", cs("#r2", "outlineColor"), rgb("blue", "300"))
    check("dark scope inherited text = slate-50", cs("#t2", "color"), rgb("slate", "50"))
    check("dark + nested mobile: bg blue-400", cs("#b3", "backgroundColor"), rgb("blue", "400"))
    check("dark + nested mobile: height 48px", cs("#b3", "height"), "48px")
    # One semantic change → every consumer updates
    pg.eval_on_selector("#x", "e => e.style.setProperty('--cv-color-action-primary-bg', 'var(--cv-color-teal-700)')")
    # component vars re-resolve only where re-declared: #x is not a scope, so set data-theme to make it one
    pg.eval_on_selector("#x", "e => e.setAttribute('data-theme','light')")
    for sel, name in [("#p1", "button"), ("#p2", "time slot (selected)"), ("#p3", "date strip (selected)"), ("#p4", "checkbox (checked)")]:
        check(f"semantic swap → {name} = teal-700", cs(sel, "backgroundColor"), rgb("teal", "700"))
    check("semantic swap → tab indicator = teal-700", cs("#p5", "borderBottomColor"), rgb("teal", "700"))
    br.close()
for n, ok, got, want in checks:
    print("PASS" if ok else "FAIL", n, "" if ok else f"(got {got}, want {want})")
print(f"{sum(c[1] for c in checks)}/{len(checks)} propagation checks passed")
sys.exit(0 if all(c[1] for c in checks) else 1)
