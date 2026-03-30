"""
NASCAR Race Simulation Engine
Core discrete-event simulator for a full multi-car race.
"""

from __future__ import annotations
import random
from dataclasses import dataclass
from enum import Enum


class CarStatus(Enum):
    RACING = "racing"
    PITTING = "pitting"
    DNF = "dnf"


@dataclass
class Driver:
    number: str
    name: str
    team: str
    skill: float
    aggression: float
    fuel_mgmt: float


@dataclass
class CarState:
    driver: Driver
    position: int
    lap: int = 0
    track_position: float = 0.0
    tire_age: int = 0
    fuel: float = 1.0
    pit_stops: int = 0
    status: CarStatus = CarStatus.RACING
    last_lap_time: float = 0.0
    total_time: float = 0.0
    laps_led: int = 0
    incident_count: int = 0
    pitting_this_lap: bool = False
    pit_laps_remaining: int = 0


class RaceEngine:
    BASE_LAP_TIME = 30.5
    SKILL_SPREAD = 2.5        # best driver is 2.5s/lap faster than worst
    TIRE_FALLOFF_RATE = 0.018
    FUEL_PER_LAP = 1 / 65
    PIT_ROAD_PENALTY = 22.0
    NOISE_SIGMA = 0.08

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

    def _init_cars(self):
        sorted_drivers = sorted(self.drivers, key=lambda d: d.skill, reverse=True)
        for i, driver in enumerate(sorted_drivers):
            start_pos = 1.0 - (i * 0.012)
            self.cars.append(CarState(
                driver=driver,
                position=i + 1,
                track_position=max(0.0, start_pos),
                fuel=1.0,
                tire_age=0,
            ))

    def _base_lap_time(self, car: CarState, caution: bool) -> float:
        if caution:
            return self.BASE_LAP_TIME * 1.55 + random.gauss(0, 0.15)
        skill_delta = (1.0 - car.driver.skill) * self.SKILL_SPREAD
        tire_delta = max(0, car.tire_age - 10) * self.TIRE_FALLOFF_RATE
        fuel_delta = car.fuel * 0.25
        noise = random.gauss(0, self.NOISE_SIGMA)
        return self.BASE_LAP_TIME + skill_delta + tire_delta + fuel_delta + noise

    def _should_pit(self, car: CarState) -> bool:
        if car.status != CarStatus.RACING:
            return False
        laps_left = self.total_laps - car.lap
        fuel_laps_left = car.fuel / self.FUEL_PER_LAP
        if fuel_laps_left <= 2:
            return True
        if laps_left <= fuel_laps_left and car.tire_age < 55:
            return False
        if car.tire_age >= 45 and fuel_laps_left < (self.fuel_window * 0.4):
            return True
        return False

    def _execute_pit(self, car: CarState):
        car.status = CarStatus.PITTING
        car.pitting_this_lap = True
        car.pit_laps_remaining = 1
        car.pit_stops += 1

    def _complete_pit(self, car: CarState) -> float:
        car.tire_age = 0
        car.fuel = 1.0
        car.status = CarStatus.RACING
        car.pitting_this_lap = False
        return self.pit_road_time + self.PIT_ROAD_PENALTY + random.gauss(0, 0.5)

    def _check_incident(self, car: CarState) -> bool:
        base_prob = 0.0015
        aggression_factor = car.driver.aggression * 0.002
        tire_factor = max(0, (car.tire_age - 45)) * 0.0003
        return random.random() < (base_prob + aggression_factor + tire_factor)

    def _recompute_positions(self):
        active = [c for c in self.cars if c.status != CarStatus.DNF]
        dnf = [c for c in self.cars if c.status == CarStatus.DNF]
        active.sort(key=lambda c: (c.lap, c.track_position), reverse=True)
        dnf.sort(key=lambda c: (c.lap, c.track_position), reverse=True)
        for i, car in enumerate(active):
            car.position = i + 1
        for i, car in enumerate(dnf):
            car.position = len(active) + i + 1

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

            if car.pit_laps_remaining > 0:
                car.pit_laps_remaining -= 1
                if car.pit_laps_remaining == 0:
                    extra = self._complete_pit(car)
                    car.total_time += extra
                    car.track_position = max(0.01, car.track_position - 0.08)
                continue

            if self._should_pit(car):
                self._execute_pit(car)

            lap_time = self._base_lap_time(car, caution)
            car.last_lap_time = lap_time
            car.total_time += lap_time
            car.lap += 1
            car.tire_age += 1
            car.fuel = max(0.0, car.fuel - self.FUEL_PER_LAP)

            if not car.pitting_this_lap:
                speed_factor = (33.5 - min(lap_time, 33.5)) / 4.0
                advance = 0.85 + speed_factor * 0.3 + random.uniform(-0.02, 0.02)
                car.track_position = (car.track_position + advance) % 1.0

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

        leader = next((c for c in self.cars if c.position == 1), None)
        if leader:
            leader.laps_led += 1

        self.lap_history.append(lap_snapshot)

    def run(self) -> dict:
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
