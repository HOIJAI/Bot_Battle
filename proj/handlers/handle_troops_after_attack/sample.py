import random
from typing import Optional, Tuple, Union, cast
from risk_helper.game import Game
from risk_shared.queries.query_troops_after_attack import QueryTroopsAfterAttack
from risk_shared.records.moves.move_troops_after_attack import MoveTroopsAfterAttack
from risk_shared.records.moves.move_attack import MoveAttack
from risk_shared.records.record_attack import RecordAttack

from data_structures.bot_state import BotState
from data_structures.mapnetwork import MapNetwork

def handle_troops_after_attack(game: Game, bot_state: BotState, query: QueryTroopsAfterAttack, mapNetwork: MapNetwork) -> MoveTroopsAfterAttack:
    """After conquering a territory in an attack, you must move troops to the new territory."""

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

    # First we need to get the record that describes the attack, and then the move that specifies
    # which territory was the attacking territory.
    record_attack = cast(RecordAttack, game.state.recording[query.record_attack_id])
    move_attack = cast(MoveAttack, game.state.recording[record_attack.move_attack_id])


    behind = move_attack.attacking_territory
    attacked = move_attack.defending_territory

    # Get neighbors of the attacking territory, excluding the just-attacked territory
    adj = list(set(mapNetwork.get_neighbors(behind)) - set([attacked]) - set(my_territories))
    # adj = mapNetwork.get_neighbors(behind)
    # Find the adjacent enemy territory with the most troops
    most_troops = 1
    for i in adj:
        if mapNetwork.get_node_troops(i) > most_troops:
            most_troops = mapNetwork.get_node_troops(i)

    troops_available = game.state.territories[move_attack.attacking_territory].troops

    # Determine the number of troops to move based on the available troops and adjacent enemy troops
    if most_troops >= troops_available-3:
        if most_troops*2 > troops_available-1:
            num_of_troops = (2 if troops_available ==3 else 3)  # only move 3 troops ahead or 2 if conquered
        else:
            num_of_troops = troops_available-1
    else:
        num_of_troops = troops_available - most_troops


    return game.move_troops_after_attack(query, num_of_troops)

