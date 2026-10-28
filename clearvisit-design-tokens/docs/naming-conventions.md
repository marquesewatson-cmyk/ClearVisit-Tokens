# Naming conventions

## Shape of a name

```
{category}.{role}.{variant?}.{state?}
```

Names use DTCG groups, so in JSON each segment is a nested object and in references they are joined with dots: `{color.action.primary.bg-hover}`. Segments are lowercase kebab-case. DTCG forbids `{`, `}` and `.` inside a segment, and forbids a leading `$`; the build rejects all four.

| Layer | Pattern | Examples | Named by |
|---|---|---|---|
| Primitive | `{category}.{family}.{step}` | `color.blue.600`, `space.16`, `size.48`, `radius.12`, `duration.150` | What the value **is** |
| Semantic | `{category}.{role}.{variant}` | `color.text.secondary`, `color.status.pending.icon`, `size.control.md`, `text-style.table-cell` | What the value **is for** |
| Component | `{component}.{part}-{state}` | `time-slot.selected-bg`, `table.row-height`, `field.border-error` | Which **component decision** it encodes |

## Primitive rules

- **Color steps** are 50–950 on a shared OKLCH lightness ladder. Neutral (`slate`) adds 850, 925, 975 for dark-theme layering. The same step number means the same perceived lightness in every hue.
- **Dimension names equal their pixel value** (`space.16` = 16px, `size.48` = 48px). Primitives never change value, so the name can describe the value honestly. Renaming is never needed; adding a step is.
- **Font sizes** use a 100–900 ramp (`font.size.300` = 16px) because the CSS output converts them to rem; a px-named token emitting rem would mislead.
- **Alpha colors** are named `{base}-alpha.{percent}`: `color.slate-alpha.48`.

## Semantic rules

- Name the **role**, never the appearance: `color.text.secondary`, not `color.text.gray`.
- Same names in every modifier context. `color.surface.default` exists in light and dark; `size.control.md` exists in mobile and desktop. The build fails if a context is missing a name the other has.
- Paired foreground/background tokens share a group: `color.status.pending.{bg, fg, border, icon}`. That makes the contrast pairs obvious and lets the audit generate them.
- Interaction states are suffixes on the property: `bg`, `bg-hover`, `bg-pressed`. Global interaction states live under `color.interaction.*`.
- T-shirt sizes (`xs`–`xl`) only where the set is ordinal and small: `space.stack.*`, `size.control.{sm,md,lg}`.
- `$root` is used once: `focus-ring.$root` is the ring, `focus-ring.offset` its gap. CSS drops `$root`: `--cv-focus-ring`.

## Component rules

- Group = component name in kebab-case (`date-strip`, `bottom-nav`).
- Property names follow CSS vocabulary where one exists: `bg`, `fg`, `border`, `radius`, `padding-x`, `gap`, `height`.
- States follow the property: `selected-bg`, `border-error`, `disabled-fg`.
- A token that refers to a typography composite ends in `-style` or `text-style`: `table.header-style`.

## Platform names

| Context | CSS | Figma |
|---|---|---|
| DTCG path `color.action.primary.bg` | `--cv-color-action-primary-bg` | `color/action/primary/bg` |
| DTCG path `focus-ring.$root` | `--cv-focus-ring` | `focus-ring/default` |
| Theme context | `[data-theme="dark"]` | Theme collection, mode **Dark** |
| Platform context | `[data-platform="mobile"]` | Platform collection, mode **Mobile** |

The `cv` prefix namespaces ClearVisit variables so they can't collide with host-page or third-party CSS.

## Don't

- Don't encode a value in a semantic name (`color.text.slate-700`).
- Don't encode a platform in a semantic name (`size.control.mobile`); use the modifier.
- Don't create a component token that only renames a semantic token with no decision added (no `badge.confirmed.bg`; use `color.status.confirmed.bg`).
- Don't let two names differ only by case; the spec allows it but CSS, Sass and Figma outputs would collide.
