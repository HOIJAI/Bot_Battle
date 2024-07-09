from collections import defaultdict
import random
from typing import Optional, Tuple, Union, cast
from risk_helper.game import Game
from risk_shared.queries.query_distribute_troops import QueryDistributeTroops
from risk_shared.records.moves.move_distribute_troops import MoveDistributeTroops

from data_structures.bot_state import BotState
from data_structures.mapnetwork import MapNetwork


def handle_distribute_troops(game: Game, bot_state: BotState, query: QueryDistributeTroops, mapNetwork: MapNetwork) -> MoveDistributeTroops:
    """After redeeming cards, distribute troops across owned territories."""
    
    distributions = defaultdict(lambda: 0)
    total_troops = game.state.me.troops_remaining
    
    # Distribute matching territory bonus
    if game.state.me.must_place_territory_bonus:
        assert total_troops >= 2
        distributions[game.state.me.must_place_territory_bonus[0]] += 2
        total_troops -= 2

    # Set owner and troops for my territories
    my_territories = game.state.get_territories_owned_by(game.state.me.player_id)
    my_territories_model = [game.state.territories[x] for x in my_territories]
    for territory_id in my_territories:
        mapNetwork.set_node_owner(territory_id, 'me')
    for territory in my_territories_model:
        mapNetwork.set_node_troops(territory.territory_id, territory.troops)

    # Set owner and troops for enemy territories
    other_players = set(range(5)) - {game.state.me.player_id}
    for player_id in other_players:
        enemy_territories = game.state.get_territories_owned_by(player_id)
        enemy_territories_model = [game.state.territories[x] for x in enemy_territories]
        for territory_id in enemy_territories:
            mapNetwork.set_node_owner(territory_id, str(player_id))
        for territory in enemy_territories_model:
            mapNetwork.set_node_troops(territory.territory_id, territory.troops)



    '''game_phases'''
    gamestate = len(game.state.recording) #game starts at 133
    avg = mapNetwork.get_average_troops() #average troops per players
    domination = len(mapNetwork.check_my_ownership()) + len(mapNetwork.check_ownership()) #how many continents are near conquered already

    # early game
    if avg <=30 or gamestate < 300 or domination <=2:
        leftover_troops = 0
        #aim to dominate current continent
        #1. Check if any player owns >75% of a continent, only attack one of them at a time
        continent_owned = mapNetwork.check_ownership() #e.g.[('NA', '0')]
        if continent_owned:
            for i in continent_owned:
                # Find adjacent to min enemy node and attack if conditions met
                out = mapNetwork.find_min_troop_adjacent_node(i[0], i[1])
                if out:
                    my_closest_node, node_to_attack = out
                    min_needed = (mapNetwork.get_node_troops(node_to_attack)*2 - mapNetwork.get_node_troops(my_closest_node))
                    if total_troops - min_needed >= total_troops//4:
                        distributions[my_closest_node] += min_needed
                        total_troops -= min_needed
                break

        #check if I can own a continent/which continent im at -> if double enemies >5 put till >5, else put till >enemy+1
        my_continents = mapNetwork.check_my_ownership() #list of continent names
        # for continent in my_continents:
        #     my_nodes = list(set(my_territories) & set(mapNetwork.continents[continent])) #find my nodes in that continent
        #     my_nodes_models = [game.state.territories[x] for x in my_nodes]
        #     for i in my_nodes_models:
        #         adjacent_to_border = game.state.get_all_adjacent_territories([i.territory_id])
        #         enemies_adjacent = list(set(adjacent_to_border) - set(my_territories))
        #         enemies_model = [game.state.territories[x] for x in enemies_adjacent]
        #         for k in enemies_model:
        #             min_needed = k.troops*2
        #             if  min_needed > 5 and total_troops >= min_needed-i.troops:
        #                 distributions[i.territory_id] += min_needed-i.troops
        #                 total_troops -= min_needed
        #             elif total_troops >= k.troops+1 - i.troops:
        #                 distributions[i.territory_id] += k.troops+1 - i.troops
        #                 total_troops -= k.troops+1 - i.troops
        #             else:
        #                 continue

        #else find all the bridges I own, place troops there
        my_bridge = list(set(mapNetwork.bridges_list())&set(my_territories))
        if my_bridge:
            # if len(my_bridge) >=3:
            #     my_bridge = random.sample(my_bridge, 1)[:3]

            troops_per_territory = total_troops // len(my_bridge)
            leftover_troops = total_troops % len(my_bridge)

            for territory in my_bridge:
                distributions[territory] += troops_per_territory

        # The leftover troops will be put some territory (we don't care)
        distributions[random.sample(list(my_territories), 1)[0]] += leftover_troops

    # mid game
    elif avg <=60 or gamestate <550 or domination <=4:
        print('k')
        #check if I own continents, if enemies > me -> if double enemies >5 put till >5, else put till >enemy+1
        # attack africa or na, whichever is closer
        #else defend bridges
    # late game
    
    else:
        #doomstack (complex placer rn)
        my_territories = game.state.get_territories_owned_by(game.state.me.player_id)
        weakest_players = sorted(game.state.players.values(), key=lambda x: sum(
            [game.state.territories[y].troops for y in game.state.get_territories_owned_by(x.player_id)]
        ))

        for player in weakest_players:
            bordering_enemy_territories = set(game.state.get_all_adjacent_territories(my_territories)) & set(game.state.get_territories_owned_by(player.player_id))
            if len(bordering_enemy_territories) > 0:
                print("my territories", [game.state.map.get_vertex_name(x) for x in my_territories])
                print("bordering enemies", [game.state.map.get_vertex_name(x) for x in bordering_enemy_territories])
                print("adjacent to target", [game.state.map.get_vertex_name(x) for x in game.state.map.get_adjacent_to(list(bordering_enemy_territories)[0])])
                selected_territory = list(set(game.state.map.get_adjacent_to(list(bordering_enemy_territories)[0])) & set(my_territories))[0]
                distributions[selected_territory] += total_troops
                break

    
    # 2. Implement logic for troop distribution around nexus, bridges, etc.
        # Placeholder logic for securing continents or strategic locations
    border_territories = game.state.get_all_border_territories(
        game.state.get_territories_owned_by(game.state.me.player_id)
    )

    if len(border_territories) >=3:
        border_territories = random.sample(border_territories, 1)[:3]
    
    troops_per_territory = total_troops // len(border_territories)
    leftover_troops = total_troops % len(border_territories)

    for territory in border_territories:
        distributions[territory] += troops_per_territory

    # The leftover troops will be put some territory (we don't care)
    distributions[random.sample(border_territories, 1)[0]] += leftover_troops
    
    return game.move_distribute_troops(query, distributions)