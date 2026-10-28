# AI-assisted workflow and contribution log

## How to read this log

This system was drafted with an AI assistant (Claude, Anthropic) in a single working session, from a written brief. The assistant wrote the generator, validator, token JSON, CSS, components, documentation and reference page, and ran the automated checks.

That means the **"Designer decision"** column is not filled in for you. Each row lists what the AI proposed and what was automatically verified; the decision column is where *you* record whether you accepted, changed or rejected the proposal, and why. Until you do, these are AI proposals, not your design decisions. Don't present them as reviewed in a portfolio until they are.

No human review, usability testing or stakeholder feedback has happened yet.

## Contribution log

| # | Task | AI contribution | Validation method (done) | Designer decision (to complete) | Deliverable |
|---|---|---|---|---|---|
| 1 | Read the standard | Read DTCG Format, Color index and Resolver 2025.10; read Figma's DTCG import constraints | Spec rules encoded as validator checks | Confirm you've read the Resolver module; decide whether to adopt modifiers or keep separate theme files | Validator rules, `architecture.md` |
| 2 | Audit existing UI values | **Not done.** No existing ClearVisit UI or brand was provided | — | Supply screens or brand assets; replace the assumed palette | — |
| 3 | Strategy and principles | Drafted problem statement and 7 principles, each tied to an enforceable token rule | None (judgement) | Edit to your own voice; cut to 5 if that tells the story better | `architecture.md` §A–B |
| 4 | Layer architecture | Proposed 3 layers + 2 orthogonal modifiers (theme, platform) and layering rules | Build enforces layering and orthogonality | Accept or change platform-as-modifier vs separate component files | `clearvisit.resolver.json` |
| 5 | Generate palette | Generated 7 hue families on a shared OKLCH lightness ladder; proposed brand blue, teal accent, violet status hue | Contrast audit (failed 3 pairs first; ladder adjusted) | Approve hues; this is where brand judgement matters most | `color.tokens.json` |
| 6 | Organize primitives | Spacing, sizing, radius, border, elevation, opacity, motion, layout, typography | Type and shape checks | Check the typeface choice and type scale against real screens | `primitives/*.tokens.json` |
| 7 | Review semantic naming | Proposed role-based names and conventions | Completeness checks across contexts | Rename anything that doesn't match how your team talks | `semantic/*.tokens.json`, `naming-conventions.md` |
| 8 | Status system | Six statuses with color, icon and label; pending dashed, cancelled struck | Contrast on fills; observed in screenshots | Validate with coordinators that the six statuses (and "conflict") match real workflows | `light/dark.tokens.json` |
| 9 | Component tokens | 30 components; chose which get their own tokens and which consume semantics | Layering rule; reference resolution | Review the "only when meaningful" calls | `components/*.tokens.json`, `component-specs.md` |
| 10 | Detect duplicates | Duplicate-value check within categories (first version flagged cross-category noise; scoped) | Automated | — | Validator |
| 11 | Generate DTCG JSON | Wrote generator; JSON is the source of truth afterwards | JSON parse; DTCG shape checks | Decide whether to keep the generator or edit JSON directly | `tokens/` |
| 12 | Validate references | Alias resolution, type compatibility, cycles, plus 10 negative tests | 10/10 negative tests | — | `scripts/build.py`, `tests/` |
| 13 | Translate JSON → CSS | Generator with var() chains, rem font sizes, scoped re-resolution, reduced motion | 875 vars, 0 undefined; 13/13 Chromium tests | Review the scoped re-declaration approach with an engineer | `generated/*.css` |
| 14 | Figma handoff | Per-mode import files, alias metadata, flattened type roles, styles spec | Checked against Figma's documented limits **only** | **Import into Figma and record what works** | `generated/figma/`, `figma-setup.md` |
| 15 | Reference components | CSS + React examples | esbuild compile, SSR render, screenshots | Compare against your own Figma components | `examples/` |
| 16 | Visual reference | 10-section page, 5 screens, live semantic-swap demo | Screenshots at 2 sizes × 2 themes; 5 layout bugs found and fixed | Critique the visual design yourself | `site/clearvisit-design-system.html` |
| 17 | Draft documentation | All docs in `docs/` | Figures pulled from build reports | Rewrite case study copy in your voice | `docs/` |

## What the AI got wrong (and how it was caught)

These are useful portfolio material: they show the validation loop working, not just the output.

1. **Contrast failures in its own palette.** The first palette failed 3 AA pairs. Caught by the build's contrast gate.
2. **Inconsistent color encoding.** Hex and sRGB components disagreed by one bit. Caught by a browser test comparing computed colors.
3. **CSS variable scoping.** First CSS output wouldn't have switched sizes in nested platform scopes. Caught by a browser test.
4. **Inherited color in dark scopes.** Dark-on-dark text in the demo. Caught by screenshot review, then a test was added.
5. **Layout bugs** in the reference page. Caught by screenshot review.
6. **Validator crashed instead of reporting** on broken references. Caught by negative tests.

## Suggested way to complete this before publishing

1. Spend an hour reviewing rows 5, 7, 8 and 9 and write your decision for each.
2. Import into Figma (row 14) and screenshot the result.
3. Run any lightweight validation you can: a 5-person preference/comprehension test of status badges, or a review by someone who has worked a scheduling desk.
4. Replace the "to complete" column with what actually happened.
