from typing import Optional, Tuple, Union, cast
from risk_helper.game import Game
from risk_shared.queries.query_attack import QueryAttack
from risk_shared.records.moves.move_attack import MoveAttack
from risk_shared.records.moves.move_attack_pass import MoveAttackPass

from data_structures.bot_state import BotState
from data_structures.mapnetwork import MapNetwork

def handle_attack(game: Game, bot_state: BotState, query: QueryAttack, mapNetwork: MapNetwork) -> Union[MoveAttack, MoveAttackPass]:
    """After the troop phase of your turn, you may attack any number of times until you decide to
    stop attacking (by passing). After a successful attack, you may move troops into the conquered
    territory. If you eliminated a player you will get a move to redeem cards and then distribute troops."""

    #####################
    # Update mapNetwork #
    #####################
    player_list = list(range(5))
    other_players = list(set(player_list) - {game.state.me.player_id})

    my_territories = game.state.get_territories_owned_by(game.state.me.player_id)
    my_territories_model = [game.state.territories[x] for x in my_territories]
    #get all the information into the map
    for i in my_territories:
        mapNetwork.set_node_owner(i,'me')
    for i in my_territories_model:
        mapNetwork.set_node_troops(i.territory_id, i.troops)

    for i in other_players:
        enemy_territories = game.state.get_territories_owned_by (i)
        enemy_territories_model = [game.state.territories[x] for x in enemy_territories]
        for j in enemy_territories:
            mapNetwork.set_node_owner(j, str(i))
        for j in enemy_territories_model:
            mapNetwork.set_node_troops(j.territory_id, j.troops)


    ##################
    # Find continent #
    ##################
    strategy = "" # either "secure_continent" or "attack"

    my_borders = game.state.get_all_border_territories(my_territories)
    weakest_continent = mapNetwork.find_optimal_paths_to_continents(my_borders)
    for continent, node_list, troops_num in weakest_continent:
        # get the first continent that is not fully owned
        if troops_num != 0:
            continent_to_attack = continent
            if len(node_list) == 1: #im already in the continent:
                strategy = "secure_continent"
            else:
                strategy = "attack"
            break
    
    min_troops_needed_to_conquer = mapNetwork.get_enemy_troops_in_continent(continent_to_attack)

    my_borders = game.state.get_all_border_territories(my_territories)
    max_troops = 0
    best_node = -1
    path = []

    if strategy == "secure_continent":
        # Algorithm choosing best border
        # Best border is chosen with the following criteria
        #   if border is in continent:
        #       select the one with highest troops
        #   if border is outside continent:
        #       select the one with highest troops after subtracting the troops needed to reach target_continent
        for border_node in my_borders:
            troops_in_border = mapNetwork.get_node_troops(border_node)
            result = mapNetwork.shortest_path_from_node_to_continent(border_node, continent_to_attack)
            min_troops_needed_to_reach_target_continent = result[0]
            troops_when_reaching_continent = troops_in_border - min_troops_needed_to_reach_target_continent
            if troops_when_reaching_continent > max_troops:
                max_troops = troops_in_border
                best_node = border_node
                path = result[1]


    elif strategy == "attack":
        # Check if we can fully occupied, if not then skip round
        max_diff = 0
        for border_node in my_borders:
            troops_in_border = mapNetwork.get_node_troops(border_node)
            if troops_in_border < min_troops_needed_to_conquer:
                continue
            result = mapNetwork.shortest_path_from_node_to_continent(border_node, continent_to_attack)
            min_troops_needed_to_reach_target_continent = result[0]
            if troops_in_border < (min_troops_needed_to_conquer + min_troops_needed_to_reach_target_continent):
                continue
            difference = troops_in_border - min_troops_needed_to_conquer - min_troops_needed_to_reach_target_continent
            if difference > max_diff:
                max_diff = difference
                best_node = border_node
                path = result[1]

    ##########################
    # Skip when no best node #
    ##########################
    # Other possible trategies when no best node
    # 1. Sabotage continents owner
    # 2. Do nothing to save troops
    # 3. Join forces with other occupied territories
    if best_node == -1:
        return game.move_attack_pass(query)

    ##########
    # Attack #
    ##########
    my_land = len(mapNetwork.check_my_ownership())
    attack_stage_late = my_land >= 2

    # if outside of the continent, follow the path returned from dijkstra
    if len(path) > 1:
        attacker = path[0]
        target = path[1]
        if attack_stage_late:
            if game.state.territories[attacker].troops >= 5 and game.state.territories[target].troops*2 <= game.state.territories[attacker].troops:
                return game.move_attack(query, attacker, target, min(3, game.state.territories[attacker].troops - 1))
        else:
            if game.state.territories[attacker].troops >= 4 and (game.state.territories[target].troops*1.5 + 1.5)//1 <= game.state.territories[attacker].troops:
                return game.move_attack(query, attacker, target, min(3, game.state.territories[attacker].troops - 1))

    # if starting from within the target continent 
    continent_enemies = list(set(mapNetwork.continents[continent_to_attack]) - set(my_territories))
    next_bridge = list(set(mapNetwork.bridges_list())&set(continent_enemies))
    best_path = []
    for i in next_bridge:
        path = []
        path = mapNetwork.find_path_through_enemies(best_node, i, continent_enemies)
        if len(path) > len(best_path):
            best_path = path

    if len(best_path) > 1:
        attacker = best_node
        target = best_path[1]
        if attack_stage_late:
            if game.state.territories[attacker].troops >= 5 and game.state.territories[target].troops*2 <= game.state.territories[attacker].troops:
                return game.move_attack(query, attacker, target, min(3, game.state.territories[attacker].troops - 1))
        else:
            if game.state.territories[attacker].troops >= 4 and (game.state.territories[target].troops*1.5 + 1.5)//1 <= game.state.territories[attacker].troops:
                return game.move_attack(query, attacker, target, min(3, game.state.territories[attacker].troops - 1))
    else:
        adjacent_enemies = list(set(mapNetwork.get_neighbors(best_node))&set(continent_enemies))
        adjacent_enemies = sorted(adjacent_enemies, key=lambda x: game.state.territories[x].troops, reverse=True)
        attacker = best_node
        for target in adjacent_enemies:
            if attack_stage_late:
                if game.state.territories[attacker].troops >= 5 and game.state.territories[target].troops*2 <= game.state.territories[attacker].troops:
                    return game.move_attack(query, attacker, target, min(3, game.state.territories[attacker].troops - 1))
            else:
                if game.state.territories[attacker].troops >= 4 and (game.state.territories[target].troops*1.5 + 1.5)//1 <= game.state.territories[attacker].troops:
                    return game.move_attack(query, attacker, target, min(3, game.state.territories[attacker].troops - 1))



    return game.move_attack_pass(query)