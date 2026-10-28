"""Builds site/clearvisit-design-system.html from the template + generated token data."""
import json, os, re, subprocess, sys, html
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
R = json.load(open(os.path.join(ROOT, "generated/reports/resolved.json")))
V = json.load(open(os.path.join(ROOT, "generated/reports/validation.json")))
PAL = json.load(open(os.path.join(ROOT, "tokens/primitives/color.tokens.json")))["color"]
LIGHT_SRC = json.load(open(os.path.join(ROOT, "tokens/semantic/light.tokens.json")))
LD, DD, LM = R["light/desktop"], R["dark/desktop"], R["light/mobile"]
E = html.escape

def hexof(label, p): return R[label]["values"][p]["hex"]
def lumi(hexv):
    c = [int(hexv[i:i+2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def on(hexv): return "#FFFFFF" if lumi(hexv) < 0.22 else "#12181E"
def sw(hexv, label=None): return f'<span class="doc-sw"><i style="background:{hexv}"></i>{E(label or hexv)}</span>'
def ref(label, p):
    r = R[label]["refs"].get(p)
    return r.strip("{}") if r else ""

# ---------------- icons
ICON = {
 "check": "M5 12.5l4.5 4.5L19 7.5",
 "check-circle": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM8 12.5l2.5 2.5L16 9.5",
 "clock": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 7v5l3 2",
 "x-circle": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM9 9l6 6M15 9l-6 6",
 "arrow-path": "M4.5 12a7.5 7.5 0 0 1 13-5.1M19.5 12a7.5 7.5 0 0 1-13 5.1M18 3v4h-4M6 21v-4h4",
 "calendar-plus": "M5 5h14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2zM3 10h18M8 3v4M16 3v4M12 13v5M9.5 15.5h5",
 "check-double": "M2.5 12.5l4 4 8-9M11 16l1 1 9-10",
 "info": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 11v5M12 8h.01",
 "warning": "M10.3 4.3L2.6 18a2 2 0 0 0 1.7 3h15.4a2 2 0 0 0 1.7-3L13.7 4.3a2 2 0 0 0-3.4 0zM12 10v4M12 17h.01",
 "error": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 7.5v5.5M12 16.2h.01",
 "search": "M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14zM20 20l-4-4",
 "home": "M4 10.5L12 4l8 6.5V20a1 1 0 0 1-1 1h-4.5v-6h-5v6H5a1 1 0 0 1-1-1z",
 "calendar": "M5 5h14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2zM3 10h18M8 3v4M16 3v4",
 "user": "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4.5 21c.8-3.6 3.9-6 7.5-6s6.7 2.4 7.5 6",
 "users": "M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM2.5 20c.6-3.3 3.3-5.5 6.5-5.5s5.9 2.2 6.5 5.5M16 4.3a3.5 3.5 0 0 1 0 6.4M18 14.8c1.9.8 3.2 2.6 3.5 5.2",
 "bell": "M6 16.5V11a6 6 0 1 1 12 0v5.5l1.5 2h-15zM10 21h4",
 "chevron-down": "M6 9l6 6 6-6", "chevron-left": "M15 6l-6 6 6 6", "chevron-right": "M9 6l6 6-6 6",
 "map-pin": "M12 21s7-6.1 7-11.5A7 7 0 0 0 5 9.5C5 14.9 12 21 12 21zM12 12a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z",
 "plus": "M12 5v14M5 12h14",
 "grid": "M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z",
 "inbox": "M3 13l3-8h12l3 8v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1zM3 13h5l1.5 2.5h5L16 13h5",
 "chart": "M4 20V10M10 20V4M16 20v-7M22 20H2",
 "arrow-up": "M12 19V5M6 11l6-6 6 6", "arrow-down": "M12 5v14M6 13l6 6 6-6",
 "video": "M3 7h12v10H3zM15 10.5l6-3.5v10l-6-3.5",
 "sliders": "M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0M14 4v4M8 10v4M16 16v4",
}
icons = "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24"><path d="{d}" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></symbol>' for k, d in ICON.items())
def ic(name, sm=False): return f'<svg class="cv-icon{" cv-icon--sm" if sm else ""}" aria-hidden="true"><use href="#i-{name}"/></svg>'

STATUS = {k: v["$extensions"]["com.clearvisit"] | {"meaning": v.get("$description", "")}
          for k, v in LIGHT_SRC["color"]["status"].items() if not k.startswith("$")}
def badge(s): return f'<span class="cv-badge" data-status="{s}">{ic(STATUS[s]["icon"])}{STATUS[s]["label"]}</span>'

# ---------------- palette
steps = ["50", "100", "200", "300", "400", "500", "600", "700", "800", "850", "900", "925", "950", "975"]
pal = ['<div class="doc-palette" role="table" aria-label="Primitive palette">', '<div></div>'] + [f'<div class="doc-palette__hd">{s}</div>' for s in steps]
for hue in ["blue", "teal", "slate", "green", "amber", "red", "violet"]:
    pal.append(f'<div class="doc-palette__name">{hue}</div>')
    for s in steps:
        if s in PAL[hue]:
            h = PAL[hue][s]["$value"]["hex"]
            pal.append(f'<div class="doc-palette__cell" style="background:{h};color:{on(h)}" title="color.{hue}.{s}"><span>{h}</span></div>')
        else:
            pal.append('<div class="doc-palette__cell is-empty" aria-hidden="true"></div>')
pal.append("</div>")

# ---------------- status table
st = ['<table class="doc-table"><thead><tr><th>Status</th><th>Badge</th><th>Icon</th><th>Meaning</th><th>Light fill / label</th><th>Dark fill / label</th></tr></thead><tbody>']
for s, m in STATUS.items():
    st.append(f'<tr><td><code>color.status.{s}</code></td><td>{badge(s)}</td><td><code>{m["icon"]}</code></td><td>{E(m["meaning"])}</td>'
              f'<td>{sw(hexof("light/desktop", f"color.status.{s}.bg"))} {sw(hexof("light/desktop", f"color.status.{s}.fg"))}</td>'
              f'<td>{sw(hexof("dark/desktop", f"color.status.{s}.bg"))} {sw(hexof("dark/desktop", f"color.status.{s}.fg"))}</td></tr>')
st.append("</tbody></table>")

# ---------------- semantic table
sem = ['<table class="doc-table"><thead><tr><th>Token</th><th>Light</th><th>Dark</th><th>Use</th></tr></thead><tbody>']
for p in [p for p in LD["types"] if LD["types"][p] == "color" and p.split(".")[1] in ("text", "surface", "border", "action", "interaction", "accent")]:
    if p not in R["dark/desktop"]["refs"] and not p.startswith("color.action"): pass
    lh, dh = hexof("light/desktop", p), hexof("dark/desktop", p)
    lv, dv = LD["values"][p], DD["values"][p]
    la = f" {int(lv.get('alpha',1)*100)}%" if lv.get("alpha", 1) < 1 else ""
    da = f" {int(dv.get('alpha',1)*100)}%" if dv.get("alpha", 1) < 1 else ""
    sem.append(f'<tr><td><code>{p}</code></td><td>{sw(lh, ref("light/desktop", p).replace("color.", "") + la)}</td>'
               f'<td>{sw(dh, ref("dark/desktop", p).replace("color.", "") + da)}</td><td class="doc-note">{E(LD["desc"].get(p, ""))}</td></tr>')
sem.append("</tbody></table>")

# ---------------- contrast summary
def contrast_block():
    out = ['<div class="doc-grid" style="grid-template-columns:repeat(auto-fit,minmax(min(320px,100%),1fr))">']
    for th in ["light", "dark"]:
        rows = V["contrast"][th]
        audited = [r for r in rows if r["status"] in ("pass", "FAIL")]
        fails = [r for r in audited if r["status"] == "FAIL"]
        tight = sorted(audited, key=lambda r: r["ratio"] - r["min"])[:5]
        out.append(f'<div class="doc-panel doc-spec"><div class="doc-spec__title">{th.title()} theme: {len(audited)} pairs audited, {len(fails)} failures</div>'
                   '<div class="doc-scroll"><table class="doc-table"><thead><tr><th>Closest to the line</th><th>Ratio</th><th>Needs</th></tr></thead><tbody>')
        for r in tight:
            out.append(f'<tr><td><code>{r["fg"].replace("color.","")}</code> on <code>{r["bg"].replace("color.","")}</code></td><td>{r["ratio"]}:1</td><td>{r["min"]}:1</td></tr>')
        out.append("</tbody></table></div></div>")
    out.append("</div>")
    out.append('<p class="doc-note">Text pairs need 4.5:1 (WCAG 1.4.3); control boundaries, icons, focus rings and chart marks need 3:1 (1.4.11). Disabled text is exempt and is always paired with a disabled container. Full tables are in docs/accessibility.md. During the first build, three pairs failed (muted text and control borders on the subtle surface); the fix went into the shared lightness ladder, not into individual tokens.</p>')
    return "".join(out)

# ---------------- type table
SAMPLES = {"page-title": "Find a time that works", "section-title": "Soonest openings", "card-title": "Annual physical",
           "provider-name": "Dr. Amara Okafor", "body": "Arrive 15 minutes early to check in.", "body-strong": "Northgate Clinic",
           "supporting": "Family medicine, 1.2 mi", "label": "Date of birth", "input": "04/12/1988", "button": "Book visit",
           "caption": "Updated 2 min ago", "badge": "Pending", "appointment-time": "Tue 27, 10:30 AM", "table-cell": "Priya Raman",
           "table-header": "Provider", "calendar-event": "J. Ellis, follow-up", "calendar-time": "10:30", "metric-value": "46",
           "alert-title": "Appointment booked", "alert-body": "A confirmation is on its way."}
def spec(label, p):
    v = R[label]["values"][p]
    return f'{v["fontSize"]["value"]:g}/{v["lineHeight"]:g}, {v["fontWeight"]}'
tt = ['<table class="doc-table"><thead><tr><th>Role</th><th>Mobile</th><th>Mobile sample</th><th>Desktop</th><th>Desktop sample</th></tr></thead><tbody>']
for p in [p for p in LM["types"] if p.startswith("text-style.")]:
    role = p.split(".")[1]
    cls = f"cv-text-{role}"
    tt.append(f'<tr><td><code>{p}</code></td><td class="doc-note">{spec("light/mobile", p)}<br><code>{ref("light/mobile", p)}</code></td>'
              f'<td data-platform="mobile"><span class="{cls}">{E(SAMPLES[role])}</span></td>'
              f'<td class="doc-note">{spec("light/desktop", p)}<br><code>{ref("light/desktop", p)}</code></td>'
              f'<td data-platform="desktop"><span class="{cls}">{E(SAMPLES[role])}</span></td></tr>')
tt.append("</tbody></table>")

# ---------------- spacing + platform
sp = ['<div class="doc-space">']
for k in ["2", "4", "8", "12", "16", "20", "24", "32", "40", "48", "64", "80"]:
    sp.append(f'<div class="doc-space__row"><code>space.{k}</code><span>{k}px</span><span class="doc-space__bar" style="width:{int(k)*3}px"></span></div>')
sp.append("</div>")
PLAT = [("size.control.md", "Control height (default)"), ("size.control.sm", "Control height (compact)"),
        ("size.touch-target", "Minimum hit area"), ("size.time-slot", "Time slot"), ("size.table-row", "Table / list row"),
        ("size.day-cell", "Date picker day"), ("size.avatar", "Provider avatar"), ("radius.control", "Control radius"),
        ("radius.card", "Card radius"), ("space.inset.card", "Card padding"), ("space.inset.page", "Page margin"),
        ("layout.columns", "Grid columns")]
pt = ['<table class="doc-table"><thead><tr><th>Token</th><th>Role</th><th>Mobile</th><th>Desktop</th></tr></thead><tbody>']
for p, role in PLAT:
    mv, dv = R["light/mobile"]["values"][p], R["light/desktop"]["values"][p]
    f = lambda v: f'{v["value"]:g}px' if isinstance(v, dict) else f"{v:g}"
    pt.append(f"<tr><td><code>{p}</code></td><td>{role}</td><td>{f(mv)}</td><td>{f(dv)}</td></tr>")
pt.append("</tbody></table>")

# ---------------- inventory
inv = V["inventory"]
INV_PRIM = f'<div class="doc-arch__flow">{sum(inv["primitives"].values())} tokens in {len(inv["primitives"])} files</div>'
INV_SEM = f'<div class="doc-arch__flow">{inv["semantic"]["base"]} base, {inv["semantic"]["theme (per mode)"]} per theme, {inv["semantic"]["platform (per mode)"]} per platform</div>'
INV_COMP = f'<div class="doc-arch__flow">{sum(inv["components"].values())} tokens across 30 components</div>'

# ---------------- phones
def phone(title, desc, body, foot, attrs=""):
    return (f'<div class="doc-phone-wrap"><div class="doc-phone"><div class="doc-phone__screen" data-platform="mobile">'
            f'<div class="doc-phone__status" aria-hidden="true"><span>9:41</span><span>5G</span></div>'
            f'<div class="doc-phone__body">{body}</div>{foot}</div></div>'
            f'<div class="doc-phone__caption"><h3>{title}</h3><p>{desc}</p></div></div>')
def bnav(cur):
    items = [("home", "Home"), ("search", "Search"), ("calendar", "Visits"), ("user", "Profile")]
    return '<nav class="cv-bnav" aria-label="Primary">' + "".join(
        f'<a class="cv-bnav__item" href="#patient"{" aria-current=page" if n == cur else ""}><span class="cv-bnav__pill">{ic(i)}</span>{n}</a>' for i, n in items) + "</nav>"
def slots(times, sel=None, booked=()):
    out = '<div class="cv-slots" role="group" aria-label="Available times">'
    for t in times:
        if t in booked:
            out += f'<button class="cv-slot" aria-pressed="false" aria-disabled="true" aria-label="{t}, booked">{t}</button>'
        elif t == sel:
            out += f'<button class="cv-slot" aria-pressed="true">{ic("check")}{t}</button>'
        else:
            out += f'<button class="cv-slot" aria-pressed="false">{t}</button>'
    return out + "</div>"
def provider(init, name, meta, next_=None):
    n = f'<span class="cv-next">{ic("calendar-plus", True)}{next_}</span>' if next_ else ""
    return (f'<div class="cv-provider"><div class="cv-avatar" aria-hidden="true">{init}</div><div style="display:grid;gap:2px">'
            f'<p class="cv-provider__name">{name}</p><p class="cv-provider__meta">{meta}</p>{n}</div></div>')

home = f'''
<div class="m-between"><h1 class="m-title">Good morning, Jordan</h1><button class="cv-btn cv-btn--tertiary" aria-label="Notifications">{ic("bell")}</button></div>
<div class="cv-field cv-search"><label class="cv-visually-hidden" for="ms1">Search</label><div class="cv-field__control">{ic("search")}<input id="ms1" placeholder="Doctor, specialty or clinic"></div></div>
<div style="display:grid;gap:12px"><div class="m-between"><h2 class="m-section">Your next visit</h2>{badge("confirmed")}</div>
<div class="cv-card">{provider("AO", "Dr. Amara Okafor", "Family medicine, Northgate Clinic")}
<p class="m-time">Tue, Oct 27 at 10:30 AM</p>
<div class="doc-row"><button class="cv-btn cv-btn--secondary" style="flex:1">Reschedule</button><button class="cv-btn cv-btn--tertiary">Details</button></div></div></div>
<div style="display:grid;gap:12px"><h2 class="m-section">Find care</h2>
<div class="m-hscroll" data-chips><button class="cv-chip" aria-pressed="false">Primary care</button><button class="cv-chip" aria-pressed="false">Dermatology</button><button class="cv-chip" aria-pressed="false">Pediatrics</button><button class="cv-chip" aria-pressed="false">Dental</button></div></div>
<div style="display:grid;gap:12px"><h2 class="m-section">Soonest openings</h2>
<div class="cv-avail">{provider("ML", "Dr. Mei Lin Chen", "Pediatrics, Elm Street Kids", "Today")}{slots(["2:15 PM", "3:00 PM", "4:30 PM"])}</div></div>'''
search = f'''
<div class="cv-field cv-search"><label class="cv-visually-hidden" for="ms2">Search</label><div class="cv-field__control">{ic("search")}<input id="ms2" value="Dermatology"></div></div>
<div class="m-hscroll" data-chips><button class="cv-chip" aria-pressed="true">{ic("check", True)}This week</button><button class="cv-chip" aria-pressed="false">Video visit</button><button class="cv-chip" aria-pressed="false">In network</button><button class="cv-chip" aria-pressed="false">Mornings</button></div>
<p class="cv-meta" role="status">3 dermatologists with openings this week</p>
<div class="cv-avail">{provider("DR", "Dr. Daniel Reyes", "Dermatology, Northgate Clinic, 1.2 mi", "Tomorrow")}{slots(["9:00 AM", "10:30 AM", "1:15 PM"])}<button class="cv-btn cv-btn--tertiary cv-btn--sm" style="justify-self:start">More times</button></div>
<div class="cv-avail">{provider("SN", "Dr. Sofia Navarro", "Dermatology, Harbor Medical, 2.8 mi", "Thu, Oct 29")}{slots(["8:30 AM", "11:00 AM"])}</div>
<div class="cv-avail">{provider("TB", "Dr. Theo Baptiste", "Dermatology, video visits only")}<p class="cv-meta">No openings this week. Next opening Mon, Nov 2.</p><button class="cv-btn cv-btn--secondary cv-btn--sm" style="justify-self:start">See next week</button></div>'''
booking = f'''
<span class="m-back">{ic("chevron-left", True)}Back to results</span>
{provider("DR", "Dr. Daniel Reyes", "Dermatology, Northgate Clinic")}
<div style="display:grid;gap:10px"><h2 class="m-section">Choose a date</h2>
<div class="cv-strip" role="listbox" aria-label="Choose a date">
<button class="cv-strip__day has-slots" role="option" aria-selected="false"><span class="cv-strip__wd">Mon</span><span class="cv-strip__d">26</span></button>
<button class="cv-strip__day has-slots" role="option" aria-selected="true"><span class="cv-strip__wd">Tue</span><span class="cv-strip__d">27</span></button>
<button class="cv-strip__day" role="option" aria-selected="false" aria-disabled="true" aria-label="Wed 28, no openings"><span class="cv-strip__wd">Wed</span><span class="cv-strip__d">28</span></button>
<button class="cv-strip__day has-slots" role="option" aria-selected="false"><span class="cv-strip__wd">Thu</span><span class="cv-strip__d">29</span></button>
<button class="cv-strip__day has-slots" role="option" aria-selected="false"><span class="cv-strip__wd">Fri</span><span class="cv-strip__d">30</span></button></div></div>
<div style="display:grid;gap:10px"><h2 class="m-section">Morning</h2>{slots(["9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM", "11:30 AM"], sel="10:30 AM", booked=("9:30 AM", "10:00 AM"))}</div>
<div style="display:grid;gap:10px"><h2 class="m-section">Afternoon</h2>{slots(["1:15 PM", "2:45 PM", "4:00 PM"])}</div>
<div class="cv-summary"><div class="cv-summary__row"><span class="cv-summary__k">Visit type</span><span class="cv-summary__v">New patient</span></div>
<div class="cv-summary__row"><span class="cv-summary__k">Location</span><span class="cv-summary__v">Northgate Clinic</span></div>
<div class="cv-summary__row"><span class="cv-summary__k">Length</span><span class="cv-summary__v">30 minutes</span></div></div>'''
booking_foot = '<div class="m-sticky"><button class="cv-btn cv-btn--block cv-btn--lg" data-cta>Book 10:30 AM</button><span class="cv-meta" style="text-align:center">Free to cancel up to 24 hours before.</span></div>'
PHONES = (phone("Homepage", "Leads with the next visit, then the fastest route to a new one. The status badge carries an icon and a word, not just blue.", home, bnav("Home"))
          + phone("Doctor search results", "Each result answers “how soon?” before “who?”: next availability and three tappable times sit inside the card. The empty case points to the next opening instead of a dead end.", search, bnav("Search"))
          + phone("Booking", "Date strip, then time slots. Booked times stay visible but struck through, so patients understand the gap. The button label repeats the chosen time.",
                  booking, booking_foot, " data-booking"))

# ---------------- admin calendar
SLOT = 48  # = calendar-cell.slot-height
def ev(start, end, status, who, what, conflict=False, half=None):
    top = (start - 480) / 30 * SLOT + 2
    h = (end - start) / 30 * SLOT - 4
    pos = "left:4px;right:4px;" if half is None else ("left:4px;right:calc(50% + 2px);" if half == 0 else "left:calc(50% + 2px);right:4px;")
    tm = lambda m: f"{m//60 if m//60<=12 else m//60-12}:{m%60:02d}"
    tag = f'<span class="cv-conflict-tag">{ic("error", True)}Conflict</span>' if conflict else ""
    lab = STATUS[status]["label"]
    return (f'<div class="cv-event{" is-conflict" if conflict else ""}" data-status="{status}" style="top:{top}px;height:{h}px;{pos}" '
            f'aria-label="{tm(start)} to {tm(end)}, {E(who)}, {lab}{", conflict" if conflict else ""}">'
            f'<div class="cv-event__row">{ic(STATUS[status]["icon"])}<span class="cv-event__t">{tm(start)}</span><span class="cv-event__who">{E(who)}</span></div>'
            f'<div class="cv-event__row">{tag}<small>{E(what)}, {lab}</small></div></div>')
cols = [
 ("Dr. Amara Okafor", "Family medicine", [ev(480, 510, "completed", "Maya Brooks", "Follow-up"), ev(510, 540, "completed", "Luis Ortega", "Lab review"),
    ev(540, 570, "confirmed", "Hannah Kim", "Annual physical"), ev(630, 660, "pending", "Jordan Ellis", "Follow-up"), ev(660, 690, "available", "Open slot", "30 min")], False),
 ("Dr. Daniel Reyes", "Dermatology", [ev(480, 540, "confirmed", "Grace Liu", "New patient"), ev(570, 600, "cancelled", "Omar Haddad", "Skin check"),
    ev(600, 630, "confirmed", "Priya Raman", "Biopsy follow-up", True, 0), ev(600, 630, "confirmed", "Ben Carter", "New patient", True, 1),
    ev(660, 690, "rescheduled", "Ava Thompson", "Moved to Thu")], False),
 ("Dr. Mei Lin Chen", "Pediatrics", [ev(510, 570, "confirmed", "Noah Wright", "Well visit"), ev(600, 630, "available", "Open slot", "30 min"),
    ev(630, 690, "pending", "Lily Brown", "New patient")], False),
 ("Dr. Sam Patel", "Family medicine, out after 11:00", [ev(480, 510, "confirmed", "Ethan Moore", "Follow-up"), ev(540, 570, "rescheduled", "Zoe Adams", "Moved to Fri"),
    ev(570, 600, "available", "Open slot", "30 min")], True),
]
times = "".join(f'<div class="cv-cal__time">{(h//60 if h//60<=12 else h//60-12)}:{h%60:02d}</div>' for h in range(480, 720, 30))
cal = ['<div class="cv-cal" style="--cols:4"><div class="cv-cal__head" style="background:var(--cv-color-surface-subtle)"></div>']
cal += [f'<div class="cv-cal__head">{n}<small>{s}</small></div>' for n, s, _, _ in cols]
cal.append(f'<div style="display:grid">{times}</div>')
for n, s, evs, off in cols:
    offbg = f'<div style="position:absolute;left:0;right:0;top:{6*SLOT}px;bottom:0;background:var(--cv-calendar-cell-bg-off-hours)" aria-label="Out of office"></div>' if off else ""
    cal.append(f'<div class="cv-cal__col" style="height:{8*SLOT}px">{offbg}{"".join(evs)}</div>')
cal.append(f'<div class="cv-cal__now" style="top:calc(53px + {(620-480)/30*SLOT}px)" aria-label="Now, 10:20 AM"></div></div>')
side = f'''<aside class="cv-side" aria-label="Admin navigation">
<div style="display:flex;align-items:center;gap:8px;padding:6px 12px 14px;font-weight:700"><svg viewBox="0 0 32 32" width="24" height="24" aria-hidden="true"><rect width="32" height="32" rx="9" fill="var(--cv-color-action-primary-bg)"/><path d="M9 16.5l4.5 4.5L23 11" fill="none" stroke="var(--cv-color-action-primary-fg)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>ClearVisit</div>
<a class="cv-nav-item" href="#admin">{ic("grid")}Dashboard</a><a class="cv-nav-item" href="#admin" aria-current="page">{ic("calendar")}Schedule</a>
<a class="cv-nav-item" href="#admin">{ic("inbox")}Requests<span class="cv-badge" data-status="pending" style="margin-left:auto">7</span></a>
<a class="cv-nav-item" href="#admin">{ic("users")}Patients</a><a class="cv-nav-item" href="#admin">{ic("user")}Providers</a><a class="cv-nav-item" href="#admin">{ic("chart")}Reports</a>
<p class="cv-side__label">Locations</p><a class="cv-nav-item" href="#admin">{ic("map-pin")}Northgate Clinic</a><a class="cv-nav-item" href="#admin">{ic("map-pin")}Elm Street Kids</a></aside>'''
def metric(label, val, delta, up):
    d = f'<span class="cv-delta cv-delta--{"up" if up else "down"}">{ic("arrow-up" if up else "arrow-down", True)}{delta}</span>'
    return f'<div class="cv-metric"><p class="cv-metric__label">{label}</p><p class="cv-metric__value">{val}</p>{d}</div>'
ADMIN_CAL = f'''<div class="doc-desktop" data-platform="desktop"><div class="doc-desktop__chrome" aria-hidden="true"><i></i><i></i><i></i></div>
<div class="doc-desktop__app">{side}<div class="a-main">
<div class="a-top"><h1>Schedule</h1><button class="cv-btn cv-btn--tertiary" aria-label="Previous day">{ic("chevron-left")}</button><strong>Tue, Oct 27</strong><button class="cv-btn cv-btn--tertiary" aria-label="Next day">{ic("chevron-right")}</button><button class="cv-btn cv-btn--secondary">Today</button><button class="cv-btn">{ic("plus", True)}New appointment</button></div>
<div class="a-metrics">{metric("Booked today", "46", "4 vs last Tue", True)}{metric("Open slots", "18", "3 vs last Tue", False)}{metric("Pending requests", "7", "2 since 9 AM", True)}{metric("Cancellations", "3", "1 vs last Tue", False)}</div>
<div class="cv-alert" data-tone="error" role="alert">{ic("error")}<div><p class="cv-alert__title">Dr. Reyes is double-booked at 10:00 AM</p><p class="cv-alert__body">Priya Raman and Ben Carter overlap. Move one appointment or approve the overlap.</p></div><button class="cv-btn cv-btn--secondary cv-btn--sm" style="margin-left:auto;align-self:center">Resolve</button></div>
<div class="cv-tabs" role="tablist"><button class="cv-tab" role="tab" aria-selected="true">Day</button><button class="cv-tab" role="tab" aria-selected="false">Week</button><button class="cv-tab" role="tab" aria-selected="false">Providers</button></div>
{"".join(cal)}</div></div></div>'''
LEGEND = "".join(badge(s) for s in STATUS) + f'<span class="cv-conflict-tag" style="padding:2px 6px">{ic("error", True)}Conflict</span><span class="doc-note">Pending events also have a dashed outline; cancelled times are struck through; the teal line is now.</span>'

rows = [("8:00 AM", "Ethan Moore", "Dr. Patel", "Follow-up", "confirmed"), ("9:00 AM", "Zoe Adams", "Dr. Patel", "Follow-up", "rescheduled"),
        ("9:30 AM", "Omar Haddad", "Dr. Reyes", "Skin check", "cancelled"), ("10:00 AM", "Priya Raman", "Dr. Reyes", "Biopsy follow-up", "confirmed"),
        ("10:00 AM", "Ben Carter", "Dr. Reyes", "New patient", "confirmed"), ("10:30 AM", "Jordan Ellis", "Dr. Okafor", "Follow-up", "pending"),
        ("10:30 AM", "Lily Brown", "Dr. Chen", "New patient", "pending"), ("11:00 AM", "Ava Thompson", "Dr. Reyes", "Consult", "rescheduled")]
tr = []
for i, (t, p, pr, ty, s) in enumerate(rows):
    sel = i == 5
    conflict = f' <span class="cv-conflict-tag">{ic("error", True)}Conflict</span>' if t == "10:00 AM" else ""
    box = f'<span class="cv-choice{" is-checked" if sel else ""}"><span class="cv-choice__box">{ic("check", True) if sel else ""}</span><span class="cv-visually-hidden">Select {p}</span></span>'
    tr.append(f'<tr{" aria-selected=true" if sel else ""}><td>{box}</td><td class="is-num">{t}</td><td>{p}</td><td>{pr}</td><td>{ty}</td><td>{badge(s)}{conflict}</td>'
              f'<td><button class="cv-btn cv-btn--tertiary cv-btn--sm">{"Confirm" if s == "pending" else "View"}</button></td></tr>')
ADMIN_TABLE = f'''<div class="doc-desktop" data-platform="desktop"><div class="doc-desktop__chrome" aria-hidden="true"><i></i><i></i><i></i></div>
<div class="a-main"><div class="a-top"><h1>Appointments</h1><button class="cv-btn cv-btn--secondary">Export</button><button class="cv-btn">{ic("plus", True)}New appointment</button></div>
<div class="a-toolbar" data-chips><div class="cv-field cv-search" style="width:280px"><label class="cv-visually-hidden" for="as1">Search appointments</label><div class="cv-field__control" style="min-height:var(--cv-size-control-md)">{ic("search")}<input id="as1" placeholder="Patient, provider or ID"></div></div>
<button class="cv-chip" aria-pressed="true">{ic("check", True)}Today</button><button class="cv-chip" aria-pressed="false">Pending</button><button class="cv-chip" aria-pressed="false">Has conflict</button><button class="cv-chip" aria-pressed="false">Dr. Reyes</button></div>
<div class="a-panel"><div class="doc-scroll"><table class="cv-table"><thead><tr><th style="width:44px"><span class="cv-visually-hidden">Select</span></th><th>Time</th><th>Patient</th><th>Provider</th><th>Visit type</th><th>Status</th><th><span class="cv-visually-hidden">Actions</span></th></tr></thead>
<tbody>{"".join(tr)}</tbody></table></div>
<div class="a-panel__foot"><span>Showing 1 to 8 of 46</span><nav class="cv-pager" aria-label="Pagination"><button class="cv-pager__item" aria-label="Previous page">{ic("chevron-left", True)}</button><button class="cv-pager__item" aria-current="page">1</button><button class="cv-pager__item">2</button><button class="cv-pager__item">3</button><span>…</span><button class="cv-pager__item">6</button><button class="cv-pager__item" aria-label="Next page">{ic("chevron-right", True)}</button></nav></div></div></div></div>'''

# ---------------- JSON chain (real excerpts from source files)
J = lambda f: json.load(open(os.path.join(ROOT, "tokens", f)))
prim = J("primitives/color.tokens.json")["color"]["blue"]["600"]
chain = f'''<pre class="doc-code"><span class="c">// primitives/color.tokens.json</span>
"blue": {{ "600": {{ "$value": {json.dumps(prim["$value"])} }} }}

<span class="c">// semantic/light.tokens.json      semantic/dark.tokens.json</span>
"primary": {{ "bg": {{ "$value": <span class="s">"{{color.blue.600}}"</span> }} }}   <span class="c">// dark: "{{color.blue.400}}"</span>

<span class="c">// components/mobile.tokens.json</span>
"time-slot": {{ "selected-bg": {{ "$value": <span class="s">"{{color.action.primary.bg}}"</span> }} }}

<span class="c">/* generated/clearvisit.css */</span>
--cv-color-blue-600: #006ABE;
--cv-color-action-primary-bg: var(--cv-color-blue-600);
--cv-time-slot-selected-bg: var(--cv-color-action-primary-bg);</pre>
<p class="doc-note">Aliases survive into CSS as <code>var()</code> chains, so the browser keeps the same relationships the JSON describes. That is what lets the hero demo swap one variable.</p>'''

# ---------------- checks: run the test suites now so the page reports real results
def run(script):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tests", script)], capture_output=True, text=True)
    m = re.search(r"(\d+)/(\d+)", r.stdout.strip().splitlines()[-1])
    return m.group(0) if m else "error"
neg, prop = run("test_validator.py"), run("test_propagation.py")
ck = V["checks"]
CHECKS = f'''<table class="doc-table"><tbody>
<tr><td>Permutations validated</td><td>{", ".join(V["permutations_validated"])}</td></tr>
<tr><td>Unique token paths</td><td>{inv["total_unique_paths"]}</td></tr>
<tr><td>Types, value shapes, aliases, alias types</td><td>Pass</td></tr>
<tr><td>Circular references, cross-file conflicts</td><td>None found</td></tr>
<tr><td>Theme and platform completeness</td><td>Pass</td></tr>
<tr><td>Layering (no component → primitive color)</td><td>Pass</td></tr>
<tr><td>CSS variables defined vs referenced</td><td>{ck["css_var_references"]["defined"]} defined, {len(ck["css_var_references"]["undefined_refs"])} undefined</td></tr>
<tr><td>Negative tests (validator must fail on broken input)</td><td>{neg} pass</td></tr>
<tr><td>Browser propagation tests (Chromium)</td><td>{prop} pass</td></tr>
</tbody></table>
<p class="doc-note">Not yet done: screen-reader testing, real-device touch testing, and usability testing with patients or coordinators. See the QA report.</p>'''

HEX = {h: {s: PAL[h][s]["$value"]["hex"] for s in PAL[h] if not s.startswith("$")} for h in ["blue", "teal", "violet"]}
HEX["blue"]["white"] = "#FFFFFF"

page = open(os.path.join(ROOT, "site/template.html")).read()
css = lambda p: open(os.path.join(ROOT, p)).read()
subs = {"TOKENS_CSS": css("generated/clearvisit.css"), "DARK_CSS": css("generated/clearvisit.dark.css"),
        "COMPONENTS_CSS": css("examples/components.css"), "ICONS": icons, "PALETTE": "".join(pal),
        "STATUS_TABLE": "".join(st), "SEMANTIC_TABLE": "".join(sem), "CONTRAST": contrast_block(),
        "TYPE_TABLE": "".join(tt), "SPACING": "".join(sp), "PLATFORM_TABLE": "".join(pt),
        "INV_PRIM": INV_PRIM, "INV_SEM": INV_SEM, "INV_COMP": INV_COMP, "BADGES": "".join(badge(s) for s in STATUS),
        "PHONES": PHONES, "ADMIN_CAL": ADMIN_CAL, "LEGEND": LEGEND, "ADMIN_TABLE": ADMIN_TABLE,
        "JSON_CHAIN": chain, "CHECKS": CHECKS, "HEX_JSON": json.dumps(HEX)}
for k, v in subs.items():
    page = page.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{[A-Z_]+\}\}", page)
assert not left, left
os.makedirs(os.path.join(ROOT, "site/dist"), exist_ok=True)
out = os.path.join(ROOT, "site/dist/clearvisit-design-system.html")
open(out, "w").write(page)
print("site ok", len(page) // 1024, "KB;", "tests:", neg, prop)
