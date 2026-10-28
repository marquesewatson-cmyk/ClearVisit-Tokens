"""
ClearVisit token build.

  tokens/**/*.tokens.json  (DTCG 2025.10 source, the only thing humans edit)
        │  1. load + structural checks (names, token/group shape)
        │  2. resolve each permutation from clearvisit.resolver.json (theme × platform)
        │  3. validate types, references, cycles, layering rules, completeness
        │  4. audit WCAG contrast for declared foreground/background pairs
        ▼
  generated/  CSS custom properties · Figma import files · resolved DTCG bundles · reports

Zero third-party dependencies so the pipeline is easy to audit. In a production repo
the transform step would typically be Style Dictionary or Terrazzo; the validation
rules here would still apply as a pre-build gate.
"""
import json, os, re, sys, copy, itertools, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOK = os.path.join(ROOT, "tokens")
GEN = os.path.join(ROOT, "generated")
ALIAS = re.compile(r"^\{([^{}]+)\}$")

TYPES = {"color", "dimension", "fontFamily", "fontWeight", "duration", "cubicBezier", "number",
         "strokeStyle", "border", "transition", "shadow", "gradient", "typography"}
FW_NAMES = {"thin": 100, "hairline": 100, "extra-light": 200, "ultra-light": 200, "light": 300,
            "normal": 400, "regular": 400, "book": 400, "medium": 500, "semi-bold": 600,
            "demi-bold": 600, "bold": 700, "extra-bold": 800, "ultra-bold": 800, "black": 900,
            "heavy": 900, "extra-black": 950, "ultra-black": 950}
STROKES = {"solid", "dashed", "dotted", "double", "groove", "ridge", "outset", "inset"}
COMPOSITE = {
    "typography": {"fontFamily": "fontFamily", "fontSize": "dimension", "fontWeight": "fontWeight",
                   "letterSpacing": "dimension", "lineHeight": "number"},
    "border": {"color": "color", "width": "dimension", "style": "strokeStyle"},
    "transition": {"duration": "duration", "delay": "duration", "timingFunction": "cubicBezier"},
    "shadow": {"color": "color", "offsetX": "dimension", "offsetY": "dimension",
               "blur": "dimension", "spread": "dimension"},
}

errors, warnings, infos = [], [], []
def err(m): errors.append(m)
def warn(m): warnings.append(m)
def info(m): infos.append(m)

# ------------------------------------------------------------------ load
def read(rel):
    with open(os.path.join(TOK, rel)) as f:
        return json.load(f)  # raises on JSON syntax errors -> build fails

def flatten(tree, file, prefix=(), inherited=None, out=None):
    """Return {path: token} for a DTCG tree. Groups pass $type down."""
    out = {} if out is None else out
    gtype = tree.get("$type", inherited)
    for k, v in tree.items():
        if k.startswith("$") and k != "$root":
            continue
        if k != "$root" and (any(ch in k for ch in "{}.")):
            err(f"{file}: illegal character in name '{k}'")
        if not isinstance(v, dict):
            err(f"{file}: '{'.'.join(prefix + (k,))}' is not an object")
            continue
        path = prefix + (k,)
        if "$value" in v:
            children = [c for c in v if not c.startswith("$")]
            if children:
                err(f"{file}: '{'.'.join(path)}' has $value and child tokens/groups {children}")
            out[".".join(path)] = {"value": v["$value"], "declared": v.get("$type"),
                                   "inherited": gtype, "desc": v.get("$description"),
                                   "ext": v.get("$extensions"), "file": file}
        else:
            if "$type" in v and v["$type"] not in TYPES:
                err(f"{file}: group '{'.'.join(path)}' has unknown $type {v['$type']}")
            flatten(v, file, path, gtype, out)
    return out

RESOLVER = read("clearvisit.resolver.json")

def set_files(name):
    return [s["$ref"] for s in RESOLVER["sets"][name]["sources"]]

def permutation(inputs):
    files = []
    for item in RESOLVER["resolutionOrder"]:
        kind, name = item["$ref"].split("/")[1:]
        if kind == "sets":
            files += set_files(name)
        else:
            m = RESOLVER["modifiers"][name]
            files += [s["$ref"] for s in m["contexts"][inputs.get(name, m.get("default"))]]
    return files

SOURCES = {}
for f in set(itertools.chain.from_iterable(
        [set_files(s) for s in RESOLVER["sets"]] +
        [[s["$ref"] for ctx in m["contexts"].values() for s in ctx] for m in RESOLVER["modifiers"].values()])):
    SOURCES[f] = flatten(read(f), f)

def layer_of(file):
    return file.split("/")[0]  # primitives | semantic | components

# Resolver document checks
assert RESOLVER["version"] == "2025.10"
for name, m in RESOLVER["modifiers"].items():
    if len(m["contexts"]) < 2: err(f"modifier {name} has <2 contexts")
    if m.get("default") not in m["contexts"]: err(f"modifier {name} default not in contexts")

PERMS = [{"theme": th, "platform": pl} for th in ["light", "dark"] for pl in ["mobile", "desktop"]]

def merged(inputs):
    tokens, origin = {}, {}
    for f in permutation(inputs):
        for p, tk in SOURCES[f].items():
            if p in tokens and origin[p] != f:
                err(f"conflict: '{p}' defined in {origin[p]} and {f} within one permutation")
            tokens[p], origin[p] = tk, f
    return tokens

# ------------------------------------------------------------------ type + value validation
def num(x): return isinstance(x, (int, float)) and not isinstance(x, bool)

def check_literal(type_, v, where, refs):
    """Validate a literal value of a type; collect alias references with their expected type."""
    if isinstance(v, str) and ALIAS.match(v):
        refs.append((ALIAS.match(v).group(1), type_))
        return
    ok = True
    if type_ == "color":
        ok = isinstance(v, dict) and v.get("colorSpace") in {"srgb", "srgb-linear", "hsl", "hwb", "lab", "lch",
                                                               "oklab", "oklch", "display-p3", "a98-rgb",
                                                               "prophoto-rgb", "rec2020", "xyz-d65", "xyz-d50"} \
             and isinstance(v.get("components"), list) and len(v["components"]) == 3 \
             and all(num(c) or c == "none" for c in v["components"]) \
             and (("alpha" not in v) or (num(v["alpha"]) and 0 <= v["alpha"] <= 1)) \
             and (("hex" not in v) or re.fullmatch(r"#[0-9A-Fa-f]{6}", v["hex"]) is not None)
        if ok and v["colorSpace"] == "srgb":
            ok = all(0 <= c <= 1 for c in v["components"] if num(c))
            if ok and "hex" in v and all(num(c) for c in v["components"]):
                if v["hex"].upper() != "#" + "".join(f"{round(c*255):02X}" for c in v["components"]):
                    err(f"hex/components disagree at {where}: {v['hex']} vs {v['components']}")
    elif type_ == "dimension":
        ok = isinstance(v, dict) and num(v.get("value")) and v.get("unit") in ("px", "rem") and len(v) == 2
    elif type_ == "duration":
        ok = isinstance(v, dict) and num(v.get("value")) and v.get("unit") in ("ms", "s") and len(v) == 2
    elif type_ == "fontFamily":
        ok = isinstance(v, str) or (isinstance(v, list) and v and all(isinstance(x, str) for x in v))
    elif type_ == "fontWeight":
        ok = (num(v) and 1 <= v <= 1000) or v in FW_NAMES
    elif type_ == "cubicBezier":
        ok = isinstance(v, list) and len(v) == 4 and all(num(x) for x in v) and 0 <= v[0] <= 1 and 0 <= v[2] <= 1
    elif type_ == "number":
        ok = num(v)
    elif type_ == "strokeStyle":
        ok = v in STROKES or (isinstance(v, dict) and set(v) == {"dashArray", "lineCap"})
    elif type_ in ("border", "transition", "typography"):
        spec = COMPOSITE[type_]
        ok = isinstance(v, dict) and set(v) == set(spec)
        if ok:
            for k, st in spec.items():
                check_literal(st, v[k], f"{where}.{k}", refs)
    elif type_ == "shadow":
        items = v if isinstance(v, list) else [v]
        for i, s in enumerate(items):
            if isinstance(s, str) and ALIAS.match(s):
                refs.append((ALIAS.match(s).group(1), "shadow")); continue
            if not (isinstance(s, dict) and set(COMPOSITE["shadow"]) <= set(s) <= set(COMPOSITE["shadow"]) | {"inset"}):
                ok = False; continue
            if "inset" in s and not isinstance(s["inset"], bool): ok = False
            for k, st in COMPOSITE["shadow"].items():
                check_literal(st, s[k], f"{where}[{i}].{k}", refs)
    else:
        ok = False
    if not ok:
        err(f"invalid {type_} value at {where}: {json.dumps(v)[:120]}")

def analyse(tokens, label):
    types, deps = {}, {}
    def rtype(p, stack=()):
        if p in types: return types[p]
        if p in stack: return None
        tk = tokens[p]
        if tk["declared"]:
            types[p] = tk["declared"]
        elif isinstance(tk["value"], str) and ALIAS.match(tk["value"]):
            tgt = ALIAS.match(tk["value"]).group(1)
            if tgt not in tokens:
                err(f"[{label}] {p} → unresolved reference {{{tgt}}}"); types[p] = None
            elif tgt in stack + (p,):
                err(f"[{label}] circular reference: {' → '.join(stack + (p, tgt))}"); types[p] = None
            else:
                types[p] = rtype(tgt, stack + (p,))
        else:
            types[p] = tk["inherited"]
        return types[p]
    for p in tokens:
        if rtype(p) is None and not any(p in e for e in errors):
            err(f"[{label}] cannot determine type of '{p}' (unresolvable alias or no $type)")
        elif types[p] not in TYPES:
            err(f"[{label}] unknown type '{types[p]}' on {p}")
    for p, tk in tokens.items():
        ty = types.get(p)
        if not ty: continue
        refs = []
        check_literal(ty, tk["value"], f"{tk['file']}#{p}", refs)
        deps[p] = []
        for tgt, expected in refs:
            if tgt not in tokens:
                err(f"[{label}] {p} → unresolved reference {{{tgt}}}"); continue
            if types.get(tgt) != expected:
                err(f"[{label}] {p} → {{{tgt}}} type mismatch: expected {expected}, got {types.get(tgt)}")
            deps[p].append(tgt)
            # layering rules
            src, dst = layer_of(tk["file"]), layer_of(tokens[tgt]["file"])
            if src == "components" and dst == "primitives":
                if types[tgt] == "color":
                    err(f"[{label}] layering: component {p} references primitive color {{{tgt}}}")
                else:
                    info(f"component {p} uses primitive {types[tgt]} {{{tgt}}} (allowed for non-color geometry)")
            if src == "primitives" and dst != "primitives":
                err(f"[{label}] layering: primitive {p} references non-primitive {{{tgt}}}")
            if src == "semantic" and dst == "components":
                err(f"[{label}] layering: semantic {p} references component {{{tgt}}}")
    # cycles (DFS with colors)
    state = {}
    def dfs(n, stack):
        state[n] = 1
        for m in deps.get(n, []):
            if state.get(m) == 1:
                err(f"[{label}] circular reference: {' → '.join(stack + [n, m])}")
            elif not state.get(m):
                dfs(m, stack + [n])
        state[n] = 2
    for n in deps:
        if not state.get(n): dfs(n, [])
    return types, deps

def resolve(tokens, p, memo):
    if p in memo: return memo[p]
    def r(v):
        if isinstance(v, str) and ALIAS.match(v):
            return resolve(tokens, ALIAS.match(v).group(1), memo)
        if isinstance(v, dict): return {k: r(x) for k, x in v.items()}
        if isinstance(v, list): return [r(x) for x in v]
        return v
    memo[p] = r(tokens[p]["value"])
    return memo[p]

# ------------------------------------------------------------------ run validation over all permutations
RES = {}
for perm in PERMS:
    label = f"{perm['theme']}/{perm['platform']}"
    tk = merged(perm)
    types, deps = analyse(tk, label)
    RES[label] = {"tokens": tk, "types": types, "deps": deps}
infos[:] = sorted(set(infos))

# completeness across modifier contexts (same names + same types)
def compare(a_file, b_file, what):
    A, B = SOURCES[a_file], SOURCES[b_file]
    for p in sorted(set(A) ^ set(B)):
        err(f"{what} incomplete: '{p}' only in {a_file if p in A else b_file}")
    LT, DT = RES["light/desktop"]["types"], RES["dark/desktop"]["types"]
    for p in set(A) & set(B):
        ta = LT.get(p) if "light" in a_file or "mobile" in a_file else None
compare("semantic/light.tokens.json", "semantic/dark.tokens.json", "theme")
compare("semantic/platform/mobile.tokens.json", "semantic/platform/desktop.tokens.json", "platform")
for p in SOURCES["semantic/light.tokens.json"]:
    if RES["light/desktop"]["types"].get(p) != RES["dark/desktop"]["types"].get(p):
        err(f"theme type mismatch on {p}")
for p in SOURCES["semantic/platform/mobile.tokens.json"]:
    if RES["light/mobile"]["types"].get(p) != RES["light/desktop"]["types"].get(p):
        err(f"platform type mismatch on {p}")
# orthogonality: a modifier must not redefine set tokens or the other modifier's tokens
setpaths = set().union(*[set(SOURCES[f]) for s in RESOLVER["sets"] for f in set_files(s)])
for f in ["semantic/light.tokens.json", "semantic/platform/mobile.tokens.json"]:
    overlap = setpaths & set(SOURCES[f])
    if overlap: err(f"{f} overrides set tokens: {sorted(overlap)[:5]}")
if set(SOURCES["semantic/light.tokens.json"]) & set(SOURCES["semantic/platform/mobile.tokens.json"]):
    err("theme and platform modifiers are not orthogonal")

def gate():
    if errors:
        print(f"errors: {len(errors)}")
        for e in errors[:60]: print("  ERROR", e)
        sys.exit(1)
gate()  # structural/reference errors stop the build before values are resolved
for label, R in RES.items():
    memo = {}
    R["values"] = {p: resolve(R["tokens"], p, memo) for p in R["tokens"]}

# duplicate-value report within primitives (same literal under two names)
seen = {}
for f, toks in SOURCES.items():
    if not f.startswith("primitives"): continue
    for p, t in toks.items():
        if isinstance(t["value"], str) and ALIAS.match(t["value"]): continue
        key = (p.split(".")[0], RES["light/desktop"]["types"].get(p), json.dumps(t["value"], sort_keys=True))
        seen.setdefault(key, []).append(p)
DUPES = [v for v in seen.values() if len(v) > 1]
for d in DUPES:
    warn(f"duplicate primitive value: {', '.join(d)}")

# ------------------------------------------------------------------ contrast audit
def lum(c):
    def ch(x): return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = [ch(x) for x in c["components"]]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b
def ratio(fg, bg):
    if fg.get("alpha", 1) < 1:  # composite over bg
        a_ = fg["alpha"]
        fg = {"components": [a_ * f + (1 - a_) * b for f, b in zip(fg["components"], bg["components"])]}
    la, lb = lum(fg), lum(bg)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

TEXT, UI = 4.5, 3.0
PAIRS = []  # (fg, bg, min, rule, note)
for fg in ["primary", "secondary", "muted", "link"]:
    for bg in ["default", "app", "subtle", "elevated", "selected"]:
        PAIRS.append((f"color.text.{fg}", f"color.surface.{bg}", TEXT, "1.4.3", "text on surface"))
PAIRS.append(("color.text.inverse", "color.surface.inverse", TEXT, "1.4.3", "tooltip/toast"))
for v in ["primary", "destructive"]:
    for s in ["bg", "bg-hover", "bg-pressed"]:
        PAIRS.append((f"color.action.{v}.fg", f"color.action.{v}.{s}", TEXT, "1.4.3", f"{v} button label"))
    PAIRS.append((f"color.action.{v}.bg", "color.surface.default", UI, "1.4.11", f"{v} button vs surface"))
for s in ["bg", "bg-hover", "bg-pressed"]:
    PAIRS.append(("color.action.secondary.fg", f"color.action.secondary.{s}", TEXT, "1.4.3", "secondary button label"))
PAIRS.append(("color.action.secondary.border", "color.surface.default", UI, "1.4.11", "secondary button outline"))
for s in ["bg-hover", "bg-pressed"]:
    PAIRS.append(("color.action.tertiary.fg", f"color.action.tertiary.{s}", TEXT, "1.4.3", "tertiary button label"))
PAIRS.append(("color.action.tertiary.fg", "color.surface.default", TEXT, "1.4.3", "tertiary button label"))
for g in ["status", "feedback"]:
    keys = ["available", "confirmed", "pending", "completed", "cancelled", "rescheduled"] if g == "status" \
        else ["success", "warning", "error", "info"]
    for k in keys:
        PAIRS.append((f"color.{g}.{k}.fg", f"color.{g}.{k}.bg", TEXT, "1.4.3", f"{k} label"))
        PAIRS.append((f"color.{g}.{k}.icon", f"color.{g}.{k}.bg", UI, "1.4.11", f"{k} icon"))
        if g == "status":
            PAIRS.append((f"color.{g}.{k}.icon", "color.surface.default", UI, "1.4.11", f"{k} dot/bar on surface"))
for bg in ["default", "app", "subtle", "elevated"]:
    PAIRS.append(("color.border.strong", f"color.surface.{bg}", UI, "1.4.11", "control boundary"))
    PAIRS.append(("color.border.focus", f"color.surface.{bg}", UI, "1.4.11 / 2.4.13", "focus ring"))
PAIRS.append(("color.border.focus", "color.action.primary.bg", 1.0, "info", "ring vs primary fill (offset gap provides separation)"))
PAIRS.append(("color.border.error", "color.surface.default", UI, "1.4.11", "error field boundary"))
PAIRS.append(("color.interaction.selected.fg", "color.interaction.selected.bg", TEXT, "1.4.3", "selected item label"))
PAIRS.append(("color.interaction.selected.border", "color.surface.default", UI, "1.4.11", "selected outline"))
PAIRS.append(("color.text.primary", "color.interaction.hover", TEXT, "1.4.3", "text on hover row"))
PAIRS.append(("color.text.secondary", "color.interaction.hover", TEXT, "1.4.3", "meta on hover row"))
PAIRS.append(("color.accent.fg", "color.accent.bg", TEXT, "1.4.3", "accent label"))
PAIRS.append(("color.accent.solid", "color.surface.default", UI, "1.4.11", "now line"))
for i in range(1, 5):
    PAIRS.append((f"color.chart.series-{i}", "color.surface.default", UI, "1.4.11", "chart mark"))
PAIRS.append(("color.text.disabled", "color.interaction.disabled.bg", 0, "exempt", "disabled text (WCAG exempt)"))

CONTRAST = {}
for theme in ["light", "dark"]:
    vals = RES[f"{theme}/desktop"]["values"]
    rows = []
    for fg, bg, mn, rule, note in PAIRS:
        r = ratio(vals[fg], vals[bg])
        status = "exempt" if rule == "exempt" else ("info" if rule == "info" else ("pass" if r >= mn else "FAIL"))
        rows.append({"fg": fg, "bg": bg, "ratio": round(r, 2), "min": mn, "wcag": rule, "use": note,
                     "status": status, "fg_hex": vals[fg]["hex"], "bg_hex": vals[bg]["hex"]})
        if status == "FAIL":
            err(f"contrast [{theme}] {fg} on {bg} = {r:.2f}:1 (needs {mn}:1, WCAG {rule})")
    CONTRAST[theme] = rows

# ------------------------------------------------------------------ report + stop on errors
def summary():
    print(f"errors: {len(errors)}  warnings: {len(warnings)}  info: {len(infos)}")
    for e in errors[:60]: print("  ERROR", e)
    for w in warnings[:20]: print("  WARN ", w)
summary()
if errors:
    sys.exit(1)

# ================================================================== TRANSFORMS
def cssname(path):
    return "--cv-" + "-".join(x for x in path.split(".") if x != "$root")

def color_css(v):
    r, g, b = v["components"]
    if v.get("alpha", 1) < 1:
        return f"rgb({round(r*255)} {round(g*255)} {round(b*255)} / {v['alpha']})"
    return v.get("hex", "#%02X%02X%02X" % (round(r*255), round(g*255), round(b*255))).upper()

def lit(type_, v, path=""):
    """Literal (or var() for aliases) CSS for a value of a type."""
    if isinstance(v, str) and ALIAS.match(v):
        return f"var({cssname(ALIAS.match(v).group(1))})"
    if type_ == "color": return color_css(v)
    if type_ == "dimension":
        if path.startswith("font.size.") and v["unit"] == "px":
            return f"{v['value']/16:g}rem"
        return f"{v['value']:g}{v['unit']}"
    if type_ == "duration": return f"{v['value']:g}{v['unit']}"
    if type_ == "number": return f"{v:g}"
    if type_ == "fontWeight": return str(FW_NAMES.get(v, v))
    if type_ == "fontFamily":
        fams = v if isinstance(v, list) else [v]
        generic = {"serif", "sans-serif", "monospace", "system-ui", "cursive", "fantasy"}
        return ", ".join(f if f in generic or f.startswith("-") else f'"{f}"' for f in fams)
    if type_ == "cubicBezier": return "cubic-bezier(" + ", ".join(f"{x:g}" for x in v) + ")"
    if type_ == "strokeStyle": return v if isinstance(v, str) else "dashed"
    if type_ == "border":
        return f"{lit('dimension', v['width'])} {lit('strokeStyle', v['style'])} {lit('color', v['color'])}"
    if type_ == "transition":
        return f"{lit('duration', v['duration'])} {lit('cubicBezier', v['timingFunction'])} {lit('duration', v['delay'])}"
    if type_ == "shadow":
        items = v if isinstance(v, list) else [v]
        out = []
        for s in items:
            if isinstance(s, str):
                out.append(lit("shadow", s)); continue
            out.append(("inset " if s.get("inset") else "") + " ".join(
                lit("dimension", s[k]) for k in ["offsetX", "offsetY", "blur", "spread"]) + " " + lit("color", s["color"]))
        return ", ".join(out)
    raise ValueError(type_)

TYPO_SUB = [("font-family", "fontFamily", "fontFamily"), ("font-size", "fontSize", "dimension"),
            ("font-weight", "fontWeight", "fontWeight"), ("letter-spacing", "letterSpacing", "dimension"),
            ("line-height", "lineHeight", "number")]

def decls(paths, label):
    tk, ty = RES[label]["tokens"], RES[label]["types"]
    lines = []
    for p in paths:
        t, v, name = ty[p], tk[p]["value"], cssname(p)
        if t == "typography":
            for suffix, key, st in TYPO_SUB:
                val = f"var({cssname(ALIAS.match(v).group(1))}-{suffix})" if isinstance(v, str) else lit(st, v[key])
                lines.append(f"  {name}-{suffix}: {val};")
        else:
            lines.append(f"  {name}: {lit(t, v, p)};")
    return lines

def paths_from(files):
    out = []
    for f in files:
        out += list(SOURCES[f].keys())
    return out

PRIM = paths_from(set_files("primitives"))
BASE = paths_from(set_files("semantic-base"))
COMP = paths_from(set_files("components"))
LIGHT = list(SOURCES["semantic/light.tokens.json"])
MOB = list(SOURCES["semantic/platform/mobile.tokens.json"])
STAMP = "Generated by scripts/build.py from DTCG 2025.10 sources. Do not edit by hand."

css = [f"/* ClearVisit design tokens — {STAMP}",
       "   Layers: primitives (:root) → semantic theme + platform → components.",
       "   Component and base-semantic variables are re-declared on every [data-theme] / [data-platform]",
       "   scope so their var() references re-resolve there (custom properties resolve where declared). */", ""]
css += ["/* 1 · Primitives */", ":root {"] + decls(PRIM, "light/desktop") + ["}", ""]
css += ['/* 2 · Semantic — theme: light (default) */', ':root, [data-theme="light"] {'] + decls(LIGHT, "light/desktop") + ["}", ""]
css += ['/* 3 · Semantic — platform: desktop (default) */', ':root, [data-platform="desktop"] {'] + decls(MOB, "light/desktop") + ["}", ""]
css += ['/* 3b · Semantic — platform: mobile */', '[data-platform="mobile"] {'] + decls(MOB, "light/mobile") + ["}", ""]
css += ["/* 4 · Semantic base + components (re-resolved per scope) */", ":root, [data-theme], [data-platform] {"] + \
       decls(BASE + COMP, "light/desktop") + ["}", ""]
dur = [p for p in PRIM if p.startswith("duration.") and p != "duration.0"]
css += ["/* Reduced motion: collapse durations at the primitive layer, every transition follows. */",
        "@media (prefers-reduced-motion: reduce) {", "  :root {"] + \
       [f"    {cssname(p)}: 0.01ms;" for p in dur] + ["  }", "}", ""]
# typography utilities
css += ["/* Text-style utilities (one class per semantic role) */"]
for p in [p for p in MOB if p.startswith("text-style.")]:
    n = cssname(p)
    css += [f".cv-{p.replace('.', '-').replace('text-style-', 'text-')} {{",
            f"  font-family: var({n}-font-family); font-size: var({n}-font-size); font-weight: var({n}-font-weight);",
            f"  line-height: var({n}-line-height); letter-spacing: var({n}-letter-spacing);", "}"]
css_text = "\n".join(css) + "\n"

dark_body = decls(LIGHT, "dark/desktop")
dark = [f"/* ClearVisit dark theme — {STAMP}", "   Load after clearvisit.css. Same semantic names, different primitive references. */", "",
        '[data-theme="dark"] {', "  color-scheme: dark;"] + dark_body + ["}", "",
        "/* Follow the OS setting unless the product forces light. */",
        "@media (prefers-color-scheme: dark) {", '  :root:not([data-theme="light"]) {', "    color-scheme: dark;"] + \
       ["  " + l for l in dark_body] + ["  }", "}", ""]
dark_text = "\n".join(dark)

os.makedirs(GEN, exist_ok=True)
open(os.path.join(GEN, "clearvisit.css"), "w").write(css_text)
open(os.path.join(GEN, "clearvisit.dark.css"), "w").write(dark_text)

# CSS sanity: every var() used is defined; braces balanced
defined = set(re.findall(r"^\s*(--cv-[a-z0-9-]+):", css_text + dark_text, re.M))
used = set(re.findall(r"var\((--cv-[a-z0-9-]+)\)", css_text + dark_text))
missing = used - defined
CSS_CHECK = {"defined": len(defined), "referenced": len(used), "undefined_refs": sorted(missing),
             "braces_balanced": (css_text + dark_text).count("{") == (css_text + dark_text).count("}")}
if missing or not CSS_CHECK["braces_balanced"]:
    print("CSS CHECK FAILED", CSS_CHECK); sys.exit(1)

# ------------------------------------------------------------------ resolved DTCG bundles (aliases preserved)
def deep_merge(a, b):
    for k, v in b.items():
        if isinstance(v, dict) and "$value" not in v and isinstance(a.get(k), dict) and "$value" not in a[k]:
            deep_merge(a[k], v)
        else:
            a[k] = copy.deepcopy(v)
    return a
os.makedirs(os.path.join(GEN, "dtcg"), exist_ok=True)
for perm in PERMS:
    tree = {}
    for f in permutation(perm):
        deep_merge(tree, read(f))
    tree["$description"] = f"ClearVisit tokens, theme={perm['theme']}, platform={perm['platform']}. Merged per clearvisit.resolver.json; all aliases preserved. {STAMP}"
    json.dump(tree, open(os.path.join(GEN, "dtcg", f"clearvisit.{perm['theme']}-{perm['platform']}.tokens.json"), "w"), indent=2, ensure_ascii=False)
bundle = copy.deepcopy(RESOLVER)
bundle["description"] += " Bundled: file references inlined (Resolver §7.1)."
for s in bundle["sets"].values():
    s["sources"] = [read(x["$ref"]) for x in s["sources"]]
for m in bundle["modifiers"].values():
    for c, srcs in m["contexts"].items():
        m["contexts"][c] = [read(x["$ref"]) for x in srcs]
json.dump(bundle, open(os.path.join(GEN, "dtcg", "clearvisit.bundle.resolver.json"), "w"), indent=2, ensure_ascii=False)

# ------------------------------------------------------------------ Figma import files
# Figma imports DTCG per mode: color, dimension(px), fontFamily(single string), duration(s), number.
# Cross-collection aliases use com.figma.aliasData; composites become Styles (see figma/styles.json).
FIGMA_OK = {"color", "dimension", "fontFamily", "duration", "number", "fontWeight"}
COLL = {"primitives": "Primitives", "semantic-base": "Platform", "theme": "Theme",
        "platform": "Platform", "components": "Components"}
def collection_of(file):
    if file.startswith("primitives"): return "Primitives"
    if file.startswith("components"): return "Components"
    if file in ("semantic/light.tokens.json", "semantic/dark.tokens.json"): return "Theme"
    return "Platform"
def fig_lit(t, v):
    if t == "duration": return {"value": v["value"] / 1000 if v["unit"] == "ms" else v["value"], "unit": "s"}
    if t == "fontFamily": return v[0] if isinstance(v, list) else v
    if t == "fontWeight": return FW_NAMES.get(v, v)
    return v
def fig_type(t): return "number" if t == "fontWeight" else t
FIGMA_MAP, STYLES = [], {"textStyles": [], "effectStyles": []}
def figma_file(paths, label, coll):
    tk, ty, vals = RES[label]["tokens"], RES[label]["types"], RES[label]["values"]
    out = {}
    for p in paths:
        t = ty[p]
        if t not in FIGMA_OK: continue
        node = out
        for part in p.split(".")[:-1]:
            node = node.setdefault(part, {})
        v = tk[p]["value"]
        entry = {"$type": fig_type(t)}
        if isinstance(v, str) and ALIAS.match(v):
            tgt = ALIAS.match(v).group(1)
            tcoll = collection_of(tk[tgt]["file"])
            if tcoll == coll:
                entry["$value"] = v
            else:
                entry["$value"] = fig_lit(t, vals[p])
                entry["$extensions"] = {"com.figma.aliasData": {
                    "targetVariableSetName": tcoll, "targetVariableName": tgt.replace(".", "/")}}
        else:
            entry["$value"] = fig_lit(t, v)
        if tk[p]["desc"]: entry["$description"] = tk[p]["desc"]
        node[p.split(".")[-1].replace("$root", "default")] = entry
    return out
fdir = os.path.join(GEN, "figma")
os.makedirs(fdir, exist_ok=True)
def dump(name, obj): json.dump(obj, open(os.path.join(fdir, name), "w"), indent=2, ensure_ascii=False)
dump("01-primitives.value.tokens.json", figma_file(PRIM, "light/desktop", "Primitives"))
dump("02-theme.light.tokens.json", figma_file(LIGHT, "light/desktop", "Theme"))
dump("02-theme.dark.tokens.json", figma_file(LIGHT, "dark/desktop", "Theme"))
def type_roles(label):
    """Figma variables can't hold typography composites, but text styles can bind number
    variables. Flatten each platform text-style role so one text style switches with the Platform mode."""
    out = {}
    for p in MOB:
        if RES[label]["types"][p] != "typography": continue
        v = RES[label]["values"][p]
        size, lh = v["fontSize"]["value"], v["lineHeight"]
        role = out.setdefault("type-role", {}).setdefault(p.split(".")[1], {})
        role["font-size"] = {"$type": "dimension", "$value": {"value": size, "unit": "px"}}
        role["line-height"] = {"$type": "dimension", "$value": {"value": round(size * lh, 2), "unit": "px"},
                               "$description": "Pixel line height for Figma (DTCG source stores a unitless multiplier)."}
        role["font-weight"] = {"$type": "number", "$value": FW_NAMES.get(v["fontWeight"], v["fontWeight"])}
        role["letter-spacing"] = {"$type": "dimension", "$value": v["letterSpacing"]}
    return out
for lab, name in [("light/mobile", "03-platform.mobile.tokens.json"), ("light/desktop", "03-platform.desktop.tokens.json")]:
    dump(name, deep_merge(figma_file(BASE + MOB, lab, "Platform"), type_roles(lab)))
dump("04-components.value.tokens.json", figma_file(COMP, "light/desktop", "Components"))
for p in PRIM + LIGHT + MOB + BASE + COMP:
    t = RES["light/desktop"]["types"][p]
    file = RES["light/desktop"]["tokens"][p]["file"]
    if t in FIGMA_OK:
        FIGMA_MAP.append((p, collection_of(file), p.replace(".", "/").replace("$root", "default"), fig_type(t)))
    elif t == "typography" and (p.startswith("text-style.") or p.startswith("typography.")):
        v = RES["light/desktop"]["tokens"][p]["value"]
        STYLES["textStyles"].append({"token": p, "styleName": p.replace(".", "/"),
                                     "mobile": RES["light/mobile"]["values"][p], "desktop": RES["light/desktop"]["values"][p],
                                     "bindVariables": None if isinstance(v, str) else {k: v[k] for k in v}})
    elif t == "shadow":
        STYLES["effectStyles"].append({"token": p, "styleName": p.replace(".", "/"),
                                       "light": RES["light/desktop"]["values"][p], "dark": RES["dark/desktop"]["values"][p]})
dump("styles.json", STYLES)

# ------------------------------------------------------------------ inventory + reports
def count(files): return sum(len(SOURCES[f]) for f in files)
INVENTORY = {
    "primitives": {f.split("/")[-1]: len(SOURCES[f]) for f in set_files("primitives")},
    "semantic": {"base": count(set_files("semantic-base")), "theme (per mode)": len(LIGHT),
                 "platform (per mode)": len(MOB)},
    "components": {f.split("/")[-1]: len(SOURCES[f]) for f in set_files("components")},
}
INVENTORY["total_unique_paths"] = len(RES["light/desktop"]["tokens"])
report = {
    "generated": datetime.date.today().isoformat(),
    "spec": "DTCG Format + Resolver 2025.10",
    "permutations_validated": [f"{p['theme']}/{p['platform']}" for p in PERMS],
    "checks": {
        "json_syntax": "pass (all files parsed with json.load)",
        "token_vs_group_shape": "pass", "names (no { } . or leading $)": "pass",
        "types_declared_or_inherited": "pass", "value_shapes_per_type": "pass",
        "alias_resolution": "pass", "alias_type_compatibility": "pass", "circular_references": "none",
        "cross_file_conflicts": "none", "theme_completeness": "pass", "platform_completeness": "pass",
        "modifier_orthogonality": "pass", "layering (no component→primitive color)": "pass",
        "css_var_references": CSS_CHECK,
    },
    "warnings": warnings, "info": infos, "inventory": INVENTORY, "contrast": CONTRAST,
}
os.makedirs(os.path.join(GEN, "reports"), exist_ok=True)
json.dump(report, open(os.path.join(GEN, "reports", "validation.json"), "w"), indent=2)

# docs tables -----------------------------------------------------------
def show(label, p):
    v, t = RES[label]["values"][p], RES[label]["types"][p]
    if t == "color": return color_css(v)
    if t == "typography":
        return f"{v['fontSize']['value']}/{v['lineHeight']} · {FW_NAMES.get(v['fontWeight'], v['fontWeight'])}"
    if t == "shadow": return "shadow"
    try: return lit(t, v, p).replace("|", "\\|")
    except Exception: return json.dumps(v)
def refcell(label, p):
    v = RES[label]["tokens"][p]["value"]
    return f"`{v}`" if isinstance(v, str) and ALIAS.match(v) else "—"
md = [f"# Token reference", "", f"_{STAMP}_", "",
      "Every token, its type, what it references, and its resolved value in each context. CSS custom property = `--cv-` + path with dots → dashes (`$root` dropped).", ""]
def table(title, paths, cols):
    md.extend([f"## {title}", "", "| Token | Type | " + " | ".join(c[0] for c in cols) + " |",
               "|---|---|" + "---|" * len(cols)])
    for p in paths:
        row = [f"`{p}`", RES['light/desktop']['types'][p]] + [c[1](p) for c in cols]
        md.append("| " + " | ".join(row) + " |")
    md.append("")
table("Primitives", PRIM, [("Value", lambda p: show("light/desktop", p))])
table("Semantic — base", BASE, [("References", lambda p: refcell("light/desktop", p)), ("Value", lambda p: show("light/desktop", p))])
table("Semantic — theme", LIGHT, [("Light →", lambda p: refcell("light/desktop", p)), ("Light", lambda p: show("light/desktop", p)),
                                   ("Dark →", lambda p: refcell("dark/desktop", p)), ("Dark", lambda p: show("dark/desktop", p))])
table("Semantic — platform", MOB, [("Mobile →", lambda p: refcell("light/mobile", p)), ("Mobile", lambda p: show("light/mobile", p)),
                                    ("Desktop →", lambda p: refcell("light/desktop", p)), ("Desktop", lambda p: show("light/desktop", p))])
table("Components", COMP, [("References", lambda p: refcell("light/desktop", p)),
                           ("Light/desktop", lambda p: show("light/desktop", p)), ("Dark/mobile", lambda p: show("dark/mobile", p))])
open(os.path.join(ROOT, "docs", "token-reference.md"), "w").write("\n".join(md) + "\n")

# figma mapping table + contrast tables as include files for docs
fm = ["| DTCG token | Figma collection | Figma variable | Variable type |", "|---|---|---|---|"]
fm += [f"| `{p}` | {c} | `{n}` | {t} |" for p, c, n, t in FIGMA_MAP]
open(os.path.join(GEN, "reports", "figma-mapping.md"), "w").write("\n".join(fm) + "\n")
cm = []
for theme in ["light", "dark"]:
    cm += [f"### {theme.title()} theme", "", "| Foreground | Background | Ratio | Min | WCAG | Use | Result |", "|---|---|---|---|---|---|---|"]
    for r in CONTRAST[theme]:
        cm.append(f"| `{r['fg']}` {r['fg_hex']} | `{r['bg']}` {r['bg_hex']} | {r['ratio']}:1 | {r['min']}:1 | {r['wcag']} | {r['use']} | {r['status']} |")
    cm.append("")
open(os.path.join(GEN, "reports", "contrast.md"), "w").write("\n".join(cm))
json.dump({"inventory": INVENTORY, "figma_count": len(FIGMA_MAP), "text_styles": len(STYLES["textStyles"]),
           "effect_styles": len(STYLES["effectStyles"]),
           "min_ratio": {t: min(r["ratio"] for r in CONTRAST[t] if r["status"] == "pass") for t in CONTRAST}},
          open(os.path.join(GEN, "reports", "summary.json"), "w"), indent=2)
print("build ok:", json.dumps(INVENTORY))

# resolved values per permutation, for documentation tooling (site/build_site.py)
json.dump({label: {"values": R["values"], "types": R["types"],
                   "refs": {p: R["tokens"][p]["value"] for p in R["tokens"] if isinstance(R["tokens"][p]["value"], str)},
                   "desc": {p: R["tokens"][p]["desc"] for p in R["tokens"] if R["tokens"][p]["desc"]},
                   "ext": {p: R["tokens"][p]["ext"] for p in R["tokens"] if R["tokens"][p]["ext"]}}
           for label, R in RES.items()}, open(os.path.join(GEN, "reports", "resolved.json"), "w"))
