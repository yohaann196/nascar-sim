import { useState } from "react";
import { API } from "../utils/api";

export default function MonteCarloPanel({ selectedTrack }) {
  const [config, setConfig] = useState({ n_simulations: 100, driver_count: 20, total_laps: 200 });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await API.post("/monte-carlo", { track_id: selectedTrack, ...config });
      setResult(data);
    } catch {
      setError("API not reachable. Run the FastAPI server first.");
    } finally {
      setLoading(false);
    }
  };

  const maxWinPct = result ? result.win_percentages[0]?.win_pct ?? 1 : 1;

  return (
    <div className="panel mc-panel">
      <h2>Monte Carlo Win Probability</h2>
      <p className="mc-desc">
        Runs N independent race simulations and computes each driver's win rate.
      </p>

      <div className="form-grid">
        <label>
          Simulations
          <input type="number" value={config.n_simulations} min={10} max={500}
            onChange={(e) => setConfig((c) => ({ ...c, n_simulations: +e.target.value }))} />
        </label>
        <label>
          Drivers
          <input type="number" value={config.driver_count} min={2} max={40}
            onChange={(e) => setConfig((c) => ({ ...c, driver_count: +e.target.value }))} />
        </label>
        <label>
          Laps
          <input type="number" value={config.total_laps} min={10} max={500}
            onChange={(e) => setConfig((c) => ({ ...c, total_laps: +e.target.value }))} />
        </label>
      </div>

      <button className="btn-primary" onClick={run} disabled={loading}>
        {loading ? `Running ${config.n_simulations} simulations…` : "▶ Run Monte Carlo"}
      </button>

      {error && <div className="error-banner">{error}</div>}

      {result && (
        <div className="mc-results">
          <div className="mc-meta">
            <span>{result.n_simulations} races simulated</span>
            <span>Avg cautions: {result.avg_cautions}</span>
            <span>Track: {result.track}</span>
          </div>
          <div className="mc-bars">
            {result.win_percentages.slice(0, 15).map((d) => (
              <div key={d.number} className="mc-bar-row">
                <span className="mc-driver">#{d.number} {d.name}</span>
                <div className="mc-bar-bg">
                  <div
                    className="mc-bar-fill"
                    style={{ width: `${(d.win_pct / maxWinPct) * 100}%` }}
                  />
                </div>
                <span className="mc-pct">{d.win_pct}%</span>
                <span className="mc-avgf">avg P{d.avg_finish}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
