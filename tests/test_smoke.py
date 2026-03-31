"""
Smoke tests — confirms the core simulator components work end-to-end.
Run with:  python -m pytest tests/test_smoke.py -v
"""

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Acceptable floating-point tolerance when checking win percentages sum to 100 %
WIN_PERCENTAGE_TOLERANCE = 0.01

from simulator.engine import RaceEngine
from simulator.drivers import get_drivers
from simulator.track import get_track, list_tracks
from simulator.monte_carlo import run_monte_carlo


# ── Track helpers ─────────────────────────────────────────────────────────────

def test_list_tracks_returns_all_six():
    tracks = list_tracks()
    assert len(tracks) == 6
    ids = {t["id"] for t in tracks}
    assert ids == {"daytona", "talladega", "charlotte", "bristol", "martinsville", "michigan"}


def test_get_track_daytona():
    track = get_track("daytona")
    assert track.name == "Daytona International Speedway"
    assert track.length_miles == 2.5


def test_get_track_invalid_raises():
    with pytest.raises(ValueError):
        get_track("nonexistent")


# ── Driver roster ─────────────────────────────────────────────────────────────

def test_get_drivers_returns_requested_count():
    for n in (1, 10, 40):
        drivers = get_drivers(n)
        assert len(drivers) == n


def test_drivers_have_valid_skill_range():
    drivers = get_drivers(40)
    for d in drivers:
        assert 0.0 <= d.skill <= 1.0, f"{d.name} skill out of range: {d.skill}"
        assert 0.0 <= d.aggression <= 1.0, f"{d.name} aggression out of range: {d.aggression}"


# ── Race engine ───────────────────────────────────────────────────────────────

def test_single_race_completes():
    track = get_track("daytona")
    drivers = get_drivers(10)
    engine = RaceEngine(
        drivers=drivers,
        total_laps=30,
        track_name=track.name,
        track_type=track.shape,
        track_length_miles=track.length_miles,
    )
    result = engine.run()

    assert result["total_laps"] == 30
    assert result["track"] == "Daytona International Speedway"
    assert len(result["finishing_order"]) == 10
    # Winner must be in position 1
    assert result["finishing_order"][0]["position"] == 1


def test_race_on_every_track():
    for track_info in list_tracks():
        track = get_track(track_info["id"])
        drivers = get_drivers(5)
        engine = RaceEngine(
            drivers=drivers,
            total_laps=20,
            track_name=track.name,
            track_type=track.shape,
            track_length_miles=track.length_miles,
        )
        result = engine.run()
        assert result["total_laps"] == 20, f"Wrong lap count for {track_info['id']}"
        assert len(result["finishing_order"]) == 5


def test_caution_count_is_non_negative():
    track = get_track("bristol")
    drivers = get_drivers(8)
    engine = RaceEngine(
        drivers=drivers,
        total_laps=50,
        track_name=track.name,
        track_type=track.shape,
        track_length_miles=track.length_miles,
    )
    result = engine.run()
    assert result["caution_count"] >= 0


def test_lap_history_length_matches_total_laps():
    track = get_track("charlotte")
    drivers = get_drivers(5)
    engine = RaceEngine(
        drivers=drivers,
        total_laps=25,
        track_name=track.name,
        track_type=track.shape,
        track_length_miles=track.length_miles,
    )
    result = engine.run()
    assert len(result["lap_history"]) == 25


# ── Monte Carlo ───────────────────────────────────────────────────────────────

def test_monte_carlo_returns_win_percentages():
    result = run_monte_carlo(
        track_id="daytona",
        n_simulations=5,
        driver_count=5,
        total_laps=20,
    )
    assert "win_percentages" in result
    assert len(result["win_percentages"]) > 0
    total_pct = sum(d["win_pct"] for d in result["win_percentages"])
    assert abs(total_pct - 100.0) < WIN_PERCENTAGE_TOLERANCE, f"Win percentages don't sum to 100: {total_pct}"


def test_monte_carlo_avg_cautions_is_non_negative():
    result = run_monte_carlo(
        track_id="talladega",
        n_simulations=5,
        driver_count=5,
        total_laps=20,
    )
    assert result["avg_cautions"] >= 0
