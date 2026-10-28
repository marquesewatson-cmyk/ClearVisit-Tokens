import { STATUS } from "./tokens";
import { Icon } from "./Icon";

/** Status badge: icon + text label on a tinted fill.
 *  Colors come from color.status.<status>.{bg,fg,border,icon} via the data-status attribute
 *  (see examples/components.css) — the component never names a hex value or a primitive. */
export function StatusBadge({ status }) {
  const meta = STATUS[status];
  return (
    <span className="cv-badge" data-status={status}>
      <Icon name={meta.icon} />
      {meta.label}
    </span>
  );
}
