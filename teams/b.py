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
    from collections import OrderedDict

    global team_signal
    DEBUG = 3
    
    my_tower = arena_data["MyTower"]
    my_troops = arena_data["MyTroops"]
    opp_troops = arena_data["OppTroops"]

    def pp(*args, **kwargs):
        if my_tower.game_timer % DEBUG == 0:
            _ = print(*args, **kwargs)

    # maintain data from documentation
    # https://tulip-cone-606.notion.site/Documentation-1ad881a58b9a80d39450d4198553a90a#1b0881a58b9a80978eade96e27373697

    # cost, flags, air_dmg, gnd_dmg, hp, range

    troop_data = {
        "Archer": { "cost": 3, "flags": {'air', 'walk'}, "air_dmg": 2596.0, "gnd_dmg": 2596.0, "hp": 1002.0, "range": 8 },
        "Minion": { "cost": 3, "flags": {'fly', 'air'}, "air_dmg": 3096.0, "gnd_dmg": 3096.0, "hp": 907.2, "range": 4 },
        "Knight": { "cost": 3, "flags": {'gnd', 'tank', 'walk'}, "air_dmg": 0, "gnd_dmg": 1326.0, "hp": 1938.0, "range": 7 },
        "Skeleton": { "cost": 3, "flags": {'gnd', 'walk'}, "air_dmg": 0, "gnd_dmg": 5340.0, "hp": 890.0, "range": 4 },
        "Dragon": { "cost": 4, "flags": {'splash', 'fly', 'air'}, "air_dmg": 2508.0, "gnd_dmg": 2508.0, "hp": 1710.45, "range": 5 },
        "Valkyrie": { "cost": 4, "flags": {'splash', 'gnd', 'walk'}, "air_dmg": 0, "gnd_dmg": 1755.0, "hp": 2097.0, "range": 7 },
        "Musketeer": { "cost": 4, "flags": {'air', 'walk'}, "air_dmg": 1434.0, "gnd_dmg": 1434.0, "hp": 1267.2, "range": 8 },
        "Giant": { "cost": 5, "flags": {'gnd', 'tank', 'walk'}, "air_dmg": 0, "gnd_dmg": 674.0, "hp": 5423.0, "range": 7 },
        "Prince": { "cost": 5, "flags": {'gnd', 'charge', 'walk'}, "air_dmg": 0, "gnd_dmg": 2352.0, "hp": 1920.0, "range": 5 },
        "Barbarian": { "cost": 3, "flags": {'gnd', 'walk'}, "air_dmg": 0, "gnd_dmg": 1449.0, "hp": 2208.0, "range": 5 },
        "Balloon": { "cost": 5, "flags": {'splash', 'fly', 'gnd'}, "air_dmg": 1908.0, "gnd_dmg": 1908.0, "hp": 2226.0, "range": 5 },
        "Wizard": { "cost": 5, "flags": {'splash', 'walk', 'air'}, "air_dmg": 7072.5, "gnd_dmg": 7072.5, "hp": 1705.0, "range": 8 },
    }
    
    win_cards = {"Giant", "Balloon"}
    
    # * based on deck
    my_win_card = "Giant"

    ######################## LOGIC FOR TRACKING ENEMY DECK AND ELIXIR ############################
    # sorted from least recently (part of current deck) to most recently deployed
    # opp_deck has comma seperated value, each value being "troop_name troop_uid1 troop_uid2..."
    # and last value is enemy elixir
    *opp_deck, opp_elixir = team_signal.split(",")
    opp_elixir = float(opp_elixir)
    _opp_deck = [] if opp_deck == [""] else opp_deck

    # convert opp_deck to ordered dict: troop_name: [troop_uids...] (minimum in case of multi troops)
    # * note using str everywhere
    opp_deck = OrderedDict()
    for a, *b in map(lambda x: x.split(" "), _opp_deck):
        opp_deck[a] = b


    # increment on per frame basis
    opp_elixir += 0.05
    double_elixir = False
    if my_tower.game_timer > 1200:
        double_elixir = True
        opp_elixir += 0.05
    opp_elixir = min(opp_elixir, 10)
    
    pp(f"> {opp_deck} ; {opp_elixir:.2f} ; {(my_tower.game_timer / 10 / 60):.0f}m{((my_tower.game_timer / 10) % 60):.0f}s")

    new_opp_troop = None

    # return whether troop with given name (and optional uid) is in deployed opp troops
    def check_deployed(name, uid=None):
        for opp_troop in opp_troops:
            if opp_troop.name == name and (uid is None or str(opp_troop.uid) == uid):
                return True
        return False

    # first, remove any troops previously added to opp_deck but not deployed anymore
    for seen_name in opp_deck:
        for seen_uid in opp_deck[seen_name]:
            # pp(f"checking {seen_name} {seen_uid}")
            if seen_uid == '':
                opp_deck[seen_name].remove(seen_uid)
                continue
            # if same name, uid is not deployed anymore, remove uid
            if not check_deployed(seen_name, seen_uid):
                # pp(f"> not seen, remove")
                opp_deck[seen_name].remove(seen_uid)

    # next, iterate over deployed troops and add/update
    for opp in opp_troops:
        # if troop not seen, add it (not with uid)
        if opp.name not in opp_deck:
            # pp(f"> adding {opp.name} {opp.uid} to deck")
            opp_deck[opp.name] = []

        # atp troop must be in opp deck

        # if same name, different uid is deployed, append uid and move to first
        if str(opp.uid) not in opp_deck[opp.name]:
            # pp(f"> updating {opp.name} with {opp.uid}")
            opp_deck[opp.name].append(str(opp.uid))
            opp_deck.move_to_end(opp.name)
            new_opp_troop = opp.name

    # remove opp elixir by that of new troop
    opp_elixir -= troop_data[new_opp_troop]["cost"] if new_opp_troop else 0

    ############################ SETUP ##############################

    # sanity check
    SANITY = bool(opp_elixir >= 0)
    
    opp_troop_names = [opp.name for opp in opp_troops]
    opp_cycle = [t for i,t in enumerate(opp_deck) if len(opp_deck) - i > 4]
    my_elixir = my_tower.total_elixir
    hand = my_tower.deployable_troops

    ############################## HELPER FUNCS #########################################

    # calculate score of a troop based on
    # - troop stats
    # - role preference
    def calc_score(troop, role):
        pass

    # assess threat and role preference based on:
    # - current deployment
    # - elixir diff
    # - cards in cycle
    def assess_threat():
        pass

    # determine optimal deployment position based on:
    # - threat
    # - troop
    # - role pref
    def optimal_position(threat, troop, role):
        pass
    # ! if enemy has wizard, deploy farther
    # ! try to distract away

    ################################## CHOOSE TROOP ####################################

    # for troop in deployable check and set

    # determine best position
    
    # Predefined win cards (troops that can break enemy towers)
    # win_cards = {"Balloon", "Prince", "Wizard"}

    # Weights for threat calculation and troop scoring
    THREAT_HP_SCALING = 1/6
    
    CYCLE_THREAT_SCALING = 1/3
    
    CYCLE_THREAT_ELIXIR_SCALING = 1/5
    
    DOUBLE_ELIXIR_SCALING = 0.8
    
    THREAT_WEIGHT_AIR = 1.4  # air attack capability
    THREAT_WEIGHT_GND = 1.0  # gnd attack capability
    THREAT_WEIGHT_FLY = 1.0  # air hp
    THREAT_WEIGHT_WALK = 1.2  # gnd hp
    
    ELIXIR_WEIGHT = 0.5  # bonus if you have extra elixir
    
    AIR_THREAT_THRESHOLD_MOD = 9_000
    GND_THREAT_THRESHOLD_MOD = 11_000
    
    AIR_THREAT_THRESHOLD_HIGH = 12_000
    GND_THREAT_THRESHOLD_HIGH = 14_000
    
    MY_ELIXIR_THRESHOLD = 4
    OPP_ELIXIR_THRESHOLD = 3
    ELIXIR_DIFF_THRESHOLD = 2
    
    WIN_COUNTER_THRESHOLDs = {
        "Giant": 10_000,
        "Balloon": 10_000
    }
    
    EARLY_GAME_TICKS = 30 * 10  # 30 seconds
    
    # Weights for troop scoring (can be tuned based on empirical performance)
    SCORE_WEIGHTS = {
        "attack": {"dmg": 1.5, "range": 20, "hp": 0.5, "cost": 1.0},
        "defense": {"dmg": 0.5, "range": 10, "hp": 1.5, "splash": 50, "cost": 1.0},
        "neutral": {"dmg": 1.0, "range": 15, "hp": 1.0, "cost": 1.0},
    }
    
    # ! temporary
    win_counter = 0

    def assess_threat_level():
        """
        Detailed threat assessment that splits air and ground threat.
        Considers:
        - Deployed enemy troops: separate summing for air-capable and ground-capable units.
        - Upcoming enemy cycle (weigh these less, since they are not yet on field).
        - Elixir difference (extra elixir gives you potential to push).
        
        Returns:
        - threat_air: computed air threat score.
        - threat_ground: computed ground threat score.
        """
        def compute_threats(troop_list):
            air = 0  # air attack capability
            gnd = 0  # gnd attack capability
            fly = 0  # air hp
            walk = 0  # gnd hp
            for t in troop_list:
                if t not in troop_data:
                    continue
                flags, air_dmg, gnd_dmg, hp, cost = troop_data[t]["flags"], troop_data[t]["air_dmg"], troop_data[t]["gnd_dmg"], troop_data[t]["hp"], troop_data[t]["cost"]
                
                gnd += gnd_dmg
                if "air" in flags:
                    air += air_dmg
                
                if "walk" in flags:
                    walk += hp
                elif "fly" in flags:
                    fly += hp
                    
            return air, gnd, fly, walk

        # Threat from currently deployed enemy troops (full weight)
        air_deployed, gnd_deployed, fly_deployed, walk_deployed = compute_threats(opp_troop_names)
        
        # Threat from enemy cycle (half weight, as they are not yet in play)
        # should scale (slowly) with opp elixir
        air_cycle, gnd_cycle, fly_cycle, walk_cycle = compute_threats(opp_cycle)
        
        cycle_factor = CYCLE_THREAT_SCALING * (1 + opp_elixir * CYCLE_THREAT_ELIXIR_SCALING)
    
        air_cycle *= cycle_factor
        gnd_cycle *= cycle_factor
        fly_cycle *= cycle_factor
        walk_cycle *= cycle_factor

        threat_air = (air_deployed + air_cycle) * THREAT_WEIGHT_AIR  # air attack capability (relevant for def)
        threat_gnd = (gnd_deployed + gnd_cycle) * THREAT_WEIGHT_GND  # gnd attack capability (relevant for def)
        threat_fly = (fly_deployed + fly_cycle) * THREAT_WEIGHT_FLY  # air hp (relevant for off)
        threat_walk = (walk_deployed + walk_cycle) * THREAT_WEIGHT_WALK  # gnd hp (relevant for off)

        # Incorporate elixir advantage: if you have more elixir, enemy threat is comparatively less dangerous.
        elixir_diff = my_elixir - opp_elixir
        if double_elixir:
            elixir_diff *= DOUBLE_ELIXIR_SCALING  # dampen the impact in double elixir mode
            
            
        # ensure non zero threat levels
        eps = 10

        threat_air = max(threat_air - (elixir_diff * ELIXIR_WEIGHT), eps)
        threat_gnd = max(threat_gnd - (elixir_diff * ELIXIR_WEIGHT), eps)
        threat_fly = max(threat_fly - (elixir_diff * ELIXIR_WEIGHT), eps)
        threat_walk = max(threat_walk - (elixir_diff * ELIXIR_WEIGHT), eps)
        
        threat_win = False
        for i in win_cards:
            if i in opp_troop_names:
                threat_win = True
                
                # if already deployed sufficient counter for win troop then stop doing so
                if win_counter > WIN_COUNTER_THRESHOLDs[i]:
                    threat_win = False

        pp(f"Air threat: {threat_air:.2f} | Ground threat: {threat_gnd:.2f} | Fly threat: {threat_fly:.2f} | Walk threat: {threat_walk:.2f}")
        
        return threat_air, threat_gnd, threat_fly, threat_walk, threat_win


    # def determine_role(threat_air, threat_ground):
    #     """
    #     Determine the overall role:
    #     - 'defense' if either threat is high or if you lack a win card.
    #     - 'attack' if threats are low, enemy is weak, and you hold a win card.
    #     - 'neutral' for early game conditions (e.g., low elixir or overall low threat).
        
    #     For this example:
    #     - High threat is defined as either threat component above 6.
    #     - Early game is assumed if my_elixir < 5.
    #     """
    #     mod_threat = threat_air > AIR_THREAT_THRESHOLD_MOD or threat_ground > GND_THREAT_THRESHOLD_MOD
    #     high_threat = threat_air > AIR_THREAT_THRESHOLD_HIGH or threat_ground > GND_THREAT_THRESHOLD_HIGH
    #     win_card_in_hand = (my_win_card in hand)
    #     win_card_deployed = (my_win_card in my_troops)
        
    #     role = "NEUTRAL"
        
    #     # ATTACK if low threat, has win card and elixir => deploy win troop
    #     if not mod_threat and win_card_in_hand and my_elixir > MY_ELIXIR_THRESHOLD:
    #         role = "ATTACK"
    #     # DEFENSE if not
    #     else:
    #         role = "DEFENSE"
        
    #     # NEUTRAL if low on elixir or insufficient info on enemy deck
    #     if my_elixir < MY_ELIXIR_THRESHOLD and my_tower.game_timer < EARLY_GAME_TICKS:
    #         role = "NEUTRAL"
        
    #     # OFFENSE if threat is low or mod and (enemy low on elixir OR win card is on ground)
    #     if not high_threat and (opp_elixir < OPP_ELIXIR_THRESHOLD or win_card_deployed):
    #         role = "OFFENSE"
        
    #     pp(f"Determined role: {role} (has win card: {win_card_in_hand}, my_elixir: {my_elixir:.2f})")
    #     return role


    def determine_role(threat_air, threat_gnd, threat_fly, threat_walk, threat_win):
        """
        Determines the overall strategy role and attack/movement preferences based on threats.
        
        Returns:
        - role (str): "NEUTRAL", "ATTACK", "OFFENSE", or "DEFENSE"
        - defense_pref (float): Preference for air (0.0 = full ground, 1.0 = full air)
        - attack_pref (float): Preference for targeting air (0.0 = full ground dmg, 1.0 = full air dmg)
        - target_win (bool): Whether to continue countering the enemy win condition
        """
        # threat_air  - air attack capability (relevant for def)
        # threat_gnd  - gnd attack capability (relevant for def)
        # threat_fly  - air hp (relevant for off)
        # threat_walk - gnd hp (relevant for off)
        
        # 0 → prefer ground troops for defense, 1 → prefer flying troops for defense
        defense_pref = threat_gnd / (threat_air + threat_gnd)
        
        # 0 → prioritize gnd dmg, 1 → prioritize air dmg
        attack_pref = threat_fly / (threat_fly + threat_walk)

        # Determine role based on threats and elixir
        moderate_threat = threat_air > AIR_THREAT_THRESHOLD_MOD or threat_gnd > GND_THREAT_THRESHOLD_MOD
        high_threat = threat_air > AIR_THREAT_THRESHOLD_HIGH or threat_gnd > GND_THREAT_THRESHOLD_HIGH

        win_card_in_hand = my_win_card in hand
        win_card_deployed = my_win_card in my_troops

        role = "NEUTRAL"

        # ATTACK if low threat and win card and sufficient elixir
        if not moderate_threat and win_card_in_hand and my_elixir > MY_ELIXIR_THRESHOLD:
            role = "ATTACK"
        # DEFENSE if high threat and or not win card
        elif high_threat or not win_card_in_hand:
            role = "DEFENSE"
        # NEUTRAL if early game or too little elixir (implied that threat is not high)
        elif my_elixir < MY_ELIXIR_THRESHOLD and my_tower.game_timer < EARLY_GAME_TICKS:
            role = "NEUTRAL"
        # OFFENSE if threat is not high (implied) and enemy low on elixir or we have win card deployed
        elif opp_elixir < OPP_ELIXIR_THRESHOLD or win_card_deployed:
            role = "OFFENSE"

        pp(f"Role: {role}, Defense Pref: {defense_pref:.2f}, Attack Pref: {attack_pref:.2f}")
        
        return role, defense_pref, attack_pref


    def calculate_troop_score(troop_name, role, troop_data, weights=SCORE_WEIGHTS):
        """
        Calculate a score for a troop based on its stats and the role.
        Uses weighted contributions from:
        - Damage potential (average of ground and air damage)
        - Range (beneficial for attack, less so for defense)
        - Hit points (more valuable on defense)
        - Splash damage bonus if applicable (for defense)
        - Cost normalization (lower cost is favorable)
        """
        if troop_name not in troop_data:
            return 0

        data = troop_data[troop_name]
        cost = data["cost"]
        hp = data["hp"]
        range_ = data["range"]
        dmg = (data["gnd_dmg"] + data["air_dmg"]) / 2
        splash_bonus = 50 if 'splash' in data["flags"] else 0

        w = weights.get(role, weights["neutral"])
        # Compute score as weighted sum, normalized by cost
        if role == "attack":
            score = (dmg * w["dmg"] + range_ * w["range"] + hp * w["hp"]) / cost
        elif role == "defense":
            score = (hp * w["hp"] + splash_bonus + range_ * w["range"] + dmg * w["dmg"]) / cost
        else:  # neutral
            score = (dmg * w["dmg"] + range_ * w["range"] + hp * w["hp"]) / cost

        pp(f"Troop {troop_name}: cost {cost}, hp {hp}, dmg {dmg:.2f}, range {range_} -> score: {score:.2f} (role: {role})")
        return score


    def find_attack_deployment_spot():
        """
        For attack, choose a spot with:
        - Least enemy resistance: assume areas with lower enemy troop density.
        - Maximum support: areas near allied support or in range of enemy tower.
        
        Here we simulate by scoring candidate positions.
        Assume enemy tower at (100,50), and support improves as you get closer.
        Candidate positions are represented as (x, y) coordinates.
        """
        # Simulated candidate positions
        candidate_positions = [(60, 40), (70, 50), (80, 50), (90, 60), (75, 45)]
        best_score = -float("inf")
        best_pos = None
        for pos in candidate_positions:
            # Heuristic: closer to enemy tower (100,50) gives higher support but may increase enemy resistance.
            dist_to_enemy = ((pos[0]-100)**2 + (pos[1]-50)**2) ** 0.5
            # Assume enemy resistance increases with proximity to enemy defensive positions.
            resistance = max(0, 100 - dist_to_enemy*2)
            # Support bonus: higher for positions closer to enemy tower but with lower resistance.
            score = (100 - dist_to_enemy) - resistance
            # A simple heuristic can be adjusted; here we want max support and minimal enemy presence.
            if score > best_score:
                best_score = score
                best_pos = pos
        pp(f"Selected attack deployment position: {best_pos} with score {best_score:.2f}")
        return best_pos


    def find_defense_deployment_spot(chosen_troop):
        """
        For defense, if the chosen troop is not a Giant or Balloon (which target buildings),
        deploy where it can distract enemy troops while protecting your tower.
        
        Otherwise, if it is a Giant or Balloon, deploy closer to the enemy tower to target buildings.
        
        Here we simulate by choosing between two positions:
        - General defense (distracting): near your tower at (20,50)
        - Building attack: near enemy tower at (80,50)
        """
        if chosen_troop in {"Giant", "Balloon"}:
            pos = (80, 50)
        else:
            pos = (20, 50)
        pp(f"Selected defense deployment position for {chosen_troop}: {pos}")
        return pos


    def main(hand, opp_troop_names, opp_deck, my_elixir, opp_elixir, double_elixir, troop_data):
        # 1. Detailed threat assessment
        threat_air, threat_ground = assess_threat_level(opp_troop_names, opp_deck, my_elixir, opp_elixir, troop_data, double_elixir)
        
        # 2. Determine role (attack, defense, neutral)
        role = determine_role(threat_air, threat_ground, hand, my_elixir)
        
        # 3. Calculate score for each troop in your hand
        troop_scores = {}
        for troop in hand:
            troop_scores[troop] = calculate_troop_score(troop, role, troop_data)
        
        sorted_troops = sorted(troop_scores.items(), key=lambda x: x[1], reverse=True)
        best_troop = sorted_troops[0][0] if sorted_troops else None
        pp("Troop scores (best to worst):")
        for t, s in sorted_troops:
            pp(f"  {t}: {s:.2f}")
        
        # 4 & 5. Determine optimal deployment position based on role
        if role == "attack":
            deploy_position = find_attack_deployment_spot()
        elif role == "defense":
            deploy_position = find_defense_deployment_spot(best_troop)
        else:
            # For neutral play, deploy at a balanced position (midfield)
            deploy_position = (50, 50)
            pp(f"Neutral deployment position selected: {deploy_position}")
        
        decision = {
            "role": role,
            "threat": {"air": threat_air, "ground": threat_ground},
            "troop_scores": troop_scores,
            "best_troop": best_troop,
            "deploy_position": deploy_position
        }
        return decision
    
    air_threat, gnd_threat = assess_threat_level()
    role = determine_role(air_threat, gnd_threat)

    deploy_list.list_.append((my_tower.deployable_troops[0], (-25, 0)))

    ############################### UPDATE GLOBAL VAR ################################

    team_signal = (
        ",".join(k + " " + " ".join(v) for k, v in opp_deck.items()) + f",{opp_elixir:.3f}"
    )
