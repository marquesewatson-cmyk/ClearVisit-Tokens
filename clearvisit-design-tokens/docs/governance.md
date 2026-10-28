# Governance and maintenance

Tokens are a public API consumed by two products and a Figma library. Changing one is a release.

## Ownership (roles, not people)

| Role | Responsible for |
|---|---|
| Design system owner | Approves semantic changes, owns naming, runs releases |
| Product designers (patient, admin) | Propose changes from product needs; review impact in their product |
| Front-end engineer (system) | Pipeline, validation rules, CSS output, release tooling |
| Accessibility reviewer | Signs off any change to color, status, focus or target size |

In a solo portfolio context one person holds all four; the roles still describe the checks each change needs.

## Change classes and versioning (semver)

| Change | Example | Version | Required before merge |
|---|---|---|---|
| New token | `color.status.no-show` | Minor | All contexts filled, label + icon for statuses, contrast pass, docs |
| Value change, same meaning | `action.primary.bg` blue 600 → 700 | Minor | Contrast pass; before/after in both products, both themes |
| Primitive tuning | Adjust OKLCH ladder | Minor | Full audit; review every semantic consumer |
| Rename / removal | `field.border-hover` → `field.border-interactive` | Major | `$deprecated` for at least one minor release first |
| New modifier context | `theme: high-contrast`, `platform: kiosk` | Minor (additive) | Complete value set; build rejects partial contexts |
| Layer rule change | Allow a new primitive reference type in components | Major | Written rationale |

## Contribution flow

1. **Propose** in terms of meaning: what decision, for which users, in which product. ("Pending should read as waiting, not warning.")
2. **Check the layer.** Can an existing semantic token express it? Only add a component token if the component makes a decision the semantic layer can't.
3. **Edit JSON** in `tokens/` (or the generator in `scripts/define_tokens.py` for palette work).
4. **Build:** `python3 scripts/build.py`. Must report 0 errors.
5. **Test:** `python3 tests/test_validator.py` and `python3 tests/test_propagation.py`.
6. **Review** in both products, both themes, both platforms; color-blindness simulation for any status/feedback change.
7. **Release:** bump version, changelog entry, re-import Figma variables from `generated/figma/` (never hand-edit Figma variables).

## Deprecation

DTCG 2025.10 supports `$deprecated` on tokens and groups:

```json
"border-hover": {
  "$value": "{color.border.hover}",
  "$deprecated": "Use {field.border-interactive}. Removed in 2.0."
}
```

Proposed tooling (not yet built): the build warns when a non-deprecated token references a deprecated one, and lists deprecated tokens in the release notes.

## Automated guardrails (built)

- JSON validity, DTCG shape and types, alias resolution and type compatibility, cycle detection
- Cross-file conflicts within a permutation; modifier orthogonality
- Theme and platform completeness
- Layering (no component → primitive color)
- WCAG contrast on 83 pairs per theme
- CSS: every `var()` reference defined
- Browser propagation tests
- Negative tests that prove the validator fails on broken input

## Drift detection (proposed)

- CI job that exports Figma variables (native export or REST API) and diffs them against `generated/figma/`.
- Lint rule in product code that flags raw hex values and `--cv-color-{hue}-*` primitives outside the token package.
- Quarterly audit: unused tokens (no consumer), near-duplicate semantic tokens, components that bypass tokens.

## Known debt (from the QA report)

- `filter-chip` is used on the patient search screen but lives in `desktop.tokens.json`. Promote to shared in 0.2.
- `text.secondary` and `text.muted` are close in light theme (#535F6C vs #5D6B79). Either widen the gap or merge them.
