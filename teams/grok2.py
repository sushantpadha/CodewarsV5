import random
import json
from teams.helper_function import Troops, Utils

team_name = "WinnerBot2"
troops = [
    Troops.giant, Troops.wizard, Troops.minion, Troops.dragon,
    Troops.archer, Troops.barbarian, Troops.skeleton, Troops.valkyrie
]
deploy_list = Troops([])
team_signal = ""  # Initialize as empty string

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
    # Parse global state from team_signal
    if team_signal:
        global_state = json.loads(team_signal)
    else:
        global_state = {"frame_count": 0}
    frame_count = global_state["frame_count"] + 1
    global_state["frame_count"] = frame_count
    team_signal = json.dumps(global_state)

    # Troop data dictionary (keys are troop names as strings)
    troops_data = {
        "Archer":    {"cost": 3, "flags": {'air', 'walk'},           "air_dmg": 2596.0, "gnd_dmg": 2596.0, "hp": 1002.0,  "range": 8, "number": 2},
        "Minion":    {"cost": 3, "flags": {'fly', 'air'},            "air_dmg": 3096.0, "gnd_dmg": 3096.0, "hp": 907.2,   "range": 4, "number": 3},
        "Skeleton":  {"cost": 3, "flags": {'gnd', 'walk'},           "air_dmg": 0,      "gnd_dmg": 4000,   "hp": 600.0,   "range": 4, "number": 10},
        "Barbarian": {"cost": 3, "flags": {'gnd', 'walk'},           "air_dmg": 0,      "gnd_dmg": 1449.0, "hp": 2208.0,  "range": 5, "number": 3},
        "Dragon":    {"cost": 4, "flags": {'splash', 'fly', 'air'},  "air_dmg": 2508.0, "gnd_dmg": 2508.0, "hp": 1910.45, "range": 5, "number": 1},
        "Valkyrie":  {"cost": 4, "flags": {'splash', 'gnd', 'walk'}, "air_dmg": 0,      "gnd_dmg": 2155.0, "hp": 2097.0,  "range": 7, "number": 1},
        "Giant":     {"cost": 5, "flags": {'gnd', 'tank', 'walk'},   "air_dmg": 0,      "gnd_dmg": 674.0,  "hp": 5423.0,  "range": 7, "number": 1},
        "Wizard":    {"cost": 5, "flags": {'splash', 'walk', 'air'}, "air_dmg": 6000,   "gnd_dmg": 6000,   "hp": 1705.0,  "range": 8, "number": 1},
    }

    # Extract data from arena_data
    my_tower = arena_data["MyTower"]
    opp_troops = arena_data["OppTroops"]
    my_troops = arena_data["MyTroops"]
    hand = my_tower.deployable_troops  # List of troop names (strings)
    my_elixir = my_tower.total_elixir

    # Determine mode based on opponent troop positions
    defensive_mode = any(troop.position[1] < 50 for troop in opp_troops)
    # Check for Wizard and tank presence
    wizard_on_field = any(t.name == "Wizard" for t in my_troops)
    tank_on_field = any("tank" in troops_data[t.name]["flags"] for t in my_troops)

    # Debug output every 10 frames
    if frame_count % 10 == 0:
        print(f"Frame {frame_count}: Elixir={my_elixir}, Hand={hand}, "
              f"Mode={'Defensive' if defensive_mode else 'Offensive'}, Wizard on field={wizard_on_field}")

    best_troop = None
    best_score = -1

    if defensive_mode:
        for troop in hand:
            if troops_data[troop]["cost"] > my_elixir:
                continue
            score = 0
            for opp_troop in opp_troops:
                opp_data = troops_data[opp_troop.name]
                can_hit = (
                    ("fly" in opp_data["flags"] and "air" in troops_data[troop]["flags"]) or
                    ("walk" in opp_data["flags"] and ("gnd" in troops_data[troop]["flags"] or "air" in troops_data[troop]["flags"]))
                )
                if can_hit:
                    damage = troops_data[troop]["air_dmg"] if "fly" in opp_data["flags"] else troops_data[troop]["gnd_dmg"]
                    score += damage * (1 - opp_troop.position[1] / 100)  # Weight by proximity
            if len(opp_troops) > 1 and "splash" in troops_data[troop]["flags"]:
                score *= 1.5  # Bonus for splash against multiple enemies
            if troop == "Wizard" and not wizard_on_field:
                score *= 2  # Prioritize Wizard if none on field
            if score > best_score:
                best_score = score
                best_troop = troop
    else:  # Offensive mode
        for troop in hand:
            if troops_data[troop]["cost"] > my_elixir:
                continue
            data = troops_data[troop]
            if not tank_on_field and "tank" in data["flags"]:
                score = 10000  # High priority for tanks if none present
            else:
                score = (data["gnd_dmg"] + data["air_dmg"] + data["hp"] / 10) / data["cost"]
                if "fly" in data["flags"]:
                    score *= 1.2  # Bonus for flying troops
            if troop == "Wizard" and not wizard_on_field:
                score *= 2  # Prioritize Wizard if none on field
            if score > best_score:
                best_score = score
                best_troop = troop

    # Deploy the best troop
    if best_troop:
        x_range = (-25, 25) if "fly" in troops_data[best_troop]["flags"] else (-10, 10)
        deploy_position = (random_x(*x_range), 0)
        deploy_list.list_.append((best_troop, deploy_position))
        print(f"Deploying {best_troop} with score {best_score} at position {deploy_position}")
    # Prevent elixir leakage
    elif my_elixir >= 9 and hand:
        cheapest = min(hand, key=lambda t: troops_data[t]["cost"])
        if troops_data[cheapest]["cost"] <= my_elixir:
            deploy_position = (random_x(), 0)
            deploy_list.list_.append((cheapest, deploy_position))
            print(f"Deploying {cheapest} to prevent elixir leakage at position {deploy_position}")