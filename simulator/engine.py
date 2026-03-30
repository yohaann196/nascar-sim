"""
NASCAR Race Simulation Engine
Core discrete-event simulator for a full multi-car race.
"""

from __future__ import annotations
import random
import math
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class TireCompound(Enum):
    FRESH = "fresh"
    USED = "used"
    OLD = "old"


class CarStatus(Enum):
    RACING = "racing"
    PITTING = "pitting"
    DNF = "dnf"


@dataclass
class Driver:
    number: str
    name: str
    team: str
    skill: float        # 0.0 – 1.0
    aggression: float   # 0.0 – 1.0; affects passing & incident rate
    fuel_mgmt: float    # 0.0 – 1.0; affects fuel-save ability


@dataclass
class CarState:
    driver: Driver
    position: int
    lap: int = 0
    track_position: float = 0.0   # 0.0–1.0 around the oval
    tire_age: int = 0             # laps since last stop
    fuel: float = 1.0             # 1.0 = full tank
    pit_stops: int = 0
    status: CarStatus = CarStatus.RACING
    last_lap_time: float = 0.0
    total_time: float = 0.0
    laps_led: int = 0
    incident_count: int = 0

    # Pit-stop state
    pitting_this_lap: bool = False
    pit_laps_remaining: int = 0


class RaceEngine:
    """
    Simulates a NASCAR-style oval race lap by lap.

    Parameters
    ----------
    drivers        : list of Driver objects
    total_laps     : race distance in laps
    track_name     : display name
    fuel_window    : laps per full tank
    pit_road_time  : seconds spent in pit stall
    caution_prob   : per-lap probability of a caution
    """

    BASE_LAP_TIME = 30.5          # seconds, e.g. Daytona pace
    LAP_TIME_SPREAD = 0.8         # max skill-based delta per lap
    TIRE_FALLOFF_RATE = 0.012     # seconds of time added per lap on tires
    FUEL_PER_LAP = 1 / 65        # fraction of tank used per lap
    PIT_ROAD_PENALTY = 22.0       # seconds lost entering/exiting pit road

    def __init__(
        self,
        drivers: list[Driver],
        total_laps: int = 200,
        track_name: str = "Daytona International Speedway",
        fuel_window: int = 55,
        pit_road_time: float = 12.5,
        caution_prob: float = 0.04,
    ):
        self.drivers = drivers
        self.total_laps = total_laps
        self.track_name = track_name
        self.fuel_window = fuel_window
        self.pit_road_time = pit_road_time
        self.caution_prob = caution_prob

        self.cars: list[CarState] = []
        self.lap_history: list[dict] = []
        self.events: list[dict] = []
        self.current_lap: int = 0
        self.caution_laps: list[int] = []

        self._init_cars()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _init_cars(self):
        random.shuffle(self.drivers)   # random starting grid
        for i, driver in enumerate(self.drivers):
            # stagger starting positions slightly around the track
            self.cars.append(CarState(
                driver=driver,
                position=i + 1,
                track_position=1.0 - (i * 0.02),
                fuel=1.0,
                tire_age=0,
            ))

    # ------------------------------------------------------------------
    # Lap time model
    # ------------------------------------------------------------------

    def _base_lap_time(self, car: CarState, caution: bool) -> float:
        if caution:
            return self.BASE_LAP_TIME * 1.6 + random.gauss(0, 0.1)

        skill_delta = (1.0 - car.driver.skill) * self.LAP_TIME_SPREAD
        tire_delta = car.tire_age * self.TIRE_FALLOFF_RATE
        fuel_delta = (1.0 - car.fuel) * 0.3   # lighter = faster
        noise = random.gauss(0, 0.05)
        return self.BASE_LAP_TIME + skill_delta + tire_delta + fuel_delta + noise

    # ------------------------------------------------------------------
    # Pit strategy
    # ------------------------------------------------------------------

    def _should_pit(self, car: CarState) -> bool:
        if car.status != CarStatus.RACING:
            return False
        laps_left = self.total_laps - car.lap
        fuel_laps_left = car.fuel / self.FUEL_PER_LAP

        # Must pit for fuel
        if fuel_laps_left <= 2:
            return True

        # Opportunistic: good tire age & fuel burn aligns with end
        if car.tire_age >= 40 and fuel_laps_left < (self.fuel_window * 0.35):
            return True

        # Can make it to the end without stopping
        if laps_left <= fuel_laps_left and car.tire_age < 50:
            return False

        return False

    def _execute_pit(self, car: CarState):
        car.status = CarStatus.PITTING
        car.pitting_this_lap = True
        car.pit_laps_remaining = 1   # off track for 1 lap cycle
        car.pit_stops += 1

    def _complete_pit(self, car: CarState) -> float:
        """Return extra time cost of pit stop."""
        car.tire_age = 0
        car.fuel = 1.0
        car.status = CarStatus.RACING
        car.pitting_this_lap = False
        return self.pit_road_time + self.PIT_ROAD_PENALTY + random.gauss(0, 0.4)

    # ------------------------------------------------------------------
    # Incidents
    # ------------------------------------------------------------------

    def _check_incident(self, car: CarState) -> bool:
        """Return True if car is involved in an incident this lap."""
        base_prob = 0.002
        aggression_factor = car.driver.aggression * 0.003
        tire_factor = max(0, (car.tire_age - 40)) * 0.0002
        prob = base_prob + aggression_factor + tire_factor
        return random.random() < prob

    # ------------------------------------------------------------------
    # Positions
    # ------------------------------------------------------------------

    def _recompute_positions(self):
        active = [c for c in self.cars if c.status != CarStatus.DNF]
        # Sort by laps completed desc, then track_position desc
        active.sort(key=lambda c: (c.lap, c.track_position), reverse=True)
        for i, car in enumerate(active):
            car.position = i + 1
        dnf_pos = len(active) + 1
        for car in self.cars:
            if car.status == CarStatus.DNF:
                car.position = dnf_pos
                dnf_pos += 1

    # ------------------------------------------------------------------
    # Main simulation loop
    # ------------------------------------------------------------------

    def simulate_lap(self):
        self.current_lap += 1
        lap = self.current_lap
        caution = random.random() < self.caution_prob
        if caution:
            self.caution_laps.append(lap)
            self.events.append({"lap": lap, "type": "caution", "detail": "On-track incident"})

        lap_snapshot = {"lap": lap, "caution": caution, "cars": []}

        for car in self.cars:
            if car.status == CarStatus.DNF:
                continue

            # Complete pit if returning
            if car.pit_laps_remaining > 0:
                car.pit_laps_remaining -= 1
                if car.pit_laps_remaining == 0:
                    extra = self._complete_pit(car)
                    car.total_time += extra
                    car.track_position = max(0.0, car.track_position - 0.05)
                continue

            # Decide to pit
            if self._should_pit(car):
                self._execute_pit(car)

            # Lap time
            lap_time = self._base_lap_time(car, caution)
            car.last_lap_time = lap_time
            car.total_time += lap_time
            car.lap += 1
            car.tire_age += 1
            car.fuel = max(0.0, car.fuel - self.FUEL_PER_LAP)

            # Advance track position
            if not car.pitting_this_lap:
                car.track_position = (car.track_position + random.uniform(0.95, 1.05)) % 1.0

            # Incident check
            if not caution and self._check_incident(car):
                car.incident_count += 1
                if car.incident_count >= 3:
                    car.status = CarStatus.DNF
                    self.events.append({
                        "lap": lap,
                        "type": "dnf",
                        "detail": f"#{car.driver.number} {car.driver.name} — out of race"
                    })

            lap_snapshot["cars"].append({
                "number": car.driver.number,
                "name": car.driver.name,
                "position": car.position,
                "lap_time": round(lap_time, 3),
                "tire_age": car.tire_age,
                "fuel": round(car.fuel, 3),
                "pit_stops": car.pit_stops,
                "status": car.status.value,
                "track_position": round(car.track_position, 4),
            })

        self._recompute_positions()

        # Record laps led
        leader = next((c for c in self.cars if c.position == 1), None)
        if leader:
            leader.laps_led += 1

        self.lap_history.append(lap_snapshot)

    def run(self) -> dict:
        """Run the full race and return results."""
        for _ in range(self.total_laps):
            self.simulate_lap()

        return self.results()

    def results(self) -> dict:
        sorted_cars = sorted(self.cars, key=lambda c: c.position)
        return {
            "track": self.track_name,
            "total_laps": self.total_laps,
            "caution_count": len(self.caution_laps),
            "caution_laps": self.caution_laps,
            "events": self.events,
            "finishing_order": [
                {
                    "position": car.position,
                    "number": car.driver.number,
                    "name": car.driver.name,
                    "team": car.driver.team,
                    "laps_led": car.laps_led,
                    "pit_stops": car.pit_stops,
                    "total_time": round(car.total_time, 3),
                    "status": car.status.value,
                    "incident_count": car.incident_count,
                }
                for car in sorted_cars
            ],
            "lap_history": self.lap_history,
        }
