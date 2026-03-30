import { useState, useEffect } from "react";
import { API } from "../utils/api";

const TRACKS_FALLBACK = [
  { id: "daytona", name: "Daytona International Speedway", length_miles: 2.5 },
  { id: "talladega", name: "Talladega Superspeedway", length_miles: 2.66 },
  { id: "charlotte", name: "Charlotte Motor Speedway", length_miles: 1.5 },
  { id: "bristol", name: "Bristol Motor Speedway", length_miles: 0.533 },
  { id: "martinsville", name: "Martinsville Speedway", length_miles: 0.526 },
  { id: "michigan", name: "Michigan International Speedway", length_miles: 2.0 },
];

export default function RaceSetup({ selectedTrack, setSelectedTrack, onRaceComplete, loading, setLoading }) {
  const [tracks, setTracks] = useState(TRACKS_FALLBACK);
  const [config, setConfig] = useState({
    total_laps: 200,
    driver_count: 40,
    caution_prob: 0.04,
    fuel_window: 55,
    pit_road_time: 12.5,
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    API.get("/tracks")
      .then((data) => setTracks(data.map((t) => ({ id: t.id, name: t.name, length_miles: t.length_miles }))))
      .catch(() => {});
  }, []);

  const set = (key) => (e) => setConfig((c) => ({ ...c, [key]: parseFloat(e.target.value) }));

  const runRace = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await API.post("/simulate", { track_id: selectedTrack, ...config });
      onRaceComplete(result);
    } catch {
      setError("API unreachable — make sure the FastAPI server is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="race-setup">
      <div className="section-label">Race Configuration</div>

      <div className="config-grid">
        <div className="config-cell" style={{ gridColumn: "span 2" }}>
          <label>Track</label>
          <select value={selectedTrack} onChange={(e) => setSelectedTrack(e.target.value)}>
            {tracks.map((t) => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
        </div>

        <div className="config-cell">
          <label>Laps</label>
          <input type="number" value={config.total_laps} min={10} max={500} onChange={set("total_laps")} />
        </div>

        <div className="config-cell">
          <label>Cars</label>
          <input type="number" value={config.driver_count} min={2} max={40} onChange={set("driver_count")} />
        </div>

        <div className="config-cell">
          <label>Caution %</label>
          <input type="number" value={config.caution_prob} step={0.01} min={0} max={0.3} onChange={set("caution_prob")} />
        </div>

        <div className="config-cell">
          <label>Fuel Window</label>
          <input type="number" value={config.fuel_window} min={20} max={80} onChange={set("fuel_window")} />
        </div>

        <div className="config-cell">
          <label>Pit Time (s)</label>
          <input type="number" value={config.pit_road_time} step={0.5} min={8} max={20} onChange={set("pit_road_time")} />
        </div>
      </div>

      <button className="run-btn" onClick={runRace} disabled={loading}>
        {loading ? <><span className="btn-loader" /> SIMULATING</> : "▶ RUN RACE"}
      </button>

      {error && <div className="error-msg">{error}</div>}
    </div>
  );
}
