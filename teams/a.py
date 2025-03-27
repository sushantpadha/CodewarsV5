import random
from teams.helper_function import Troops, Utils

team_name = "sinchpokadi"
troops = [
    Troops.knight, Troops.musketeer, Troops.wizard, Troops.valkyrie,
    Troops.minion, Troops.dragon, Troops.skeleton, Troops.giant
]
deploy_list = Troops([])
team_signal = ""

def random_x(min_val=-25, max_val=25):
    return random.randint(min_val, max_val)

def deploy(arena_data: dict):
    deploy_list.list_ = []
    logic(arena_data)
    return deploy_list.list_, team_signal

def logic(arena_data: dict):
    global team_signal
    global deploy_list
    deploy_list = Troops([])
    my_tower = arena_data["MyTower"]
    opp_troops = arena_data["OppTroops"]
    my_elixir = my_tower.total_elixir
    #track_opponent_state(opp_troops, my_elixir, my_tower.game_timer)
    
    enemy_types = {troop.name for troop in opp_troops}
    
    air_threats = {"Minion", "Dragon", "Balloon", "Musketeer"}
    ground_threats = {"Barbarian", "Knight", "Prince", "SkeletonArmy"}
    preferred_counter = "air" if len(enemy_types & ground_threats) > len(enemy_types & air_threats) else "ground"
    
    bonus = 3
    best_troop = None
    best_score = -1
    
    deployable = my_tower.deployable_troops
    troop_data = {
        Troops.balloon: {"score": 3, "category": "air", "name": "Balloon"},
        Troops.musketeer: {"score": 6, "category": "ground", "name": "Musketeer"},
        Troops.wizard: {"score": 7, "category": "ground", "name": "Wizard"},
        Troops.valkyrie: {"score": 7, "category": "ground", "name": "Valkyrie"},
        Troops.minion: {"score": 4, "category": "air", "name": "Minion"},
        Troops.dragon: {"score": 5, "category": "air", "name": "Dragon"},
        Troops.skeleton: {"score": 1, "category": "ground", "name": "Skeleton"},
        Troops.barbarian: {"score": 5, "category": "ground", "name": "Barbarian"},
        Troops.archer: {"score": 4, "category": "ground", "name": "Archer"},
        Troops.knight: {"score": 6, "category": "ground", "name": "Knight"},
        Troops.giant: {"score": 5, "category": "ground", "name": "Giant"},
        Troops.prince: {"score": 7, "category": "ground", "name": "Prince"}
    }
    num = 0
    for troop in arena_data["OppTroops"]:
        if troop.position[1] <= 40 :
            num+=1
            if Troops.skeleton in my_tower.deployable_troops:
                deploy_list.list_.append((Troops.skeleton, troop.position))
            if Troops.knight in my_tower.deployable_troops:
                deploy_list.list_.append((Troops.knight, troop.position))
            if Troops.dragon in my_tower.deployable_troops:
                deploy_list.list_.append((Troops.dragon, troop.position))
        

        if troop.name == "Musketeer" and troop.position[1] <= 55:
            if Troops.skeleton in my_tower.deployable_troops:
                deploy_list.list_.append((Troops.skeleton, troop.position))
            else :
                deploy_list.list_.append((Troops.valkyrie, troop.position))
            
        if troop.name == "Valkyrie" and troop.position[1] <= 60:
            if Troops.minion in my_tower.deployable_troops:
                deploy_list.list_.append((Troops.minion, troop.position))

        if troop.name == "Balloon" and troop.position[1] <= 60:
            if Troops.wizard in my_tower.deployable_troops:
                deploy_list.list_.append((Troops.wizard, troop.position))
            if Troops.minion in my_tower.deployable_troops:
                deploy_list.list_.append((Troops.minion, troop.position))
            else :
                deploy_list.list_.append((Troops.dragon, troop.position))


        if troop.name == "Minion" and troop.position[1] <= 55:
            if Troops.wizard in my_tower.deployable_troops:
                deploy_list.list_.append((Troops.wizard, troop.position))
            else :
                deploy_list.list_.append((Troops.dragon, troop.position))
                deploy_list.list_ = [(t, p) for t, p in deploy_list.list_ if t != Troops.skeleton]


        if troop.name == "Giant" or troop.name == "Prince" and troop.position[1] <= 55:
            if Troops.skeleton in my_tower.deployable_troops:
                deploy_list.list_.append((Troops.skeleton, troop.position))
            if Troops.knight in my_tower.deployable_troops:
                deploy_list.list_.append((Troops.knight, troop.position))

        
        if troop.name == "Dragon" or troop.name == "Wizard" or troop.name == "Valkyrie" and troop.position[1] <= 60:
            if Troops.skeleton in my_tower.deployable_troops:
                deploy_list.list_ = [(t, p) for t, p in deploy_list.list_ if t != Troops.skeleton]  # ✅ removes all skeletons safely
        
        if troop.name == "Wizard" and troop.position[1] <= 55:
            if Troops.valkyrie in my_tower.deployable_troops:
                deploy_list.list_.append((Troops.valkyrie, troop.position))
            if Troops.knight in my_tower.deployable_troops:
                deploy_list.list_.append((Troops.knight, troop.position))
            deploy_list.list_ = [(t, p) for t, p in deploy_list.list_ if t != Troops.minion or Troops.skeleton]
                
    if my_elixir >= 8 or num > 4 :
        deploy_list.list_.append((Troops.giant, (random_x(-15, 15), 15)))
        
    if len(opp_troops) > 2 :
        for troop in troops:
            if troop not in deployable:
                continue
            base = troop_data[troop]["score"]
            cat = troop_data[troop]["category"]
            score = base + (bonus if preferred_counter and cat == preferred_counter else 0)
            if score > best_score:
                best_score = score
                best_troop = troop
    
        if best_troop is not None:
            selected_category = troop_data[best_troop]["category"]
            deploy_position = (random_x(-10, 10), 0) if selected_category == "ground" else (random_x(-15, 15), 0)
            deploy_list.list_.append((best_troop, deploy_position))