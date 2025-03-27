import random
from teams.helper_function import Troops, Utils

team_name = "WinnerBot"
troops = [
    Troops.giant, Troops.wizard, Troops.minion, Troops.dragon,
    Troops.archer, Troops.barbarian, Troops.skeleton, Troops.valkyrie
]
deploy_list = Troops([])
team_signal = ""  # Not used, but maintained for compatibility

def random_x(min_val=-10, max_val=10):
    return random.randint(min_val, max_val)

def deploy(arena_data: dict):
    """
    DON'T TEMPER DEPLOY FUNCTION
    """
    deploy_list.list_ = []
    logic(arena_data)
    return deploy_list.list_, team_signal

def logic(arena_data: dict):
    global team_signal
    troops_data = {
        "Archer":    { "cost": 3, "flags": {'air', 'walk'},           "air_dmg": 2596.0, "gnd_dmg": 2596.0, "hp": 1002.0,   "range": 8, "number": 2},
        "Minion":    { "cost": 3, "flags": {'fly', 'air'},            "air_dmg": 3096.0, "gnd_dmg": 3096.0, "hp": 907.2,    "range": 4, "number": 3},
        "Knight":    { "cost": 3, "flags": {'gnd', 'tank', 'walk'},   "air_dmg": 0,      "gnd_dmg": 1326.0, "hp": 1938.0,   "range": 7, "number": 1},
        # "Skeleton":  { "cost": 3, "flags": {'gnd', 'walk'},           "air_dmg": 0,      "gnd_dmg": 5340.0, "hp": 890.0,    "range": 4,   "number": 10},  # original
        "Skeleton":  { "cost": 3, "flags": {'gnd', 'walk'},           "air_dmg": 0,      "gnd_dmg": 4000, "hp": 600.0,    "range": 4,   "number": 10},
        # "Dragon":    { "cost": 4, "flags": {'splash', 'fly', 'air'},  "air_dmg": 2508.0, "gnd_dmg": 2508.0, "hp": 1710.45,  "range": 5,   "number": 1},
        "Dragon":    { "cost": 4, "flags": {'splash', 'fly', 'air'},  "air_dmg": 2508.0, "gnd_dmg": 2508.0, "hp": 1910.45,  "range": 5, "number": 1},
        # "Musketeer": { "cost": 4, "flags": {'air', 'walk'},           "air_dmg": 1434.0, "gnd_dmg": 1434.0, "hp": 1267.2,   "range": 8,   "number": 1},  # original
        "Musketeer": { "cost": 4, "flags": {'air', 'walk'},           "air_dmg": 2034.0, "gnd_dmg": 2034.0, "hp": 1267.2,   "range": 8, "number": 1},
        # "Valkyrie":  { "cost": 4, "flags": {'splash', 'gnd', 'walk'}, "air_dmg": 0,      "gnd_dmg": 1755.0, "hp": 2097.0,   "range": 7,   "number": 1},  # original
        "Valkyrie":  { "cost": 4, "flags": {'splash', 'gnd', 'walk'}, "air_dmg": 0,      "gnd_dmg": 2155.0, "hp": 2097.0,   "range": 7, "number": 1},
        "Giant":     { "cost": 5, "flags": {'gnd', 'tank', 'walk'},   "air_dmg": 0,      "gnd_dmg": 674.0,  "hp": 5423.0,   "range": 7, "number": 1},
        "Prince":    { "cost": 5, "flags": {'gnd', 'charge', 'walk'}, "air_dmg": 0,      "gnd_dmg": 2352.0, "hp": 1920.0,   "range": 5, "number": 1},
        "Barbarian": { "cost": 3, "flags": {'gnd', 'walk'},           "air_dmg": 0,      "gnd_dmg": 1449.0, "hp": 2208.0,   "range": 5, "number": 3},
        "Balloon":   { "cost": 5, "flags": {'splash', 'fly', 'gnd'},  "air_dmg": 1908.0, "gnd_dmg": 1908.0, "hp": 2226.0,   "range": 5, "number": 1},
        # "Wizard":    { "cost": 5, "flags": {'splash', 'walk', 'air'}, "air_dmg": 7072.5, "gnd_dmg": 7072.5, "hp": 1705.0,   "range": 8,   "number": 1},
        "Wizard":    { "cost": 5, "flags": {'splash', 'walk', 'air'}, "air_dmg": 6000, "gnd_dmg": 6000, "hp": 1705.0,   "range": 8, "number": 1},
    }
    my_tower = arena_data["MyTower"]
    opp_troops = arena_data["OppTroops"]
    my_troops = arena_data["MyTroops"]
    hand = my_tower.deployable_troops
    my_elixir = my_tower.total_elixir

    # Calculate threat level from opponent troops
    threat_level = 0
    for troop in opp_troops:
        # troop_enum = Troops[troop.name]
        data = troops_data[troop.name]
        # Use appropriate damage based on troop type
        damage = data["gnd_dmg"] if "walk" in data["flags"] else data["air_dmg"]
        y = troop.position[1]  # y=0 is my tower, y=100 is opponent's
        # Threat increases as troops near my tower
        threat_level += damage * (1 - y / 100)

    # Define tank role (high HP troops)
    tank_on_field = any("tank" in troops_data[t.name]["flags"] for t in my_troops)
    # Assume Giant is tagged as 'tank' in troops_data; adjust if needed
    # Alternatively, check HP > threshold, e.g., 1000, if 'tank' flag is unavailable

    best_troop = None
    best_score = -1

    if threat_level > 300:  # Defensive mode if threat is high
        for troop in hand:
            if troops_data[troop]["cost"] > my_elixir:
                continue
            score = 0
            for opp_troop in opp_troops:
                # opp_enum = Troops[opp_troop.name]
                opp_data = troops_data[opp_troop.name]
                # Check if troop can hit the opponent
                can_hit = (
                    ("fly" in opp_data["flags"] and "air" in troops_data[troop]["flags"]) or
                    ("walk" in opp_data["flags"] and "gnd" in troops_data[troop]["flags"])
                )
                if can_hit:
                    damage = troops_data[troop]["air_dmg"] if "fly" in opp_data["flags"] else troops_data[troop]["gnd_dmg"]
                    # Weight by proximity to my tower
                    score += damage * (1 - opp_troop.position[1] / 100)
            # Prefer splash troops for multiple enemies
            if len(opp_troops) > 1 and "splash" in troops_data[troop]["flags"]:
                score *= 1.5
            if score > best_score:
                best_score = score
                best_troop = troop
    else:  # Offensive mode
        for troop in hand:
            if troops_data[troop]["cost"] > my_elixir:
                continue
            data = troops_data[troop]
            # Prioritize tank if none on field
            if not tank_on_field and "tank" in data["flags"]:
                score = 10000  # High priority for tank
            else:
                # Score based on damage potential, adjusted by cost
                score = (data["gnd_dmg"] + data["air_dmg"] + data["hp"] / 10) / data["cost"]
                # Bonus for air troops to counter enemy’s ground preference
                if "fly" in data["flags"]:
                    score *= 1.2
            if score > best_score:
                best_score = score
                best_troop = troop

    # Deploy the best troop
    if best_troop:
        # Adjust x based on troop type to counter enemy positions
        x_range = (-25, 25) if "fly" in troops_data[best_troop]["flags"] else (-10, 10)
        deploy_position = (random_x(*x_range), 0)
        deploy_list.list_.append((best_troop, deploy_position))
    # Prevent elixir leakage: deploy cheapest troop if elixir is near full
    elif my_elixir >= 9 and hand:
        cheapest = min(hand, key=lambda t: troops_data[t]["cost"])
        if troops_data[cheapest]["cost"] <= my_elixir:
            deploy_position = (random_x(), 0)
            deploy_list.list_.append((cheapest, deploy_position))
