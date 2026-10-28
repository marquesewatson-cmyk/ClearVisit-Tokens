"""
ClearVisit design tokens — source definitions.

This script is the authoring layer. It writes the DTCG 2025.10 source files in
tokens/. Everything downstream (validation, CSS, Figma import files, docs) reads
those JSON files, never this script, so the JSON stays the single source of truth.

Palettes are generated in OKLCH so every hue family shares the same perceptual
lightness ladder; this is what makes "step 600 on white passes 4.5:1" hold
across blue, green, red, violet, etc. Generated values are then frozen as sRGB.
"""
import json, math, os

ROOT = os.path.join(os.path.dirname(__file__), "..")
TOK = os.path.join(ROOT, "tokens")

# ---------------------------------------------------------------- helpers
def ref(path):
    return "{" + path + "}"

def t(type_, value, desc=None, ext=None):
    d = {"$type": type_, "$value": value}
    if desc:
        d["$description"] = desc
    if ext:
        d["$extensions"] = {"com.clearvisit": ext}
    return d

def a(value, desc=None, ext=None):
    """Alias token without explicit $type (type resolves from the target)."""
    d = {"$value": value}
    if desc:
        d["$description"] = desc
    if ext:
        d["$extensions"] = {"com.clearvisit": ext}
    return d

def px(v):
    return {"value": v, "unit": "px"}

def ms(v):
    return {"value": v, "unit": "ms"}

# ---------------------------------------------------------------- OKLCH -> sRGB
def oklch_to_linear(L, C, h):
    hr = math.radians(h)
    a_, b_ = C * math.cos(hr), C * math.sin(hr)
    l_ = L + 0.3963377774 * a_ + 0.2158037573 * b_
    m_ = L - 0.1055613458 * a_ - 0.0638541728 * b_
    s_ = L - 0.0894841775 * a_ - 1.2914855480 * b_
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )

def encode(c):
    c = min(max(c, 0.0), 1.0)
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055

def in_gamut(rgb):
    return all(-0.0001 <= c <= 1.0001 for c in rgb)

def oklch_srgb(L, C, h):
    lo, hi = 0.0, C
    if in_gamut(oklch_to_linear(L, C, h)):
        lo = C
    else:  # reduce chroma until in gamut (preserves lightness + hue)
        for _ in range(30):
            mid = (lo + hi) / 2
            if in_gamut(oklch_to_linear(L, mid, h)):
                lo = mid
            else:
                hi = mid
    return tuple(encode(c) for c in oklch_to_linear(L, lo, h))

def color_value(rgb, alpha=None):
    # Quantise to 8-bit first so `components` and `hex` describe exactly the same color.
    bytes_ = [round(min(max(c, 0), 1) * 255) for c in rgb]
    comps = [round(b / 255, 4) for b in bytes_]
    hexv = "#" + "".join(f"{b:02X}" for b in bytes_)
    v = {"colorSpace": "srgb", "components": comps}
    if alpha is not None:
        v["alpha"] = alpha
    v["hex"] = hexv
    return v

# Shared lightness ladder (OKLCH L) and chroma envelope per step
STEPS = {
    "50": (0.975, 0.12), "100": (0.945, 0.25), "200": (0.895, 0.45),
    "300": (0.82, 0.70), "400": (0.72, 0.90), "500": (0.60, 1.00),
    "600": (0.52, 1.00), "700": (0.48, 0.95), "800": (0.41, 0.85),
    "900": (0.33, 0.75), "950": (0.255, 0.60),
}
# Neutral gets extra dark steps for layered dark-theme surfaces
NEUTRAL_EXTRA = {"850": (0.37, 0.80), "925": (0.29, 0.70), "975": (0.205, 0.55)}

HUES = {
    #  name     hue   max chroma  role
    "blue":   (252, 0.165, "Brand primary — 'Harbor blue'. Trust, primary actions, confirmed appointments."),
    "teal":   (192, 0.115, "Secondary / accent. Calm highlight moments, secondary data series."),
    "slate":  (250, 0.028, "Cool neutral. Text, surfaces, borders."),
    "green":  (152, 0.150, "Success and appointment availability."),
    "amber":  (72,  0.160, "Warning and pending states."),
    "red":    (25,  0.190, "Error, destructive actions, cancellations."),
    "violet": (296, 0.165, "Rescheduled appointments. Extended status hue (assumption: not in original brief's palette list)."),
}

def build_palette():
    color = {"$type": "color",
             "$description": "Primitive color palette. Generated on a shared OKLCH lightness ladder; never consumed directly by components."}
    color["white"] = t("color", color_value((1, 1, 1)))
    color["transparent"] = t("color", color_value((1, 1, 1), alpha=0),
                             "Fully transparent. Used for ghost/tertiary backgrounds.")
    for name, (h, cmax, role) in HUES.items():
        grp = {"$description": role}
        steps = dict(STEPS)
        if name == "slate":
            steps.update(NEUTRAL_EXTRA)
        for step in sorted(steps, key=lambda s: int(s)):
            L, k = steps[step]
            grp[step] = {"$value": color_value(oklch_srgb(L, cmax * k, h)),
                         "$extensions": {"com.clearvisit": {"oklch": [L, round(cmax * k, 4), h]}}}
        color[name] = grp
    s975 = oklch_srgb(0.205, 0.028 * 0.55, 250)
    color["slate-alpha"] = {
        "$description": "Translucent slate-975 for scrims and shadows.",
        "8": t("color", color_value(s975, 0.08)),
        "12": t("color", color_value(s975, 0.12)),
        "16": t("color", color_value(s975, 0.16)),
        "24": t("color", color_value(s975, 0.24)),
        "48": t("color", color_value(s975, 0.48)),
        "64": t("color", color_value(s975, 0.64)),
    }
    color["black-alpha"] = {
        "$description": "Translucent black for dark-theme shadows and scrims.",
        "32": t("color", color_value((0, 0, 0), 0.32)),
        "48": t("color", color_value((0, 0, 0), 0.48)),
        "72": t("color", color_value((0, 0, 0), 0.72)),
    }
    return {"color": color}

# ---------------------------------------------------------------- primitives
def typography_primitives():
    font = {
        "family": {
            "$type": "fontFamily",
            "sans": t("fontFamily", ["Atkinson Hyperlegible Next", "Atkinson Hyperlegible", "system-ui",
                                     "-apple-system", "Segoe UI", "Roboto", "sans-serif"],
                      "Primary UI family. Atkinson Hyperlegible Next was designed by the Braille Institute for low-vision readers: distinct letterforms (Il1, 0O) reduce misreads of names, times and IDs."),
        },
        "weight": {
            "$type": "fontWeight",
            "regular": {"$value": 400}, "medium": {"$value": 500},
            "semibold": {"$value": 600}, "bold": {"$value": 700},
        },
        "size": {
            "$type": "dimension",
            "$description": "Font-size scale. Authored in px for Figma compatibility; converted to rem in CSS so text respects user font-size settings.",
            "100": {"$value": px(12)}, "200": {"$value": px(14)}, "300": {"$value": px(16)},
            "400": {"$value": px(18)}, "500": {"$value": px(20)}, "600": {"$value": px(24)},
            "700": {"$value": px(28)}, "800": {"$value": px(32)}, "900": {"$value": px(40)},
        },
        "line-height": {
            "$type": "number",
            "$description": "Unitless multipliers of font size (DTCG typography.lineHeight is a number).",
            "tight": {"$value": 1.2}, "snug": {"$value": 1.3},
            "normal": {"$value": 1.45}, "relaxed": {"$value": 1.6},
        },
        "letter-spacing": {
            "$type": "dimension",
            "tight": {"$value": px(-0.4)}, "normal": {"$value": px(0)}, "wide": {"$value": px(0.2)},
        },
    }
    def style(size, weight, lh, ls="normal", desc=None):
        return t("typography", {
            "fontFamily": ref("font.family.sans"),
            "fontSize": ref(f"font.size.{size}"),
            "fontWeight": ref(f"font.weight.{weight}"),
            "letterSpacing": ref(f"font.letter-spacing.{ls}"),
            "lineHeight": ref(f"font.line-height.{lh}"),
        }, desc)
    typography = {
        "$description": "Context-free type ramp. Product roles (page title, table cell…) live in the semantic platform layer.",
        "display": style("900", "bold", "tight", "tight"),
        "heading": {
            "xl": style("800", "bold", "tight", "tight"),
            "lg": style("700", "bold", "snug", "tight"),
            "md": style("600", "semibold", "snug"),
            "sm": style("500", "semibold", "snug"),
            "xs": style("400", "semibold", "snug"),
        },
        "body": {
            "lg": style("400", "regular", "relaxed"),
            "md": style("300", "regular", "normal"),
            "md-strong": style("300", "semibold", "normal"),
            "sm": style("200", "regular", "normal"),
            "sm-strong": style("200", "semibold", "normal"),
        },
        "label": {
            "lg": style("300", "medium", "snug"),
            "md": style("200", "medium", "snug"),
            "sm": style("100", "medium", "snug", "wide"),
        },
        "caption": style("100", "regular", "normal", "wide"),
    }
    return {"font": font, "typography": typography}

def spacing_primitives():
    vals = [0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80]
    g = {"$type": "dimension",
         "$description": "4px base grid (2px half-step for hairline adjustments). Names equal pixel values."}
    for v in vals:
        g[str(v)] = {"$value": px(v)}
    return {"space": g}

def sizing_primitives():
    vals = [8, 12, 16, 18, 20, 22, 24, 28, 32, 36, 40, 44, 48, 56, 64, 72, 88, 96, 256, 280, 560, 600]
    g = {"$type": "dimension",
         "$description": "Fixed sizes for controls, icons, targets and containers. Names equal pixel values."}
    for v in vals:
        g[str(v)] = {"$value": px(v)}
    return {"size": g}

def radius_primitives():
    g = {"$type": "dimension"}
    for v in [0, 4, 6, 8, 12, 16, 24]:
        g[str(v)] = {"$value": px(v)}
    g["full"] = t("dimension", px(9999), "Pill / circle.")
    return {"radius": g}

def border_primitives():
    return {
        "border-width": {"$type": "dimension",
                         "0": {"$value": px(0)}, "1": {"$value": px(1)},
                         "2": {"$value": px(2)}, "3": {"$value": px(3)}, "4": {"$value": px(4)}},
        "stroke-style": {"$type": "strokeStyle",
                         "solid": {"$value": "solid"},
                         "dashed": t("strokeStyle", "dashed",
                                     "Reserved for tentative/pending holds so pending is distinguishable without color.")},
    }

def elevation_primitives():
    def sh(color, y, blur, spread=0):
        return {"color": ref(color), "offsetX": px(0), "offsetY": px(y), "blur": px(blur), "spread": px(spread)}
    return {"shadow": {
        "$type": "shadow",
        "$description": "Two-layer shadows (tight contact + soft ambient). 'soft' tuned for light surfaces, 'strong' for dark.",
        "soft": {
            "1": {"$value": [sh("color.slate-alpha.8", 1, 2), sh("color.slate-alpha.8", 1, 3)]},
            "2": {"$value": [sh("color.slate-alpha.8", 2, 4), sh("color.slate-alpha.12", 4, 12, -2)]},
            "3": {"$value": [sh("color.slate-alpha.12", 4, 8, -2), sh("color.slate-alpha.16", 16, 32, -4)]},
        },
        "strong": {
            "1": {"$value": [sh("color.black-alpha.32", 1, 2), sh("color.black-alpha.32", 1, 3)]},
            "2": {"$value": [sh("color.black-alpha.32", 2, 4), sh("color.black-alpha.48", 4, 12, -2)]},
            "3": {"$value": [sh("color.black-alpha.48", 4, 8, -2), sh("color.black-alpha.72", 16, 32, -4)]},
        },
    }}

def opacity_primitives():
    g = {"$type": "number", "$description": "Opacity multipliers 0–1."}
    for k, v in {"0": 0, "8": 0.08, "16": 0.16, "38": 0.38, "64": 0.64, "100": 1}.items():
        g[k] = {"$value": v}
    return {"opacity": g}

def motion_primitives():
    return {
        "duration": {"$type": "duration",
                     "0": {"$value": ms(0)}, "100": {"$value": ms(100)}, "150": {"$value": ms(150)},
                     "200": {"$value": ms(200)}, "300": {"$value": ms(300)}, "400": {"$value": ms(400)}},
        "easing": {"$type": "cubicBezier",
                   "standard": t("cubicBezier", [0.2, 0, 0, 1], "Default for state changes."),
                   "decelerate": t("cubicBezier", [0, 0, 0, 1], "Elements entering (sheets, modals)."),
                   "accelerate": t("cubicBezier", [0.3, 0, 1, 1], "Elements leaving."),
                   "linear": {"$value": [0, 0, 1, 1]}},
    }

def layout_primitives():
    return {
        "breakpoint": {"$type": "dimension",
                       "$description": "Min-width breakpoints. Patient app is designed at 360–430; admin is designed at ≥1200.",
                       "sm": {"$value": px(600)}, "md": {"$value": px(900)},
                       "lg": {"$value": px(1200)}, "xl": {"$value": px(1440)}},
        "grid": {"columns": {"$type": "number",
                             "4": {"$value": 4}, "8": {"$value": 8}, "12": {"$value": 12}}},
        "z-index": {"$type": "number",
                    "$description": "Stacking order. Unitless numbers.",
                    "base": {"$value": 0}, "sticky": {"$value": 100}, "dropdown": {"$value": 1000},
                    "overlay": {"$value": 1200}, "modal": {"$value": 1300},
                    "toast": {"$value": 1400}, "tooltip": {"$value": 1500}},
    }

# ---------------------------------------------------------------- semantic: theme
STATUS_META = {
    "available":   {"hue": "green",  "label": "Available",   "icon": "calendar-plus",
                    "meaning": "Open slot a patient can book."},
    "confirmed":   {"hue": "blue",   "label": "Confirmed",   "icon": "check-circle",
                    "meaning": "Booked and confirmed by practice and patient."},
    "pending":     {"hue": "amber",  "label": "Pending",     "icon": "clock",
                    "meaning": "Requested or held; awaiting confirmation. Rendered with dashed outline on calendars."},
    "completed":   {"hue": "slate",  "label": "Completed",   "icon": "check-double",
                    "meaning": "Visit has happened. De-emphasised on purpose."},
    "cancelled":   {"hue": "red",    "label": "Cancelled",   "icon": "x-circle",
                    "meaning": "Cancelled by patient or practice. Time text is struck through."},
    "rescheduled": {"hue": "violet", "label": "Rescheduled", "icon": "arrow-path",
                    "meaning": "Moved to a new time; links to the new appointment."},
}
FEEDBACK_META = {
    "success": {"hue": "green", "icon": "check-circle"},
    "warning": {"hue": "amber", "icon": "exclamation-triangle"},
    "error":   {"hue": "red",   "icon": "exclamation-circle"},
    "info":    {"hue": "blue",  "icon": "information-circle"},
}

def theme(mode):
    L = mode == "light"
    c = lambda h, s: ref(f"color.{h}.{s}")
    sl = lambda s: c("slate", s)

    def tone(hue, neutral=False):
        if L:
            return {"fg": a(c(hue, "800") if not neutral else sl("700")),
                    "bg": a(c(hue, "50") if not neutral else sl("100")),
                    "border": a(c(hue, "200") if not neutral else sl("300")),
                    "icon": a(c(hue, "600") if not neutral else sl("500"))}
        return {"fg": a(c(hue, "200") if not neutral else sl("200")),
                "bg": a(c(hue, "950") if not neutral else sl("900")),
                "border": a(c(hue, "800") if not neutral else sl("700")),
                "icon": a(c(hue, "400") if not neutral else sl("400"))}

    status = {"$description": "Appointment statuses. Color is never the only cue: every status ships with a text label and a distinct icon (see $extensions)."}
    for k, m in STATUS_META.items():
        g = tone(m["hue"], neutral=(m["hue"] == "slate"))
        g["$description"] = m["meaning"]
        g["$extensions"] = {"com.clearvisit": {"label": m["label"], "icon": m["icon"]}}
        status[k] = g
    feedback = {}
    for k, m in FEEDBACK_META.items():
        g = tone(m["hue"])
        g["$extensions"] = {"com.clearvisit": {"icon": m["icon"]}}
        feedback[k] = g

    color = {
        "$type": "color",
        "text": {
            "primary":   a(sl("900") if L else sl("50"), "Body copy, headings, data."),
            "secondary": a(sl("700") if L else sl("300"), "Supporting copy, table headers, meta."),
            "muted":     a(sl("600") if L else sl("400"), "Placeholders, timestamps. Still meets 4.5:1 on default and subtle surfaces."),
            "disabled":  a(sl("400") if L else sl("600"), "Disabled text. Exempt from WCAG 1.4.3 but always paired with a disabled container."),
            "inverse":   a(sl("50") if L else sl("900"), "Text on inverse surfaces (tooltips, toasts)."),
            "link":      a(c("blue", "700") if L else c("blue", "300")),
            "link-hover": a(c("blue", "800") if L else c("blue", "200")),
        },
        "surface": {
            "app":      a(sl("50") if L else sl("975"), "Page/app background."),
            "default":  a(ref("color.white") if L else sl("950"), "Cards, tables, inputs."),
            "elevated": a(ref("color.white") if L else sl("900"), "Menus, modals, sheets. In dark mode elevation is expressed by lightness."),
            "subtle":   a(sl("100") if L else sl("925"), "Table headers, search fields, off-hours calendar cells."),
            "selected": a(c("blue", "50") if L else c("blue", "950"), "Selected rows, active nav items."),
            "inverse":  a(sl("900") if L else sl("100")),
            "overlay":  a(ref("color.slate-alpha.48") if L else ref("color.black-alpha.72"), "Modal scrim."),
        },
        "border": {
            "subtle":  a(sl("100") if L else sl("925"), "Dividers inside a surface. Decorative."),
            "default": a(sl("200") if L else sl("850"), "Card and container edges. Decorative; containers are also separated by surface color."),
            "strong":  a(sl("500") if L else sl("500"), "Boundaries of interactive controls (inputs, checkboxes, chips). Meets 3:1 (WCAG 1.4.11)."),
            "hover":   a(sl("600") if L else sl("400")),
            "focus":   a(c("blue", "600") if L else c("blue", "300"), "Focus ring color. Meets 3:1 against all surfaces."),
            "error":   a(c("red", "600") if L else c("red", "400")),
            "selected": a(c("blue", "600") if L else c("blue", "400")),
        },
        "action": {
            "primary": {
                "bg": a(c("blue", "600") if L else c("blue", "400")),
                "bg-hover": a(c("blue", "700") if L else c("blue", "300")),
                "bg-pressed": a(c("blue", "800") if L else c("blue", "200")),
                "fg": a(ref("color.white") if L else c("blue", "950")),
            },
            "secondary": {
                "bg": a(ref("color.white") if L else sl("950")),
                "bg-hover": a(c("blue", "50") if L else c("blue", "950")),
                "bg-pressed": a(c("blue", "100") if L else c("blue", "900")),
                "fg": a(c("blue", "700") if L else c("blue", "200")),
                "border": a(c("blue", "600") if L else c("blue", "400")),
            },
            "tertiary": {
                "bg": a(ref("color.transparent")),
                "bg-hover": a(sl("100") if L else sl("900")),
                "bg-pressed": a(sl("200") if L else sl("850")),
                "fg": a(c("blue", "700") if L else c("blue", "300")),
            },
            "destructive": {
                "bg": a(c("red", "600") if L else c("red", "400")),
                "bg-hover": a(c("red", "700") if L else c("red", "300")),
                "bg-pressed": a(c("red", "800") if L else c("red", "200")),
                "fg": a(ref("color.white") if L else c("red", "950")),
            },
        },
        "interaction": {
            "hover":   a(sl("100") if L else sl("900"), "Hover fill for rows, list items, ghost controls."),
            "pressed": a(sl("200") if L else sl("850")),
            "selected": {
                "bg": a(c("blue", "50") if L else c("blue", "950")),
                "fg": a(c("blue", "800") if L else c("blue", "100")),
                "border": a(c("blue", "600") if L else c("blue", "400")),
            },
            "focus": {
                "ring": a(ref("color.border.focus")),
                "offset": a(ref("color.surface.default"), "Gap between control and ring so the ring reads on any fill."),
            },
            "disabled": {
                "bg": a(sl("100") if L else sl("925")),
                "fg": a(ref("color.text.disabled")),
                "border": a(sl("200") if L else sl("850")),
            },
        },
        "status": status,
        "feedback": feedback,
        "accent": {
            "bg": a(c("teal", "50") if L else c("teal", "950")),
            "fg": a(c("teal", "800") if L else c("teal", "200")),
            "border": a(c("teal", "200") if L else c("teal", "800")),
            "solid": a(c("teal", "600") if L else c("teal", "400"), "Graphic accents, the calendar 'now' line."),
        },
        "chart": {
            "series-1": a(c("blue", "600") if L else c("blue", "400")),
            "series-2": a(c("teal", "500") if L else c("teal", "400")),
            "series-3": a(c("violet", "500") if L else c("violet", "400")),
            "series-4": a(c("amber", "500") if L else c("amber", "400")),
        },
    }
    shadow = {"$type": "shadow",
              "$description": "Theme-aware elevation. Dark theme uses stronger shadows plus lighter surfaces.",
              "raised":  a(ref("shadow.soft.1") if L else ref("shadow.strong.1")),
              "popover": a(ref("shadow.soft.2") if L else ref("shadow.strong.2")),
              "overlay": a(ref("shadow.soft.3") if L else ref("shadow.strong.3"))}
    return {"color": color, "elevation": shadow}

# ---------------------------------------------------------------- semantic: base (shared, theme/platform independent)
def base_semantic():
    return {
        "space": {
            "inline": {"$description": "Horizontal gaps between siblings.",
                       "xs": a(ref("space.4")), "sm": a(ref("space.8")),
                       "md": a(ref("space.12")), "lg": a(ref("space.16"))},
            "stack": {"$description": "Vertical rhythm between stacked elements.",
                      "xs": a(ref("space.4")), "sm": a(ref("space.8")), "md": a(ref("space.16")),
                      "lg": a(ref("space.24")), "xl": a(ref("space.32"))},
            "inset": {"xs": a(ref("space.4")), "sm": a(ref("space.8")), "md": a(ref("space.12"))},
        },
        "radius": {"xs": a(ref("radius.4")), "sm": a(ref("radius.6")), "pill": a(ref("radius.full"))},
        "stroke": {"default": a(ref("border-width.1")),
                   "focus": a(ref("border-width.2"), "Focus ring thickness (≥2px CSS px for WCAG 2.4.13-style visibility)."),
                   "indicator": a(ref("border-width.3"), "Active tab underline, calendar event status bar.")},
        "focus-ring": {
            "$root": t("border", {"color": ref("color.interaction.focus.ring"),
                                  "width": ref("stroke.focus"), "style": ref("stroke-style.solid")},
                       "Focus indicator for every interactive element. Applied as an outline with an offset."),
            "offset": a(ref("space.2")),
        },
        "size": {
            "badge": a(ref("size.24")),
            "status-dot": a(ref("size.8")),
            "tooltip-max": a(ref("size.280")),
        },
        "motion": {
            "control": t("transition", {"duration": ref("duration.150"), "delay": ref("duration.0"),
                                        "timingFunction": ref("easing.standard")},
                         "Hover/press/selection feedback. Reduced-motion users get duration 0 (see CSS)."),
            "enter": t("transition", {"duration": ref("duration.300"), "delay": ref("duration.0"),
                                      "timingFunction": ref("easing.decelerate")}),
            "exit": t("transition", {"duration": ref("duration.200"), "delay": ref("duration.0"),
                                     "timingFunction": ref("easing.accelerate")}),
            "tooltip-delay": a(ref("duration.400")),
        },
        "opacity": {"disabled-media": a(ref("opacity.38"), "Images/avatars inside disabled rows. Never used for text.")},
        "layer": {k: a(ref(f"z-index.{k}")) for k in ["sticky", "dropdown", "overlay", "modal", "toast", "tooltip"]},
    }

# ---------------------------------------------------------------- semantic: platform
def platform(p):
    M = p == "mobile"
    pick = lambda m, d: m if M else d
    return {
        "size": {
            "control": {"$description": "Control heights. Mobile = touch-first, desktop = density-first.",
                        "sm": a(ref(pick("size.36", "size.28"))),
                        "md": a(ref(pick("size.48", "size.36"))),
                        "lg": a(ref(pick("size.56", "size.44")))},
            "touch-target": a(ref(pick("size.48", "size.24")),
                              "Minimum hit area. Mobile 48 exceeds WCAG 2.5.8 (24) and matches platform HIG guidance; desktop uses the 24px AA minimum for pointer input."),
            "icon": {"sm": a(ref("size.16")), "md": a(ref(pick("size.24", "size.20"))), "lg": a(ref(pick("size.32", "size.24")))},
            "avatar": a(ref(pick("size.56", "size.32"))),
            "selection-control": a(ref(pick("size.24", "size.18")), "Checkbox/radio visual size (hit area is touch-target)."),
            "nav-bar": a(ref(pick("size.64", "size.56")), "Mobile bottom nav height / desktop top bar height."),
            "table-row": a(ref(pick("size.56", "size.40"))),
            "table-header": a(ref(pick("size.48", "size.40"))),
            "day-cell": a(ref(pick("size.44", "size.32")), "Date picker day."),
            "time-slot": a(ref(pick("size.48", "size.32"))),
            "modal-max": a(ref(pick("size.600", "size.560"))),
        },
        "space": {
            "inset": {
                "control-x": a(ref(pick("space.16", "space.12"))),
                "card": a(ref(pick("space.16", "space.20"))),
                "modal": a(ref(pick("space.20", "space.32"))),
                "cell-x": a(ref(pick("space.16", "space.12")), "Table/list cell horizontal padding."),
                "page": a(ref(pick("space.16", "space.32"))),
            },
            "section": a(ref(pick("space.24", "space.32"))),
        },
        "radius": {"control": a(ref(pick("radius.12", "radius.6"))),
                   "card": a(ref(pick("radius.16", "radius.8"))),
                   "modal": a(ref(pick("radius.24", "radius.12")), "Mobile modals render as bottom sheets (top corners only).")},
        "layout": {"columns": a(ref(pick("grid.columns.4", "grid.columns.12"))),
                   "gutter": a(ref(pick("space.16", "space.24"))),
                   "margin": a(ref(pick("space.16", "space.32")))},
        "text-style": {
            "$description": "Role-based type. Same role names on both platforms; values differ by density.",
            "page-title":       a(ref(pick("typography.heading.lg", "typography.heading.md"))),
            "section-title":    a(ref(pick("typography.heading.sm", "typography.heading.xs"))),
            "card-title":       a(ref(pick("typography.heading.xs", "typography.body.md-strong"))),
            "provider-name":    a(ref(pick("typography.heading.xs", "typography.body.md-strong"))),
            "body":             a(ref(pick("typography.body.md", "typography.body.sm"))),
            "body-strong":      a(ref(pick("typography.body.md-strong", "typography.body.sm-strong"))),
            "supporting":       a(ref("typography.body.sm")),
            "label":            a(ref(pick("typography.label.lg", "typography.label.md"))),
            "input":            a(ref(pick("typography.body.md", "typography.body.sm")),
                                  "Mobile inputs stay at 16px so iOS Safari does not zoom on focus."),
            "button":           a(ref(pick("typography.label.lg", "typography.label.md"))),
            "caption":          a(ref("typography.caption")),
            "badge":            a(ref("typography.label.sm")),
            "appointment-time": a(ref(pick("typography.heading.sm", "typography.body.md-strong"))),
            "table-cell":       a(ref(pick("typography.body.md", "typography.body.sm"))),
            "table-header":     a(ref("typography.label.md")),
            "calendar-event":   a(ref(pick("typography.label.md", "typography.label.sm"))),
            "calendar-time":    a(ref("typography.caption")),
            "metric-value":     a(ref(pick("typography.heading.sm", "typography.heading.xl"))),
            "alert-title":      a(ref(pick("typography.body.md-strong", "typography.body.sm-strong"))),
            "alert-body":       a(ref(pick("typography.body.md", "typography.body.sm"))),
        },
    }

# ---------------------------------------------------------------- components
def shared_components():
    S = lambda p: a(ref(p))
    return {
        "button": {
            "$description": "Primary/secondary/tertiary/destructive buttons. Variant colors come straight from color.action.*; only geometry is tokenised here.",
            "height": {"sm": S("size.control.sm"), "md": S("size.control.md"), "lg": S("size.control.lg")},
            "padding-x": S("space.inset.control-x"), "gap": S("space.inline.sm"),
            "radius": S("radius.control"), "text-style": S("text-style.button"),
            "min-target": S("size.touch-target"), "transition": S("motion.control"),
        },
        "field": {
            "$description": "Shared by text input, search field and dropdown trigger.",
            "height": S("size.control.md"), "padding-x": S("space.inset.control-x"), "gap": S("space.inline.sm"),
            "radius": S("radius.control"), "text-style": S("text-style.input"), "label-style": S("text-style.label"),
            "bg": S("color.surface.default"), "fg": S("color.text.primary"), "placeholder": S("color.text.muted"),
            "border": S("color.border.strong"), "border-hover": S("color.border.hover"),
            "border-focus": S("color.border.focus"), "border-error": S("color.border.error"),
            "helper": S("color.text.secondary"), "error-text": S("color.feedback.error.fg"),
            "label-gap": S("space.stack.xs"),
        },
        "search": {
            "bg": S("color.surface.subtle"), "icon": S("color.text.secondary"),
            "radius": S("radius.pill"), "height": S("size.control.lg"),
        },
        "dropdown": {
            "menu-bg": S("color.surface.elevated"), "menu-shadow": S("elevation.popover"),
            "menu-radius": S("radius.control"), "menu-layer": S("layer.dropdown"),
            "option-height": S("size.control.md"), "option-hover": S("color.interaction.hover"),
            "option-selected-bg": S("color.interaction.selected.bg"),
            "option-selected-fg": S("color.interaction.selected.fg"),
        },
        "checkbox": {
            "size": S("size.selection-control"), "radius": S("radius.xs"), "target": S("size.touch-target"),
            "border": S("color.border.strong"), "checked-bg": S("color.action.primary.bg"),
            "checked-fg": S("color.action.primary.fg"),
        },
        "radio": {
            "size": S("size.selection-control"), "target": S("size.touch-target"),
            "border": S("color.border.strong"), "checked": S("color.action.primary.bg"),
        },
        "badge": {
            "$description": "Status badge = icon + label on tinted fill. Colors read directly from color.status.<status>.* (no per-status component tokens; they would duplicate the semantic layer).",
            "height": S("size.badge"), "padding-x": S("space.inset.sm"), "gap": S("space.inline.xs"),
            "radius": S("radius.pill"), "text-style": S("text-style.badge"), "icon-size": S("size.icon.sm"),
        },
        "card": {
            "bg": S("color.surface.default"), "border": S("color.border.default"),
            "border-hover": S("color.border.hover"), "radius": S("radius.card"),
            "padding": S("space.inset.card"), "gap": S("space.stack.sm"), "shadow": S("elevation.raised"),
        },
        "tabs": {
            "height": S("size.control.md"), "gap": S("space.inline.lg"), "text-style": S("text-style.label"),
            "fg": S("color.text.secondary"), "fg-selected": S("color.text.primary"),
            "indicator": S("color.action.primary.bg"), "indicator-height": S("stroke.indicator"),
            "divider": S("color.border.default"),
        },
        "alert": {
            "padding": S("space.inset.card"), "gap": S("space.inline.md"), "radius": S("radius.control"),
            "border-width": S("stroke.default"), "icon-size": S("size.icon.md"),
            "title-style": S("text-style.alert-title"), "body-style": S("text-style.alert-body"),
        },
        "modal": {
            "bg": S("color.surface.elevated"), "scrim": S("color.surface.overlay"),
            "radius": S("radius.modal"), "padding": S("space.inset.modal"), "shadow": S("elevation.overlay"),
            "max-width": S("size.modal-max"), "layer": S("layer.modal"), "enter": S("motion.enter"),
        },
        "tooltip": {
            "bg": S("color.surface.inverse"), "fg": S("color.text.inverse"), "radius": S("radius.sm"),
            "padding-x": S("space.inset.sm"), "padding-y": S("space.inset.xs"), "text-style": S("text-style.caption"),
            "max-width": S("size.tooltip-max"), "delay": S("motion.tooltip-delay"), "layer": S("layer.tooltip"),
        },
        "nav-item": {
            "height": S("size.control.md"), "gap": S("space.inline.md"), "radius": S("radius.control"),
            "fg": S("color.text.secondary"), "fg-active": S("color.interaction.selected.fg"),
            "bg-hover": S("color.interaction.hover"), "bg-active": S("color.interaction.selected.bg"),
            "icon-size": S("size.icon.md"),
        },
        "date-picker": {
            "day-size": S("size.day-cell"), "day-radius": S("radius.pill"), "day-target": S("size.touch-target"),
            "day-fg": S("color.text.primary"), "day-muted": S("color.text.muted"),
            "day-unavailable": S("color.text.disabled"),
            "day-selected-bg": S("color.action.primary.bg"), "day-selected-fg": S("color.action.primary.fg"),
            "today-ring": S("color.border.selected"), "availability-dot": S("color.status.available.icon"),
        },
        "time-selector": {
            "$description": "Time picker list (admin) / wheel (mobile). Slot buttons are a separate mobile component.",
            "option-height": S("size.control.md"), "text-style": S("text-style.input"),
            "option-selected-bg": S("color.interaction.selected.bg"),
            "option-selected-fg": S("color.interaction.selected.fg"),
        },
    }

def mobile_components():
    S = lambda p: a(ref(p))
    return {
        "provider-card": {
            "avatar-size": S("size.avatar"), "gap": S("space.inline.md"), "padding": S("space.inset.card"),
            "name-style": S("text-style.provider-name"), "meta-style": S("text-style.supporting"),
            "meta-fg": S("color.text.secondary"), "next-available-fg": S("color.status.available.fg"),
            "next-available-bg": S("color.status.available.bg"),
        },
        "availability-card": {
            "$description": "Search result card that leads with the soonest open time.",
            "bg": S("color.surface.default"), "border": S("color.border.default"), "radius": S("radius.card"),
            "padding": S("space.inset.card"), "slot-gap": S("space.inline.sm"),
            "time-style": S("text-style.appointment-time"),
        },
        "booking-card": {
            "bg": S("color.surface.elevated"), "radius": S("radius.card"), "padding": S("space.inset.card"),
            "shadow": S("elevation.popover"), "section-gap": S("space.section"),
        },
        "date-strip": {
            "item-width": S("size.56"), "item-height": S("size.72"), "radius": S("radius.control"),
            "gap": S("space.inline.sm"), "weekday-style": S("text-style.caption"),
            "date-style": S("text-style.section-title"),
            "bg": S("color.surface.default"), "border": S("color.border.strong"),
            "selected-bg": S("color.action.primary.bg"), "selected-fg": S("color.action.primary.fg"),
            "availability-dot": S("color.status.available.icon"),
            "unavailable-fg": S("color.text.disabled"),
        },
        "time-slot": {
            "$description": "Bookable time button. Selected = filled + check icon; booked = disabled fill + struck-through time + 'Booked' a11y label.",
            "height": S("size.time-slot"), "min-width": S("size.88"), "radius": S("radius.control"),
            "gap": S("space.inline.sm"), "text-style": S("text-style.button"),
            "bg": S("color.surface.default"), "fg": S("color.action.secondary.fg"),
            "border": S("color.border.strong"), "bg-hover": S("color.action.secondary.bg-hover"),
            "selected-bg": S("color.action.primary.bg"), "selected-fg": S("color.action.primary.fg"),
            "disabled-bg": S("color.interaction.disabled.bg"), "disabled-fg": S("color.interaction.disabled.fg"),
            "disabled-border": S("color.interaction.disabled.border"),
        },
        "summary-card": {
            "bg": S("color.surface.subtle"), "radius": S("radius.card"), "padding": S("space.inset.card"),
            "row-gap": S("space.stack.sm"), "divider": S("color.border.default"),
            "label-style": S("text-style.supporting"), "label-fg": S("color.text.secondary"),
            "value-style": S("text-style.body-strong"),
        },
        "bottom-nav": {
            "height": S("size.nav-bar"), "bg": S("color.surface.elevated"), "border": S("color.border.default"),
            "fg": S("color.text.secondary"), "fg-active": S("color.interaction.selected.fg"),
            "indicator": S("color.interaction.selected.bg"), "label-style": S("text-style.caption"),
            "icon-size": S("size.icon.md"), "layer": S("layer.sticky"),
        },
    }

def desktop_components():
    S = lambda p: a(ref(p))
    return {
        "calendar-cell": {
            "slot-height": S("size.48"), "bg": S("color.surface.default"), "bg-off-hours": S("color.surface.subtle"),
            "border": S("color.border.subtle"), "today-bg": S("color.surface.selected"),
            "time-style": S("text-style.calendar-time"), "time-fg": S("color.text.secondary"),
            "now-line": S("color.accent.solid"),
        },
        "calendar-event": {
            "$description": "Event chip. Fill/text/bar come from color.status.<status>.*; pending adds a dashed outline; conflicts add an error outline + icon + 'Conflict' label.",
            "radius": S("radius.sm"), "padding": S("space.inset.xs"), "text-style": S("text-style.calendar-event"),
            "bar-width": S("stroke.indicator"), "gap": S("space.inline.xs"),
            "pending-style": S("stroke-style.dashed"),
            "conflict-outline": t("border", {"color": ref("color.feedback.error.icon"),
                                             "width": ref("stroke.focus"), "style": ref("stroke-style.solid")}),
        },
        "table": {
            "row-height": S("size.table-row"), "header-height": S("size.table-header"),
            "cell-padding-x": S("space.inset.cell-x"), "header-bg": S("color.surface.subtle"),
            "header-fg": S("color.text.secondary"), "header-style": S("text-style.table-header"),
            "cell-style": S("text-style.table-cell"), "row-border": S("color.border.subtle"),
            "row-hover": S("color.interaction.hover"), "row-selected": S("color.interaction.selected.bg"),
        },
        "status-indicator": {
            "dot-size": S("size.status-dot"), "gap": S("space.inline.sm"), "text-style": S("text-style.body"),
        },
        "filter-chip": {
            "height": S("size.control.sm"), "padding-x": S("space.inset.md"), "radius": S("radius.pill"),
            "text-style": S("text-style.label"), "bg": S("color.surface.default"), "border": S("color.border.strong"),
            "selected-bg": S("color.interaction.selected.bg"), "selected-fg": S("color.interaction.selected.fg"),
            "selected-border": S("color.interaction.selected.border"),
        },
        "pagination": {
            "item-size": S("size.control.sm"), "radius": S("radius.control"), "gap": S("space.inline.xs"),
            "fg": S("color.text.secondary"), "current-bg": S("color.interaction.selected.bg"),
            "current-fg": S("color.interaction.selected.fg"),
        },
        "metric-card": {
            "padding": S("space.inset.card"), "radius": S("radius.card"), "bg": S("color.surface.default"),
            "border": S("color.border.default"), "value-style": S("text-style.metric-value"),
            "label-style": S("text-style.supporting"), "label-fg": S("color.text.secondary"),
            "delta-up": S("color.feedback.success.fg"), "delta-down": S("color.feedback.error.fg"),
        },
        "sidebar": {
            "width": S("size.256"), "bg": S("color.surface.default"), "border": S("color.border.default"),
            "padding": S("space.inset.md"), "section-style": S("text-style.caption"),
            "section-fg": S("color.text.secondary"),
        },
    }

# ---------------------------------------------------------------- write
def write(rel, data, schema_note=None):
    path = os.path.join(TOK, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

if __name__ == "__main__":
    write("primitives/color.tokens.json", build_palette())
    write("primitives/typography.tokens.json", typography_primitives())
    write("primitives/spacing.tokens.json", spacing_primitives())
    write("primitives/sizing.tokens.json", sizing_primitives())
    write("primitives/radius.tokens.json", radius_primitives())
    write("primitives/border.tokens.json", border_primitives())
    write("primitives/elevation.tokens.json", elevation_primitives())
    write("primitives/opacity.tokens.json", opacity_primitives())
    write("primitives/motion.tokens.json", motion_primitives())
    write("primitives/layout.tokens.json", layout_primitives())
    write("semantic/base.tokens.json", base_semantic())
    write("semantic/light.tokens.json", theme("light"))
    write("semantic/dark.tokens.json", theme("dark"))
    write("semantic/platform/mobile.tokens.json", platform("mobile"))
    write("semantic/platform/desktop.tokens.json", platform("desktop"))
    write("components/shared.tokens.json", shared_components())
    write("components/mobile.tokens.json", mobile_components())
    write("components/desktop.tokens.json", desktop_components())
    resolver = {
        "$schema": "https://www.designtokens.org/schemas/2025.10/resolver.json",
        "name": "ClearVisit",
        "version": "2025.10",
        "description": "ClearVisit token resolution: 2 themes × 2 platforms = 4 permutations.",
        "sets": {
            "primitives": {"description": "Raw values. Never referenced by components for color.",
                           "sources": [{"$ref": f"primitives/{n}.tokens.json"} for n in
                                       ["color", "typography", "spacing", "sizing", "radius", "border",
                                        "elevation", "opacity", "motion", "layout"]]},
            "semantic-base": {"description": "Theme- and platform-independent semantic tokens.",
                              "sources": [{"$ref": "semantic/base.tokens.json"}]},
            "components": {"description": "Component tokens. Reference semantic tokens.",
                           "sources": [{"$ref": "components/shared.tokens.json"},
                                       {"$ref": "components/mobile.tokens.json"},
                                       {"$ref": "components/desktop.tokens.json"}]},
        },
        "modifiers": {
            "theme": {"description": "Color theme", "default": "light",
                      "contexts": {"light": [{"$ref": "semantic/light.tokens.json"}],
                                   "dark": [{"$ref": "semantic/dark.tokens.json"}]}},
            "platform": {"description": "Density/platform. Orthogonal to theme: no token is defined by both modifiers.",
                         "default": "desktop",
                         "contexts": {"mobile": [{"$ref": "semantic/platform/mobile.tokens.json"}],
                                      "desktop": [{"$ref": "semantic/platform/desktop.tokens.json"}]}},
        },
        "resolutionOrder": [
            {"$ref": "#/sets/primitives"}, {"$ref": "#/sets/semantic-base"},
            {"$ref": "#/modifiers/theme"}, {"$ref": "#/modifiers/platform"},
            {"$ref": "#/sets/components"},
        ],
    }
    write("clearvisit.resolver.json", resolver)
    print("source tokens written")
