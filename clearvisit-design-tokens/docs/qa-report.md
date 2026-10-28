# Quality assurance report

Date: October 22, 2026. Scope: token package v0.1, generated CSS/Figma outputs, reference components, visual reference page.

Three kinds of result are kept separate:

- **Verified:** checked by an automated test or a tool run, reproducible with the commands below.
- **Observed:** seen in rendered screenshots (Chromium via Playwright, 1440×900 and 390×844, light and dark). One reviewer, no assistive tech.
- **Not verified:** needs people, devices or tools that weren't available.

## Reproduce

```bash
python3 scripts/define_tokens.py      # regenerate palette + source JSON (optional)
python3 scripts/build.py              # validate + generate; exits 1 on any error
python3 tests/test_validator.py       # negative tests
python3 tests/test_propagation.py     # browser tests (needs Playwright + Chromium)
```

## 1. Technical (verified)

| Check | Result |
|---|---|
| JSON syntax, 18 source files + resolver | Pass |
| Token vs group shape (no `$value` with children) | Pass |
| Names (no `{ } .` or leading `$`) | Pass |
| Every token has a declared, inherited or alias-resolved `$type` | Pass, all 4 permutations |
| Value shape per type (color, dimension, duration, fontFamily, fontWeight, cubicBezier, number, strokeStyle, border, transition, shadow, typography) | Pass |
| `hex` agrees with `components` for every color | Pass (failed once during development; fixed at source) |
| Alias resolution and alias type compatibility | Pass |
| Circular references | None |
| Cross-file conflicts within a permutation | None |
| Theme completeness (light ↔ dark, same names + types) | Pass, 99 tokens |
| Platform completeness (mobile ↔ desktop) | Pass, 47 tokens |
| Modifier orthogonality | Pass |
| Layering: component → primitive color | 0 violations; 7 allowed primitive geometry/stroke references listed as info |
| Duplicate primitive values within a category | None |
| CSS: `var()` references defined | 875 variables defined, 0 undefined |
| Negative tests (validator must reject broken input) | **10/10** |
| Browser propagation tests (Chromium) | **13/13** |
| Squarespace embed tests (hostile host CSS, JS disabled, 390px) | **17/17** |
| React examples compile (esbuild) and server-render | Pass |

**Caveat:** DTCG conformance is checked by this project's own validator, written against the 2025.10 spec text. It has not been cross-checked with an independent tool (Style Dictionary 4/5, Terrazzo) because the build environment had no network access. Do that before calling the package spec-compliant.

## 2. Accessibility

| Check | Status | Result |
|---|---|---|
| Text contrast ≥ 4.5:1, 83 pairs × 2 themes | Verified | Pass. Tightest: light muted text on subtle surface 4.64:1 |
| Non-text contrast ≥ 3:1 (borders, focus, icons, chart marks) | Verified | Pass. Tightest: dark control border on elevated surface 3.12:1 |
| Focus ring visible on every surface | Verified (contrast) | 2px + 2px offset; ≥3:1 everywhere |
| Status never color alone | Observed | Every status shows icon + label; pending dashed and cancelled struck on calendar |
| Selected vs disabled time slots distinguishable | Observed | Selected: fill + check icon. Booked: grey fill + strike-through + "booked" label |
| Touch targets | Verified (token values) | Mobile 48px; desktop ≥24px |
| Reduced motion | Verified (CSS output) | Durations collapse to 0.01ms |
| Theme scopes reset inherited text color | Verified (browser test) | Failed during development (dark-on-dark in nested dark scope); fixed |
| Screen readers, keyboard-only calendar, 200% zoom, 320px reflow, color-blindness simulation | **Not verified** | — |

## 3. Architecture

| Check | Result |
|---|---|
| Naming consistent with `naming-conventions.md` | Verified by inspection of generated `token-reference.md` |
| Alias depth | Max chain: component → semantic → (semantic) → primitive. No component skips the semantic layer for color. |
| Duplication | No duplicate primitives. Button, badge and alert colors intentionally consume semantic tokens directly instead of duplicating them. |
| Shared vs platform split | 47 platform tokens; all color is shared. |

## 4. Product application (observed in the reference page)

| Check | Result |
|---|---|
| Mobile booking hierarchy | Provider → date strip → slots → summary → sticky primary CTA that repeats the chosen time. Reads in task order. |
| Availability readability | Search results lead with "next available" + three tappable times per provider; empty state gives the next opening date. |
| Admin table usability | 40px rows, tabular times, status badges, selected row has fill + bar + checked box. |
| Scheduling conflicts | Error banner with names and action, red outline + "Conflict" tag on both events, and the tag repeated in table rows. |
| Calendar status legibility at 30-minute slots | Passable at 48px slots after reducing events to two lines; half-width conflict events truncate patient names. |

## 5. Findings

### Fixed during this build

1. Muted text and control borders failed contrast on the subtle surface → shared lightness ladder adjusted.
2. Color `hex` and `components` disagreed by one 8-bit step → quantisation moved before both are derived; validator rule added.
3. Component tokens didn't switch inside `[data-platform]` subtrees in CSS → re-declaration on every scope; browser test added.
4. Inherited text color stayed light-theme inside dark scopes → `[data-theme]` resets `color`; browser test added.
5. Reference page: horizontal overflow at 390px (absolutely positioned labels escaping scroll containers; a forced 2-column grid span), heading styles leaking into phone mockups, a chip row collapsing in a scrolling grid.

### Open

| # | Finding | Severity | Suggested action |
|---|---|---|---|
| O1 | `text.secondary` (#535F6C) and `text.muted` (#5D6B79) are perceptually close in light theme; hierarchy relies on size and weight | Medium | Darken secondary to slate-800 or merge the two roles; re-run audit |
| O2 | `filter-chip` lives in `desktop.tokens.json` but the patient search screen uses it | Low | Promote to `shared.tokens.json` in 0.2 |
| O3 | Half-width conflict events in a 150px calendar column truncate names | Medium | Minimum column width for conflict days, or stacked conflict layout |
| O4 | Dark theme error fill (`red.950`) is heavy at banner size | Low | Consider a desaturated dark error surface; needs review in context |
| O5 | Atkinson Hyperlegible Next tabular-figure support not confirmed | Medium | Check font features; fall back to a tabular font for times if missing |
| O6 | Figma variables created via Plugin API (618 vars, 0 unresolved aliases); native JSON import route untested; text/effect styles not yet created | Medium | Build text styles bound to `type-role/*` and elevation effect styles; optionally test the JSON import |
| O7 | No independent DTCG validator run | Medium | Run Style Dictionary or Terrazzo against `generated/dtcg/` |
| O8 | Desktop touch target 24px assumes pointer-only admin use | Assumption | Confirm with real admin hardware; add `kiosk` platform if needed |

### Requires manual review

All items in section 2 marked "Not verified", plus the brand assumptions in `architecture.md` (palette, violet status hue, typeface).
