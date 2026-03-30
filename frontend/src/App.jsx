import { useState } from "react";
import RaceSetup from "./components/RaceSetup";
import RaceResults from "./components/RaceResults";
import TrackMap from "./components/TrackMap";
import MonteCarloPanel from "./components/MonteCarloPanel";
import LapChart from "./components/LapChart";
import "./App.css";

const TABS = ["Setup & Race", "Track Map", "Lap Chart", "Monte Carlo"];

export default function App() {
  const [tab, setTab] = useState(0);
  const [raceResult, setRaceResult] = useState(null);
  const [selectedTrack, setSelectedTrack] = useState("daytona");
  const [loading, setLoading] = useState(false);

  return (
    <div className="app">
      <header className="app-header">
        <span className="flag">🏁</span>
        <h1>NASCAR Race Simulator</h1>
        <span className="flag">🏁</span>
      </header>

      <nav className="tab-bar">
        {TABS.map((t, i) => (
          <button
            key={t}
            className={`tab-btn ${tab === i ? "active" : ""}`}
            onClick={() => setTab(i)}
          >
            {t}
          </button>
        ))}
      </nav>

      <main className="app-body">
        {tab === 0 && (
          <RaceSetup
            selectedTrack={selectedTrack}
            setSelectedTrack={setSelectedTrack}
            onRaceComplete={setRaceResult}
            loading={loading}
            setLoading={setLoading}
          />
        )}
        {tab === 0 && raceResult && (
          <RaceResults result={raceResult} />
        )}
        {tab === 1 && (
          <TrackMap trackId={selectedTrack} raceResult={raceResult} />
        )}
        {tab === 2 && raceResult && (
          <LapChart lapHistory={raceResult.lap_history} />
        )}
        {tab === 2 && !raceResult && (
          <div className="empty-state">Run a race first to see the lap chart.</div>
        )}
        {tab === 3 && (
          <MonteCarloPanel selectedTrack={selectedTrack} />
        )}
      </main>
    </div>
  );
}
