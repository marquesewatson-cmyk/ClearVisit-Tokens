import "../../generated/clearvisit.css";
import "../../generated/clearvisit.dark.css";
import "../components.css";
import { TimeSlotPicker } from "./TimeSlotPicker";
import { AppointmentTable } from "./AppointmentTable";

/** Theme and platform are just attributes. Any subtree can switch either one,
 *  and every component token below it re-resolves (see docs/architecture.md, "Scoped re-resolution"). */
export default function App({ theme = "light" }) {
  return (
    <div className="cv" data-theme={theme}>
      <section data-platform="mobile" aria-label="Patient booking">
        <TimeSlotPicker slots={[{ time: "9:00 AM" }, { time: "9:30 AM", booked: true }, { time: "10:30 AM" }]} />
      </section>
      <section data-platform="desktop" aria-label="Scheduling admin">
        <AppointmentTable
          selectedId="a2"
          rows={[
            { id: "a1", time: "8:30 AM", patient: "Sample patient A", provider: "Dr. Okafor", type: "Follow-up", status: "confirmed" },
            { id: "a2", time: "9:00 AM", patient: "Sample patient B", provider: "Dr. Reyes", type: "New patient", status: "pending" },
            { id: "a3", time: "9:30 AM", patient: "Sample patient C", provider: "Dr. Chen", type: "Well visit", status: "rescheduled" },
          ]}
        />
      </section>
    </div>
  );
}
