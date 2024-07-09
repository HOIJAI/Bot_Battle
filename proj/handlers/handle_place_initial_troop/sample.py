import random
from typing import Optional, Tuple, Union, cast
from risk_helper.game import Game
from risk_shared.queries.query_place_initial_troop import QueryPlaceInitialTroop
from risk_shared.records.moves.move_place_initial_troop import MovePlaceInitialTroop

from data_structures.bot_state import BotState
from data_structures.mapnetwork import MapNetwork

def handle_place_initial_troop(game: Game, bot_state: BotState, query: QueryPlaceInitialTroop, mapNetwork: MapNetwork) -> MovePlaceInitialTroop:
    """After all the territories have been claimed, you can place a single troop on one
    of your territories each turn until each player runs out of troops."""

    my_territories = game.state.get_territories_owned_by(game.state.me.player_id)
    my_territories_model = [game.state.territories[x] for x in my_territories]
    for i in my_territories:
        mapNetwork.set_node_owner(i,'me')
    for i in my_territories_model:
        mapNetwork.set_node_troops(i.territory_id, i.troops)
    
    cluster = mapNetwork.get_5cluster()
    centre = mapNetwork.get_centre()
    # We will place troops along the territories on our border/cluster if no nexus.
    border_territories = list(set(cluster)-set(centre))

    min_troops_territory=None
    border_territory_models = [game.state.territories[x] for x in border_territories]
   
    #This function checks for nearby territories and then strengthen the troops if nearby are increasing their numbers
    weak_list = []
    for i in border_territory_models:
        adjacent_to_border = game.state.get_all_adjacent_territories([i.territory_id])
        enemies_adjacent = list(set(adjacent_to_border) - set(my_territories))
        enemies_model = [game.state.territories[x] for x in enemies_adjacent]
        for k in enemies_model:
            if i.troops < k.troops:
                weak_list.append(i.territory_id)
    
    next_list = []
    outer_border = list(set(my_territories) - set(cluster))
    outer_models = [game.state.territories[x] for x in outer_border]
    for i in outer_models:
        adjacent_to_border = game.state.get_all_adjacent_territories([i.territory_id])
        enemies_adjacent = list(set(adjacent_to_border) - set(my_territories))
        enemies_model = [game.state.territories[x] for x in enemies_adjacent]
        for k in enemies_model:
            if i.troops < k.troops:
                next_list.append(i.territory_id)

    if weak_list:
        min_troops_territory = random.sample(weak_list, 1)[0]

    elif next_list:
        min_troops_territory = random.sample(next_list, 1)[0]

    else:
        min_troops_territory_model = max(border_territory_models, key=lambda x: x.troops)
        min_troops_territory = min_troops_territory_model.territory_id

    return game.move_place_initial_troop(query, min_troops_territory)

