"""
Builds a self-contained, JavaScript-free embed for a Squarespace Code Block.

- Every selector is scoped under .cvx so nothing leaks into (or is fought by) the site theme.
- Token CSS is pruned to the variables the snippet actually uses (transitive closure over var()).
- Primary-color and theme toggles are radio inputs + :has(), so they work on every Squarespace
  plan, in the editor preview, and after Squarespace's AJAX page transitions.
"""
import json, os, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSS = open(os.path.join(ROOT, "generated/clearvisit.css")).read()
DARK = open(os.path.join(ROOT, "generated/clearvisit.dark.css")).read()
COMP = open(os.path.join(ROOT, "examples/components.css")).read()
PAL = json.load(open(os.path.join(ROOT, "tokens/primitives/color.tokens.json")))["color"]

def blocks(text):
    """Top-level `selector { decls }` blocks (ignores @media wrappers' inner structure)."""
    out = []
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    for m in re.finditer(r"(^|\n)([^{}\n@][^{}]*?)\s*\{([^{}]*)\}", text):
        out.append((m.group(2).strip(), m.group(3)))
    return out
def decls(body):
    return dict(re.findall(r"(--cv-[a-z0-9-]+):\s*([^;]+);", body))

B = {}
for sel, body in blocks(CSS):
    B.setdefault(sel, decls(body))  # first occurrence wins (skip the reduced-motion :root override)
PRIM, LIGHT = B[":root"], B[':root, [data-theme="light"]']
DESK, MOB = B[':root, [data-platform="desktop"]'], B['[data-platform="mobile"]']
REDO = B[":root, [data-theme], [data-platform]"]
DRK = decls(re.search(r'\[data-theme="dark"\] \{(.*?)\n\}', DARK, re.S).group(1))
ALL = {**PRIM, **LIGHT, **DESK, **REDO}

# ---------- component rules needed by the snippet, re-scoped under .cvx
NEED = ["cv-btn", "cv-provider", "cv-avatar", "cv-strip", "cv-slot", "cv-slots", "cv-tabs", "cv-tab",
        "cv-table", "cv-choice", "cv-badge", "cv-icon", "data-status", "data-theme", "cv-visually-hidden"]
comp_rules = []
for sel, body in blocks(re.sub(r"/\*.*?\*/", "", COMP, flags=re.S)):
    if "@media" in sel or ":focus-visible" in sel or "is-focus" in sel: continue
    if not any(n in sel for n in NEED): continue
    scoped = ", ".join(".cvx " + s.strip() if not s.strip().startswith(".cv ") else ".cvx " + s.strip()[4:]
                       for s in sel.split(","))
    comp_rules.append(f"{scoped}{{{body.strip()}}}")

SNIPPET_CSS = """
.cvx{container-type:inline-size;font-family:var(--cv-font-family-sans);color:var(--cv-color-text-primary);font-size:16px;line-height:1.5;letter-spacing:0;text-transform:none;text-align:left;-webkit-font-smoothing:antialiased}
.cvx *,.cvx *::before,.cvx *::after{box-sizing:border-box;margin:0;letter-spacing:inherit;text-transform:none;font-family:inherit;line-height:inherit;color:inherit}
.cvx :where(table,thead,tbody,tr,th,td){border:0;background:none;padding:0;width:auto;height:auto;font:inherit;color:inherit;text-align:left;vertical-align:middle;box-shadow:none}
.cvx :where(label,span,div,p,i,svg){display:revert;float:none;font-size:inherit;font-weight:inherit;background:none;border:0;padding:0;text-decoration:none}
.cvx .cvx-seg label{display:inline-block}
.cvx .cvx-frame{border:1px solid var(--cv-color-border-default);border-radius:20px;overflow:hidden;background:var(--cv-color-surface-default)}
.cvx .cvx-bar{display:flex;flex-wrap:wrap;gap:12px 28px;align-items:center;padding:16px 20px;border-bottom:1px solid var(--cv-color-border-default)}
.cvx .cvx-group{display:flex;align-items:center;gap:10px;flex-wrap:wrap;border:0;padding:0;min-width:0}
.cvx .cvx-legend{font-size:14px;font-weight:600;padding:0;float:left;margin-right:2px}
.cvx .cvx-seg{position:relative;display:inline-flex;padding:3px;gap:2px;background:var(--cv-color-surface-subtle);border-radius:999px}
.cvx .cvx-seg input{position:absolute;opacity:0;width:1px;height:1px;pointer-events:none}
.cvx .cvx-seg label{cursor:pointer;padding:6px 12px;border-radius:999px;font-size:14px;font-weight:500;color:var(--cv-color-text-secondary);line-height:1.3;user-select:none}
.cvx .cvx-seg input:checked+label{background:var(--cv-color-surface-default);color:var(--cv-color-text-primary);font-weight:600;box-shadow:0 1px 2px rgb(18 24 30/.12)}
.cvx .cvx-seg input:focus-visible+label{outline:var(--cv-focus-ring);outline-offset:1px}
.cvx .cvx-demo{color:var(--cv-color-text-primary);background:var(--cv-color-surface-app)}
.cvx .cvx-stage{display:grid;grid-template-columns:auto minmax(0,1fr);gap:24px;padding:24px;align-items:start}
.cvx .cvx-phone{width:300px;max-width:100%;display:grid;gap:16px;background:var(--cv-color-surface-default);border-radius:var(--cv-radius-card);padding:var(--cv-space-inset-card);box-shadow:0 1px 2px rgb(18 24 30/.08),0 1px 3px rgb(18 24 30/.08)}
.cvx .cvx-name{font-size:var(--cv-provider-card-name-style-font-size);font-weight:var(--cv-provider-card-name-style-font-weight);line-height:1.3}
.cvx .cvx-meta{font-size:14px;color:var(--cv-color-text-secondary);line-height:1.4}
.cvx .cvx-admin{display:grid;gap:14px;min-width:0}
.cvx .cvx-top{display:flex;flex-wrap:wrap;align-items:center;gap:10px}
.cvx .cvx-top .cvx-h{font-size:18px;font-weight:600;margin-right:auto;white-space:nowrap}
.cvx .cvx-scroll{overflow-x:auto;position:relative}
.cvx .cvx-table{background:var(--cv-color-surface-default)}
.cvx .cv-btn{border-style:solid;text-decoration:none}
.cvx .cvx-chain{display:flex;flex-wrap:wrap;align-items:center;gap:8px 10px;padding:14px 20px;border-top:1px solid var(--cv-color-border-default);font-size:13px;background:var(--cv-color-surface-default);color:var(--cv-color-text-primary)}
.cvx .cvx-node{display:inline-flex;align-items:center;gap:8px;padding:4px 9px;border-radius:6px;background:var(--cv-color-surface-subtle);font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:12px}
.cvx .cvx-sw{width:12px;height:12px;border-radius:3px;background:var(--cv-color-action-primary-bg)}
.cvx .cvx-arrow{color:var(--cv-color-text-muted)}
.cvx .cvx-ratio{margin-left:auto;color:var(--cv-color-text-secondary)}
.cvx .cvx-state{display:none}
.cvx .cvx-caption{font-size:14px;color:var(--cv-color-text-secondary);padding:12px 2px 0}
@container (max-width:700px){.cvx .cvx-stage{grid-template-columns:1fr;padding:16px}.cvx .cvx-phone{width:100%}}
@media (prefers-reduced-motion:no-preference){.cvx .cv-btn,.cvx .cv-slot,.cvx .cv-strip__day,.cvx .cvx-sw,.cvx .cvx-demo{transition:background-color .3s cubic-bezier(.2,0,0,1),color .3s,border-color .3s}}
"""

# ---------- CSS-only state: theme + primary hue
HUES = {"blue": "Harbor blue", "teal": "Teal", "violet": "Violet"}
MAP = {"light": {"bg": "600", "bg-hover": "700", "bg-pressed": "800", "fg": None},
       "dark": {"bg": "400", "bg-hover": "300", "bg-pressed": "200", "fg": "950"}}
DEMO_DARK = '.cvx [data-theme="dark"],.cvx:has(#cvx-dark:checked) .cvx-demo'
state_css = []
for hue in ["teal", "violet"]:
    for theme in ["light", "dark"]:
        m = MAP[theme]
        sel = f".cvx:has(#cvx-{hue}:checked)" + (":has(#cvx-dark:checked)" if theme == "dark" else "") + " .cvx-demo"
        fg = "var(--cv-color-white)" if m["fg"] is None else f"var(--cv-color-{hue}-{m['fg']})"
        state_css.append(sel + "{" + "".join(f"--cv-color-action-primary-{k}:var(--cv-color-{hue}-{m[k]});" for k in ["bg", "bg-hover", "bg-pressed"])
                         + f"--cv-color-action-primary-fg:{fg};}}")

def lum(h):
    c = [int(h[i:i+2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.04045 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]
def ratio(a, b):
    x, y = lum(a), lum(b); return (max(x, y) + .05) / (min(x, y) + .05)
readouts, show = [], []
for hue in HUES:
    for theme in ["light", "dark"]:
        m = MAP[theme]
        bg = PAL[hue][m["bg"]]["$value"]["hex"]
        fg = "#FFFFFF" if m["fg"] is None else PAL[hue][m["fg"]]["$value"]["hex"]
        r = ratio(bg, fg)
        sid = f"s-{hue}-{theme}"
        readouts.append(f'<span class="cvx-state {sid}"><span class="cvx-node"><i class="cvx-sw"></i>color.{hue}.{m["bg"]}</span></span>')
        readouts.append(f'<span class="cvx-state {sid} cvx-ratio">Label contrast {r:.2f}:1, {"passes" if r >= 4.5 else "fails"} WCAG AA</span>')
        th = ":has(#cvx-dark:checked)" if theme == "dark" else ":has(#cvx-light:checked)"
        show.append(f".cvx:has(#cvx-{hue}:checked){th} .{sid}{{display:inline-flex}}")
state_css += show

# ---------- prune tokens to what is used (transitive closure)
used_css = SNIPPET_CSS + "\n".join(comp_rules) + "\n".join(state_css)
need, frontier = set(), set(re.findall(r"var\((--cv-[a-z0-9-]+)\)", used_css))
while frontier:
    v = frontier.pop()
    if v in need: continue
    need.add(v)
    for src in (PRIM, LIGHT, DESK, MOB, REDO, DRK):
        if v in src:
            frontier |= set(re.findall(r"var\((--cv-[a-z0-9-]+)\)", src[v])) - need
def emit(sel, d):
    body = "".join(f"{k}:{v};" for k, v in d.items() if k in need)
    return f"{sel}{{{body}}}" if body else ""
tokens_css = "\n".join(filter(None, [
    emit(".cvx", PRIM),
    emit('.cvx,.cvx [data-theme="light"]', LIGHT),
    emit('.cvx,.cvx [data-platform="desktop"]', DESK),
    emit('.cvx [data-platform="mobile"]', MOB),
    emit(DEMO_DARK, DRK),
    emit(".cvx,.cvx [data-theme],.cvx [data-platform]", REDO),
]))
missing = sorted(v for v in need if not any(v in s for s in (PRIM, LIGHT, DESK, MOB, REDO, DRK)))
assert not missing, missing

ICON = {"check": "M5 12.5l4.5 4.5L19 7.5", "clock": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 7v5l3 2",
        "check-circle": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM8 12.5l2.5 2.5L16 9.5", "plus": "M12 5v14M5 12h14",
        "arrow-path": "M4.5 12a7.5 7.5 0 0 1 13-5.1M19.5 12a7.5 7.5 0 0 1-13 5.1M18 3v4h-4M6 21v-4h4"}
def ic(n, cls="cv-icon cv-icon--sm"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="{ICON[n]}"/></svg>'

radios_hue = "".join(f'<input type="radio" name="cvx-hue" id="cvx-{h}"{" checked" if h == "blue" else ""}><label for="cvx-{h}">{l}</label>' for h, l in HUES.items())
radios_theme = '<input type="radio" name="cvx-theme" id="cvx-light" checked><label for="cvx-light">Light</label><input type="radio" name="cvx-theme" id="cvx-dark"><label for="cvx-dark">Dark</label>'

HTML = f'''<!-- ClearVisit design tokens: interactive showcase. No JavaScript; all styles scoped to .cvx. -->
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:wght@400;500;600;700&display=swap" rel="stylesheet">
<div class="cvx">
<style>
{tokens_css}
{SNIPPET_CSS.strip()}
{chr(10).join(comp_rules)}
{chr(10).join(state_css)}
</style>
<div class="cvx-frame">
  <div class="cvx-bar">
    <div class="cvx-group" role="radiogroup" aria-label="Primary action color"><span class="cvx-legend">Primary action</span><span class="cvx-seg">{radios_hue}</span></div>
    <div class="cvx-group" role="radiogroup" aria-label="Theme"><span class="cvx-legend">Theme</span><span class="cvx-seg">{radios_theme}</span></div>
  </div>
  <div class="cvx-demo" data-theme="light">
    <div class="cvx-stage">
      <div class="cvx-phone" data-platform="mobile" aria-label="Patient booking, mobile density">
        <div class="cv-provider"><div class="cv-avatar" aria-hidden="true">AO</div><div><div class="cvx-name">Dr. Amara Okafor</div><div class="cvx-meta">Family medicine, Northgate Clinic</div></div></div>
        <div class="cv-strip">
          <span class="cv-strip__day has-slots" aria-selected="false"><span class="cv-strip__wd">Mon</span><span class="cv-strip__d">26</span></span>
          <span class="cv-strip__day has-slots" aria-selected="true"><span class="cv-strip__wd">Tue</span><span class="cv-strip__d">27</span></span>
          <span class="cv-strip__day" aria-disabled="true"><span class="cv-strip__wd">Wed</span><span class="cv-strip__d">28</span></span>
          <span class="cv-strip__day has-slots" aria-selected="false"><span class="cv-strip__wd">Thu</span><span class="cv-strip__d">29</span></span>
        </div>
        <div class="cv-slots"><span class="cv-slot" aria-pressed="false">9:00</span><span class="cv-slot" aria-disabled="true">9:30<span class="cv-visually-hidden">, booked</span></span><span class="cv-slot" aria-pressed="true">{ic("check")}10:30</span></div>
        <span class="cv-btn" style="width:100%">Book Tue 27, 10:30 AM</span>
      </div>
      <div class="cvx-admin" data-platform="desktop" aria-label="Scheduling admin, desktop density">
        <div class="cvx-top"><span class="cvx-h">Today at Northgate</span><span class="cv-btn cv-btn--secondary">Export</span><span class="cv-btn">{ic("plus")}New appointment</span></div>
        <div class="cv-tabs"><span class="cv-tab" aria-selected="true">Calendar</span><span class="cv-tab" aria-selected="false">Appointments</span><span class="cv-tab" aria-selected="false">Requests</span></div>
        <div class="cvx-scroll"><table class="cv-table cvx-table">
          <thead><tr><th style="width:40px"></th><th>Time</th><th>Patient</th><th>Provider</th><th>Status</th></tr></thead>
          <tbody>
            <tr aria-selected="true"><td><span class="cv-choice is-checked"><span class="cv-choice__box">{ic("check")}</span></span></td><td class="is-num">10:30 AM</td><td>Jordan Ellis</td><td>Dr. Okafor</td><td><span class="cv-badge" data-status="pending">{ic("clock", "cv-icon")}Pending</span></td></tr>
            <tr><td><span class="cv-choice"><span class="cv-choice__box"></span></span></td><td class="is-num">11:00 AM</td><td>Priya Raman</td><td>Dr. Reyes</td><td><span class="cv-badge" data-status="confirmed">{ic("check-circle", "cv-icon")}Confirmed</span></td></tr>
            <tr><td><span class="cv-choice"><span class="cv-choice__box"></span></span></td><td class="is-num">11:30 AM</td><td>Ava Thompson</td><td>Dr. Reyes</td><td><span class="cv-badge" data-status="rescheduled">{ic("arrow-path", "cv-icon")}Rescheduled</span></td></tr>
          </tbody></table></div>
      </div>
    </div>
    <div class="cvx-chain" aria-live="polite">
      {"".join(r for r in readouts if "cvx-ratio" not in r)}
      <span class="cvx-arrow" aria-hidden="true">→</span><span class="cvx-node">color.action.primary.bg</span>
      <span class="cvx-arrow" aria-hidden="true">→</span><span class="cvx-node">button, time-slot, date-strip, checkbox, tabs</span>
      {"".join(r for r in readouts if "cvx-ratio" in r)}
    </div>
  </div>
</div>
<p class="cvx-caption">Live demo built from the ClearVisit token CSS. One semantic token, color.action.primary.bg, drives the primary button, selected time slot, selected date, checkbox and tab indicator in both products; theme and density come from the same token names. Names are sample data.</p>
</div>
'''
out = os.path.join(ROOT, "embed/squarespace-code-block.html")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w").write(HTML)
print("snippet:", len(HTML), "chars;", len(need), "tokens kept;", len(comp_rules), "component rules")
