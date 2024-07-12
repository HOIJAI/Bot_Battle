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


    def attack_weakest(territories: list[int]) -> Optional[MoveAttack]:
        # We will attack the weakest territory from the list.
        territories = sorted(territories, key=lambda x: game.state.territories[x].troops)
        for candidate_target in territories:
            candidate_attackers = sorted(list(set(game.state.map.get_adjacent_to(candidate_target)) & set(my_territories)), key=lambda x: game.state.territories[x].troops, reverse=True)
            for candidate_attacker in candidate_attackers:
                if game.state.territories[candidate_attacker].troops >= 4 and game.state.territories[candidate_target].troops <= game.state.territories[candidate_attacker].troops//2:
                    attacker_surrounding = (set(game.state.map.get_adjacent_to(candidate_attacker))-set(my_territories))
                    target_surrounding = (set(game.state.map.get_adjacent_to(candidate_target))-set(my_territories))
                    surrounding_enemies = list(attacker_surrounding.union(target_surrounding))
                    surrounding_troops = []
                    for i in surrounding_enemies:
                        surrounding_troops.append(mapNetwork.get_node_troops(i))
                    if max(surrounding_troops) < mapNetwork.get_node_troops(candidate_attacker):
                        return game.move_attack(query, candidate_attacker, candidate_target, min(3, game.state.territories[candidate_attacker].troops - 1))

    '''game_phase'''
    game_state = len(game.state.recording) #game starts at 133
    avg = mapNetwork.get_average_troops() #average troops per players
    domination = len(mapNetwork.check_my_ownership()) + len(mapNetwork.check_ownership()) #how many continents are near conquered already


    # base_territories = list(set(my_territories)&set(mapNetwork.continents[my_base_continent]))
    # all_borders = game.state.get_all_border_territories(my_territories) #my territories in that base
    # border_to_base = game.state.get_all_border_territories(base_territories) #those are MINE
    # enemies_around_base = list(set(game.state.get_all_adjacent_territories(border_to_base))-set(my_territories))
    
    # weakest_continents = mapNetwork.calculate_enemy_troops_by_continent() #list of tuples [('NA',0)]


    # early game
    if avg <=30 or game_state < 300 or domination <=2:
        strongest_territories = sorted(my_territories, key=lambda x: game.state.territories[x].troops, reverse=False)
        for territory in strongest_territories:
            move = attack_weakest(list(set(game.state.map.get_adjacent_to(territory)) - set(my_territories)))
            if move != None:
                return move
    
    # # mid game
    elif avg <=60 or game_state <800 and domination <=5: #remember to change back to elif
        strongest_territories = sorted(my_territories, key=lambda x: game.state.territories[x].troops, reverse=False)
        for territory in strongest_territories:
            move = attack_weakest(list(set(game.state.map.get_adjacent_to(territory)) - set(my_territories)))
            if move != None:
                return move
            
    # # late game
    else:
        strongest_territories = sorted(my_territories, key=lambda x: game.state.territories[x].troops, reverse=False)
        for territory in strongest_territories:
            move = attack_weakest(list(set(game.state.map.get_adjacent_to(territory)) - set(my_territories)))
            if move != None:
                return move

    return game.move_attack_pass(query)