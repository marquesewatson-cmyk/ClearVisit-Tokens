import { StatusBadge } from "./StatusBadge";

/** Admin appointment table. Row height, padding and type come from table.* tokens
 *  (desktop: 40px rows, 14px text). Selection uses fill + left indicator bar, not color alone. */
export function AppointmentTable({ rows, selectedId, onSelect }) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table className="cv-table">
        <thead>
          <tr><th scope="col">Time</th><th scope="col">Patient</th><th scope="col">Provider</th>
              <th scope="col">Visit type</th><th scope="col">Status</th></tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} aria-selected={r.id === selectedId} onClick={() => onSelect?.(r.id)}>
              <td className="is-num">{r.time}</td><td>{r.patient}</td><td>{r.provider}</td>
              <td>{r.type}</td><td><StatusBadge status={r.status} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
