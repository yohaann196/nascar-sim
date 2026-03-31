"""
FastAPI backend — serves race simulation data to the React frontend.
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from simulator.engine import RaceEngine
from simulator.drivers import get_drivers
from simulator.track import generate_oval_coords, list_tracks, get_track
from simulator.monte_carlo import run_monte_carlo

app = FastAPI(
    title="NASCAR Simulator API",
    description="Race simulation engine with Monte Carlo strategy analysis",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────

class SimulateRequest(BaseModel):
    track_id: str = Field("daytona", description="Track key, e.g. 'daytona'")
    total_laps: int = Field(200, ge=10, le=500)
    driver_count: int = Field(40, ge=2, le=40)
    caution_prob: float = Field(0.03, ge=0.0, le=0.3)
    fuel_window: Optional[int] = Field(None, ge=20)
    pit_road_time: float = Field(12.5, ge=8.0, le=20.0)


class MonteCarloRequest(BaseModel):
    track_id: str = "daytona"
    n_simulations: int = Field(100, ge=10, le=1000)
    driver_count: int = Field(40, ge=2, le=40)
    total_laps: int = Field(200, ge=10, le=500)
    caution_prob: float = Field(0.03, ge=0.0, le=0.3)


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "NASCAR Simulator API running"}


@app.get("/tracks")
def get_tracks():
    """List all available tracks."""
    return list_tracks()


@app.get("/tracks/{track_id}/coords")
def track_coords(track_id: str, points: int = Query(200, ge=50, le=500)):
    """Return lat/lng coordinates tracing the track oval."""
    try:
        config = get_track(track_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    coords = generate_oval_coords(config, num_points=points)
    return {"track_id": track_id, "name": config.name, "coords": coords}


@app.get("/drivers")
def get_driver_roster(count: int = Query(40, ge=1, le=40)):
    """Return the driver roster."""
    drivers = get_drivers(count)
    return [
        {
            "number": d.number,
            "name": d.name,
            "team": d.team,
            "skill": d.skill,
            "aggression": d.aggression,
            "fuel_mgmt": d.fuel_mgmt,
        }
        for d in drivers
    ]


@app.post("/simulate")
def simulate_race(req: SimulateRequest):
    """Run a single full race simulation."""
    try:
        track = get_track(req.track_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    drivers = get_drivers(req.driver_count)
    engine = RaceEngine(
        drivers=drivers,
        total_laps=req.total_laps,
        track_name=track.name,
        track_type=track.shape,
        track_length_miles=track.length_miles,
        fuel_window=req.fuel_window,
        pit_road_time=req.pit_road_time,
        caution_prob=req.caution_prob,
    )
    result = engine.run()
    return result


@app.post("/monte-carlo")
def monte_carlo(req: MonteCarloRequest):
    """Run Monte Carlo win probability analysis."""
    try:
        result = run_monte_carlo(
            track_id=req.track_id,
            n_simulations=req.n_simulations,
            driver_count=req.driver_count,
            total_laps=req.total_laps,
            caution_prob=req.caution_prob,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/simulate/quick")
def quick_race(
    track_id: str = "daytona",
    laps: int = 200,
    drivers: int = 10,
):
    """Quick GET endpoint for testing — small field, default settings."""
    try:
        track = get_track(track_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    driver_list = get_drivers(min(drivers, 40))
    engine = RaceEngine(
        drivers=driver_list,
        total_laps=laps,
        track_name=track.name,
        track_type=track.shape,
        track_length_miles=track.length_miles,
    )
    return engine.run()
