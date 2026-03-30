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

  const handleChange = (e) => {
    const { name, value } = e.target;
    setConfig((c) => ({ ...c, [name]: parseFloat(value) }));
  };

  const runRace = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await API.post("/simulate", {
        track_id: selectedTrack,
        ...config,
      });
      onRaceComplete(result);
    } catch (err) {
      setError("Could not connect to API. Make sure the FastAPI server is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel race-setup">
      <h2>Race Configuration</h2>
      {error && <div className="error-banner">{error}</div>}

      <div className="form-grid">
        <label>
          Track
          <select value={selectedTrack} onChange={(e) => setSelectedTrack(e.target.value)}>
            {tracks.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name} ({t.length_miles} mi)
              </option>
            ))}
          </select>
        </label>

        <label>
          Total Laps
          <input type="number" name="total_laps" value={config.total_laps}
            min={10} max={500} onChange={handleChange} />
        </label>

        <label>
          Car Count
          <input type="number" name="driver_count" value={config.driver_count}
            min={2} max={40} onChange={handleChange} />
        </label>

        <label>
          Caution Probability
          <input type="number" name="caution_prob" value={config.caution_prob}
            step={0.01} min={0} max={0.3} onChange={handleChange} />
        </label>

        <label>
          Fuel Window (laps)
          <input type="number" name="fuel_window" value={config.fuel_window}
            min={20} max={80} onChange={handleChange} />
        </label>

        <label>
          Pit Road Time (sec)
          <input type="number" name="pit_road_time" value={config.pit_road_time}
            step={0.5} min={8} max={20} onChange={handleChange} />
        </label>
      </div>

      <button className="btn-primary" onClick={runRace} disabled={loading}>
        {loading ? "Simulating…" : "🏁 Run Race"}
      </button>
    </div>
  );
}
