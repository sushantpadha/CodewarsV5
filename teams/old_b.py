from teams.helper_function import Troops, Utils

team_name = "leviOsa"
troops = [
    Troops.giant,
    Troops.musketeer,
    Troops.wizard,
    Troops.archer,
    Troops.knight,
    Troops.minion,
    Troops.skeleton,
    Troops.valkyrie,
]
deploy_list = Troops([])

# format: Opptroop____, Opptroop___, Opptroop, ..., N
# no. of _ = cycles before it appears in opp deck
# N = opp. elixir
team_signal = ",10"


def deploy(arena_data: dict):
    """
    DON'T TEMPER DEPLOY FUCNTION
    """
    deploy_list.list_ = []
    logic(arena_data)
    return deploy_list.list_, team_signal


def logic(arena_data: dict):
    global team_signal
    
    # maintain data from documentation
    # https://tulip-cone-606.notion.site/Documentation-1ad881a58b9a80d39450d4198553a90a#1b0881a58b9a80978eade96e27373697
    troop_data = {
        # troop_name:     [elixir,]
        Troops.archer:    [3,],
        Troops.minion:    [3,],
        Troops.knight:    [3,],
        Troops.skeleton:  [3,],
        Troops.dragon:    [4,],
        Troops.valkyrie:  [4,],
        Troops.musketeer: [4,],
        Troops.giant:     [5,],
        Troops.prince:    [5,],
        Troops.barbarian: [3,],
        Troops.balloon:   [5,],
        Troops.wizard:    [5,],
    }
    
    my_tower = arena_data["MyTower"]
    my_troops = arena_data["MyTroops"]
    opp_troops = arena_data["OppTroops"]
    
    elixir = float(team_signal.split(",")[-1])
    
    print(f"{my_tower.total_elixir} == {elixir}")
    
    troop = my_tower.deployable_troops[0]
    troop_elixir = troop_data[troop][0]
    
    elixir += 0.05
    
    if my_tower.total_elixir > troop_elixir:
        deploy_list.list_.append((troop, (-25, 0)))
        elixir -= troop_elixir
    # deploy_list.list_.append((arena_data["MyTower"].deployable_troops[1], (25, 0)))
    
    team_signal = ",".join(team_signal.split(",")[:-1]) + str(elixir)