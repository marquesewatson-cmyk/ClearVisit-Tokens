"""Negative tests: each case breaks a copy of the token package and asserts the build fails
with the expected message. Run: python3 tests/test_validator.py"""
import json, os, shutil, subprocess, sys, tempfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def case(name, file, mutate, expect):
    tmp = tempfile.mkdtemp()
    for d in ["tokens", "scripts", "docs"]:
        shutil.copytree(os.path.join(ROOT, d), os.path.join(tmp, d))
    p = os.path.join(tmp, "tokens", file)
    data = json.load(open(p)); mutate(data); json.dump(data, open(p, "w"))
    r = subprocess.run([sys.executable, os.path.join(tmp, "scripts", "build.py")], capture_output=True, text=True)
    ok = r.returncode != 0 and expect in r.stdout
    print(("PASS" if ok else "FAIL"), name)
    if not ok: print(r.stdout[-800:])
    shutil.rmtree(tmp)
    return ok

results = [
  case("unresolved alias", "semantic/light.tokens.json",
       lambda d: d["color"]["text"].__setitem__("primary", {"$value": "{color.slate.1234}"}), "unresolved reference"),
  case("circular reference", "semantic/light.tokens.json",
       lambda d: (d["color"]["text"].__setitem__("primary", {"$value": "{color.text.secondary}"}),
                  d["color"]["text"].__setitem__("secondary", {"$value": "{color.text.primary}"})), "circular reference"),
  case("type mismatch", "semantic/light.tokens.json",
       lambda d: d["color"]["text"].__setitem__("primary", {"$type": "color", "$value": "{space.16}"}), "type mismatch"),
  case("component → primitive color", "components/shared.tokens.json",
       lambda d: d["button"].__setitem__("gap", {"$value": "{color.blue.600}"}), "layering"),
  case("dark theme missing token", "semantic/dark.tokens.json",
       lambda d: d["color"]["text"].pop("link"), "theme incomplete"),
  case("bad dimension unit", "primitives/spacing.tokens.json",
       lambda d: d["space"].__setitem__("8", {"$value": {"value": 8, "unit": "pt"}}), "invalid dimension"),
  case("token with children", "primitives/radius.tokens.json",
       lambda d: d["radius"]["4"].__setitem__("child", {"$value": {"value": 1, "unit": "px"}}), "has $value and child"),
  case("illegal name character", "primitives/radius.tokens.json",
       lambda d: d["radius"].__setitem__("1.5", {"$value": {"value": 1.5, "unit": "px"}}), "illegal character"),
  case("contrast regression", "semantic/light.tokens.json",
       lambda d: d["color"]["text"].__setitem__("muted", {"$value": "{color.slate.400}"}), "contrast [light]"),
  case("platform modifiers overlap", "semantic/platform/mobile.tokens.json",
       lambda d: d.__setitem__("color", {"text": {"primary": {"$value": "{color.slate.900}"}}}), "conflict"),
]
print(f"{sum(results)}/{len(results)} negative tests passed")
sys.exit(0 if all(results) else 1)
