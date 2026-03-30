"""
Track geometry module.
Generates oval and road course coordinate paths for map rendering.
"""

from __future__ import annotations
import math
from dataclasses import dataclass


@dataclass
class TrackConfig:
    name: str
    center_lat: float
    center_lng: float
    length_miles: float
    banking_deg: float
    shape: str = "oval"           # oval | superspeedway | short_track | road_course
    # Oval tuning
    straightaway_ratio: float = 0.45   # fraction of track that is straight
    width_factor: float = 1.0


# Real NASCAR tracks (approximate center coordinates)
TRACKS: dict[str, TrackConfig] = {
    "daytona": TrackConfig(
        "Daytona International Speedway",
        29.1853, -81.0698, 2.5, 31.0, "superspeedway", 0.52, 1.8,
    ),
    "talladega": TrackConfig(
        "Talladega Superspeedway",
        33.5690, -86.0664, 2.66, 33.0, "superspeedway", 0.54, 2.0,
    ),
    "charlotte": TrackConfig(
        "Charlotte Motor Speedway",
        35.3515, -80.6832, 1.5, 24.0, "oval", 0.44, 1.3,
    ),
    "bristol": TrackConfig(
        "Bristol Motor Speedway",
        36.5157, -82.2579, 0.533, 36.0, "short_track", 0.22, 0.7,
    ),
    "martinsville": TrackConfig(
        "Martinsville Speedway",
        36.6367, -79.8534, 0.526, 12.0, "short_track", 0.30, 0.6,
    ),
    "michigan": TrackConfig(
        "Michigan International Speedway",
        42.0672, -84.2456, 2.0, 18.0, "oval", 0.50, 1.6,
    ),
}


def _deg_to_rad(deg: float) -> float:
    return deg * math.pi / 180.0


def generate_oval_coords(
    config: TrackConfig,
    num_points: int = 200,
) -> list[dict]:
    """
    Generate lat/lng coordinates tracing an oval track layout.

    Returns a list of {lat, lng, section} dicts ordered around the track.
    Sections: 'frontstretch', 'turn1', 'backstretch', 'turn3'
    """
    # Scale degrees per mile at given latitude
    lat_deg_per_mile = 1 / 69.0
    lng_deg_per_mile = 1 / (69.0 * math.cos(_deg_to_rad(config.center_lat)))

    # Oval semi-axes in degrees
    length_factor = config.length_miles * config.width_factor
    a = length_factor * lng_deg_per_mile * 0.5          # semi-major (east-west)
    b = length_factor * lat_deg_per_mile * 0.25         # semi-minor (north-south)

    # Adjust shape by straightaway ratio
    straight_angle = config.straightaway_ratio * math.pi

    coords = []
    for i in range(num_points):
        t = 2 * math.pi * i / num_points    # 0 → 2π

        # Squircle-like shape: straights on east/west, turns on north/south
        # Map t through a "stadium oval" curve
        cos_t = math.cos(t)
        sin_t = math.sin(t)

        # Stretch straights
        stretch = 1 + config.straightaway_ratio * abs(cos_t)
        x = a * cos_t * stretch
        y = b * sin_t

        lat = config.center_lat + y
        lng = config.center_lng + x

        # Classify section
        if abs(cos_t) > 0.7:
            section = "frontstretch" if cos_t > 0 else "backstretch"
        else:
            section = "turn1" if sin_t > 0 else "turn3"

        coords.append({"lat": round(lat, 6), "lng": round(lng, 6), "section": section})

    # Close the loop
    coords.append(coords[0])
    return coords


def track_position_to_coords(
    track_position: float,
    coords: list[dict],
) -> tuple[float, float]:
    """
    Convert a 0.0–1.0 track position to lat/lng.
    track_position=0.0 → start/finish line (index 0).
    """
    n = len(coords) - 1   # exclude closing duplicate
    idx = int(track_position * n) % n
    next_idx = (idx + 1) % n
    frac = (track_position * n) - int(track_position * n)

    lat = coords[idx]["lat"] + frac * (coords[next_idx]["lat"] - coords[idx]["lat"])
    lng = coords[idx]["lng"] + frac * (coords[next_idx]["lng"] - coords[idx]["lng"])
    return round(lat, 6), round(lng, 6)


def get_track(name: str) -> TrackConfig:
    key = name.lower().replace(" ", "_")
    if key not in TRACKS:
        raise ValueError(f"Unknown track '{name}'. Available: {list(TRACKS.keys())}")
    return TRACKS[key]


def list_tracks() -> list[dict]:
    return [
        {
            "id": k,
            "name": v.name,
            "lat": v.center_lat,
            "lng": v.center_lng,
            "length_miles": v.length_miles,
            "banking_deg": v.banking_deg,
            "shape": v.shape,
        }
        for k, v in TRACKS.items()
    ]
