import random
from collections import defaultdict, deque
from typing import Optional, Tuple, Union, cast
from risk_helper.game import Game
from risk_shared.queries.query_fortify import QueryFortify
from risk_shared.records.moves.move_fortify import MoveFortify
from risk_shared.records.moves.move_fortify_pass import MoveFortifyPass

from data_structures.bot_state import BotState
from data_structures.mapnetwork import MapNetwork

def handle_fortify(game: Game, bot_state: BotState, query: QueryFortify, mapNetwork: MapNetwork) -> Union[MoveFortify, MoveFortifyPass]:
    """At the end of your turn, after you have finished attacking, you may move a number of troops between
    any two of your territories (they must be adjacent)."""

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

    #if some troops stuck inside, move them up (from shallow to deep)
    #else check all the border nodes and see which one < enemy troops, and see if adjacent have troops, move until == enemy troops
    #else pass

    all_borders = game.state.get_all_border_territories(my_territories)
    centre = mapNetwork.get_centre()
    behind_borders =  game.state.get_all_border_territories(centre)
    max_troops_behind = 0
    troops_behind_node = None

    min_troops_ahead = 0
    troops_ahead_node = None

    for i in behind_borders:
        if mapNetwork.get_node_troops(i) > max_troops_behind:
            max_troops_behind = mapNetwork.get_node_troops(i)
            troops_behind_node = i


    if max_troops_behind > 3:
        next_to_max = list(set(mapNetwork.get_neighbors(troops_behind_node))&set(all_borders))
        for i in next_to_max:
            adj_to_this_border_node = list(set(mapNetwork.get_neighbors(i))-set(my_territories))
            for j in adj_to_this_border_node: #find the most troops that are near this border
                if mapNetwork.get_node_troops(j) > min_troops_ahead: #this is max troops in front of border
                    min_troops_ahead = mapNetwork.get_node_troops(j)
                    troops_ahead_node = i

    else:
        for i in centre:
            if mapNetwork.get_node_troops(i) > max_troops_behind:
                max_troops_behind = mapNetwork.get_node_troops(i)
                troops_behind_node = i
        list_ahead_node = mapNetwork.shortest_path_to_border(my_territories, troops_behind_node)
        if list_ahead_node:
            troops_ahead_node = list_ahead_node[1]
        

    if troops_behind_node and troops_ahead_node:
        return game.move_fortify(query, troops_behind_node, troops_ahead_node, max_troops_behind - 1)
    else:
        return game.move_fortify_pass(query)

