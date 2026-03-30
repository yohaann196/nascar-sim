export default function RaceResults({ result }) {
  if (!result) return null;
  const { finishing_order, events, caution_count, track, total_laps } = result;

  const statusIcon = (s) => s === "dnf" ? "💥" : "✅";

  return (
    <div className="panel race-results">
      <h2>Race Results — {track}</h2>
      <div className="race-meta">
        <span>🏁 {total_laps} laps</span>
        <span>🟡 {caution_count} cautions</span>
        <span>🏆 Winner: <strong>#{finishing_order[0].number} {finishing_order[0].name}</strong></span>
      </div>

      {events.length > 0 && (
        <div className="events-feed">
          <h3>Race Events</h3>
          {events.slice(-10).map((e, i) => (
            <div key={i} className={`event event-${e.type}`}>
              <span className="event-lap">Lap {e.lap}</span>
              <span className="event-detail">{e.type === "caution" ? "🟡" : "💥"} {e.detail}</span>
            </div>
          ))}
        </div>
      )}

      <div className="results-table-wrap">
        <table className="results-table">
          <thead>
            <tr>
              <th>Pos</th><th>#</th><th>Driver</th><th>Team</th>
              <th>Laps Led</th><th>Pit Stops</th><th>Total Time</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            {finishing_order.map((car) => (
              <tr key={car.number} className={car.position === 1 ? "winner-row" : ""}>
                <td><strong>{car.position}</strong></td>
                <td>#{car.number}</td>
                <td>{car.name}</td>
                <td className="team-cell">{car.team}</td>
                <td>{car.laps_led}</td>
                <td>{car.pit_stops}</td>
                <td>{(car.total_time / 60).toFixed(2)} min</td>
                <td>{statusIcon(car.status)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
