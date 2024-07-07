import random
from typing import Optional, Tuple, Union, cast
from risk_helper.game import Game
from risk_shared.queries.query_place_initial_troop import QueryPlaceInitialTroop
from risk_shared.records.moves.move_place_initial_troop import MovePlaceInitialTroop

from data_structures.bot_state import BotState

def handle_place_initial_troop(game: Game, bot_state: BotState, query: QueryPlaceInitialTroop) -> MovePlaceInitialTroop:
    """After all the territories have been claimed, you can place a single troop on one
    of your territories each turn until each player runs out of troops."""

    # Pick a random territory.
    my_territories = game.state.get_territories_owned_by(game.state.me.player_id)
    return game.move_place_initial_troop(query, random.sample(my_territories, 1)[0])
