"""
Monte Carlo race strategy optimizer.
Runs N simulations and reports strategy win rates.
"""

from __future__ import annotations
import random
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Callable

from simulator.engine import RaceEngine, Driver
from simulator.drivers import get_drivers
from simulator.track import TrackConfig, get_track


def _single_run(args: dict) -> dict:
    """Run one simulation — picklable for multiprocessing."""
    random.seed(args.get("seed"))
    track: TrackConfig = args["track"]
    drivers: list[Driver] = args["drivers"]

    engine = RaceEngine(
        drivers=drivers,
        total_laps=args["total_laps"],
        track_name=track.name,
        track_type=track.shape,
        track_length_miles=track.length_miles,
        fuel_window=args.get("fuel_window"),
        pit_road_time=args.get("pit_road_time", 12.5),
        caution_prob=args.get("caution_prob", 0.03),
    )
    result = engine.run()
    winner = result["finishing_order"][0]
    return {
        "winner_number": winner["number"],
        "winner_name": winner["name"],
        "winner_team": winner["team"],
        "caution_count": result["caution_count"],
        "laps_led": {r["number"]: r["laps_led"] for r in result["finishing_order"]},
        "finishing_order": [r["number"] for r in result["finishing_order"]],
    }


def run_monte_carlo(
    track_id: str = "daytona",
    n_simulations: int = 200,
    driver_count: int = 40,
    total_laps: int = 200,
    caution_prob: float = 0.03,
    max_workers: int = 4,
    progress_callback: Callable[[int, int], None] | None = None,
) -> dict:
    """
    Run `n_simulations` independent races and aggregate stats.

    Returns
    -------
    dict with keys:
        track, n_simulations, win_counts, avg_laps_led,
        avg_cautions, finish_distribution
    """
    track = get_track(track_id)
    base_drivers = get_drivers(driver_count)

    args_list = [
        {
            "track": track,
            "drivers": [Driver(**d.__dict__) for d in base_drivers],
            "total_laps": total_laps,
            "caution_prob": caution_prob,
            "seed": i * 7919,
        }
        for i in range(n_simulations)
    ]

    win_counts: dict[str, int] = defaultdict(int)
    laps_led_totals: dict[str, float] = defaultdict(float)
    finish_dist: dict[str, list[int]] = defaultdict(list)
    caution_counts: list[int] = []

    completed = 0
    # Run single-threaded to avoid pickle issues in notebooks
    for args in args_list:
        result = _single_run(args)
        win_counts[result["winner_number"]] += 1
        caution_counts.append(result["caution_count"])
        for num, laps in result["laps_led"].items():
            laps_led_totals[num] += laps
        for pos, num in enumerate(result["finishing_order"], 1):
            finish_dist[num].append(pos)
        completed += 1
        if progress_callback:
            progress_callback(completed, n_simulations)

    # Build driver index for name lookup
    driver_map = {d.number: d for d in base_drivers}

    win_pct = {
        num: round(count / n_simulations * 100, 2)
        for num, count in sorted(win_counts.items(), key=lambda x: -x[1])
    }
    avg_laps_led = {
        num: round(total / n_simulations, 1)
        for num, total in sorted(laps_led_totals.items(), key=lambda x: -x[1])
    }
    avg_finish = {
        num: round(sum(positions) / len(positions), 2)
        for num, positions in finish_dist.items()
    }

    return {
        "track": track.name,
        "track_id": track_id,
        "n_simulations": n_simulations,
        "driver_count": driver_count,
        "total_laps": total_laps,
        "avg_cautions": round(sum(caution_counts) / len(caution_counts), 2),
        "win_percentages": [
            {
                "number": num,
                "name": driver_map[num].name,
                "team": driver_map[num].team,
                "win_pct": pct,
                "wins": win_counts[num],
                "avg_laps_led": avg_laps_led.get(num, 0),
                "avg_finish": avg_finish.get(num, driver_count),
            }
            for num, pct in win_pct.items()
            if num in driver_map
        ],
    }
