# ClearVisit design tokens

A design token system for **ClearVisit**, a concept healthcare scheduling platform with a patient mobile app and a coordinator desktop tool. Source format: **Design Tokens Community Group (DTCG) Format and Resolver Modules 2025.10.**

> Concept portfolio project. Brand values are assumptions (see `docs/architecture.md`). Names and figures in examples are sample data.

## What's here

```
tokens/                          DTCG source of truth (edit these)
  clearvisit.resolver.json       sets + theme/platform modifiers → 4 permutations
  primitives/                    color, typography, spacing, sizing, radius, border,
                                 elevation, opacity, motion, layout
  semantic/base.tokens.json      theme- and platform-independent semantics
  semantic/light|dark.tokens.json          theme modifier contexts
  semantic/platform/mobile|desktop.tokens.json   platform modifier contexts
  components/shared|mobile|desktop.tokens.json
generated/                       build output (don't edit)
  clearvisit.css                 primitives, light theme, platforms, components
  clearvisit.dark.css            dark theme ([data-theme="dark"] + OS preference)
  dtcg/                          4 merged permutations + bundled resolver
  figma/                         per-mode Figma import files + styles.json
  reports/                       validation, contrast, Figma mapping, resolved values
examples/components.css          reference implementation of all 30 components
examples/react/                  React examples
site/dist/clearvisit-design-system.html  visual design system reference (self-contained)
docs/                            architecture, naming, token reference, component specs,
                                 Figma setup, accessibility, governance, QA report,
                                 AI process log, portfolio case study outline
scripts/                         define_tokens.py, build.py, build_component_docs.py
tests/                           negative validator tests, browser propagation tests
```

## Build

Python 3.10+, no dependencies for the build. Browser tests need Playwright with Chromium.

```bash
python3 scripts/build.py           # validate all 4 permutations, generate outputs; exits 1 on error
python3 tests/test_validator.py    # 10 tests: validator must reject broken input
python3 tests/test_propagation.py  # 13 Chromium checks: theme/platform scopes, semantic swap
python3 scripts/build_component_docs.py
python3 site/build_site.py         # rebuild the reference page (runs both test suites)
```

`scripts/define_tokens.py` regenerates the source JSON from the OKLCH palette definition. Use it for palette-level changes; otherwise edit the JSON directly. **If you edit JSON by hand, don't re-run `define_tokens.py`**, or it will overwrite your edits.

## Use in a web app

```html
<link rel="stylesheet" href="generated/clearvisit.css">
<link rel="stylesheet" href="generated/clearvisit.dark.css">
<body data-platform="mobile">   <!-- patient app; admin uses "desktop" (the default) -->
```

```css
.book-button {
  background: var(--cv-color-action-primary-bg);
  min-height: var(--cv-button-height-md);   /* 48px mobile, 36px desktop */
  border-radius: var(--cv-button-radius);
}
```

Theme follows the OS unless forced with `data-theme="light|dark"`. Any element can set `data-theme` or `data-platform`; component tokens re-resolve inside it. If you set `data-theme` on an inner element, also set `color: var(--cv-color-text-primary)` there (the component CSS does this).

Consume component and semantic variables only. Never use `--cv-color-{hue}-{step}` in product code.

## Status

| | |
|---|---|
| Validation | 0 errors across 4 permutations, 627 tokens each |
| Contrast | 81/81 audited pairs pass WCAG 2.2 AA in each theme |
| Tests | 10/10 negative, 13/13 browser |
| Not done | Figma import, independent DTCG validator run, assistive-tech and user testing |

See `docs/qa-report.md` for open findings.
