"""Writes docs/component-specs.md: authored guidance + generated token tables per component."""
import json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
R = json.load(open(os.path.join(ROOT, "generated/reports/resolved.json")))
SRC = {f: json.load(open(os.path.join(ROOT, "tokens/components", f + ".tokens.json"))) for f in ["shared", "mobile", "desktop"]}

# Components with no tokens of their own (by design) map to the tokens they consume.
NOTES = {
 "button": ("Buttons", "shared", "Default, hover, pressed, focus-visible, disabled. Loading = disabled + spinner + `aria-busy`.",
   "Label always visible (icon-only buttons need `aria-label`). Min hit area = `size.touch-target`. Destructive confirms in a modal, never on first tap. Disabled buttons keep text at `color.interaction.disabled.fg`, which is WCAG-exempt; prefer explaining why an action is unavailable.",
   "Mobile 48px default height, 16px text, 12px radius; desktop 36px, 14px, 6px."),
 "field": ("Text inputs (shared by search and dropdown triggers)", "shared", "Default, hover, focus (2px ring via border + 1px shadow), error (red border + icon + message), disabled, read-only.",
   "Visible `<label>` always; placeholder is a hint, not a label. Errors use `aria-invalid` + `aria-describedby` and an icon so they don't rely on red. Mobile text stays 16px to prevent iOS zoom.",
   "Height 48 vs 36; text 16 vs 14."),
 "search": ("Search fields", "shared", "Empty, typing, with results, no results.", "Use `role=search` on the form; announce result counts with a polite live region.", "Mobile uses the 56px `size.control.lg` pill on the home screen; desktop toolbar search uses `size.control.md`."),
 "dropdown": ("Dropdowns", "shared", "Closed, open, option hover, option selected (bold + check icon), disabled option.", "Native `<select>` on mobile where possible; custom listbox follows the ARIA listbox pattern with arrow-key support.", "Mobile prefers a bottom sheet for long lists."),
 "checkbox": ("Checkboxes", "shared", "Unchecked, checked (fill + check glyph), indeterminate (fill + dash), disabled, focus.", "Visual box is 24/18px but the clickable label row is at least `size.touch-target`. Border uses `color.border.strong` (3:1).", "Box 24 vs 18."),
 "radio": ("Radio buttons", "shared", "Unselected, selected (ring + dot), disabled, focus.", "Group with `fieldset`/`legend`; arrow keys move selection.", "Same as checkbox."),
 "badge": ("Status badges", "shared", "One per appointment status, plus feedback tones.", "Icon + text label always; icon is `aria-hidden` because the label carries meaning. Never truncate the label.", "Identical on both platforms (12px label)."),
 "card": ("Cards", "shared", "Static, interactive (hover border), selected (uses `color.surface.selected`).", "Interactive cards have one primary link target; don't nest buttons inside a clickable card.", "Radius 16 vs 8, padding 16 vs 20."),
 "tabs": ("Tabs", "shared", "Default, hover, selected (bold + 3px indicator), focus, disabled.", "ARIA tabs pattern; selected state is weight + indicator, not color alone.", "Height 48 vs 36."),
 "alert": ("Alerts", "shared", "Info, success, warning, error; optional action and dismiss.", "`role=status` for non-urgent, `role=alert` for errors that block work. Icon differs per tone.", "Text 16 vs 14."),
 "modal": ("Modals", "shared", "Enter (300ms decelerate), open, exit (200ms accelerate).", "Focus trapped and returned on close; Escape closes; title linked by `aria-labelledby`. Destructive confirmations name the object (“Cancel Dr. Okafor, Tue 10:30?”).", "Mobile renders as a bottom sheet (top radius 24); desktop centered dialog, max 560px."),
 "tooltip": ("Tooltips", "shared", "Hidden, shown after 400ms hover or on focus.", "Supplementary only: never the sole location of essential information; dismissible with Escape (WCAG 1.4.13).", "Mobile avoids tooltips; use inline help text instead."),
 "nav-item": ("Navigation", "shared", "Default, hover, current (fill + bold + `aria-current`).", "Current page announced via `aria-current=page`.", "Mobile primary nav is the bottom nav component; desktop uses the sidebar."),
 "date-picker": ("Date pickers", "shared", "Default, today (ring), selected (fill), has-openings (dot), unavailable (struck + disabled), outside month (muted).", "ARIA grid pattern; the dot is decorative and the accessible name includes “openings available”.", "Day cell 44 vs 32."),
 "time-selector": ("Time selectors", "shared", "Option default, hover, selected (fill + bold + check).", "Times use 12-hour format with AM/PM in labels; listbox pattern.", "Option height 48 vs 36."),
 "provider-card": ("Provider profile cards", "mobile", "Default, pressed.", "Avatar is decorative (initials); name is the heading. “Next available” has an icon and text.", "Mobile-first; desktop admin shows providers in tables instead."),
 "availability-card": ("Appointment availability cards", "mobile", "With openings, no openings this week (shows next date + secondary action).", "Slots are real buttons inside the card; the card itself is not clickable to avoid nested interactive targets.", "Mobile only."),
 "booking-card": ("Appointment booking cards", "mobile", "Draft, ready to book, booking (loading), booked (success alert).", "Primary CTA repeats the chosen time (“Book 10:30 AM”).", "Mobile only."),
 "date-strip": ("Date selection controls", "mobile", "Default, has openings (dot), selected (fill), no openings (dashed + disabled).", "`listbox` with `aria-selected`; unavailable days announce “no openings”.", "Mobile only; desktop uses the date picker."),
 "time-slot": ("Time-slot selection buttons", "mobile", "Default, hover, selected (fill + check icon + `aria-pressed`), booked (disabled fill + strike-through + “booked” in label).", "Booked slots stay visible so the gap in availability is understandable. 48px tall, 88px minimum width.", "Tokens resolve to 32px on desktop if reused in admin quick-book."),
 "summary-card": ("Appointment summary cards", "mobile", "Static.", "Key/value rows read in order; values are left-aligned on narrow screens if they wrap.", "Mobile only."),
 "bottom-nav": ("Mobile bottom navigation", "mobile", "Item default, current (pill + bold + `aria-current`).", "Four destinations max; labels always shown under icons.", "Mobile only."),
 "calendar-cell": ("Scheduling calendar cells", "desktop", "Working hours, off-hours (subtle fill), today, now line (teal).", "Now line is decorative; current time is also shown in the header.", "Desktop only."),
 "calendar-event": ("Calendar event cards", "desktop", "Per status (fill + bar + icon + text), pending (dashed outline), cancelled (struck time), conflict (red outline + “Conflict” tag).", "Each event has an accessible name with time, patient, status and conflict state.", "Desktop only."),
 "table": ("Data table rows and headers", "desktop", "Row default, hover, selected (fill + 3px left bar + checked box).", "Real `<table>` with `<th scope>`; times use tabular figures.", "Desktop 40px rows; tokens give 56px rows if the table pattern is used on mobile lists."),
 "status-indicator": ("Scheduling status indicators", "desktop", "Per status: icon + label (dot variant for dense views must keep the label).", "Never dot-only.", "Desktop only."),
 "filter-chip": ("Filter controls", "desktop", "Default, selected (fill + check icon + bold), focus.", "Toggle buttons with `aria-pressed`.", "Also used on the patient search screen; see QA report (candidate to promote to shared)."),
 "pagination": ("Pagination", "desktop", "Default, hover, current (fill + bold + `aria-current`), disabled prev/next.", "Wrapped in `nav` with a label; prev/next have text labels for screen readers.", "Desktop only."),
 "metric-card": ("Dashboard metric cards", "desktop", "Default; delta up/down uses arrow icon + color + text.", "Delta direction is conveyed by the arrow and the words, not green/red alone.", "Desktop only."),
 "sidebar": ("Desktop sidebar navigation", "desktop", "Item default, hover, current.", "Landmark `nav` with label; current item `aria-current=page`.", "Desktop only."),
}

def tokens_of(group, src):
    out = []
    def walk(node, path):
        for k, v in node.items():
            if k.startswith("$"): continue
            if "$value" in v: out.append(".".join(path + [k]))
            else: walk(v, path + [k])
    walk(SRC[src][group], [group])
    return out

def fmt(label, p):
    v, t = R[label]["values"][p], R[label]["types"][p]
    if t == "color": return v["hex"] + (f" ({int(v['alpha']*100)}%)" if v.get("alpha", 1) < 1 else "")
    if t == "dimension": return f"{v['value']:g}{v['unit']}"
    if t == "typography": return f"{v['fontSize']['value']:g}/{v['lineHeight']:g} w{v['fontWeight']}"
    if t == "duration": return f"{v['value']:g}{v['unit']}"
    if t == "transition": return f"{v['duration']['value']:g}ms"
    if t == "border": return f"{v['width']['value']:g}px {v['style']}"
    if t == "shadow": return "shadow"
    return str(v)

md = ["# Component specifications", "",
      "Thirty components: 15 shared, 7 patient-mobile, 8 admin-desktop. For each: the component tokens (with the semantic token they reference) and resolved values in light/mobile, light/desktop and dark/desktop. Token tables are generated from `tokens/components/*.tokens.json`; guidance is authored.", "",
      "**Rule of thumb used:** a component token exists only when the component makes a decision the semantic layer can't express (a geometry choice, or a role mapping that a designer would otherwise have to remember). Variant colors that map 1:1 to semantic tokens (button variants, badge statuses) are consumed directly and not duplicated.", ""]
for comp, (title, src, states, a11y, plat) in NOTES.items():
    md += [f"## {title}", "", f"`{comp}` in `components/{src}.tokens.json`", "",
           f"**States.** {states}", "", f"**Accessibility.** {a11y}", "", f"**Mobile vs desktop.** {plat}", "",
           "| Token | References | Light/mobile | Light/desktop | Dark/desktop |", "|---|---|---|---|---|"]
    for p in tokens_of(comp, src):
        r = R["light/desktop"]["refs"].get(p, "")
        md.append(f"| `{p}` | `{r}` | {fmt('light/mobile', p)} | {fmt('light/desktop', p)} | {fmt('dark/desktop', p)} |")
    if comp == "button":
        md.append("| *variant colors* | `color.action.{primary,secondary,tertiary,destructive}.*` | | | |")
    if comp == "badge":
        md.append("| *status colors* | `color.status.{status}.{bg,fg,border,icon}` | | | |")
    if comp == "alert":
        md.append("| *tone colors* | `color.feedback.{tone}.{bg,fg,border,icon}` | | | |")
    md.append("")
open(os.path.join(ROOT, "docs/component-specs.md"), "w").write("\n".join(md))
print("component specs:", len(NOTES), "components")
