"""Compact Figma variable payloads (for the Plugin API) from the resolved token build."""
import json, re
R = json.load(open("generated/reports/resolved.json"))
rows = [l.split("|") for l in open("generated/reports/figma-mapping.md").read().splitlines()[2:]]
MAP = {r[1].strip().strip("`"): (r[2].strip(), r[3].strip().strip("`"), r[4].strip()) for r in rows}
MODES = {"Primitives": [("Value", "light/desktop")], "Theme": [("Light", "light/desktop"), ("Dark", "dark/desktop")],
         "Platform": [("Mobile", "light/mobile"), ("Desktop", "light/desktop")], "Components": [("Value", "light/desktop")]}
TC = {"color": "C", "dimension": "F", "number": "F", "fontWeight": "F", "duration": "F", "fontFamily": "S"}
def lit(t, v):
    if t == "color":
        a = v.get("alpha", 1); return v["hex"] + ("" if a == 1 else "%02X" % round(a * 255))
    if t == "dimension": return v["value"]
    if t == "duration": return v["value"] / 1000 if v["unit"] == "ms" else v["value"]
    if t == "fontFamily": return v[0] if isinstance(v, list) else v
    return {"regular": 400}.get(v, v) if not isinstance(v, (int, float)) else v
def val(p, label):
    ref = R[label]["refs"].get(p)
    if ref:
        tgt = ref.strip("{}")
        if tgt in MAP: return "@" + MAP[tgt][1]
    return lit(R[label]["types"][p], R[label]["values"][p])
out = {c: {"modes": [m for m, _ in ms], "v": []} for c, ms in MODES.items()}
for p, (coll, name, _) in MAP.items():
    t = R["light/desktop"]["types"][p]
    out[coll]["v"].append([name, TC[t]] + [val(p, lab) for _, lab in MODES[coll]])
for lab, mode in [("light/mobile", 0), ("light/desktop", 1)]:
    pass
# flattened type roles (Platform)
for p in [p for p in R["light/mobile"]["types"] if p.startswith("text-style.")]:
    role = p.split(".")[1]; rowsv = {}
    for lab in ["light/mobile", "light/desktop"]:
        v = R[lab]["values"][p]
        rowsv.setdefault("font-size", []).append(v["fontSize"]["value"])
        rowsv.setdefault("line-height", []).append(round(v["fontSize"]["value"] * v["lineHeight"], 2))
        rowsv.setdefault("font-weight", []).append(v["fontWeight"])
        rowsv.setdefault("letter-spacing", []).append(v["letterSpacing"]["value"])
    for k, vs in rowsv.items():
        out["Platform"]["v"].append([f"type-role/{role}/{k}", "F"] + vs)
for c in out: print(c, len(out[c]["v"]))
json.dump({k: out[k] for k in ["Primitives", "Theme", "Platform"]}, open("/tmp/p1.json", "w"), separators=(",", ":"))
json.dump({"Components": out["Components"]}, open("/tmp/p2.json", "w"), separators=(",", ":"))
