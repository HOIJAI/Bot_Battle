import random
from typing import Optional, Tuple, Union, cast
from risk_helper.game import Game
from risk_shared.models.card_model import CardModel
from risk_shared.queries.query_redeem_cards import QueryRedeemCards
from risk_shared.records.moves.move_redeem_cards import MoveRedeemCards

from data_structures.bot_state import BotState

def handle_redeem_cards(game: Game, bot_state: BotState, query: QueryRedeemCards) -> MoveRedeemCards:
    """After the claiming and placing initial troops phases are over, you can redeem any
    cards you have at the start of each turn, or after killing another player."""

    # Redeem as many cards as we can.
    card_sets: list[Tuple[CardModel, CardModel, CardModel]] = []
    cards_remaining = game.state.me.cards.copy()

    if query.cause == "turn_started":
        card_set = game.state.get_card_set(cards_remaining)
        while card_set != None:
            card_sets.append(card_set)
            cards_remaining = [card for card in cards_remaining if card not in card_set]
            card_set = game.state.get_card_set(cards_remaining)

    elif query.cause == "player_eliminated":
        while len(cards_remaining) >= 5:
            card_set = game.state.get_card_set(cards_remaining)
            # According to the pigeonhole principle, we should always be able to make a set
            # of cards if we have at least 5 cards.
            assert card_set != None
            card_sets.append(card_set)
            cards_remaining = [card for card in cards_remaining if card not in card_set]
            
    
    return game.move_redeem_cards(query, [(x[0].card_id, x[1].card_id, x[2].card_id) for x in card_sets])
