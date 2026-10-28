// Status metadata mirrors color.status.* $extensions in tokens/semantic/*.tokens.json.
// Label + icon travel with every status so meaning never depends on color alone.
export const STATUS = {
  available:   { label: "Available",   icon: "calendar-plus" },
  confirmed:   { label: "Confirmed",   icon: "check-circle" },
  pending:     { label: "Pending",     icon: "clock" },
  completed:   { label: "Completed",   icon: "check-double" },
  cancelled:   { label: "Cancelled",   icon: "x-circle" },
  rescheduled: { label: "Rescheduled", icon: "arrow-path" },
};
