import { useState } from "react";
import { API } from "../utils/api";

export default function MonteCarloPanel({ selectedTrack }) {
  const [config, setConfig] = useState({ n_simulations: 100, driver_count: 20, total_laps: 200 });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const set = (key) => (e) => setConfig((c) => ({ ...c, [key]: +e.target.value }));

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

  const maxPct = result?.win_percentages?.[0]?.win_pct ?? 1;

  return (
    <div className="mc-panel">
      <div className="section-label">Monte Carlo Analysis</div>
      <p style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--white-dim)", marginBottom: 20, letterSpacing: 1 }}>
        Run N independent race simulations to compute win probabilities across the field.
      </p>

      <div className="mc-config">
        <div className="config-cell">
          <label>Simulations</label>
          <input type="number" value={config.n_simulations} min={10} max={500} onChange={set("n_simulations")} />
        </div>
        <div className="config-cell">
          <label>Drivers</label>
          <input type="number" value={config.driver_count} min={2} max={40} onChange={set("driver_count")} />
        </div>
        <div className="config-cell">
          <label>Laps</label>
          <input type="number" value={config.total_laps} min={10} max={500} onChange={set("total_laps")} />
        </div>
      </div>

      <button className="run-btn" onClick={run} disabled={loading}>
        {loading
          ? <><span className="btn-loader" /> RUNNING {config.n_simulations} RACES</>
          : `▶ RUN ${config.n_simulations} SIMULATIONS`}
      </button>

      {error && <div className="error-msg">{error}</div>}

      {result && (
        <div className="mc-results" style={{ marginTop: 32 }}>
          <div className="section-label">Win Probability</div>

          <div className="mc-meta-row">
            <div className="mc-meta-item"><strong>{result.n_simulations}</strong> RACES</div>
            <div className="mc-meta-item"><strong>{result.avg_cautions}</strong> AVG CAUTIONS</div>
            <div className="mc-meta-item"><strong>{result.track}</strong></div>
          </div>

          <div className="mc-bar-list">
            {result.win_percentages.slice(0, 15).map((d) => (
              <div key={d.number} className="mc-bar-row">
                <div className="mc-name">
                  <span>#{d.number}</span>{d.name}
                </div>
                <div className="mc-track">
                  <div className="mc-fill" style={{ width: `${(d.win_pct / maxPct) * 100}%` }} />
                </div>
                <div className="mc-pct">{d.win_pct}%</div>
                <div className="mc-avg">P{d.avg_finish} avg</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
