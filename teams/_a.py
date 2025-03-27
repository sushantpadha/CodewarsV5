import random
import math
from teams.helper_function import Troops, Utils
# from collections import Counter

team_name = "avengers"
troops = [
    Troops.wizard, Troops.minion, Troops.archer, Troops.musketeer,
    Troops.dragon, Troops.skeleton, Troops.valkyrie, Troops.barbarian
]
deploy_list = Troops([])
team_signal = "h, Prince, Knight, Barbarian, Princess"

def random_x(min_val=-25, max_val=25):
    return random.randint(min_val, max_val)
def get_troop_damage(my_troops, troop_name):
    for troop in my_troops:
        if troop.name == troop_name:
            return troop.damage
    return None  # Return None if troop is not found
def safe_from_wizard(my_tower, opp_troops):
    """
    Check if the Wizard is far enough from my_tower to deploy a low-cost troop.
    Assumes each troop has attributes 'name' and 'position'.
    """
    # Filter opponent troops for Wizards only.
    wizards = [troop for troop in opp_troops if troop.name.strip() == "Wizard"]
    
    # Return True if no Wizard is found.
    if not wizards:
        return True

    # Find the wizard with the minimum distance from my_tower.
    closest_wizard = min(wizards, key=lambda t: distance(t.position, my_tower.position))
    return distance(closest_wizard.position, my_tower.position) > 40
def closest_target(my_tower, opp_troops):
    # Detremine the closest troop to my my_tower within a distance of 45
    closest_troop = None
    closest_distance = 45      # Maximum distance to consider
    for troop in opp_troops:        
        dist = distance(my_tower.position, troop.position)
        if dist < closest_distance:
            closest_distance = dist
            closest_troop = troop
    return closest_troop
def safe(my_tower,opp_troops):
    #check if no troop within 40 of my tower
    for troop in opp_troops:
        if distance(troop.position, my_tower.position) < 40:
            return False
    return True
def closest_target_dist(my_tower, opp_troops):
    # Find the distance of the tower to the closest opp troop
    closest_distance = 100
    for troop in opp_troops:    
        dist = distance(my_tower.position, troop.position)
        if dist < closest_distance:
            closest_distance = dist
    return closest_distance
def distance(pos1, pos2):
    """Compute Euclidean distance between two points."""
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)
def my_closest_troop_pos(my_troopsi,mytroop,my_tower):
    # Find the closest wizard to my tower
    closest_distance = 1000
    closest_troop = (0,25)
    for troop in my_troopsi:
        if troop.position[1]<25: 
            if troop.name == mytroop:
                dist = distance(troop.position, my_tower.position)
                if dist < closest_distance:
                    closest_distance = dist
                    closest_troop = troop.position
    return closest_troop
def continue_deploying_troops(my_tower, my_troops, deploy_list, deploy_area):
    """
    Deploy troops until the total elixir is less than 8 or no Wizard is close to my_tower.
    Assumes each troop has attributes 'name' and 'position'.
    """
    # Check if the total elixir is less than 8.
    
    
    # Deploy a low-cost troop if no Wizard is close to my_tower.
    if "Valkyrie" in my_tower.deployable_troops and my_tower.total_elixir >=4:
        deploy_list.list_.append(("Valkyrie", (random_x(-23,23),25)))
        my_tower.total_elixir -= 4
    elif "Minion" in my_tower.deployable_troops and my_tower.total_elixir >=3:
        deploy_list.list_.append(("Minion", my_closest_troop_pos(my_troops, "Dragon", my_tower)))
        my_tower.total_elixir -= 3
    
    elif "Musketeer" in my_tower.deployable_troops and my_tower.total_elixir >=4:
        deploy_list.list_.append(("Musketeer", (random_x(-23,23),25)))
        my_tower.total_elixir -= 4    
    elif "Archer" in my_tower.deployable_troops and my_tower.total_elixir >=3:
        deploy_list.list_.append(("Archer", my_closest_troop_pos(my_troops, "Skeleton", my_tower)))
        my_tower.total_elixir -= 3    
    elif "Skeleton" in my_tower.deployable_troops and my_tower.total_elixir >=3:
        deploy_list.list_.append(("Skeleton", my_closest_troop_pos(my_troops, "Wizard", my_tower)))
        my_tower.total_elixir -= 3
    elif "Barbarian" in my_tower.deployable_troops and my_tower.total_elixir >=3:
        deploy_list.list_.append(("Barbarian", (random_x(-23,23),25)))
        my_tower.total_elixir -= 3
    elif "Knight" in my_tower.deployable_troops and my_tower.total_elixir >=3:
        deploy_list.list_.append("Knight", (random_x(-23,23),25))
        my_tower.total_elixir -= 3

def try_priorities(my_tower, priorities,target_pos=None):
    """
    Deploy troops based on a list of priorities.
    """
    troops_data= Troops.troops_data
    tpos= my_tower.position
    if target_pos:
        tpos = target_pos
    for troop in priorities:
        if troop in my_tower.deployable_troops and my_tower.total_elixir >=troops_data[troop].elixir:
            deploy_list.list_.append((troop, tpos))
            my_tower.total_elixir -= troops_data[troop].elixir
            return
    
    
def get_closest_wizard(pos, opp_troops):
    """
    Return the opponent Wizard troop that is closest to your tower.
    Assumes each troop has attributes 'name' and 'position'.
    """
    # Filter opponent troops for Wizards only.
    wizards = [troop for troop in opp_troops if troop.name.strip() == "Wizard"]
    
    # Return None if no Wizard is found.
    if not wizards:
        return None

    # Find the wizard with the minimum distance from my_tower.
    closest_wizard = min(wizards, key=lambda t: distance(t.position, pos))
    return closest_wizard
def get_dynamic_bonus(my_tower, troop, fps=10, base_bonus=2):
    """
    Compute a bonus that increases with game time and available elixir,
    but scales down for high-cost troops when elixir is low.

    - total_game_frames: total frames in 3 minutes (fps * 180).
    - time_ratio: fraction of game time elapsed.
    - elixir_ratio: current elixir relative to maximum (assumed 10).
    - troop_elixir_factor: computed as min(1, my_tower.total_elixir / troop.elixir), 
      but not less than 0.3.
    
    The dynamic bonus is:
         base_bonus * (1 + 0.5 * time_ratio + 0.5 * elixir_ratio) * troop_elixir_factor
    """
    cost_map = {
        "Archer":    3, "Minion": 3, "Knight": 3, "Skeleton": 3,
        "Valkyrie":  4, "Musketeer": 4, "Giant": 5, "Balloon": 5,
        "Wizard":    5, "Dragon": 4, "Prince": 5, "Barbarian": 3
    }
    total_game_frames = fps * 180  # total frames in 3 minutes
    time_ratio = my_tower.game_timer / total_game_frames if hasattr(my_tower, "game_timer") else 0.5
    elixir_ratio = my_tower.total_elixir / 10.0  # assuming maximum elixir is 10
    # Compute the troop elixir factor: if current elixir is low relative to troop cost, bonus is scaled down.
    if troop is None:
        raise ValueError("Troop name is None, but it should never be.")
    
    troop_cost = cost_map[troop.strip()]  # Strip spaces if needed

    # *Compute troop elixir factor*
    troop_elixir_factor = min(2, 1 + my_tower.total_elixir / troop_cost)  
    troop_elixir_factor = max(0.3, troop_elixir_factor)  # Ensure min factor is 0.3

    return base_bonus * (1 + 0.5 * time_ratio + 0.5 * elixir_ratio) + troop_elixir_factor
def deploy(arena_data: dict):
    """
    DON'T TEMPER DEPLOY FUNCTION
    """
    deploy_list.list_ = []
    logic(arena_data)
    return deploy_list.list_, team_signal
def logic(arena_data: dict):
    global team_signal
    fps=10
    # Unpack arena data
    my_tower = arena_data["MyTower"]
    opp_troops = arena_data["OppTroops"]
    opp_tower = arena_data["OppTower"]
    my_troops = arena_data["MyTroops"]
    cost_map = {
        "Archer":    3, "Minion": 3, "Knight": 3, "Skeleton": 3,
        "Valkyrie":  4, "Musketeer": 4, "Giant": 5, "Balloon": 5,
        "Wizard":    5, "Dragon": 4, "Prince": 5, "Barbarian": 3
    }
    max_health = 7032  # Fixed maximum health for opponent tower

    # -------------------------------------------------------------------------
    # 1. Update team_signal (kept as a string) for opponent troop history.
    #    We update it using current opponent troops.
    # -------------------------------------------------------------------------
    for troop in opp_troops:
        name = troop.name.strip()
        if name not in team_signal:
            team_signal += ", " + name if team_signal else name
            if len(team_signal) > 200:
                tokens = team_signal.split(", ")
                tokens.pop(0)
                team_signal = ", ".join(tokens)

    # -------------------------------------------------------------------------
    # 2. Compute frequencies for ONLY CURRENT opponent troops using a dictionary.
    # -------------------------------------------------------------------------
    current_opp_counts = {}
    for troop in opp_troops:
        name = troop.name
        current_opp_counts[name] = current_opp_counts.get(name, 0) + 1

    # -------------------------------------------------------------------------
    # 3. Define base scores for each troop type.
    # -------------------------------------------------------------------------
    base_scores = {
        "Archer":    4,
        "Minion":    3,
        "Knight":    3,
        "Skeleton":  2,
        "Valkyrie":  4,
        "Musketeer": 3,
        "Giant":     5,
        "Balloon":   5,
        "Wizard":    5,
        "Dragon":    5,
        "Prince":    5,
        "Barbarian": 3
    }
    
    # -------------------------------------------------------------------------
    # 4. Iterate Over Deployable Troops and Compute Their Scores
    # Each candidate: (troop_name, score, troop_elixir)
    # -------------------------------------------------------------------------
    scored_troops = []
    combo_cost = cost_map["Dragon"] + cost_map["Barbarian"]  # e.g., 4 + 3 = 7

# Check if the opponent troop is a Wizard and if we have enough elixir for the combo.
    ARENA_HEIGHT = 100
    ARENA_WIDTH = 50
    arena_display_size = (ARENA_WIDTH, ARENA_HEIGHT)
    # deploy_area: (min_x, max_x, min_y, max_y)
    deploy_area = (0, arena_display_size[0], arena_display_size[1]/2, arena_display_size[1])  
    # Assume cost_map, opp_troops, my_tower, and deploy_list are defined
#     combo_cost = cost_map["Dragon"] + cost_map["Barbarian"]  # Example: 4 + 3 = 7
    # Check for a Wizard among opponent troops.

    closest_wiz = get_closest_wizard(my_tower.position, opp_troops)
    if closest_wiz :
        wizard_pos = closest_wiz.position

    if closest_wiz and distance (my_tower.position, wizard_pos) < 60:
        # favtroop ="Wizard","Skeleton","Barbarian"
        # for i in range(0,3):
        #     if favtroop[i]  in my_tower.deployable_troops :
        #         deploy_list.list_.append((favtroop[i], my_tower.position))

            

        # if my_tower.total_elixir < 3:
        #     return  # Not enough elixir; wait for a later frame.
        
        # Get the first Wizard's position (assumed attribute 'position').

        # Calculate a nearby target with a small random offset.
        # offset = (random_x(-1, 1), random_x(-1, 1))
        offset=(0,0)
        target_pos = (wizard_pos[0] + offset[0], wizard_pos[1] + offset[1])
    
        # Clamp the target position within the deploy area.
        # min_x, max_x, min_y, max_y = deploy_area
        # target_x = min(max(target_pos[0], min_x), max_x)
        # target_y = min(max(target_pos[1], min_y), max_y)
        # target_pos = (target_x, target_y)
        try_priorities(my_tower, ["Wizard","Skeleton","Minion","Valkyrie","Dragon","Barbarian","Musketeer","Knight"],wizard_pos)
        # deploy_list.list_.append(("Barbarian", target_pos))
    # elif closest_wiz and distance (my_tower.position, wizard_pos) >=70:
    #     if my_tower.total_elixir >=5 and "Wizard" in my_tower.deployable_troops:
    #         deploy_list.list_.append(("Wizard", (0,0)))
    #         my_tower.total_elixir-=5
    #     elif my_tower.total_elixir >=4 and "Dragon" in my_tower.deployable_troops:
    #         deploy_list.list_.append(("Dragon", (0,0)))
    #         my_tower.total_elixir-=4     
    #     elif my_tower.total_elixir >=4 and "Musketeer" in my_tower.deployable_troops:
    #         deploy_list.list_.append(("Musketeer", (0,0)))
    #         my_tower.total_elixir-=4    
        
    cost_map = {
        "Archer":    3, "Minion": 3, "Knight": 3, "Skeleton": 3,
        "Valkyrie":  4, "Musketeer": 4, "Giant": 5, "Balloon": 5,
        "Wizard":    5, "Dragon": 4, "Prince": 5, "Barbarian": 3
    }
    
    if "Wizard" in my_tower.deployable_troops and closest_target_dist(my_tower, opp_troops) >= 45 and my_tower.total_elixir <5:
        return
    if "Wizard" in my_tower.deployable_troops and my_tower.total_elixir >=5:
        deploy_list.list_.append(("Wizard", my_tower.position))
        my_tower.total_elixir-=5
    elif "Dragon" in my_tower.deployable_troops and my_tower.total_elixir >=4:
        pos= my_closest_troop_pos(my_troops, "Wizard", my_tower)
        if pos != (0,25): 
            deploy_list.list_.append(("Dragon", pos))
        else:
            deploy_list.list_.append(("Dragon", my_tower.position))
            my_tower.total_elixir-=4    
    elif my_tower.total_elixir ==10 and   "Wizard" in my_tower.deployable_troops and "Dragon" in my_tower.deployable_troops:
        deploy_list.list_.append(("Wizard", my_tower.position))
        deploy_list.list_.append(("Dragon",  my_tower.position))

        my_tower.total_elixir-=10
    
    

    
    if safe_from_wizard(my_tower, opp_troops):
        tar =closest_target(my_tower, opp_troops)
        if tar=="Dragon":

            try_priorities(my_tower, ["Wizard","Skeleton","Minion","Archer","Barbarian","Valkyrie","Musketeer"],tar.position)
        if tar:
            
            if "Archer" in my_tower.deployable_troops and my_tower.total_elixir >=3:
                deploy_list.list_.append(("Archer", tar.position))
                my_tower.total_elixir-=3
            elif "Minion" in my_tower.deployable_troops and my_tower.total_elixir >=3:
                deploy_list.list_.append(("Minion", tar.position))
                my_tower.total_elixir-=3
            elif "Knight" in my_tower.deployable_troops and my_tower.total_elixir >=3:
                deploy_list.list_.append(("Knight", tar.position))
                my_tower.total_elixir-=3
            elif "Skeleton" in my_tower.deployable_troops and my_tower.total_elixir >=3:
                deploy_list.list_.append(("Skeleton", tar.position))
                my_tower.total_elixir-=3
            elif "Dragon" in my_tower.deployable_troops and my_tower.total_elixir >=4:
                deploy_list.list_.append(("Dragon", tar.position))
                my_tower.total_elixir-=4
            elif "Valkyrie" in my_tower.deployable_troops and my_tower.total_elixir >=4:
                deploy_list.list_.append(("Valkyrie", tar.position))
                my_tower.total_elixir-=4
            elif "Barbarian" in my_tower.deployable_troops and my_tower.total_elixir >=3:
                deploy_list.list_.append(("Barbarian", tar.position))
                my_tower.total_elixir-=3    
            elif "Musketeer" in my_tower.deployable_troops and my_tower.total_elixir >=4:
                deploy_list.list_.append(("Musketeer", tar.position))
                my_tower.total_elixir-=4
                
            
            

                

            
            
        else :
            continue_deploying_troops(my_tower, my_troops, deploy_list, deploy_area)
            

                
            

    # for troop in my_tower.deployable_troops:
    #     troop_name = troop
    #     troop_elixir = cost_map.get(troop)

    #     if troop_name not in base_scores:
    #         continue

    #     score = base_scores[troop_name]
    #     # Apply base dynamic bonus weighted by current elixir and game time.
    #     score += get_dynamic_bonus(my_tower, troop, fps, 2)
        
    #     # Additional bonus conditions based on current opponent troop counts
    #     if troop_name == "Balloon" and my_tower.total_elixir >=5:
    #         target_pos = opp_tower.position
    #         a= get_closest_wizard((24,0), opp_troops)
    #         b= get_closest_wizard((-24,0), opp_troops)
    #         if a:
    #             if distance((24,0), a.position) < distance((-24,0), a.position):
    #                deploy_list.list_.append(("Balloon", (-24,0)))
    #         elif b:
    #             deploy_list.list_.append(("Balloon", (24,0)))
    #         else :
    #             deploy_list.list_.append(("Balloon", (24,0)))
    #         my_tower.total_elixir-=5
        # if troop_name == "Giant" and (current_opp_counts.get("Giant", 0) >= 1 or current_opp_counts.get("Archer", 0) >= 1):
        #     score += get_dynamic_bonus(my_tower, troop, fps, 2)
        # if troop_name == "Minion" and (current_opp_counts.get("Giant", 0) >= 1 or current_opp_counts.get("Knight", 0) >= 1):
        #     score += get_dynamic_bonus(my_tower, troop, fps, 2)
       
        # if troop_name == "Valkyrie" and (current_opp_counts.get("Barbarian", 0) >= 1 or current_opp_counts.get("Skeleton", 0) >= 1):
        #     score += get_dynamic_bonus(my_tower, troop, fps, 3)
        # if troop_name == "Musketeer" and (current_opp_counts.get("Minion", 0) >= 1 or 
        #                                   current_opp_counts.get("Balloon", 0) >= 1 or 
        #                                   current_opp_counts.get("Dragon", 0) >= 1 or 
        #                                   current_opp_counts.get("Prince", 0) >= 1):
        #     score += get_dynamic_bonus(my_tower, troop, fps, 3)
        # if troop_name == "Wizard" :
        #     score += get_dynamic_bonus(my_tower, troop, fps, 3002334444444)
        # if troop_name == "Barbarian" and (current_opp_counts.get("Wizard", 0) >= 1 or current_opp_counts.get("Dragon", 0) >= 1):
        #     score += get_dynamic_bonus(my_tower, troop, fps, 233333)
        # if troop_name == "Dragon" and (current_opp_counts.get("Skeleton", 0) >= 1):
        #     score += get_dynamic_bonus(my_tower, troop, fps, 2)
        # if troop_name == "Knight" and (current_opp_counts.get("Archer", 0) >= 1 or current_opp_counts.get("Musketeer", 0) >= 1):
        #     score += get_dynamic_bonus(my_tower, troop, fps, 2)
        # if troop_name == "Prince" and (current_opp_counts.get("Wizard", 0) >= 1):
        #     score += get_dynamic_bonus(my_tower, troop, fps, 2333)
        # Additional dynamic conditions:
        # if opp_tower.health < 0.5 * 7032 or my_tower.health > 0.8 *7032:
        #     if troop in ["Giant", "Prince", "Balloon", "Wizard"]:
        #         score += get_dynamic_bonus(my_tower, troop)
        # if current_opp_counts.get("Musketeer", 0) == 0:
        #     if troop in ["Minion", "Dragon", "Balloon"]:
        #         score += get_dynamic_bonus(my_tower, troop)
        # if my_tower.total_elixir > 6:
        #     if troop in ["Giant", "Prince", "Dragon", "Balloon"]:
        #         score += get_dynamic_bonus(my_tower, troop)
        # if (current_opp_counts.get("Minion", 0) + current_opp_counts.get("Balloon", 0) + current_opp_counts.get("Dragon", 0)) == 0:
        #     if troop in ["Minion", "Dragon", "Balloon"]:
        #         score += get_dynamic_bonus(my_tower, troop)
        # if opp_tower.health > 0.8 * 7032:
        #     if troop in ["Archer", "Knight"]:
        #         score += get_dynamic_bonus(my_tower, troop)

        # # Aggressive offense in last minute:
        # if hasattr(my_tower, "game_timer") and my_tower.game_timer > fps * 120:
        #     if my_tower.total_elixir > 4:
        #         if troop in ["Giant", "Prince", "Balloon", "Dragon", "Wizard", "Knight"]:
        #             score += get_dynamic_bonus(my_tower,troop,fps, 3000000)
        #     if opp_tower.health < 0.3 * 7032:
        #         if troop in ["Giant", "Prince", "Balloon", "Dragon", "Wizard", "Knight"]:
        #             score += get_dynamic_bonus(my_tower,troop,fps, 4000000)

        # scored_troops.append((troop, score,cost_map[troop.strip()]))

    # -------------------------------------------------------------------------
    # 5. Build Combo Candidates (each candidate is a tuple: (combo_list, combo_score, count))
    # -------------------------------------------------------------------------
    # combo_candidates = []
    # # Combo: Giant + Archer
    # if "Giant" in my_tower.deployable_troops and "Archer" in my_tower.deployable_troops:
    #     combo_score = base_scores["Giant"] + base_scores["Archer"] + get_dynamic_bonus(my_tower, 3)
    #     combo_candidates.append((["Giant", "Archer"], combo_score, 2))
    # # Combo: Dragon + Balloon
    # if "Dragon" in my_tower.deployable_troops and "Balloon" in my_tower.deployable_troops:
    #     combo_score = base_scores["Dragon"] + base_scores["Balloon"] + get_dynamic_bonus(my_tower, 3)
    #     combo_candidates.append((["Dragon", "Balloon"], combo_score, 2))
    # # Combo: Knight + Minion
    # if "Knight" in my_tower.deployable_troops and "Minion" in my_tower.deployable_troops:
    #     combo_score = base_scores["Knight"] + base_scores["Minion"] + get_dynamic_bonus(my_tower, 3)
    #     combo_candidates.append((["Knight", "Minion"], combo_score, 2))
    # # Combo: Wizard + Skeleton
    # if "Wizard" in my_tower.deployable_troops and "Skeleton" in my_tower.deployable_troops:
    #     combo_score = base_scores["Wizard"] + base_scores["Skeleton"] + get_dynamic_bonus(my_tower, 3)
    #     combo_candidates.append((["Wizard", "Skeleton"], combo_score, 2))

    # -------------------------------------------------------------------------
    # 6. Combine Individual and Combo Candidates.
    # Create a list where each element is (candidate, score, count).
    # For individuals, candidate is a string and count is 1.
    # -------------------------------------------------------------------------
    # combined_candidates = []
    # for candidate, score in scored_troops:
    #     combined_candidates.append((candidate, score, count))
    # for candidate, score, count in combo_candidates:
    #     combined_candidates.append((candidate, score, count))
    
    # # Sort combined candidates by score (highest first)
    # combined_candidates.sort(key=lambda x: x[1], reverse=True)
    
    # -------------------------------------------------------------------------
    # 7. Select Final Recommended Candidates without exceeding 4 units.
    # -------------------------------------------------------------------------
    # final_recommended = []  # This will be a list of candidates; each candidate can be a string or list.
    # total_units = 0
    # total_cost = 0
    # for candidate, score, count in combined_candidates:
    #     # Determine cost for candidate:
    #     if isinstance(candidate, list):
    #         candidate_cost = sum(cost_map.get(t, 3) for t in candidate)
    #     else:
    #         candidate_cost = cost_map.get(candidate, 3)
        
    #     # Check if adding this candidate would exceed 4 units and if we have enough elixir
    #     if total_units + count <= 4 and my_tower.total_elixir - total_cost >= candidate_cost:
    #         final_recommended.append(candidate)
    #         total_units += count
    #         total_cost += candidate_cost
    #     if total_units >= 4:
    #         break

    # -------------------------------------------------------------------------
    # 8. Deploy the Selected Candidates.
    # For combos, deploy each troop individually.
    # -------------------------------------------------------------------------
    # scored_troops.sort(key=lambda x: x[1], reverse=True)  # Sort troops by score (highest first)

    # i = 0
    # while i < len(scored_troops):
    #     best_troop, best_score, best_cost = scored_troops[i]

    #     # Check if there's enough elixir for deployment
    #     if my_tower.total_elixir >= best_cost:
    #         pos = (random_x(-25, 25), 0) if best_troop in ["Minion", "Dragon", "Balloon"] else (random_x(-10, 10), 0)
    #         deploy_list.list_.append((best_troop, pos))  # Deploy the troop
    #         break  # Stop after deploying one troop

    #     i += 1  # Move to the next troop if elixir is insufficient