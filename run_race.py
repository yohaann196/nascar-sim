#!/usr/bin/env python3
"""
Quick CLI race runner — no API or frontend needed.
Usage: python run_race.py [track_id] [laps] [drivers]
"""

import sys
import json
import time

sys.path.insert(0, ".")
from simulator.engine import RaceEngine
from simulator.drivers import get_drivers
from simulator.track import get_track, list_tracks
from simulator.monte_carlo import run_monte_carlo


def print_results(result: dict):
    print(f"\n{'='*60}")
    print(f"  🏁  {result['track']}")
    print(f"{'='*60}")
    print(f"  Laps: {result['total_laps']}   Cautions: {result['caution_count']}")
    print()

    print(f"  {'POS':<4} {'#':<5} {'DRIVER':<24} {'LAPS LED':<10} {'PIT STOPS':<10} {'STATUS'}")
    print(f"  {'-'*65}")
    for car in result["finishing_order"][:15]:
        status = "✅" if car["status"] == "racing" else "💥 DNF"
        print(
            f"  {car['position']:<4} "
            f"#{car['number']:<4} "
            f"{car['name']:<24} "
            f"{car['laps_led']:<10} "
            f"{car['pit_stops']:<10} "
            f"{status}"
        )

    print(f"\n  🏆  Winner: #{result['finishing_order'][0]['number']} "
          f"{result['finishing_order'][0]['name']} "
          f"({result['finishing_order'][0]['team']})")

    print(f"\n  Race Events:")
    for ev in result["events"][-8:]:
        icon = "🟡" if ev["type"] == "caution" else "💥"
        print(f"    Lap {ev['lap']:>3}: {icon} {ev['detail']}")


def run_single(track_id="daytona", laps=200, driver_count=20):
    print(f"\nLoading track: {track_id}...")
    track = get_track(track_id)
    drivers = get_drivers(driver_count)

    print(f"Starting {laps}-lap race at {track.name} with {driver_count} cars...")
    t0 = time.time()

    engine = RaceEngine(
        drivers=drivers,
        total_laps=laps,
        track_name=track.name,
        track_type=track.shape,
        track_length_miles=track.length_miles,
    )
    result = engine.run()
    elapsed = time.time() - t0
    print(f"Simulated in {elapsed:.2f}s")
    print_results(result)


def run_mc(track_id="daytona", n=50, driver_count=20, laps=200):
    print(f"\nRunning {n} Monte Carlo simulations at {track_id}...")
    t0 = time.time()
    result = run_monte_carlo(
        track_id=track_id,
        n_simulations=n,
        driver_count=driver_count,
        total_laps=laps,
    )
    elapsed = time.time() - t0
    print(f"Done in {elapsed:.2f}s  |  Avg cautions: {result['avg_cautions']}")
    print(f"\n  {'#':<5} {'DRIVER':<24} {'WIN %':<8} {'AVG FINISH'}")
    print(f"  {'-'*50}")
    for d in result["win_percentages"][:10]:
        bar = "█" * int(d["win_pct"] / 2)
        print(f"  #{d['number']:<4} {d['name']:<24} {d['win_pct']:>5.1f}%  {bar}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "race"

    if mode == "tracks":
        for t in list_tracks():
            print(f"  {t['id']:<15} {t['name']}  ({t['length_miles']} mi)")

    elif mode == "mc":
        track_id = sys.argv[2] if len(sys.argv) > 2 else "daytona"
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        run_mc(track_id, n)

    else:
        track_id = sys.argv[2] if len(sys.argv) > 2 else "daytona"
        laps = int(sys.argv[3]) if len(sys.argv) > 3 else 200
        driver_count = int(sys.argv[4]) if len(sys.argv) > 4 else 20
        run_single(track_id, laps, driver_count)
