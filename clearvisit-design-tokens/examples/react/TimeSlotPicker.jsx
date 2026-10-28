import { useState } from "react";
import { Icon } from "./Icon";

/** Mobile time-slot picker (patient booking).
 *  States: default · hover · selected (filled + check icon + aria-pressed) · booked (disabled, struck through).
 *  Geometry comes from time-slot.* component tokens, which resolve per platform:
 *  48px tall inside [data-platform="mobile"], 32px inside [data-platform="desktop"]. */
export function TimeSlotPicker({ slots, onSelect }) {
  const [selected, setSelected] = useState(null);
  return (
    <div role="group" aria-label="Available times" className="cv-slots">
      {slots.map(({ time, booked }) => {
        const isSelected = selected === time;
        return (
          <button
            key={time}
            type="button"
            className="cv-slot"
            aria-pressed={isSelected}
            aria-disabled={booked || undefined}
            aria-label={booked ? `${time}, booked` : time}
            onClick={() => {
              if (booked) return;
              setSelected(time);
              onSelect?.(time);
            }}
          >
            {isSelected && <Icon name="check" />}
            {time}
          </button>
        );
      })}
    </div>
  );
}
