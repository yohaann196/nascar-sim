"""
NASCAR Race Simulation Engine
Core discrete-event simulator for a full multi-car race.
"""

from __future__ import annotations
import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional


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


# Incident types for variety in event reporting
_INCIDENT_TYPES = [
    "crash into the wall",
    "multi-car accident",
    "blown engine",
    "mechanical failure",
    "tire failure",
    "brake failure",
    "oil leak — terminal",
]


class RaceEngine:
    SKILL_SPREAD = 4.0        # best driver 4s/lap faster than worst

    # Average speeds (mph) by track type — used to derive realistic base lap times
    TRACK_AVG_SPEEDS: dict[str, float] = {
        "superspeedway": 188.0,   # Daytona, Talladega draft packs
        "oval": 176.0,            # Charlotte, Michigan
        "short_track": 108.0,     # Bristol, Martinsville
        "road_course": 88.0,      # COTA, Sonoma
    }

    # Tire falloff (seconds/lap per lap of age) by track type
    TRACK_TIRE_FALLOFF: dict[str, float] = {
        "superspeedway": 0.010,   # low lateral load, tires last well
        "oval": 0.018,            # moderate
        "short_track": 0.035,     # high lateral load, tires wear quickly
        "road_course": 0.025,
    }

    # Tire stint factor (fraction of fuel window) by track type
    TIRE_STINT_FACTOR: dict[str, float] = {
        "superspeedway": 0.85,   # long stints — tires last on banking
        "oval": 0.70,            # moderate stints
        "short_track": 0.45,     # frequent tire changes — high lateral load
        "road_course": 0.50,
    }

    # Superspeedway drafting speed bonus: random boost/drag per lap
    DRAFT_SIGMA: dict[str, float] = {
        "superspeedway": 0.8,     # big swings from drafting
        "oval": 0.25,
        "short_track": 0.15,
        "road_course": 0.20,
    }

    # Cup car: ~22-gallon tank at ~5.5 mpg ≈ 121 miles per tank
    TANK_RANGE_MILES = 121.0
    PIT_ROAD_PENALTY = 22.0

    def __init__(
        self,
        drivers: list[Driver],
        total_laps: int = 200,
        track_name: str = "Daytona International Speedway",
        track_type: str = "oval",
        track_length_miles: float = 1.5,
        fuel_window: Optional[int] = None,
        pit_road_time: float = 12.5,
        caution_prob: float = 0.03,   # ~6 cautions/200 laps (realistic)
    ):
        self.drivers = drivers
        self.total_laps = total_laps
        self.track_name = track_name
        self.track_type = track_type
        self.track_length_miles = track_length_miles
        self.pit_road_time = pit_road_time
        self.caution_prob = caution_prob

        # Compute realistic base lap time from track geometry
        avg_speed = self.TRACK_AVG_SPEEDS.get(track_type, 176.0)
        self.BASE_LAP_TIME = (track_length_miles / avg_speed) * 3600

        # Track-specific tire falloff
        self.TIRE_FALLOFF_RATE = self.TRACK_TIRE_FALLOFF.get(track_type, 0.018)

        # Track-specific noise/drafting variance
        self.NOISE_SIGMA = self.DRAFT_SIGMA.get(track_type, 0.25)

        # Track-specific fuel consumption (miles-based, realistic)
        self.FUEL_PER_LAP = track_length_miles / self.TANK_RANGE_MILES

        # Fuel window: laps until the car needs to pit for fuel
        laps_per_tank = int(self.TANK_RANGE_MILES / track_length_miles)
        self.fuel_window = fuel_window if fuel_window is not None else laps_per_tank

        # Expected tire stint: fraction of fuel window depending on track type
        stint_factor = self.TIRE_STINT_FACTOR.get(track_type, 0.70)
        self.tire_stint = max(40, int(self.fuel_window * stint_factor))

        # NASCAR stage structure: guaranteed caution at ~33% and ~65% of race distance
        if total_laps >= 30:
            self.stage_laps: set[int] = {
                round(total_laps * 0.325),
                round(total_laps * 0.650),
            }
        else:
            self.stage_laps = set()

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
            # Under caution all cars run ~55% slower; small skill delta persists
            skill_delta = (1.0 - car.driver.skill) * 0.5
            noise = random.gauss(0, self.BASE_LAP_TIME * 0.003)
            return self.BASE_LAP_TIME * 1.55 + skill_delta + noise
        skill_delta = (1.0 - car.driver.skill) * self.SKILL_SPREAD
        tire_delta = max(0, car.tire_age - 8) * self.TIRE_FALLOFF_RATE
        fuel_delta = car.fuel * (self.BASE_LAP_TIME * 0.005)   # heavier car = slower
        noise = random.gauss(0, self.NOISE_SIGMA)
        return self.BASE_LAP_TIME + skill_delta + tire_delta + fuel_delta + noise

    def _should_pit(self, car: CarState) -> bool:
        if car.status != CarStatus.RACING:
            return False
        laps_left = self.total_laps - car.lap
        fuel_laps_left = car.fuel / self.FUEL_PER_LAP
        # Emergency: almost out of fuel
        if fuel_laps_left <= 3:
            return True
        # Can make it to the finish without stopping
        if laps_left <= fuel_laps_left and car.tire_age < self.tire_stint:
            return False
        # Tire-driven stop: tires worn past the expected stint length
        if car.tire_age >= self.tire_stint:
            return True
        # Strategic pit: tires worn AND fuel is getting low
        tire_worn = car.tire_age >= int(self.fuel_window * 0.80)
        fuel_low = fuel_laps_left < (self.fuel_window * 0.20)
        if tire_worn and fuel_low:
            return True
        return False

    def _bunch_field(self):
        """Compress the field under caution — cars close up behind the leader."""
        active = [c for c in self.cars if c.status == CarStatus.RACING]
        if len(active) < 2:
            return
        active.sort(key=lambda c: (c.lap, c.track_position), reverse=True)
        leader_pos = active[0].track_position
        # Each car bunches to within 0.005 track-fraction per position of the leader
        for i, car in enumerate(active[1:], 1):
            target = leader_pos - (i * 0.005)
            if car.track_position < target:
                car.track_position = target

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
        base_prob = 0.0012
        aggression_factor = car.driver.aggression * 0.0015
        # Tire factor only amplifies once past the expected tire stint
        tire_factor = max(0, (car.tire_age - self.tire_stint)) * 0.0004
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

        # Stage cautions always fire at the designated laps
        stage_caution = lap in self.stage_laps
        green_incident = random.random() < self.caution_prob
        caution = stage_caution or green_incident

        if caution:
            self.caution_laps.append(lap)
            if stage_caution:
                stage_num = sorted(self.stage_laps).index(lap) + 1
                self.events.append({
                    "lap": lap,
                    "type": "caution",
                    "detail": f"End of Stage {stage_num}",
                })
            else:
                self.events.append({
                    "lap": lap,
                    "type": "caution",
                    "detail": "On-track incident",
                })
            self._bunch_field()

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
                # Advance is proportional to how fast the car goes vs. average
                ref_time = self.BASE_LAP_TIME * 1.05  # slightly above base = reference slow car
                speed_factor = (ref_time - min(lap_time, ref_time)) / max(ref_time * 0.12, 1.0)
                advance = 0.85 + speed_factor * 0.3 + random.uniform(-0.02, 0.02)
                car.track_position = (car.track_position + advance) % 1.0

            if not caution and self._check_incident(car):
                car.incident_count += 1
                if car.incident_count >= 3:
                    cause = random.choice(_INCIDENT_TYPES)
                    car.status = CarStatus.DNF
                    self.events.append({
                        "lap": lap,
                        "type": "dnf",
                        "detail": f"#{car.driver.number} {car.driver.name} — {cause}",
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
