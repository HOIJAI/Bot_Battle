from collections import defaultdict
import random
from typing import Optional, Tuple, Union, cast
from risk_helper.game import Game
from risk_shared.queries.query_distribute_troops import QueryDistributeTroops
from risk_shared.records.moves.move_distribute_troops import MoveDistributeTroops

from data_structures.bot_state import BotState
from data_structures.mapnetwork import MapNetwork

def handle_distribute_troops(game: Game, bot_state: BotState, query: QueryDistributeTroops, mapNetwork: MapNetwork) -> MoveDistributeTroops:
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


    #1. check if any players are close to owning continents, check any nodes next to his continent (we want to use minimum number of troops to disrupt them)
    continent_owned = mapNetwork.check_ownership() #currently its more than 3/4, can change later
    #will place troops there if adjacent to that enemy who has the most territories
    if len(continent_owned) != 0:
        for k,v in continent_owned:
            out = mapNetwork.find_max_troop_adjacent_node(k, v)
            if out != None:
                my_closet_node, node_to_attack = out
                if mapNetwork.get_node_property(node_to_attack, 'troops') <=2:
                    while mapNetwork.get_node_property(node_to_attack, 'troops') <= mapNetwork.get_node_property(node_to_attack, 'troops')*2:
                        distributions[my_closet_node]+=1
                total_troops -= distributions[my_closet_node]
    
    #2. around nexus, locate node with the greatest difference in forces on the same continent/bridges→ put more until troops num ≥ 2.5x of the opposite force

    #3. check if my continent is secured, if not, reinforce troops in border and poke (1,2), if yes, use dijkstra to find shortest path to own another continent, and start stacking on the bridge (late game)
    
    distributions[random.sample(my_territories, 1)[0]] += total_troops

    return game.move_distribute_troops(query, distributions)