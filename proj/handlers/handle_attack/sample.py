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
        territories = sorted(territories, key=lambda x: game.state.territories[x].troops, reverse=True)
        for candidate_target in territories:
            if mapNetwork.get_node_owner(candidate_target) != 'me':
                candidate_attackers = sorted(list(set(game.state.map.get_adjacent_to(candidate_target)) & set(my_territories)), key=lambda x: game.state.territories[x].troops, reverse=False)
                
                for candidate_attacker in candidate_attackers:
                    if game.state.territories[candidate_attacker].troops >= 3 and (game.state.territories[candidate_target].troops*1.2 + 2)//1 <= game.state.territories[candidate_attacker].troops:
                        # attacker_surrounding = (set(game.state.map.get_adjacent_to(candidate_attacker))-set(my_territories))
                        target_surrounding = (set(game.state.map.get_adjacent_to(candidate_target))-set(my_territories))
                        #attacker_surrounding.union
                        surrounding_enemies = list(target_surrounding)
                        surrounding_troops = []
                        
                        for i in surrounding_enemies:
                            surrounding_troops.append(mapNetwork.get_node_troops(i))
                        
                        if surrounding_troops and max(surrounding_troops) < mapNetwork.get_node_troops(candidate_attacker):
                            if game.state.territories[candidate_attacker].troops >= 4:
                                return game.move_attack(query, candidate_attacker, candidate_target, min(3, game.state.territories[candidate_attacker].troops - 1))
                        
                        elif len(surrounding_troops) == 0:
                            return game.move_attack(query, candidate_attacker, candidate_target, min(3, game.state.territories[candidate_attacker].troops - 1))
                        
    '''game_phase'''
    game_state = len(game.state.recording) #game starts after 127
    avg = mapNetwork.get_average_troops() #average troops per players
    domination = len(mapNetwork.check_my_ownership()) + len(mapNetwork.check_ownership()) #how many continents are near conquered already
    # locate my continent

    my_borders = game.state.get_all_border_territories(my_territories)
    weakest_continent = mapNetwork.find_optimal_paths_to_continents(my_borders)
    for continent, node_list, troops_num in weakest_continent:
        if troops_num != 0:
            if len(node_list)>1: #not fully conquered
                move = attack_weakest(node_list[1:])
                if move != None:
                    return move
            elif len(node_list)==1: #im already in the continent:
                continent_enemies = list(set(mapNetwork.continents[continent]) - set(my_territories))
                #should make a path such that it will end at the next bridge
                move = attack_weakest(continent_enemies)
                if move != None:
                    return move

    # if move == None:
    #     strongest_territories = sorted(my_territories, key=lambda x: game.state.territories[x].troops, reverse=False)
    #     for territory in strongest_territories:
    #         move = attack_weakest(list(set(game.state.map.get_adjacent_to(territory)) - set(my_territories)))
    #         if move != None:
    #             return move
            
    return game.move_attack_pass(query)