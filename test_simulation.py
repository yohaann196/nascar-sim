"""
Tests that the NASCAR race simulator works correctly.
Runs a full race simulation 10 times to verify consistent behaviour.
"""

import pytest
from simulator.engine import RaceEngine
from simulator.drivers import get_drivers
from simulator.track import get_track, list_tracks


def _run_race(track_id: str = "daytona", laps: int = 50, driver_count: int = 10) -> dict:
    """Helper: run one race and return the result dict."""
    track = get_track(track_id)
    drivers = get_drivers(driver_count)
    engine = RaceEngine(
        drivers=drivers,
        total_laps=laps,
        track_name=track.name,
        track_type=track.shape,
        track_length_miles=track.length_miles,
    )
    return engine.run()


def _assert_valid_result(result: dict, expected_laps: int, driver_count: int):
    """Assert that a race result contains valid, self-consistent data."""
    # Top-level keys present
    assert "track" in result
    assert "total_laps" in result
    assert "caution_count" in result
    assert "finishing_order" in result
    assert "lap_history" in result
    assert "events" in result
    assert "caution_laps" in result

    assert result["total_laps"] == expected_laps
    assert result["caution_count"] >= 0

    # Correct number of cars finished
    finishing_order = result["finishing_order"]
    assert len(finishing_order) == driver_count

    # Positions are a contiguous sequence starting from 1
    positions = [car["position"] for car in finishing_order]
    assert sorted(positions) == list(range(1, driver_count + 1))

    # Every car has a valid status
    valid_statuses = {"racing", "dnf"}
    for car in finishing_order:
        assert car["status"] in valid_statuses
        assert car["pit_stops"] >= 0
        assert car["laps_led"] >= 0
        assert car["total_time"] > 0

    # Winner exists and is in position 1
    winner = finishing_order[0]
    assert winner["position"] == 1
    assert winner["status"] == "racing"

    # Lap history has the right number of entries
    assert len(result["lap_history"]) == expected_laps

    # caution_count matches the number of caution laps recorded
    assert result["caution_count"] == len(result["caution_laps"])


@pytest.mark.parametrize("run_number", range(1, 11))
def test_simulation_run(run_number):
    """Run the full simulation and verify the result is valid (10 times)."""
    result = _run_race(track_id="daytona", laps=50, driver_count=10)
    _assert_valid_result(result, expected_laps=50, driver_count=10)


def test_all_tracks_run():
    """Each track completes a short race without error."""
    for track_info in list_tracks():
        result = _run_race(track_id=track_info["id"], laps=20, driver_count=5)
        _assert_valid_result(result, expected_laps=20, driver_count=5)
