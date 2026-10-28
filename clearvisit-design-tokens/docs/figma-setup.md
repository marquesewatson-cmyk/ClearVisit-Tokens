# Figma implementation guide

Status: the four collections now exist in the Figma file **ClearVisit Design Tokens** (https://www.figma.com/design/zlFzNokKlHYPcMs4kgigYV), created through the Figma Plugin API from the same build data: 618 variables, 505 aliases, 0 unresolved, scopes and `WEB` code syntax (`var(--cv-…)`) set, Primitives hidden from publishing. Spot checks resolved correctly in every mode (e.g. `color/action/primary/bg` → blue/600 Light, blue/400 Dark; `size/control/md` → 48 Mobile, 36 Desktop).

The JSON import route below (`generated/figma/`) remains an alternative for rebuilding from scratch; it has **not** been tested through Figma's importer. Text and effect styles are not created yet.

## What Figma imports natively, and what it doesn't

Figma's Variables view imports DTCG JSON, one file per mode, one collection per import. Its documented limits shaped the generated files:

| DTCG type | Figma | Limit, and how the build handles it |
|---|---|---|
| color | Color variable | sRGB/HSL only. Source is sRGB. |
| dimension | Number variable | **px only.** Source is authored in px (CSS output converts font sizes to rem). |
| fontFamily | String variable | **Single name only.** Build takes the first family from the fallback stack. |
| duration | Number variable | **Seconds only.** Build converts 150ms → 0.15. |
| number, fontWeight | Number variable | fontWeight emitted as a number. |
| typography, shadow, border, transition, cubicBezier, strokeStyle | **Not imported** | Become Text styles / Effect styles (`generated/figma/styles.json`) or stay code-only. |

Other rules that matter:

- Variables are created only for tokens **present in every file** of a multi-file import, with the **same type** in each. The build's completeness check guarantees this for Light/Dark and Mobile/Desktop.
- Dotted groups become slash names: `color.text.primary` → `color/text/primary`.
- **Cross-collection aliases** are not expressed with `{curly}` references. They use the `com.figma.aliasData` extension (target collection name + variable name). The generated files write the resolved literal value *and* the alias data, so if Figma can't find the target, you still get the correct value rather than an empty variable.

## Collections

| # | Collection | Modes | Contents | Variables |
|---|---|---|---|---|
| 1 | **Primitives** | Value | Palette, spacing, sizing, radius, border widths, opacity, durations, font primitives, layout | 186 |
| 2 | **Theme** | Light, Dark | Semantic color (text, surface, border, action, interaction, status, feedback, accent, chart) | 96 |
| 3 | **Platform** | Mobile, Desktop | Semantic size/space/radius/layout, base rhythm (same value in both modes), flattened type roles | 57 + 80 type-role |
| 4 | **Components** | Value | Component tokens aliasing Theme and Platform | 199 |

The brief suggested separate Spacing and Sizing collections. I merged them into **Platform**: they switch together (a designer never wants mobile spacing with desktop control heights), and one mode switch on a frame is less error-prone than two.

Components has a single mode on purpose. A component variable aliases a Theme or Platform variable, and Figma resolves that alias using whatever mode the *frame* has set for the Theme and Platform collections. So a button placed in a frame set to Dark + Mobile gets dark colors and 48px height with no component-level modes.

## Import order

Import in order, because aliases point backwards:

1. New collection **Primitives** → drag `01-primitives.value.tokens.json` → rename mode to `Value`.
2. New collection **Theme** → drag `02-theme.light.tokens.json` and `02-theme.dark.tokens.json` together → rename modes `Light`, `Dark`.
3. New collection **Platform** → drag `03-platform.mobile.tokens.json` and `03-platform.desktop.tokens.json` → rename `Mobile`, `Desktop`.
4. New collection **Components** → `04-components.value.tokens.json`.
5. Spot-check aliases: `Theme › color/action/primary/bg` should show an alias chip to `Primitives › color/blue/600`, not a raw hex.

## Styles (things variables can't hold)

**Text styles.** Create one per role in `generated/figma/styles.json` (`text-style/body`, `text-style/table-cell`, …). Bind font size, line height, weight and letter spacing to `Platform › type-role/<role>/*`. Because those variables have Mobile and Desktop modes, a single text style switches with the frame's platform mode. Font family: bind to `Primitives › font/family/sans`.

Line height is emitted in px for Figma (`16 × 1.45 = 23.2`) because Figma binds pixel line heights; the DTCG source keeps the unitless multiplier. This is a deliberate, documented divergence between source and Figma.

**Effect styles.** `elevation/raised`, `elevation/popover`, `elevation/overlay` for Light and Dark (6 styles), plus the primitive shadow ramps. Shadow colors can be bound to the alpha color variables.

**Code-only.** Transitions, easing curves, z-index layers and stroke styles don't have useful Figma representations. They stay in code and in component documentation.

## Variable scoping

Set scopes so the picker only offers sensible options:

| Variables | Scope |
|---|---|
| `color/text/*`, `color/action/*/fg` | Text fill |
| `color/surface/*`, `color/action/*/bg*`, `color/status/*/bg` | Frame fill, Shape fill |
| `color/border/*` | Stroke |
| `space/*`, `space/inset/*` | Gap, Padding |
| `size/*` | Width and height |
| `radius/*` | Corner radius |
| All **Primitives** | Hide from publishing |

Hiding primitives from the published library is the Figma equivalent of the build's layering rule: designers pick `color/text/secondary`, not `color/slate/700`.

## Components in the library

- **Shared library page:** the 15 shared components, built once, with frames set to Platform = Desktop by default. Variants for state (`Default, Hover, Pressed, Focus, Disabled`) and, where relevant, `Status` or `Tone`.
- **Mobile page:** the 7 patient components, frames set to Platform = Mobile.
- **Desktop page:** the 8 admin components, Platform = Desktop.
- Size is **not** a variant property. Mobile vs desktop size comes from the Platform mode, which avoids doubling every variant set.
- Use `Status` as a variant property on badges and calendar events with values matching token names (`available`, `confirmed`, …). A string variable can then drive the variant if needed.

## Full mapping

Every DTCG path, its collection, Figma variable name and type: `generated/reports/figma-mapping.md` (538 rows).

## Verification still needed

These are not yet confirmed and should be checked on first import:

1. That `com.figma.aliasData` with `targetVariableSetName` + `targetVariableName` (no IDs) links correctly on a fresh file.
2. Whether Figma imports `$description` (a community report says Figma's export omits it).
3. That durations import correctly as seconds and dimensions with decimal values (letter spacing −0.4px).
4. Mode limits on your Figma plan (Platform and Theme each need 2 modes).

If native import misbehaves, fall back to Tokens Studio or the Figma Variables REST API; the per-permutation bundles in `generated/dtcg/` are suitable inputs for both.
