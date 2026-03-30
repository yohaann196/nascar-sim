"""
Default driver roster for simulation.
Skill, aggression, fuel_mgmt are fictional ratings 0.0–1.0.
"""

from simulator.engine import Driver

DEFAULT_DRIVERS = [
    Driver("9",  "Chase Elliott",       "Hendrick Motorsports", skill=0.92, aggression=0.55, fuel_mgmt=0.80),
    Driver("48", "Alex Bowman",         "Hendrick Motorsports", skill=0.78, aggression=0.50, fuel_mgmt=0.75),
    Driver("5",  "Kyle Larson",         "Hendrick Motorsports", skill=0.95, aggression=0.70, fuel_mgmt=0.72),
    Driver("24", "William Byron",       "Hendrick Motorsports", skill=0.82, aggression=0.52, fuel_mgmt=0.78),
    Driver("22", "Joey Logano",         "Team Penske",          skill=0.85, aggression=0.72, fuel_mgmt=0.70),
    Driver("12", "Ryan Blaney",         "Team Penske",          skill=0.87, aggression=0.60, fuel_mgmt=0.74),
    Driver("2",  "Austin Cindric",      "Team Penske",          skill=0.74, aggression=0.65, fuel_mgmt=0.68),
    Driver("11", "Denny Hamlin",        "Joe Gibbs Racing",     skill=0.90, aggression=0.68, fuel_mgmt=0.85),
    Driver("18", "Kyle Busch",          "Richard Childress",    skill=0.88, aggression=0.75, fuel_mgmt=0.76),
    Driver("19", "Martin Truex Jr.",    "Joe Gibbs Racing",     skill=0.86, aggression=0.50, fuel_mgmt=0.88),
    Driver("20", "Christopher Bell",    "Joe Gibbs Racing",     skill=0.83, aggression=0.58, fuel_mgmt=0.77),
    Driver("54", "Ty Gibbs",            "Joe Gibbs Racing",     skill=0.72, aggression=0.68, fuel_mgmt=0.65),
    Driver("1",  "Ross Chastain",       "Trackhouse Racing",    skill=0.81, aggression=0.88, fuel_mgmt=0.62),
    Driver("99", "Daniel Suárez",       "Trackhouse Racing",    skill=0.76, aggression=0.62, fuel_mgmt=0.70),
    Driver("4",  "Kevin Harvick",       "Stewart-Haas Racing",  skill=0.84, aggression=0.60, fuel_mgmt=0.82),
    Driver("10", "Aric Almirola",       "Stewart-Haas Racing",  skill=0.70, aggression=0.55, fuel_mgmt=0.72),
    Driver("14", "Chase Briscoe",       "Stewart-Haas Racing",  skill=0.73, aggression=0.66, fuel_mgmt=0.68),
    Driver("41", "Cole Custer",         "Stewart-Haas Racing",  skill=0.68, aggression=0.60, fuel_mgmt=0.65),
    Driver("3",  "Austin Dillon",       "Richard Childress",    skill=0.72, aggression=0.63, fuel_mgmt=0.70),
    Driver("8",  "Tyler Reddick",       "23XI Racing",          skill=0.80, aggression=0.70, fuel_mgmt=0.73),
    Driver("23", "Bubba Wallace",       "23XI Racing",          skill=0.75, aggression=0.65, fuel_mgmt=0.68),
    Driver("43", "Erik Jones",          "Legacy Motor Club",    skill=0.71, aggression=0.58, fuel_mgmt=0.69),
    Driver("42", "Noah Gragson",        "Legacy Motor Club",    skill=0.65, aggression=0.72, fuel_mgmt=0.60),
    Driver("34", "Michael McDowell",    "Front Row Motorsports",skill=0.69, aggression=0.55, fuel_mgmt=0.74),
    Driver("38", "Todd Gilliland",      "Front Row Motorsports",skill=0.64, aggression=0.60, fuel_mgmt=0.65),
    Driver("17", "Chris Buescher",      "RFK Racing",           skill=0.74, aggression=0.57, fuel_mgmt=0.71),
    Driver("6",  "Brad Keselowski",     "RFK Racing",           skill=0.82, aggression=0.69, fuel_mgmt=0.74),
    Driver("45", "Tyler Reddick",       "23XI Racing",          skill=0.79, aggression=0.62, fuel_mgmt=0.72),
    Driver("47", "Ricky Stenhouse Jr.", "JTG Daugherty",        skill=0.71, aggression=0.75, fuel_mgmt=0.63),
    Driver("77", "Ty Dillon",           "Spire Motorsports",    skill=0.60, aggression=0.55, fuel_mgmt=0.62),
    Driver("7",  "Corey LaJoie",        "Spire Motorsports",    skill=0.58, aggression=0.60, fuel_mgmt=0.60),
    Driver("78", "BJ McLeod",           "Live Fast Motorsports",skill=0.52, aggression=0.50, fuel_mgmt=0.55),
    Driver("15", "JJ Yeley",            "Rick Ware Racing",     skill=0.50, aggression=0.52, fuel_mgmt=0.58),
    Driver("51", "Cody Ware",           "Rick Ware Racing",     skill=0.48, aggression=0.50, fuel_mgmt=0.55),
    Driver("66", "Mike Rockenfeller",   "Trackhouse (Special)", skill=0.55, aggression=0.48, fuel_mgmt=0.60),
    Driver("16", "AJ Allmendinger",     "Kaulig Racing",        skill=0.73, aggression=0.63, fuel_mgmt=0.67),
    Driver("31", "Justin Haley",        "Kaulig Racing",        skill=0.64, aggression=0.57, fuel_mgmt=0.66),
    Driver("21", "Harrison Burton",     "Wood Brothers",        skill=0.67, aggression=0.60, fuel_mgmt=0.65),
    Driver("50", "Landon Cassill",      "TMT Racing",           skill=0.46, aggression=0.55, fuel_mgmt=0.52),
    Driver("84", "Jimmie Johnson",      "Legacy MC (Special)",  skill=0.83, aggression=0.55, fuel_mgmt=0.80),
]


def get_drivers(count: int = 40) -> list[Driver]:
    """Return up to `count` drivers from the default roster."""
    return DEFAULT_DRIVERS[:min(count, len(DEFAULT_DRIVERS))]
