import { useState } from "react";
import RaceSetup from "./components/RaceSetup";
import RaceResults from "./components/RaceResults";
import TrackMap from "./components/TrackMap";
import MonteCarloPanel from "./components/MonteCarloPanel";
import LapChart from "./components/LapChart";
import "./App.css";

const TABS = [
  { id: 0, label: "RACE", icon: "⬛" },
  { id: 1, label: "TRACK", icon: "○" },
  { id: 2, label: "CHART", icon: "╱╲" },
  { id: 3, label: "ANALYSIS", icon: "▦" },
];

export default function App() {
  const [tab, setTab] = useState(0);
  const [raceResult, setRaceResult] = useState(null);
  const [selectedTrack, setSelectedTrack] = useState("daytona");
  const [loading, setLoading] = useState(false);

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <span className="header-tag">SIM</span>
          <h1>NASCAR-SIM</h1>
        </div>
        <div className="header-right">
          <span className="header-sub">NASCAR Race Simulator</span>
          {raceResult && (
            <span className="header-winner">
              P1 — #{raceResult.finishing_order[0].number} {raceResult.finishing_order[0].name}
            </span>
          )}
        </div>
      </header>

      <nav className="tab-bar">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`tab-btn ${tab === t.id ? "active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            <span className="tab-icon">{t.icon}</span>
            {t.label}
          </button>
        ))}
        <div className="tab-line" style={{ left: `${tab * 25}%` }} />
      </nav>

      <main className="app-body">
        {tab === 0 && (
          <>
            <RaceSetup
              selectedTrack={selectedTrack}
              setSelectedTrack={setSelectedTrack}
              onRaceComplete={setRaceResult}
              loading={loading}
              setLoading={setLoading}
            />
            {raceResult && <RaceResults result={raceResult} />}
          </>
        )}
        {tab === 1 && <TrackMap trackId={selectedTrack} raceResult={raceResult} />}
        {tab === 2 && (
          raceResult
            ? <LapChart lapHistory={raceResult.lap_history} />
            : <Empty msg="Run a race to see the position chart." />
        )}
        {tab === 3 && <MonteCarloPanel selectedTrack={selectedTrack} />}
      </main>

      <footer className="app-footer">
        <span>NASCAR-SIM v1.0</span>
        <span>Python + FastAPI + React</span>
      </footer>
    </div>
  );
}

function Empty({ msg }) {
  return (
    <div className="empty-state">
      <div className="empty-flag">🏁</div>
      <p>{msg}</p>
    </div>
  );
}
