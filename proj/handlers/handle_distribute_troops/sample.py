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
    
    '''game_phases'''
    game_state = len(game.state.recording) #game starts at 133
    avg = mapNetwork.get_average_troops() #average troops per players
    domination = len(mapNetwork.check_my_ownership()) + len(mapNetwork.check_ownership()) #how many continents are near conquered already
    # locate my continent

    my_borders = game.state.get_all_border_territories(my_territories)
    weakest_continent = mapNetwork.find_optimal_paths_to_continents(my_borders)
    my_bridges = (set(mapNetwork.bridges_list())&set(my_territories))

    weak_bridge = None
    least_troops_bridge = float('inf')
    for i in my_bridges:
        if mapNetwork.get_node_troops(i) < least_troops_bridge:
            weak_bridge = i
            least_troops_bridge = mapNetwork.get_node_troops(i)
    
    strong_border = None
    most_troops_border = 0
    for i in my_borders:
        if mapNetwork.get_node_troops(i) >most_troops_border:
            strong_border = i
            most_troops_border = mapNetwork.get_node_troops(i)

    # check if any enemy border territories have *2 troops than mine, if yes, place troops until my territories = enemies if possible

    for i in weakest_continent:
        troops_needed = i[2] * 2 - mapNetwork.get_node_troops(i[1][0])
        if i[2] !=0 and troops_needed > 0: 
            if total_troops > troops_needed: #0 is when I own the entire continent
            # troops_needed = i[2] * 2 - mapNetwork.get_node_troops(i[1][0])
            # if total_troops >= troops_needed:
                distributions[i[1][0]] += troops_needed
                total_troops -= troops_needed
            else: # Distribute total troops if not enough for 2*i[2]
                distributions[i[1][0]] += total_troops
                total_troops = 0
            
    
    if total_troops !=0:
        if my_bridges != None: # The leftover troops will be put some territory (we don't care)
            distributions[weak_bridge] += total_troops
        else:
            distributions[strong_border] += total_troops

    return game.move_distribute_troops(query, distributions)