import random
from typing import Optional, Tuple, Union, cast
from risk_helper.game import Game
from risk_shared.queries.query_claim_territory import QueryClaimTerritory
from risk_shared.records.moves.move_claim_territory import MoveClaimTerritory

from data_structures.bot_state import BotState
from data_structures.mapnetwork import MapNetwork

def handle_claim_territory(game: Game, bot_state: BotState, query: QueryClaimTerritory, mapNetwork: MapNetwork) -> MoveClaimTerritory:
    """setup nexus as much as possible (centre has the most connection, surrounding has the least connections) - look for centre first
        if no more places in adjacent, pick least links"""
    all_territories = list(range(42))
    # Pick a random territory.
    unclaimed_territories = game.state.get_territories_owned_by(None)
    my_territories = game.state.get_territories_owned_by(game.state.me.player_id)
    claimed_territories = list(set(all_territories)-set(unclaimed_territories) - set(my_territories))

    for i in claimed_territories:
        mapNetwork.set_node_owner(i, 'enemies')
    for i in my_territories:
        mapNetwork.set_node_owner(i,'me')

    nexus_list = mapNetwork.nexus()
    if len(nexus_list)!=0:
        curr_nexus = nexus_list[0]
    #first selection
    if len(unclaimed_territories) > 37:
        selected_territory = curr_nexus

    #next 4 selections surrounding the nexus, if got broken choose a new nexus
    elif 37 >= len(unclaimed_territories) > 17:
        adjacent_territories = game.state.get_all_adjacent_territories(my_territories)
        claimed = 0
        for i in adjacent_territories:
            if mapNetwork.get_node_owner(i) != None and mapNetwork.get_node_owner(i) != 'me':
                claimed +=1
        
        available = list(set(unclaimed_territories) & set(adjacent_territories))
        #choose the ones with the least link (easier to defend)
        if len(available)!=0 : #and len(available) + claimed >= len(adjacent_territories)-1
            # Calculate the number of connections for each node in the available list
            links = {i: len(mapNetwork.get_neighbors(i)) for i in available}
            # Find the node with the least links
            selected_territory = min(links, key=lambda k: links[k])
        #else find a new nexus since the current one is compromised
        elif len(available) + claimed < 2:
            selected_territory = nexus_list[0]
        else:
            selected_territory = sorted(unclaimed_territories, key=lambda x: len(game.state.map.get_adjacent_to(x)), reverse=True)[0]

    #just choose the random ones at the end
    else:
        adjacent_territories = game.state.get_all_adjacent_territories(my_territories)
        available = list(set(unclaimed_territories) & set(adjacent_territories))
        if len(available) != 0:

            # We will pick the one with the most connections to our territories
            # this should make our territories clustered together a little bit.
            def count_adjacent_friendly(x: int) -> int:
                return len(set(my_territories) & set(game.state.map.get_adjacent_to(x)))

            selected_territory = sorted(available, key=lambda x: count_adjacent_friendly(x), reverse=True)[0]
        
        # Or if there are no such territories, we will pick just an unclaimed one with the greatest degree.
        else:
            selected_territory = sorted(unclaimed_territories, key=lambda x: len(game.state.map.get_adjacent_to(x)), reverse=True)[0]
    
    return game.move_claim_territory(query, selected_territory)
