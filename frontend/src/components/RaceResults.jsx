export default function RaceResults({ result }) {
  if (!result) return null;
  const { finishing_order, events, caution_count, track, total_laps } = result;
  const winner = finishing_order[0];
  const dnfs = finishing_order.filter((c) => c.status === "dnf").length;

  const posClass = (p) => p === 1 ? "p1" : p === 2 ? "p2" : p === 3 ? "p3" : "";
  const fmtTime = (s) => {
    const m = Math.floor(s / 60);
    const sec = (s % 60).toFixed(2);
    return `${m}:${sec.padStart(5, "0")}`;
  };

  return (
    <div className="race-results">
      <div className="section-label">Results — {track}</div>

      {/* Summary stats */}
      <div className="results-meta">
        <div className="meta-cell">
          <div className="meta-label">Total Laps</div>
          <div className="meta-value">{total_laps}</div>
        </div>
        <div className="meta-cell">
          <div className="meta-label">Cautions</div>
          <div className="meta-value yellow">{caution_count}</div>
        </div>
        <div className="meta-cell">
          <div className="meta-label">DNFs</div>
          <div className="meta-value red">{dnfs}</div>
        </div>
        <div className="meta-cell">
          <div className="meta-label">Lead Changes</div>
          <div className="meta-value">{finishing_order.filter(c => c.laps_led > 0).length}</div>
        </div>
      </div>

      {/* Winner */}
      <div className="winner-card">
        <div className="winner-pos">P1</div>
        <div className="winner-number">#{winner.number}</div>
        <div className="winner-info">
          <div className="winner-name">{winner.name}</div>
          <div className="winner-team">{winner.team}</div>
        </div>
        <div className="winner-stat">
          <div className="stat-n">{winner.laps_led}</div>
          <div className="stat-l">LAPS LED</div>
        </div>
        <div className="winner-stat">
          <div className="stat-n">{winner.pit_stops}</div>
          <div className="stat-l">PIT STOPS</div>
        </div>
      </div>

      {/* Events strip */}
      {events.length > 0 && (
        <div className="events-strip">
          {events.map((e, i) => (
            <div key={i} className={`event-chip ${e.type}`}>
              {e.type === "caution" ? `🟡 LAP ${e.lap}` : `💥 LAP ${e.lap} · ${e.detail.split("—")[1]?.trim() ?? ""}`}
            </div>
          ))}
        </div>
      )}

      {/* Table */}
      <div className="section-label">Full Results</div>
      <div className="results-table-wrap">
        <table className="results-table">
          <thead>
            <tr>
              <th>Pos</th>
              <th>#</th>
              <th>Driver</th>
              <th>Team</th>
              <th>Laps Led</th>
              <th>Pit Stops</th>
              <th>Race Time</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {finishing_order.map((car) => (
              <tr key={car.number + car.position}>
                <td className={`td-pos ${posClass(car.position)}`}>{car.position}</td>
                <td className="td-num">#{car.number}</td>
                <td className="td-driver">{car.name}</td>
                <td className="td-team">{car.team}</td>
                <td className="td-mono">{car.laps_led}</td>
                <td className="td-mono">{car.pit_stops}</td>
                <td className="td-mono">{fmtTime(car.total_time)}</td>
                <td className="td-status">
                  {car.status === "dnf"
                    ? <span className="badge-dnf">DNF</span>
                    : <span className="badge-ok" />}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
