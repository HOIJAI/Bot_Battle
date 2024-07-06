from collections import defaultdict
import random
from typing import Optional, Tuple, Union, cast
from risk_helper.game import Game
from risk_shared.queries.query_distribute_troops import QueryDistributeTroops
from risk_shared.records.moves.move_distribute_troops import MoveDistributeTroops

from data_structures.bot_state import BotState

def handle_distribute_troops(game: Game, bot_state: BotState, query: QueryDistributeTroops) -> MoveDistributeTroops:
    """After you redeem cards (you may have chosen to not redeem any), you need to distribute
    all the troops you have available across your territories. This can happen at the start of
    your turn or after killing another player.
    """

    distributions = defaultdict(lambda: 0)
    total_troops = game.state.me.troops_remaining
    # Distribute our matching territory bonus.
    if len(game.state.me.must_place_territory_bonus) != 0:
        assert total_troops >= 2
        distributions[game.state.me.must_place_territory_bonus[0]] += 2
        total_troops -= 2

    # Distribute all our troops to a single random territory.
    my_territories = game.state.get_territories_owned_by(game.state.me.player_id)
    distributions[random.sample(my_territories, 1)[0]] += total_troops
    return game.move_distribute_troops(query, distributions)