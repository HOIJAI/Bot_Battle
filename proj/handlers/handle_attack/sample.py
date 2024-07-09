from typing import Optional, Tuple, Union, cast
from risk_helper.game import Game
from risk_shared.queries.query_attack import QueryAttack
from risk_shared.records.moves.move_attack import MoveAttack
from risk_shared.records.moves.move_attack_pass import MoveAttackPass

from data_structures.bot_state import BotState
from data_structures.mapnetwork import MapNetwork

def handle_attack(game: Game, bot_state: BotState, query: QueryAttack, mapNetwork: MapNetwork) -> Union[MoveAttack, MoveAttackPass]:
    """After the troop phase of your turn, you may attack any number of times until you decide to
    stop attacking (by passing). After a successful attack, you may move troops into the conquered
    territory. If you eliminated a player you will get a move to redeem cards and then distribute troops."""

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


    '''game_phase'''
    gamestate = len(game.state.recording) #game starts at 133
    avg = mapNetwork.get_average_troops() #average troops per players
    domination = len(mapNetwork.check_my_ownership()) + len(mapNetwork.check_ownership()) #how many continents are near conquered already

    # early game
    if avg <=30 or gamestate < 300 or domination <=2:
        print('k')
    # mid game
    elif avg <=60 or gamestate <550 or domination <=4:
        print('k')
    # late game
    else:
        print('k')


    
    # Attack anyone.
    def attack_if_possible(territories: list[int]):
        for candidate_target in territories:
            candidate_attackers = list(set(game.state.map.get_adjacent_to(candidate_target)) & set(my_territories))
            for candidate_attacker in candidate_attackers:
                if game.state.territories[candidate_attacker].troops > 1:
                    return game.move_attack(query, candidate_attacker, candidate_target, min(3, game.state.territories[candidate_attacker].troops - 1))

    bordering_territories = game.state.get_all_adjacent_territories(my_territories)
    attack = attack_if_possible(bordering_territories)
    if attack:
        return attack
    else:
        return game.move_attack_pass(query)