# 🏁 NASCAR Race Simulator

A full multi-car NASCAR race simulation engine with a React frontend, FastAPI backend, and Monte Carlo strategy analysis.

## Features

- **40-car race engine** with realistic lap times, tire degradation, and fuel management
- **Pit stop strategy** — automatic fuel and tire decisions based on race situation
- **Caution simulation** — random yellows that bunch the field
- **DNF system** — aggressive drivers accumulate incidents and can retire
- **Monte Carlo analyzer** — run 100s of races to compute win probabilities
- **Track map** — oval geometry rendered on real OpenStreetMap tiles via Leaflet
- **Lap chart** — position-over-time visualization for the top 10

## Project Structure

```
nascar-sim/
├── simulator/
│   ├── engine.py         # Core race simulation (lap-by-lap)
│   ├── track.py          # Oval geometry + 6 real NASCAR tracks
│   ├── drivers.py        # 40-driver roster with skill ratings
│   └── monte_carlo.py    # Multi-simulation strategy analysis
├── api/
│   └── main.py           # FastAPI REST server
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── components/
│       │   ├── RaceSetup.jsx
│       │   ├── RaceResults.jsx
│       │   ├── TrackMap.jsx     # Leaflet map
│       │   ├── LapChart.jsx     # SVG position chart
│       │   └── MonteCarloPanel.jsx
│       └── utils/api.js
├── run_race.py           # CLI runner (no server needed)
└── requirements.txt
```

## Quick Start

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Run a race in the terminal (no server needed)
```bash
# Single race at Daytona
python run_race.py race daytona 200 20

# List available tracks
python run_race.py tracks

# Monte Carlo (50 sims at Talladega)
python run_race.py mc talladega 50
```

### 3. Start the API server
```bash
cd api
uvicorn main:app --reload --port 8000
```

### 4. Start the React frontend
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/tracks` | List all tracks |
| GET | `/tracks/{id}/coords` | Track oval lat/lng points |
| GET | `/drivers` | Full driver roster |
| POST | `/simulate` | Run a single race |
| POST | `/monte-carlo` | Run N simulations |
| GET | `/simulate/quick` | Quick test race (GET) |

## Available Tracks

| ID | Track | Length |
|----|-------|--------|
| `daytona` | Daytona International Speedway | 2.5 mi |
| `talladega` | Talladega Superspeedway | 2.66 mi |
| `charlotte` | Charlotte Motor Speedway | 1.5 mi |
| `bristol` | Bristol Motor Speedway | 0.533 mi |
| `martinsville` | Martinsville Speedway | 0.526 mi |
| `michigan` | Michigan International Speedway | 2.0 mi |

## Extending the Simulator

Ideas for next steps:
- Add **road courses** (COTA, Watkins Glen) with sector-based lap time models
- Implement **stage racing** (Stage 1/2/3 with playoff points)
- Add **weather simulation** (rain delays, track temp affecting grip)
- Build a **telemetry replay** mode with animated car positions
- Scrape real NASCAR lap data to calibrate skill ratings
- Add **driver contracts** and a multi-season franchise mode

## Tech Stack

- **Python** — simulation core (`engine.py`, `monte_carlo.py`)
- **FastAPI** — REST API bridge
- **React + Vite** — frontend dashboard
- **Leaflet.js** — map rendering (OpenStreetMap tiles)
- **SVG** — lap position chart (zero dependencies)
