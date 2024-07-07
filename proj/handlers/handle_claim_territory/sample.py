import random
from typing import Optional, Tuple, Union, cast
from risk_helper.game import Game
from risk_shared.queries.query_claim_territory import QueryClaimTerritory
from risk_shared.records.moves.move_claim_territory import MoveClaimTerritory

from data_structures.bot_state import BotState

def handle_claim_territory(game: Game, bot_state: BotState, query: QueryClaimTerritory) -> MoveClaimTerritory:
    """At the start of the game, you can claim a single unclaimed territory every turn 
    until all the territories have been claimed by players."""

    # Pick a random territory.
    unclaimed_territories = game.state.get_territories_owned_by(None)
    selected_territory = random.sample(unclaimed_territories, 1)[0]
    return game.move_claim_territory(query, selected_territory)
