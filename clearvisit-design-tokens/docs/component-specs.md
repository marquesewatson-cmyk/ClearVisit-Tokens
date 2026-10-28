# Component specifications

Thirty components: 15 shared, 7 patient-mobile, 8 admin-desktop. For each: the component tokens (with the semantic token they reference) and resolved values in light/mobile, light/desktop and dark/desktop. Token tables are generated from `tokens/components/*.tokens.json`; guidance is authored.

**Rule of thumb used:** a component token exists only when the component makes a decision the semantic layer can't express (a geometry choice, or a role mapping that a designer would otherwise have to remember). Variant colors that map 1:1 to semantic tokens (button variants, badge statuses) are consumed directly and not duplicated.

## Buttons

`button` in `components/shared.tokens.json`

**States.** Default, hover, pressed, focus-visible, disabled. Loading = disabled + spinner + `aria-busy`.

**Accessibility.** Label always visible (icon-only buttons need `aria-label`). Min hit area = `size.touch-target`. Destructive confirms in a modal, never on first tap. Disabled buttons keep text at `color.interaction.disabled.fg`, which is WCAG-exempt; prefer explaining why an action is unavailable.

**Mobile vs desktop.** Mobile 48px default height, 16px text, 12px radius; desktop 36px, 14px, 6px.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `button.height.sm` | `{size.control.sm}` | 36px | 28px | 28px |
| `button.height.md` | `{size.control.md}` | 48px | 36px | 36px |
| `button.height.lg` | `{size.control.lg}` | 56px | 44px | 44px |
| `button.padding-x` | `{space.inset.control-x}` | 16px | 12px | 12px |
| `button.gap` | `{space.inline.sm}` | 8px | 8px | 8px |
| `button.radius` | `{radius.control}` | 12px | 6px | 6px |
| `button.text-style` | `{text-style.button}` | 16/1.3 w500 | 14/1.3 w500 | 14/1.3 w500 |
| `button.min-target` | `{size.touch-target}` | 48px | 24px | 24px |
| `button.transition` | `{motion.control}` | 150ms | 150ms | 150ms |
| *variant colors* | `color.action.{primary,secondary,tertiary,destructive}.*` | | | |

## Text inputs (shared by search and dropdown triggers)

`field` in `components/shared.tokens.json`

**States.** Default, hover, focus (2px ring via border + 1px shadow), error (red border + icon + message), disabled, read-only.

**Accessibility.** Visible `<label>` always; placeholder is a hint, not a label. Errors use `aria-invalid` + `aria-describedby` and an icon so they don't rely on red. Mobile text stays 16px to prevent iOS zoom.

**Mobile vs desktop.** Height 48 vs 36; text 16 vs 14.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `field.height` | `{size.control.md}` | 48px | 36px | 36px |
| `field.padding-x` | `{space.inset.control-x}` | 16px | 12px | 12px |
| `field.gap` | `{space.inline.sm}` | 8px | 8px | 8px |
| `field.radius` | `{radius.control}` | 12px | 6px | 6px |
| `field.text-style` | `{text-style.input}` | 16/1.45 w400 | 14/1.45 w400 | 14/1.45 w400 |
| `field.label-style` | `{text-style.label}` | 16/1.3 w500 | 14/1.3 w500 | 14/1.3 w500 |
| `field.bg` | `{color.surface.default}` | #FFFFFF | #FFFFFF | #1D242B |
| `field.fg` | `{color.text.primary}` | #2D3640 | #2D3640 | #F5F7F9 |
| `field.placeholder` | `{color.text.muted}` | #5D6B79 | #5D6B79 | #99A6B4 |
| `field.border` | `{color.border.strong}` | #748291 | #748291 | #748291 |
| `field.border-hover` | `{color.border.hover}` | #5D6B79 | #5D6B79 | #99A6B4 |
| `field.border-focus` | `{color.border.focus}` | #006ABE | #006ABE | #98C8FF |
| `field.border-error` | `{color.border.error}` | #BE222A | #BE222A | #FE736C |
| `field.helper` | `{color.text.secondary}` | #535F6C | #535F6C | #BBC5D1 |
| `field.error-text` | `{color.feedback.error.fg}` | #8E0816 | #8E0816 | #FFCFCA |
| `field.label-gap` | `{space.stack.xs}` | 4px | 4px | 4px |

## Search fields

`search` in `components/shared.tokens.json`

**States.** Empty, typing, with results, no results.

**Accessibility.** Use `role=search` on the form; announce result counts with a polite live region.

**Mobile vs desktop.** Mobile uses the 56px `size.control.lg` pill on the home screen; desktop toolbar search uses `size.control.md`.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `search.bg` | `{color.surface.subtle}` | #E9EDF1 | #E9EDF1 | #242C35 |
| `search.icon` | `{color.text.secondary}` | #535F6C | #535F6C | #BBC5D1 |
| `search.radius` | `{radius.pill}` | 9999px | 9999px | 9999px |
| `search.height` | `{size.control.lg}` | 56px | 44px | 44px |

## Dropdowns

`dropdown` in `components/shared.tokens.json`

**States.** Closed, open, option hover, option selected (bold + check icon), disabled option.

**Accessibility.** Native `<select>` on mobile where possible; custom listbox follows the ARIA listbox pattern with arrow-key support.

**Mobile vs desktop.** Mobile prefers a bottom sheet for long lists.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `dropdown.menu-bg` | `{color.surface.elevated}` | #FFFFFF | #FFFFFF | #2D3640 |
| `dropdown.menu-shadow` | `{elevation.popover}` | shadow | shadow | shadow |
| `dropdown.menu-radius` | `{radius.control}` | 12px | 6px | 6px |
| `dropdown.menu-layer` | `{layer.dropdown}` | 1000 | 1000 | 1000 |
| `dropdown.option-height` | `{size.control.md}` | 48px | 36px | 36px |
| `dropdown.option-hover` | `{color.interaction.hover}` | #E9EDF1 | #E9EDF1 | #2D3640 |
| `dropdown.option-selected-bg` | `{color.interaction.selected.bg}` | #F1F8FF | #F1F8FF | #002346 |
| `dropdown.option-selected-fg` | `{color.interaction.selected.fg}` | #004B8A | #004B8A | #E0EFFF |

## Checkboxes

`checkbox` in `components/shared.tokens.json`

**States.** Unchecked, checked (fill + check glyph), indeterminate (fill + dash), disabled, focus.

**Accessibility.** Visual box is 24/18px but the clickable label row is at least `size.touch-target`. Border uses `color.border.strong` (3:1).

**Mobile vs desktop.** Box 24 vs 18.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `checkbox.size` | `{size.selection-control}` | 24px | 18px | 18px |
| `checkbox.radius` | `{radius.xs}` | 4px | 4px | 4px |
| `checkbox.target` | `{size.touch-target}` | 48px | 24px | 24px |
| `checkbox.border` | `{color.border.strong}` | #748291 | #748291 | #748291 |
| `checkbox.checked-bg` | `{color.action.primary.bg}` | #006ABE | #006ABE | #58A8FE |
| `checkbox.checked-fg` | `{color.action.primary.fg}` | #FFFFFF | #FFFFFF | #002346 |

## Radio buttons

`radio` in `components/shared.tokens.json`

**States.** Unselected, selected (ring + dot), disabled, focus.

**Accessibility.** Group with `fieldset`/`legend`; arrow keys move selection.

**Mobile vs desktop.** Same as checkbox.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `radio.size` | `{size.selection-control}` | 24px | 18px | 18px |
| `radio.target` | `{size.touch-target}` | 48px | 24px | 24px |
| `radio.border` | `{color.border.strong}` | #748291 | #748291 | #748291 |
| `radio.checked` | `{color.action.primary.bg}` | #006ABE | #006ABE | #58A8FE |

## Status badges

`badge` in `components/shared.tokens.json`

**States.** One per appointment status, plus feedback tones.

**Accessibility.** Icon + text label always; icon is `aria-hidden` because the label carries meaning. Never truncate the label.

**Mobile vs desktop.** Identical on both platforms (12px label).

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `badge.height` | `{size.badge}` | 24px | 24px | 24px |
| `badge.padding-x` | `{space.inset.sm}` | 8px | 8px | 8px |
| `badge.gap` | `{space.inline.xs}` | 4px | 4px | 4px |
| `badge.radius` | `{radius.pill}` | 9999px | 9999px | 9999px |
| `badge.text-style` | `{text-style.badge}` | 12/1.3 w500 | 12/1.3 w500 | 12/1.3 w500 |
| `badge.icon-size` | `{size.icon.sm}` | 16px | 16px | 16px |
| *status colors* | `color.status.{status}.{bg,fg,border,icon}` | | | |

## Cards

`card` in `components/shared.tokens.json`

**States.** Static, interactive (hover border), selected (uses `color.surface.selected`).

**Accessibility.** Interactive cards have one primary link target; don't nest buttons inside a clickable card.

**Mobile vs desktop.** Radius 16 vs 8, padding 16 vs 20.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `card.bg` | `{color.surface.default}` | #FFFFFF | #FFFFFF | #1D242B |
| `card.border` | `{color.border.default}` | #D6DDE5 | #D6DDE5 | #37414B |
| `card.border-hover` | `{color.border.hover}` | #5D6B79 | #5D6B79 | #99A6B4 |
| `card.radius` | `{radius.card}` | 16px | 8px | 8px |
| `card.padding` | `{space.inset.card}` | 16px | 20px | 20px |
| `card.gap` | `{space.stack.sm}` | 8px | 8px | 8px |
| `card.shadow` | `{elevation.raised}` | shadow | shadow | shadow |

## Tabs

`tabs` in `components/shared.tokens.json`

**States.** Default, hover, selected (bold + 3px indicator), focus, disabled.

**Accessibility.** ARIA tabs pattern; selected state is weight + indicator, not color alone.

**Mobile vs desktop.** Height 48 vs 36.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `tabs.height` | `{size.control.md}` | 48px | 36px | 36px |
| `tabs.gap` | `{space.inline.lg}` | 16px | 16px | 16px |
| `tabs.text-style` | `{text-style.label}` | 16/1.3 w500 | 14/1.3 w500 | 14/1.3 w500 |
| `tabs.fg` | `{color.text.secondary}` | #535F6C | #535F6C | #BBC5D1 |
| `tabs.fg-selected` | `{color.text.primary}` | #2D3640 | #2D3640 | #F5F7F9 |
| `tabs.indicator` | `{color.action.primary.bg}` | #006ABE | #006ABE | #58A8FE |
| `tabs.indicator-height` | `{stroke.indicator}` | 3px | 3px | 3px |
| `tabs.divider` | `{color.border.default}` | #D6DDE5 | #D6DDE5 | #37414B |

## Alerts

`alert` in `components/shared.tokens.json`

**States.** Info, success, warning, error; optional action and dismiss.

**Accessibility.** `role=status` for non-urgent, `role=alert` for errors that block work. Icon differs per tone.

**Mobile vs desktop.** Text 16 vs 14.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `alert.padding` | `{space.inset.card}` | 16px | 20px | 20px |
| `alert.gap` | `{space.inline.md}` | 12px | 12px | 12px |
| `alert.radius` | `{radius.control}` | 12px | 6px | 6px |
| `alert.border-width` | `{stroke.default}` | 1px | 1px | 1px |
| `alert.icon-size` | `{size.icon.md}` | 24px | 20px | 20px |
| `alert.title-style` | `{text-style.alert-title}` | 16/1.45 w600 | 14/1.45 w600 | 14/1.45 w600 |
| `alert.body-style` | `{text-style.alert-body}` | 16/1.45 w400 | 14/1.45 w400 | 14/1.45 w400 |
| *tone colors* | `color.feedback.{tone}.{bg,fg,border,icon}` | | | |

## Modals

`modal` in `components/shared.tokens.json`

**States.** Enter (300ms decelerate), open, exit (200ms accelerate).

**Accessibility.** Focus trapped and returned on close; Escape closes; title linked by `aria-labelledby`. Destructive confirmations name the object (“Cancel Dr. Okafor, Tue 10:30?”).

**Mobile vs desktop.** Mobile renders as a bottom sheet (top radius 24); desktop centered dialog, max 560px.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `modal.bg` | `{color.surface.elevated}` | #FFFFFF | #FFFFFF | #2D3640 |
| `modal.scrim` | `{color.surface.overlay}` | #12181E (48%) | #12181E (48%) | #000000 (72%) |
| `modal.radius` | `{radius.modal}` | 24px | 12px | 12px |
| `modal.padding` | `{space.inset.modal}` | 20px | 32px | 32px |
| `modal.shadow` | `{elevation.overlay}` | shadow | shadow | shadow |
| `modal.max-width` | `{size.modal-max}` | 600px | 560px | 560px |
| `modal.layer` | `{layer.modal}` | 1300 | 1300 | 1300 |
| `modal.enter` | `{motion.enter}` | 300ms | 300ms | 300ms |

## Tooltips

`tooltip` in `components/shared.tokens.json`

**States.** Hidden, shown after 400ms hover or on focus.

**Accessibility.** Supplementary only: never the sole location of essential information; dismissible with Escape (WCAG 1.4.13).

**Mobile vs desktop.** Mobile avoids tooltips; use inline help text instead.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `tooltip.bg` | `{color.surface.inverse}` | #2D3640 | #2D3640 | #E9EDF1 |
| `tooltip.fg` | `{color.text.inverse}` | #F5F7F9 | #F5F7F9 | #2D3640 |
| `tooltip.radius` | `{radius.sm}` | 6px | 6px | 6px |
| `tooltip.padding-x` | `{space.inset.sm}` | 8px | 8px | 8px |
| `tooltip.padding-y` | `{space.inset.xs}` | 4px | 4px | 4px |
| `tooltip.text-style` | `{text-style.caption}` | 12/1.45 w400 | 12/1.45 w400 | 12/1.45 w400 |
| `tooltip.max-width` | `{size.tooltip-max}` | 280px | 280px | 280px |
| `tooltip.delay` | `{motion.tooltip-delay}` | 400ms | 400ms | 400ms |
| `tooltip.layer` | `{layer.tooltip}` | 1500 | 1500 | 1500 |

## Navigation

`nav-item` in `components/shared.tokens.json`

**States.** Default, hover, current (fill + bold + `aria-current`).

**Accessibility.** Current page announced via `aria-current=page`.

**Mobile vs desktop.** Mobile primary nav is the bottom nav component; desktop uses the sidebar.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `nav-item.height` | `{size.control.md}` | 48px | 36px | 36px |
| `nav-item.gap` | `{space.inline.md}` | 12px | 12px | 12px |
| `nav-item.radius` | `{radius.control}` | 12px | 6px | 6px |
| `nav-item.fg` | `{color.text.secondary}` | #535F6C | #535F6C | #BBC5D1 |
| `nav-item.fg-active` | `{color.interaction.selected.fg}` | #004B8A | #004B8A | #E0EFFF |
| `nav-item.bg-hover` | `{color.interaction.hover}` | #E9EDF1 | #E9EDF1 | #2D3640 |
| `nav-item.bg-active` | `{color.interaction.selected.bg}` | #F1F8FF | #F1F8FF | #002346 |
| `nav-item.icon-size` | `{size.icon.md}` | 24px | 20px | 20px |

## Date pickers

`date-picker` in `components/shared.tokens.json`

**States.** Default, today (ring), selected (fill), has-openings (dot), unavailable (struck + disabled), outside month (muted).

**Accessibility.** ARIA grid pattern; the dot is decorative and the accessible name includes “openings available”.

**Mobile vs desktop.** Day cell 44 vs 32.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `date-picker.day-size` | `{size.day-cell}` | 44px | 32px | 32px |
| `date-picker.day-radius` | `{radius.pill}` | 9999px | 9999px | 9999px |
| `date-picker.day-target` | `{size.touch-target}` | 48px | 24px | 24px |
| `date-picker.day-fg` | `{color.text.primary}` | #2D3640 | #2D3640 | #F5F7F9 |
| `date-picker.day-muted` | `{color.text.muted}` | #5D6B79 | #5D6B79 | #99A6B4 |
| `date-picker.day-unavailable` | `{color.text.disabled}` | #99A6B4 | #99A6B4 | #5D6B79 |
| `date-picker.day-selected-bg` | `{color.action.primary.bg}` | #006ABE | #006ABE | #58A8FE |
| `date-picker.day-selected-fg` | `{color.action.primary.fg}` | #FFFFFF | #FFFFFF | #002346 |
| `date-picker.today-ring` | `{color.border.selected}` | #006ABE | #006ABE | #58A8FE |
| `date-picker.availability-dot` | `{color.status.available.icon}` | #007E3F | #007E3F | #5ABC7A |

## Time selectors

`time-selector` in `components/shared.tokens.json`

**States.** Option default, hover, selected (fill + bold + check).

**Accessibility.** Times use 12-hour format with AM/PM in labels; listbox pattern.

**Mobile vs desktop.** Option height 48 vs 36.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `time-selector.option-height` | `{size.control.md}` | 48px | 36px | 36px |
| `time-selector.text-style` | `{text-style.input}` | 16/1.45 w400 | 14/1.45 w400 | 14/1.45 w400 |
| `time-selector.option-selected-bg` | `{color.interaction.selected.bg}` | #F1F8FF | #F1F8FF | #002346 |
| `time-selector.option-selected-fg` | `{color.interaction.selected.fg}` | #004B8A | #004B8A | #E0EFFF |

## Provider profile cards

`provider-card` in `components/mobile.tokens.json`

**States.** Default, pressed.

**Accessibility.** Avatar is decorative (initials); name is the heading. “Next available” has an icon and text.

**Mobile vs desktop.** Mobile-first; desktop admin shows providers in tables instead.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `provider-card.avatar-size` | `{size.avatar}` | 56px | 32px | 32px |
| `provider-card.gap` | `{space.inline.md}` | 12px | 12px | 12px |
| `provider-card.padding` | `{space.inset.card}` | 16px | 20px | 20px |
| `provider-card.name-style` | `{text-style.provider-name}` | 18/1.3 w600 | 16/1.45 w600 | 16/1.45 w600 |
| `provider-card.meta-style` | `{text-style.supporting}` | 14/1.45 w400 | 14/1.45 w400 | 14/1.45 w400 |
| `provider-card.meta-fg` | `{color.text.secondary}` | #535F6C | #535F6C | #BBC5D1 |
| `provider-card.next-available-fg` | `{color.status.available.fg}` | #005A2B | #005A2B | #BCEAC7 |
| `provider-card.next-available-bg` | `{color.status.available.bg}` | #EEFBF1 | #EEFBF1 | #002C11 |

## Appointment availability cards

`availability-card` in `components/mobile.tokens.json`

**States.** With openings, no openings this week (shows next date + secondary action).

**Accessibility.** Slots are real buttons inside the card; the card itself is not clickable to avoid nested interactive targets.

**Mobile vs desktop.** Mobile only.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `availability-card.bg` | `{color.surface.default}` | #FFFFFF | #FFFFFF | #1D242B |
| `availability-card.border` | `{color.border.default}` | #D6DDE5 | #D6DDE5 | #37414B |
| `availability-card.radius` | `{radius.card}` | 16px | 8px | 8px |
| `availability-card.padding` | `{space.inset.card}` | 16px | 20px | 20px |
| `availability-card.slot-gap` | `{space.inline.sm}` | 8px | 8px | 8px |
| `availability-card.time-style` | `{text-style.appointment-time}` | 20/1.3 w600 | 16/1.45 w600 | 16/1.45 w600 |

## Appointment booking cards

`booking-card` in `components/mobile.tokens.json`

**States.** Draft, ready to book, booking (loading), booked (success alert).

**Accessibility.** Primary CTA repeats the chosen time (“Book 10:30 AM”).

**Mobile vs desktop.** Mobile only.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `booking-card.bg` | `{color.surface.elevated}` | #FFFFFF | #FFFFFF | #2D3640 |
| `booking-card.radius` | `{radius.card}` | 16px | 8px | 8px |
| `booking-card.padding` | `{space.inset.card}` | 16px | 20px | 20px |
| `booking-card.shadow` | `{elevation.popover}` | shadow | shadow | shadow |
| `booking-card.section-gap` | `{space.section}` | 24px | 32px | 32px |

## Date selection controls

`date-strip` in `components/mobile.tokens.json`

**States.** Default, has openings (dot), selected (fill), no openings (dashed + disabled).

**Accessibility.** `listbox` with `aria-selected`; unavailable days announce “no openings”.

**Mobile vs desktop.** Mobile only; desktop uses the date picker.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `date-strip.item-width` | `{size.56}` | 56px | 56px | 56px |
| `date-strip.item-height` | `{size.72}` | 72px | 72px | 72px |
| `date-strip.radius` | `{radius.control}` | 12px | 6px | 6px |
| `date-strip.gap` | `{space.inline.sm}` | 8px | 8px | 8px |
| `date-strip.weekday-style` | `{text-style.caption}` | 12/1.45 w400 | 12/1.45 w400 | 12/1.45 w400 |
| `date-strip.date-style` | `{text-style.section-title}` | 20/1.3 w600 | 18/1.3 w600 | 18/1.3 w600 |
| `date-strip.bg` | `{color.surface.default}` | #FFFFFF | #FFFFFF | #1D242B |
| `date-strip.border` | `{color.border.strong}` | #748291 | #748291 | #748291 |
| `date-strip.selected-bg` | `{color.action.primary.bg}` | #006ABE | #006ABE | #58A8FE |
| `date-strip.selected-fg` | `{color.action.primary.fg}` | #FFFFFF | #FFFFFF | #002346 |
| `date-strip.availability-dot` | `{color.status.available.icon}` | #007E3F | #007E3F | #5ABC7A |
| `date-strip.unavailable-fg` | `{color.text.disabled}` | #99A6B4 | #99A6B4 | #5D6B79 |

## Time-slot selection buttons

`time-slot` in `components/mobile.tokens.json`

**States.** Default, hover, selected (fill + check icon + `aria-pressed`), booked (disabled fill + strike-through + “booked” in label).

**Accessibility.** Booked slots stay visible so the gap in availability is understandable. 48px tall, 88px minimum width.

**Mobile vs desktop.** Tokens resolve to 32px on desktop if reused in admin quick-book.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `time-slot.height` | `{size.time-slot}` | 48px | 32px | 32px |
| `time-slot.min-width` | `{size.88}` | 88px | 88px | 88px |
| `time-slot.radius` | `{radius.control}` | 12px | 6px | 6px |
| `time-slot.gap` | `{space.inline.sm}` | 8px | 8px | 8px |
| `time-slot.text-style` | `{text-style.button}` | 16/1.3 w500 | 14/1.3 w500 | 14/1.3 w500 |
| `time-slot.bg` | `{color.surface.default}` | #FFFFFF | #FFFFFF | #1D242B |
| `time-slot.fg` | `{color.action.secondary.fg}` | #005EAB | #005EAB | #C4DFFF |
| `time-slot.border` | `{color.border.strong}` | #748291 | #748291 | #748291 |
| `time-slot.bg-hover` | `{color.action.secondary.bg-hover}` | #F1F8FF | #F1F8FF | #002346 |
| `time-slot.selected-bg` | `{color.action.primary.bg}` | #006ABE | #006ABE | #58A8FE |
| `time-slot.selected-fg` | `{color.action.primary.fg}` | #FFFFFF | #FFFFFF | #002346 |
| `time-slot.disabled-bg` | `{color.interaction.disabled.bg}` | #E9EDF1 | #E9EDF1 | #242C35 |
| `time-slot.disabled-fg` | `{color.interaction.disabled.fg}` | #99A6B4 | #99A6B4 | #5D6B79 |
| `time-slot.disabled-border` | `{color.interaction.disabled.border}` | #D6DDE5 | #D6DDE5 | #37414B |

## Appointment summary cards

`summary-card` in `components/mobile.tokens.json`

**States.** Static.

**Accessibility.** Key/value rows read in order; values are left-aligned on narrow screens if they wrap.

**Mobile vs desktop.** Mobile only.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `summary-card.bg` | `{color.surface.subtle}` | #E9EDF1 | #E9EDF1 | #242C35 |
| `summary-card.radius` | `{radius.card}` | 16px | 8px | 8px |
| `summary-card.padding` | `{space.inset.card}` | 16px | 20px | 20px |
| `summary-card.row-gap` | `{space.stack.sm}` | 8px | 8px | 8px |
| `summary-card.divider` | `{color.border.default}` | #D6DDE5 | #D6DDE5 | #37414B |
| `summary-card.label-style` | `{text-style.supporting}` | 14/1.45 w400 | 14/1.45 w400 | 14/1.45 w400 |
| `summary-card.label-fg` | `{color.text.secondary}` | #535F6C | #535F6C | #BBC5D1 |
| `summary-card.value-style` | `{text-style.body-strong}` | 16/1.45 w600 | 14/1.45 w600 | 14/1.45 w600 |

## Mobile bottom navigation

`bottom-nav` in `components/mobile.tokens.json`

**States.** Item default, current (pill + bold + `aria-current`).

**Accessibility.** Four destinations max; labels always shown under icons.

**Mobile vs desktop.** Mobile only.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `bottom-nav.height` | `{size.nav-bar}` | 64px | 56px | 56px |
| `bottom-nav.bg` | `{color.surface.elevated}` | #FFFFFF | #FFFFFF | #2D3640 |
| `bottom-nav.border` | `{color.border.default}` | #D6DDE5 | #D6DDE5 | #37414B |
| `bottom-nav.fg` | `{color.text.secondary}` | #535F6C | #535F6C | #BBC5D1 |
| `bottom-nav.fg-active` | `{color.interaction.selected.fg}` | #004B8A | #004B8A | #E0EFFF |
| `bottom-nav.indicator` | `{color.interaction.selected.bg}` | #F1F8FF | #F1F8FF | #002346 |
| `bottom-nav.label-style` | `{text-style.caption}` | 12/1.45 w400 | 12/1.45 w400 | 12/1.45 w400 |
| `bottom-nav.icon-size` | `{size.icon.md}` | 24px | 20px | 20px |
| `bottom-nav.layer` | `{layer.sticky}` | 100 | 100 | 100 |

## Scheduling calendar cells

`calendar-cell` in `components/desktop.tokens.json`

**States.** Working hours, off-hours (subtle fill), today, now line (teal).

**Accessibility.** Now line is decorative; current time is also shown in the header.

**Mobile vs desktop.** Desktop only.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `calendar-cell.slot-height` | `{size.48}` | 48px | 48px | 48px |
| `calendar-cell.bg` | `{color.surface.default}` | #FFFFFF | #FFFFFF | #1D242B |
| `calendar-cell.bg-off-hours` | `{color.surface.subtle}` | #E9EDF1 | #E9EDF1 | #242C35 |
| `calendar-cell.border` | `{color.border.subtle}` | #E9EDF1 | #E9EDF1 | #242C35 |
| `calendar-cell.today-bg` | `{color.surface.selected}` | #F1F8FF | #F1F8FF | #002346 |
| `calendar-cell.time-style` | `{text-style.calendar-time}` | 12/1.45 w400 | 12/1.45 w400 | 12/1.45 w400 |
| `calendar-cell.time-fg` | `{color.text.secondary}` | #535F6C | #535F6C | #BBC5D1 |
| `calendar-cell.now-line` | `{color.accent.solid}` | #007976 | #007976 | #44B9B5 |

## Calendar event cards

`calendar-event` in `components/desktop.tokens.json`

**States.** Per status (fill + bar + icon + text), pending (dashed outline), cancelled (struck time), conflict (red outline + “Conflict” tag).

**Accessibility.** Each event has an accessible name with time, patient, status and conflict state.

**Mobile vs desktop.** Desktop only.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `calendar-event.radius` | `{radius.sm}` | 6px | 6px | 6px |
| `calendar-event.padding` | `{space.inset.xs}` | 4px | 4px | 4px |
| `calendar-event.text-style` | `{text-style.calendar-event}` | 14/1.3 w500 | 12/1.3 w500 | 12/1.3 w500 |
| `calendar-event.bar-width` | `{stroke.indicator}` | 3px | 3px | 3px |
| `calendar-event.gap` | `{space.inline.xs}` | 4px | 4px | 4px |
| `calendar-event.pending-style` | `{stroke-style.dashed}` | dashed | dashed | dashed |
| `calendar-event.conflict-outline` | `` | 2px solid | 2px solid | 2px solid |

## Data table rows and headers

`table` in `components/desktop.tokens.json`

**States.** Row default, hover, selected (fill + 3px left bar + checked box).

**Accessibility.** Real `<table>` with `<th scope>`; times use tabular figures.

**Mobile vs desktop.** Desktop 40px rows; tokens give 56px rows if the table pattern is used on mobile lists.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `table.row-height` | `{size.table-row}` | 56px | 40px | 40px |
| `table.header-height` | `{size.table-header}` | 48px | 40px | 40px |
| `table.cell-padding-x` | `{space.inset.cell-x}` | 16px | 12px | 12px |
| `table.header-bg` | `{color.surface.subtle}` | #E9EDF1 | #E9EDF1 | #242C35 |
| `table.header-fg` | `{color.text.secondary}` | #535F6C | #535F6C | #BBC5D1 |
| `table.header-style` | `{text-style.table-header}` | 14/1.3 w500 | 14/1.3 w500 | 14/1.3 w500 |
| `table.cell-style` | `{text-style.table-cell}` | 16/1.45 w400 | 14/1.45 w400 | 14/1.45 w400 |
| `table.row-border` | `{color.border.subtle}` | #E9EDF1 | #E9EDF1 | #242C35 |
| `table.row-hover` | `{color.interaction.hover}` | #E9EDF1 | #E9EDF1 | #2D3640 |
| `table.row-selected` | `{color.interaction.selected.bg}` | #F1F8FF | #F1F8FF | #002346 |

## Scheduling status indicators

`status-indicator` in `components/desktop.tokens.json`

**States.** Per status: icon + label (dot variant for dense views must keep the label).

**Accessibility.** Never dot-only.

**Mobile vs desktop.** Desktop only.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `status-indicator.dot-size` | `{size.status-dot}` | 8px | 8px | 8px |
| `status-indicator.gap` | `{space.inline.sm}` | 8px | 8px | 8px |
| `status-indicator.text-style` | `{text-style.body}` | 16/1.45 w400 | 14/1.45 w400 | 14/1.45 w400 |

## Filter controls

`filter-chip` in `components/desktop.tokens.json`

**States.** Default, selected (fill + check icon + bold), focus.

**Accessibility.** Toggle buttons with `aria-pressed`.

**Mobile vs desktop.** Also used on the patient search screen; see QA report (candidate to promote to shared).

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `filter-chip.height` | `{size.control.sm}` | 36px | 28px | 28px |
| `filter-chip.padding-x` | `{space.inset.md}` | 12px | 12px | 12px |
| `filter-chip.radius` | `{radius.pill}` | 9999px | 9999px | 9999px |
| `filter-chip.text-style` | `{text-style.label}` | 16/1.3 w500 | 14/1.3 w500 | 14/1.3 w500 |
| `filter-chip.bg` | `{color.surface.default}` | #FFFFFF | #FFFFFF | #1D242B |
| `filter-chip.border` | `{color.border.strong}` | #748291 | #748291 | #748291 |
| `filter-chip.selected-bg` | `{color.interaction.selected.bg}` | #F1F8FF | #F1F8FF | #002346 |
| `filter-chip.selected-fg` | `{color.interaction.selected.fg}` | #004B8A | #004B8A | #E0EFFF |
| `filter-chip.selected-border` | `{color.interaction.selected.border}` | #006ABE | #006ABE | #58A8FE |

## Pagination

`pagination` in `components/desktop.tokens.json`

**States.** Default, hover, current (fill + bold + `aria-current`), disabled prev/next.

**Accessibility.** Wrapped in `nav` with a label; prev/next have text labels for screen readers.

**Mobile vs desktop.** Desktop only.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `pagination.item-size` | `{size.control.sm}` | 36px | 28px | 28px |
| `pagination.radius` | `{radius.control}` | 12px | 6px | 6px |
| `pagination.gap` | `{space.inline.xs}` | 4px | 4px | 4px |
| `pagination.fg` | `{color.text.secondary}` | #535F6C | #535F6C | #BBC5D1 |
| `pagination.current-bg` | `{color.interaction.selected.bg}` | #F1F8FF | #F1F8FF | #002346 |
| `pagination.current-fg` | `{color.interaction.selected.fg}` | #004B8A | #004B8A | #E0EFFF |

## Dashboard metric cards

`metric-card` in `components/desktop.tokens.json`

**States.** Default; delta up/down uses arrow icon + color + text.

**Accessibility.** Delta direction is conveyed by the arrow and the words, not green/red alone.

**Mobile vs desktop.** Desktop only.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `metric-card.padding` | `{space.inset.card}` | 16px | 20px | 20px |
| `metric-card.radius` | `{radius.card}` | 16px | 8px | 8px |
| `metric-card.bg` | `{color.surface.default}` | #FFFFFF | #FFFFFF | #1D242B |
| `metric-card.border` | `{color.border.default}` | #D6DDE5 | #D6DDE5 | #37414B |
| `metric-card.value-style` | `{text-style.metric-value}` | 20/1.3 w600 | 32/1.2 w700 | 32/1.2 w700 |
| `metric-card.label-style` | `{text-style.supporting}` | 14/1.45 w400 | 14/1.45 w400 | 14/1.45 w400 |
| `metric-card.label-fg` | `{color.text.secondary}` | #535F6C | #535F6C | #BBC5D1 |
| `metric-card.delta-up` | `{color.feedback.success.fg}` | #005A2B | #005A2B | #BCEAC7 |
| `metric-card.delta-down` | `{color.feedback.error.fg}` | #8E0816 | #8E0816 | #FFCFCA |

## Desktop sidebar navigation

`sidebar` in `components/desktop.tokens.json`

**States.** Item default, hover, current.

**Accessibility.** Landmark `nav` with label; current item `aria-current=page`.

**Mobile vs desktop.** Desktop only.

| Token | References | Light/mobile | Light/desktop | Dark/desktop |
|---|---|---|---|---|
| `sidebar.width` | `{size.256}` | 256px | 256px | 256px |
| `sidebar.bg` | `{color.surface.default}` | #FFFFFF | #FFFFFF | #1D242B |
| `sidebar.border` | `{color.border.default}` | #D6DDE5 | #D6DDE5 | #37414B |
| `sidebar.padding` | `{space.inset.md}` | 12px | 12px | 12px |
| `sidebar.section-style` | `{text-style.caption}` | 12/1.45 w400 | 12/1.45 w400 | 12/1.45 w400 |
| `sidebar.section-fg` | `{color.text.secondary}` | #535F6C | #535F6C | #BBC5D1 |
