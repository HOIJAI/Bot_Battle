from collections import defaultdict
import random
from typing import Optional, Tuple, Union, cast
from risk_helper.game import Game
from risk_shared.queries.query_distribute_troops import QueryDistributeTroops
from risk_shared.records.moves.move_distribute_troops import MoveDistributeTroops

from data_structures.bot_state import BotState
from data_structures.mapnetwork import MapNetwork


def handle_distribute_troops(game: Game, bot_state: BotState, query: QueryDistributeTroops, mapNetwork: MapNetwork) -> MoveDistributeTroops:
    """After redeeming cards, distribute troops across owned territories."""
    
    distributions = defaultdict(lambda: 0)
    total_troops = game.state.me.troops_remaining
    
    # Distribute matching territory bonus
    if game.state.me.must_place_territory_bonus:
        assert total_troops >= 2
        distributions[game.state.me.must_place_territory_bonus[0]] += 2
        total_troops -= 2

    # Set owner and troops for my territories
    my_territories = game.state.get_territories_owned_by(game.state.me.player_id)
    my_territories_model = [game.state.territories[x] for x in my_territories]
    for territory_id in my_territories:
        mapNetwork.set_node_owner(territory_id, 'me')
    for territory in my_territories_model:
        mapNetwork.set_node_troops(territory.territory_id, territory.troops)

    # Set owner and troops for enemy territories
    other_players = set(range(5)) - {game.state.me.player_id}
    for player_id in other_players:
        enemy_territories = game.state.get_territories_owned_by(player_id)
        enemy_territories_model = [game.state.territories[x] for x in enemy_territories]
        for territory_id in enemy_territories:
            mapNetwork.set_node_owner(territory_id, str(player_id))
        for territory in enemy_territories_model:
            mapNetwork.set_node_troops(territory.territory_id, territory.troops)



    '''game_phases'''
    game_state = len(game.state.recording) #game starts at 133
    avg = mapNetwork.get_average_troops() #average troops per players
    domination = len(mapNetwork.check_my_ownership()) + len(mapNetwork.check_ownership()) #how many continents are near conquered already
    # locate my continent

    my_base_continent = mapNetwork.calculate_continent_groups(my_territories)[0][0] #string of the name
    base_territories = list(set(my_territories)&set(mapNetwork.continents[my_base_continent])) #my territories in that base
    border_to_base = game.state.get_all_border_territories(base_territories) #those are MINE
    enemies_around_base = list(set(game.state.get_all_adjacent_territories(border_to_base))-set(my_territories))
    weakest_continents = mapNetwork.calculate_enemy_troops_by_continent() #list of tuples [('NA',0)]

    remaining_troops = total_troops
    # check if any enemy border territories have *2 troops than mine, if yes, place troops until my territories = enemies if possible
    stationed_troops = []
    for j in border_to_base:
        stationed_troops.append((j, mapNetwork.get_node_troops(j)))
    stationed_troops = sorted(stationed_troops, key=lambda x: x[1], reverse=True)

    # early game
    if avg <=30 or game_state < 300 and domination <=3:
        for i in enemies_around_base:
            enemy_troops = mapNetwork.get_node_troops(i)
            adj_nodes = mapNetwork.get_neighbors(i)
            for node, troops in stationed_troops:
                if node in adj_nodes and troops*2 <= enemy_troops and total_troops > (enemy_troops-troops):
                    distributions[node] += (enemy_troops-troops)
                    remaining_troops -= (enemy_troops-troops)
                    break
                break
            break

        for i in weakest_continents:
            for node, troops in stationed_troops:
                if mapNetwork.G.nodes[node]['group'] == i[0]:
                    distributions[node]+= remaining_troops
                    remaining_troops = 0
                    break
                break
            break

    # mid game
    elif avg <=60 or game_state < 550 and domination <=4:
        if my_base_continent[1]!=1: #continent not conquered
            for i in enemies_around_base:
                enemy_troops = mapNetwork.get_node_troops(i)
                adj_nodes = mapNetwork.get_neighbors(i)
                for node, troops in stationed_troops:
                    if node in adj_nodes and troops*2 <= enemy_troops and total_troops > (enemy_troops-troops):
                        distributions[node] += (enemy_troops-troops)
                        remaining_troops -= (enemy_troops-troops)
                        break
                    break
                break
        

        for i in weakest_continents:
            for node, troops in stationed_troops:
                if mapNetwork.G.nodes[node]['group'] == i[0]:
                    distributions[node]+= remaining_troops
                    remaining_troops = 0
                    break
                break
            break
        # check all continents total troops except mine: -> place troops towards weakest continent, weakest troops, from the strongest border if adjacent

    else:
#       #doomstack
        #find enemies with most territories owned, if nearby, all in troops to the weakest link if my border node + all troops = *2 troops 
        # else all in troops towards the nearby weakest continent
        for i in weakest_continents:
            for j in border_to_base:
                stationed_troops = []
                for k in border_to_base:
                    stationed_troops.append((k, mapNetwork.get_node_troops(k)))
                stationed_troops = sorted(stationed_troops, key=lambda x: x[1], reverse=True)

                if mapNetwork.G.nodes[j]['group'] == i[0]:
                    distributions[stationed_troops[0][0]]+=total_troops
                break
            break
    
    

    return game.move_distribute_troops(query, distributions)