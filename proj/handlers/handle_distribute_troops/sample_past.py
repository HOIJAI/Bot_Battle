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
    game_state = len(game.state.recording) #game starts at 133
    avg = mapNetwork.get_average_troops() #average troops per players
    domination = len(mapNetwork.check_my_ownership()) + len(mapNetwork.check_ownership()) #how many continents are near conquered already

    # early game
    # if avg <=30 or game_state < 300 and domination <=3:
        # locate my continent
        # check if any enemy border territories have *2 troops than mine, if yes, place troops until my territories = enemies
        # check if I own a continent, if not, place troops in the continents
        # if yes, check adjacent continent troops, place leftover troops towards the weakest continent, weakest troops from the strongest border in continent
        

    # mid game
    if avg <=60 or game_state < 550 and domination <=4:
        border_territories = game.state.get_all_border_territories(my_territories)

        # if len(border_territories) >=3:
        #     border_territories = random.sample(border_territories, 1)[:3]
        if len(border_territories)!=0:
            if len(border_territories) >=3:
                border_territories = random.sample(border_territories, 1)[:3]
            troops_per_territory = total_troops // len(border_territories)

            for territory in border_territories:
                distributions[territory] += troops_per_territory
                total_troops-= troops_per_territory
        
        distributions[border_territories[random.randint(0,len(border_territories)-1)]] += total_troops

    # if avg <=60 or game_state <550 and domination <=4:
    #      #doomstack (complex placer rn)
    #     border_territories = game.state.get_all_border_territories(my_territories)
    #     my_territories = game.state.get_territories_owned_by(game.state.me.player_id)
    #     weakest_players = sorted(game.state.players.values(), key=lambda x: sum(
    #         [game.state.territories[y].troops for y in game.state.get_territories_owned_by(x.player_id)]
    #     ))

    #     for player in weakest_players:
    #         bordering_enemy_territories = set(game.state.get_all_adjacent_territories(border_territories)) & set(game.state.get_territories_owned_by(player.player_id))
    #         if len(bordering_enemy_territories) > 0:
    #             print("my territories", [game.state.map.get_vertex_name(x) for x in my_territories])
    #             print("bordering enemies", [game.state.map.get_vertex_name(x) for x in bordering_enemy_territories])
    #             print("adjacent to target", [game.state.map.get_vertex_name(x) for x in game.state.map.get_adjacent_to(list(bordering_enemy_territories)[0])])
    #             selected_territory = list(set(game.state.map.get_adjacent_to(list(bordering_enemy_territories)[0])) & set(my_territories))[0]
    #             distributions[selected_territory] += total_troops
    #             break
        #check if I own continents, if enemies > me -> if double enemies >5 put till >5, else put till >enemy+1
        # attack africa or na, whichever is closer
        #else defend bridges
    # late game
    
    else:
#         #doomstack (complex placer rn)
        border_territories = game.state.get_all_border_territories(my_territories)
        my_territories = game.state.get_territories_owned_by(game.state.me.player_id)
        strongest_players = sorted(game.state.players.values(), key=lambda x: sum(
            [game.state.territories[y].troops for y in game.state.get_territories_owned_by(x.player_id)]
        ), reverse = True)

        for player in strongest_players:
            bordering_enemy_territories = set(game.state.get_all_adjacent_territories(border_territories)) & set(game.state.get_territories_owned_by(player.player_id))
            if len(bordering_enemy_territories) > 0:
                print("my territories", [game.state.map.get_vertex_name(x) for x in my_territories])
                print("bordering enemies", [game.state.map.get_vertex_name(x) for x in bordering_enemy_territories])
                print("adjacent to target", [game.state.map.get_vertex_name(x) for x in game.state.map.get_adjacent_to(list(bordering_enemy_territories)[0])])
                selected_territory = list(set(game.state.map.get_adjacent_to(list(bordering_enemy_territories)[0])) & set(my_territories))[0]
                distributions[selected_territory] += total_troops
                break

    return game.move_distribute_troops(query, distributions)