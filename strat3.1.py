from collections import defaultdict, deque
import random
from typing import Optional, Tuple, Union, cast
from risk_helper.game import Game
from risk_shared.models.card_model import CardModel
from risk_shared.queries.query_attack import QueryAttack
from risk_shared.queries.query_claim_territory import QueryClaimTerritory
from risk_shared.queries.query_defend import QueryDefend
from risk_shared.queries.query_distribute_troops import QueryDistributeTroops
from risk_shared.queries.query_fortify import QueryFortify
from risk_shared.queries.query_place_initial_troop import QueryPlaceInitialTroop
from risk_shared.queries.query_redeem_cards import QueryRedeemCards
from risk_shared.queries.query_troops_after_attack import QueryTroopsAfterAttack
from risk_shared.queries.query_type import QueryType
from risk_shared.records.moves.move_attack import MoveAttack
from risk_shared.records.moves.move_attack_pass import MoveAttackPass
from risk_shared.records.moves.move_claim_territory import MoveClaimTerritory
from risk_shared.records.moves.move_defend import MoveDefend
from risk_shared.records.moves.move_distribute_troops import MoveDistributeTroops
from risk_shared.records.moves.move_fortify import MoveFortify
from risk_shared.records.moves.move_fortify_pass import MoveFortifyPass
from risk_shared.records.moves.move_place_initial_troop import MovePlaceInitialTroop
from risk_shared.records.moves.move_redeem_cards import MoveRedeemCards
from risk_shared.records.moves.move_troops_after_attack import MoveTroopsAfterAttack
from risk_shared.records.record_attack import RecordAttack
from risk_shared.records.types.move_type import MoveType
import numpy as np
import networkx as nx


# Appended content from other files

# data_structures/bot_state.py

# We will store our enemy in the bot state.
class BotState():
    def __init__(self):
        self.enemy: Optional[int] = None

# data_structures/mapnetwork.py

class MapNetwork:
    def __init__(self):
        self.G = nx.Graph()

        # Add nodes from 0 to 41 with default attributes
        self.G.add_nodes_from(list(range(42)), troops=0, owner=None)

        # Add edges
        edges = [
            (0,1), (0,5), (0,21), (1,5), (1,6), (1,8), (2,8), (2,3), (2,30),
            (3,2), (3,8), (3,6), (3,7), (4,5), (4,6), (4,7), (4,10), (5,0),
            (5,1), (5,6), (5,4), (6,1), (6,5), (6,4), (6,7), (6,3), (6,8),
            (7,3), (7,4), (7,6), (9,10), (9,11), (9,12), (9,15), (10,4),
            (10,9), (10,12), (11,12), (11,9), (11,15), (11,13), (11,14),
            (12,10), (12,9), (12,11), (12,14), (13,11), (13,14), (13,15),
            (13,34), (14,12), (14,11), (14,13), (14,16), (14,22), (15,9),
            (15,11), (15,13), (15,36), (16,14), (16,26), (16,17), (16,18),
            (16,22), (17,16), (17,18), (17,26), (17,25), (17,23), (17,24),
            (18,16), (18,17), (18,22), (18,24), (19,25), (19,21), (19,23),
            (19,27), (20,23), (20,21), (21,27), (21,20), (21,19), (24,17),
            (24,18), (24,40), (25,26), (25,27), (25,19), (25,17), (28,29),
            (28,31), (29,30), (29,36), (29,31), (29,28), (30,2), (30,31),
            (30,29), (32,36), (32,33), (32,37), (33,34), (33,35), (33,32),
            (33,37), (34,36), (34,13), (34,33), (35,37), (35,33), (38,39),
            (38,41), (39,41), (40,24), (40,41), (40,39)
        ]
        self.G.add_edges_from(edges)

        # Define continent groups
        self.NA = [8, 3, 2, 6, 1, 0, 7, 5, 4]
        self.SA = [30, 31, 29, 28]
        self.EU = [14, 11, 10, 9, 12, 15, 13]
        self.AF = [35, 32, 34, 33, 36, 37]
        self.AS = [19, 23, 24, 21, 20, 26, 16, 22, 25, 17, 18, 27]
        self.AU = [40, 41, 39, 38]

        self.continents = {'NA': self.NA, 'SA': self.SA, 'EU': self.EU, 'AF': self.AF, 'AS': self.AS, 'AU': self.AU}

        # Assign 'group' attribute to nodes based on continents
        for group, nodes in self.continents.items():
            for node in nodes:
                self.G.nodes[node]['group'] = group

    #copy the values from the engine to our map
    def set_node_troops(self, node, value):
        self.G.nodes[node]['troops'] = value
    
     #copy the values from the engine to our map
    def set_node_owner(self, node, value):
        self.G.nodes[node]['owner'] = value
    
    #get the properties of the territory
    def get_node_troops(self, node):
        return self.G.nodes[node]['troops']
    
    def get_node_owner(self, node):
        return self.G.nodes[node]['owner']
    
    def get_average_troops(self):
        all_territories = list(range(42))
        sum_troops = 0
        alive = set()
        for i in all_territories:
            sum_troops += self.get_node_troops(i)
            alive.add(self.get_node_owner(i))
        avg = sum_troops/len(alive)
        return int(avg)

    #find all the nodes that have bridges that connect between territories
    def bridges_list(self):
        # Find nodes connected to another continent
        connected_to_another_continent = []
        for u, v in self.G.edges():
            if self.G.nodes[u]['group'] != self.G.nodes[v]['group']:
                connected_to_another_continent.append(u)
                connected_to_another_continent.append(v)

        connected_to_another_continent = list(set(connected_to_another_continent))
        return connected_to_another_continent
    
    def nexus(self):
        nodes_with_none_owner = [n for n, attr in self.G.nodes(data=True) if attr.get('owner') is None]
        
        # Calculate the number of nodes in each continent
        continent_node_counts = {continent: len(nodes) for continent, nodes in self.continents.items()}
        
        node_scores = []
        
        for node in nodes_with_none_owner:
            node_degree = self.G.degree(node) # type: ignore
            continent = self.G.nodes[node].get('group')
            continent_size = continent_node_counts[continent]

            surrounding_none_owner_count = 0
            surrounding_low_link_count = 0
            
            for neighbor in self.G.neighbors(node):
                neighbor_degree = self.G.degree[neighbor] # type: ignore
                if self.G.nodes[neighbor].get('owner') is None:
                    surrounding_none_owner_count += 1
                surrounding_low_link_count += neighbor_degree
            
            # Score calculation: prioritize few links of surrounding nodes -> most owner = none -> many links of this node
            score = -1 * surrounding_low_link_count + 2 * surrounding_none_owner_count + node_degree
            
            # Adjust the score based on the continent size (fewer nodes in continent means higher score)
            # score_adjustment = 1 / continent_size
            # score *= score_adjustment
            
            node_scores.append((node, score))
        
        sorted_nodes = sorted(node_scores, key=lambda x: x[1], reverse=True)
        return [node for node, score in sorted_nodes]

    #get adjacent territories (list of adj)
    def get_neighbors(self, node):
        return list(self.G.neighbors(node))

    #get the number of territories owned by the owner (list)
    def nodes_with_same_owner(self, owner):
        return [node for node in self.G.nodes if self.G.nodes[node]['owner'] == owner]
    
    #get the player who got the most territories in specific continents (>75% of owning the entire continent) --> list (continent, owner):
    def check_ownership(self):
        results = []
        for continent, nodes in self.continents.items():
            owner_count = {}
            for node in nodes:
                owner = self.get_node_owner(node)
                if owner != 'me':
                    if owner not in owner_count:
                        owner_count[owner] = 0
                    owner_count[owner] += 1
            for owner, count in owner_count.items():
                if count / len(nodes) >= 0.75:
                    results.append((continent, owner))
                    break 
        return results
    
    def check_strongest(self):
        strongest = []
        for i in range(5):
            troops = 0
            player_nodes = self.nodes_with_same_owner(str(i))
            for node in player_nodes:
                troops += self.get_node_troops(node)
            force = troops * len(player_nodes)
            strongest.append((i,force))
        sorted_strongest = sorted(strongest, key=lambda x: x[1], reverse=True)
        return sorted_strongest #list of tuple (playerid(not 'me'), force)
            
    
    def check_my_ownership(self):
        results = []
        for continent, nodes in self.continents.items():
            owner_count = {'me': 0}  # Initialize owner count for 'me'
            for node in nodes:
                owner = self.G.nodes[node]['owner']
                if owner == 'me':
                    owner_count['me'] += 1

            if owner_count['me'] / len(nodes) >= 0.6:
                results.append(continent)
        # Sort results based on the length of the continent (number of nodes)
        results.sort(key=lambda x: len(self.continents[x]), reverse=True)
        return results
    
    def calculate_continent_portion_owned(self, territories_list):
        con = list(self.continents.keys())
        continent_groups = {}

        for continent in con:
            continent_territories = set(self.continents[continent])
            my_continent_territories = set(territories_list) & continent_territories
            portion = len(my_continent_territories) / len(continent_territories)
            continent_groups[continent] = portion

        sorted_continent_groups = sorted(continent_groups.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_continent_groups #return list of tuples
    
    #return all the centre nodes that are surrounded by me
    def get_centre (self): #recursion to find the centre
        nodes_owned_by_me = self.nodes_with_same_owner('me')
        # Check if there is a node surrounded by nodes also owned by 'me'
        centre_nodes = []
        for node in nodes_owned_by_me:
            neighbors = self.get_neighbors(node)
            if all(self.get_node_owner(neighbor) == 'me' for neighbor in neighbors):
                centre_nodes.append(node)
        return centre_nodes

    def calculate_enemy_troops_by_continent(self):
        enemy_troops_by_continent = {continent: 0 for continent in self.continents}
        territories_owned_by_others = {continent: 0 for continent in self.continents}

        for continent, nodes in self.continents.items():
            total_troops = 0
            owned_by_others = 0
            for node in nodes:
                if self.G.nodes[node].get('owner') != 'me':
                    total_troops += self.G.nodes[node].get('troops', 0)
                    owned_by_others += 1
            enemy_troops_by_continent[continent] = total_troops
            territories_owned_by_others[continent] = owned_by_others

        # Filter out continents with zero enemy troops
        filtered_enemy_troops = {continent: troops for continent, troops in enemy_troops_by_continent.items() if troops > 0}
        
        # Sort the continents based on the adjusted enemy troops in ascending order
        sorted_continents = sorted(filtered_enemy_troops.items(), key=lambda x: x[1])

        return sorted_continents

    def find_border_nodes(self, group):
        border_nodes = []
        for node in group:
            for neighbor in self.G.neighbors(node):
                if neighbor not in group:
                    border_nodes.append(node)
                    break
        return border_nodes

    def shortest_path_to_border(self, group, start_node):
        if start_node not in group:
            return None

        border_nodes = self.find_border_nodes(group)
        shortest_path = None

        for border_node in border_nodes:
            path = nx.shortest_path(self.G, source=start_node, target=border_node)
            if shortest_path is None or len(path) < len(shortest_path):
                shortest_path = path

        return shortest_path #return list from start_node

# handlers/handle_attack/sample.py


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

    my_base_continent = mapNetwork.calculate_continent_portion_owned(my_territories)[0][0] #string of the name
    my_base_percent = mapNetwork.calculate_continent_portion_owned(my_territories)[0][1]

    bordering_territories = game.state.get_all_adjacent_territories(my_territories)

    weakest_continents = mapNetwork.calculate_enemy_troops_by_continent() #list of tuples [('NA',35troops/7territories)]

    strongest_list = mapNetwork.check_strongest() #[('0', forces 15)]


    # early game
    if avg <=30 or game_state < 300 and domination <=3:
        for strongest, power in strongest_list:
            if strongest != game.state.me.player_id and power != 0:
                man_nodes = mapNetwork.nodes_with_same_owner(str(strongest))

                strongest_territories = sorted(my_territories, key=lambda x: game.state.territories[x].troops, reverse=False)
                for group, force in weakest_continents:
                    for territory in strongest_territories:
                        if mapNetwork.G.nodes[territory]['group'] == group:
                            #adjacent territories that are both from the strongest players and not my territories
                            move = attack_weakest(list(set(set(game.state.map.get_adjacent_to(territory)) - set(my_territories))&set(man_nodes)))
                            if move != None:
                                return move

    # attack most continent owned player
    # attack least dominance troops
    # attack weakest continents

    # # mid game
    elif avg <=60 or game_state <800 and domination <=5:
        for strongest, power in strongest_list:
            if strongest != game.state.me.player_id and power != 0:
                man_nodes = mapNetwork.nodes_with_same_owner(str(strongest))

                strongest_territories = sorted(my_territories, key=lambda x: game.state.territories[x].troops, reverse=False)
                for group, force in weakest_continents:
                    for territory in strongest_territories:
                        if mapNetwork.G.nodes[territory]['group'] == group:
                            #adjacent territories that are both from the strongest players and not my territories
                            move = attack_weakest(list(set(set(game.state.map.get_adjacent_to(territory)) - set(my_territories))&set(man_nodes)))
                            if move != None:
                                return move
    # attack most continent owned player
    # attack least dominance troops
            
    # # late game
    else:
    #attack weakest
        weakest_list = sorted(strongest_list, key=lambda x: x[1], reverse=False)
        for weakest, power in weakest_list:
            if weakest != game.state.me.player_id and power != 0:
                man_nodes = mapNetwork.nodes_with_same_owner(str(weakest))

                strongest_territories = sorted(my_territories, key=lambda x: game.state.territories[x].troops, reverse=False)
                for group, force in weakest_continents:
                    for territory in strongest_territories:
                        if mapNetwork.G.nodes[territory]['group'] == group:
                            #adjacent territories that are both from the weakest players and not my territories
                            move = attack_weakest(list(set(set(game.state.map.get_adjacent_to(territory)) - set(my_territories))&set(man_nodes)))
                            if move != None:
                                return move

    return game.move_attack_pass(query)

# handlers/handle_claim_territory/sample.py


def handle_claim_territory(game: Game, bot_state: BotState, query: QueryClaimTerritory, mapNetwork: MapNetwork) -> MoveClaimTerritory:
    """setup nexus as much as possible (centre has the most connection, surrounding has the least connections) - look for centre first
        if no more places in adjacent, pick least links"""
    all_territories = list(range(42))
    # Pick a random territory.
    unclaimed_territories = game.state.get_territories_owned_by(None)
    my_territories = game.state.get_territories_owned_by(game.state.me.player_id)
    claimed_territories = list(set(all_territories)-set(unclaimed_territories) - set(my_territories))

    for i in claimed_territories:
        mapNetwork.set_node_owner(i, 'enemies')
    for i in my_territories:
        mapNetwork.set_node_owner(i,'me')

    nexus_list = mapNetwork.nexus()
    if len(nexus_list)!=0:
        curr_nexus = nexus_list[0]
    #first selection
    if len(unclaimed_territories) > 37:
        selected_territory = curr_nexus

    #next 4 selections surrounding the nexus, if got broken choose a new nexus
    elif 37 >= len(unclaimed_territories) > 17:
        adjacent_territories = game.state.get_all_adjacent_territories(my_territories)
        claimed = 0
        for i in adjacent_territories:
            if mapNetwork.get_node_owner(i) != None and mapNetwork.get_node_owner(i) != 'me':
                claimed +=1
        
        available = list(set(unclaimed_territories) & set(adjacent_territories))
        #choose the ones with the least link (easier to defend)
        if len(available)!=0 : #and len(available) + claimed >= len(adjacent_territories)-1
            # Calculate the number of connections for each node in the available list
            links = {i: len(mapNetwork.get_neighbors(i)) for i in available}
            # Find the node with the least links
            selected_territory = min(links, key=lambda k: links[k])
        #else find a new nexus since the current one is compromised
        elif len(available) + claimed < 2:
            selected_territory = nexus_list[0]
        else:
            selected_territory = sorted(unclaimed_territories, key=lambda x: len(game.state.map.get_adjacent_to(x)), reverse=True)[0]

    #just choose the random ones at the end
    else:
        adjacent_territories = game.state.get_all_adjacent_territories(my_territories)
        available = list(set(unclaimed_territories) & set(adjacent_territories))
        if len(available) != 0:

            # We will pick the one with the most connections to our territories
            # this should make our territories clustered together a little bit.
            def count_adjacent_friendly(x: int) -> int:
                return len(set(my_territories) & set(game.state.map.get_adjacent_to(x)))

            selected_territory = sorted(available, key=lambda x: count_adjacent_friendly(x), reverse=True)[0]
        
        # Or if there are no such territories, we will pick just an unclaimed one with the greatest degree.
        else:
            selected_territory = sorted(unclaimed_territories, key=lambda x: len(game.state.map.get_adjacent_to(x)), reverse=True)[0]
    
    return game.move_claim_territory(query, selected_territory)


# handlers/handle_place_initial_troop/sample.py


def handle_place_initial_troop(game: Game, bot_state: BotState, query: QueryPlaceInitialTroop, mapNetwork: MapNetwork) -> MovePlaceInitialTroop:
    """After all the territories have been claimed, you can place a single troop on one
    of your territories each turn until each player runs out of troops."""

    my_territories = game.state.get_territories_owned_by(game.state.me.player_id)
    my_territories_model = [game.state.territories[x] for x in my_territories]
    for i in my_territories:
        mapNetwork.set_node_owner(i,'me')
    for i in my_territories_model:
        mapNetwork.set_node_troops(i.territory_id, i.troops)
    
    my_cluster = []
    #check territories and continents
    my_base_continent = mapNetwork.check_my_ownership()
    if my_base_continent:
        my_cluster = list(set(mapNetwork.continents[my_base_continent[0]])&set(my_territories)) #find my territories in the continent
    else:
        my_cluster = game.state.get_all_border_territories(my_territories) #any borders
    # cluster = mapNetwork.get_5cluster()
    centre = list(set(mapNetwork.get_centre())-set(mapNetwork.bridges_list()))

    # We will place troops along the territories on our border/cluster if no nexus.
    border_territories = list(set(my_cluster)-set(centre))
    outer_border = list(set(my_territories)-set(my_cluster))

    if border_territories == None:
        border_territories = game.state.get_all_border_territories(my_territories)
        outer_border = game.state.get_all_border_territories(my_territories)

    min_troops_territory= random.sample(border_territories, 1)[0]
    border_territory_models = [game.state.territories[x] for x in border_territories]
    outer_models = [game.state.territories[x] for x in outer_border]
   
    #This function checks for nearby territories and then strengthen the troops if nearby are increasing their numbers
    weak_list = []
    for i in border_territory_models:
        adjacent_to_border = game.state.get_all_adjacent_territories([i.territory_id])
        enemies_adjacent = list(set(adjacent_to_border) - set(my_territories))
        enemies_model = [game.state.territories[x] for x in enemies_adjacent]
        for k in enemies_model:
            if i.troops < k.troops:
                weak_list.append(i.territory_id)
    
    next_list = []
    for i in outer_models:
        adjacent_to_border = game.state.get_all_adjacent_territories([i.territory_id])
        enemies_adjacent = list(set(adjacent_to_border) - set(my_territories))
        enemies_model = [game.state.territories[x] for x in enemies_adjacent]
        for k in enemies_model:
            if i.troops < k.troops:
                next_list.append(i.territory_id)

    if weak_list:
        min_troops_territory = random.sample(weak_list, 1)[0]

    elif next_list:
        min_troops_territory = random.sample(next_list, 1)[0]

    else:
        min_troops_territory_model = max(border_territory_models, key=lambda x: x.troops)
        min_troops_territory = min_troops_territory_model.territory_id

    return game.move_place_initial_troop(query, min_troops_territory)



# handlers/handle_redeem_cards/sample.py


def handle_redeem_cards(game: Game, bot_state: BotState, query: QueryRedeemCards) -> MoveRedeemCards:
    """After the claiming and placing initial troops phases are over, you can redeem any
    cards you have at the start of each turn, or after killing another player."""

    # We will always redeem the minimum number of card sets we can until the 12th card set has been redeemed.
    # This is just an arbitrary choice to try and save our cards for the late game.
    card_sets: list[Tuple[CardModel, CardModel, CardModel]] = []
    cards_remaining = game.state.me.cards.copy()

    while len(cards_remaining) >= 5:
        card_set = game.state.get_card_set(cards_remaining)
        # According to the pigeonhole principle, we should always be able to make a set
        # of cards if we have at least 5 cards.
        assert card_set != None
        card_sets.append(card_set)
        cards_remaining = [card for card in cards_remaining if card not in card_set]

    # Remember we can't redeem any more than the required number of card sets if 
    # we have just eliminated a player.
    if game.state.card_sets_redeemed > 12 and query.cause == "turn_started":
        card_set = game.state.get_card_set(cards_remaining)
        while card_set != None:
            card_sets.append(card_set)
            cards_remaining = [card for card in cards_remaining if card not in card_set]
            card_set = game.state.get_card_set(cards_remaining)
            
    
    return game.move_redeem_cards(query, [(x[0].card_id, x[1].card_id, x[2].card_id) for x in card_sets])



# handlers/handle_distribute_troops/sample.py



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

    my_base_continent = mapNetwork.calculate_continent_portion_owned(my_territories)[0][0] #string of the name
    my_base_percent = mapNetwork.calculate_continent_portion_owned(my_territories)[0][1]
    
    base_territories = list(set(my_territories)&set(mapNetwork.continents[my_base_continent]))
    all_borders = game.state.get_all_border_territories(my_territories) #my territories in that base
    border_to_base = game.state.get_all_border_territories(base_territories) #those are MINE
    enemies_around_base = list(set(game.state.get_all_adjacent_territories(border_to_base))-set(my_territories))
    
    weakest_continents = mapNetwork.calculate_enemy_troops_by_continent() #list of tuples [('NA',0)]

    remaining_troops = total_troops
    # check if any enemy border territories have *2 troops than mine, if yes, place troops until my territories = enemies if possible
    stationed_troops = []
    if my_base_percent!=1:
        for j in border_to_base:
            stationed_troops.append((j, mapNetwork.get_node_troops(j)))
    else:
        for j in all_borders:
            stationed_troops.append((j, mapNetwork.get_node_troops(j)))
    stationed_troops = sorted(stationed_troops, key=lambda x: x[1], reverse=True)

    # early game
    if avg <=30 or game_state < 300 and domination <=3:
        if my_base_percent!=1: #continent not conquered
            for i in enemies_around_base:
                enemy_troops = mapNetwork.get_node_troops(i)
                adj_nodes = mapNetwork.get_neighbors(i)
                for node, troops in stationed_troops:
                    if node in adj_nodes and troops*2 <= enemy_troops and total_troops > (enemy_troops-troops):
                        distributions[node] += (enemy_troops-troops)
                        remaining_troops -= (enemy_troops-troops)
                    break
                break

        for i in weakest_continents: #if people in there
            for node, troops in stationed_troops:
                adj_to_station = mapNetwork.get_neighbors(node)
                for j in adj_to_station:
                    if mapNetwork.G.nodes[j]['group'] == i[0]:
                        distributions[node]+= remaining_troops
                        remaining_troops = 0
                    break
                break
            break

    # mid game
    elif avg <=60 or game_state <800 and domination <=5:
        if my_base_percent!=1: #continent not conquered
            for i in enemies_around_base:
                enemy_troops = mapNetwork.get_node_troops(i)
                adj_nodes = mapNetwork.get_neighbors(i)
                for node, troops in stationed_troops:
                    if node in adj_nodes and troops*2 <= enemy_troops and total_troops > (enemy_troops-troops):
                        distributions[node] += (enemy_troops-troops)
                        remaining_troops -= (enemy_troops-troops)
                    break
                break
        
        for i in weakest_continents:
            for node, troops in stationed_troops:
                adj_to_station = mapNetwork.get_neighbors(node)
                for j in adj_to_station:
                    if mapNetwork.G.nodes[j]['group'] == i[0]:
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
        if my_base_percent!=1: #continent not conquered
            for i in enemies_around_base:
                enemy_troops = mapNetwork.get_node_troops(i)
                adj_nodes = mapNetwork.get_neighbors(i)
                for node, troops in stationed_troops:
                    if node in adj_nodes and troops*2 <= enemy_troops and total_troops > (enemy_troops-troops):
                        distributions[node] += (enemy_troops-troops)
                        remaining_troops -= (enemy_troops-troops)
                    break
                break

        for i in weakest_continents:
            for node, troops in stationed_troops:
                adj_to_station = mapNetwork.get_neighbors(node)
                for j in adj_to_station:
                    if mapNetwork.G.nodes[j]['group'] == i[0]:
                        distributions[node]+= remaining_troops
                        remaining_troops = 0
                    break
                break
            break
    
    # The leftover troops will be put some territory (we don't care)
    distributions[stationed_troops[0][0]] += remaining_troops

    return game.move_distribute_troops(query, distributions)

# handlers/handle_troops_after_attack/sample.py


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
            num_of_troops = 3  # only move 3 troops ahead
        else:
            num_of_troops = troops_available-1
    else:
        num_of_troops = troops_available - most_troops


    return game.move_troops_after_attack(query, num_of_troops)



# handlers/handle_defend/sample.py


def handle_defend(game: Game, bot_state: BotState, query: QueryDefend) -> MoveDefend:
    """If you are being attacked by another player, you must choose how many troops to defend with."""

    # We will always defend with the most troops that we can.

    # First we need to get the record that describes the attack we are defending against.
    move_attack = cast(MoveAttack, game.state.recording[query.move_attack_id])
    defending_territory = move_attack.defending_territory
    
    # We can only defend with up to 2 troops, and no more than we have stationed on the defending
    # territory.
    defending_troops = min(game.state.territories[defending_territory].troops, 2)
    return game.move_defend(query, defending_troops)

# handlers/handle_fortify/sample.py


def handle_fortify(game: Game, bot_state: BotState, query: QueryFortify, mapNetwork: MapNetwork) -> Union[MoveFortify, MoveFortifyPass]:
    """At the end of your turn, after you have finished attacking, you may move a number of troops between
    any two of your territories (they must be adjacent)."""

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

    #if some troops stuck inside, move them up (from shallow to deep)
    #else check all the border nodes and see which one < enemy troops, and see if adjacent have troops, move until == enemy troops
    #else pass

    all_borders = game.state.get_all_border_territories(my_territories)
    centre = list(set(my_territories) - set(all_borders))
    behind_borders =  game.state.get_all_border_territories(centre)
    max_troops_behind = 0
    troops_behind_node = None

    min_troops_ahead = 0
    troops_ahead_node = None

    for i in behind_borders:
        if mapNetwork.get_node_troops(i) > max_troops_behind:
            max_troops_behind = mapNetwork.get_node_troops(i)
            troops_behind_node = i


    if max_troops_behind > 3:
        next_to_max = list(set(mapNetwork.get_neighbors(troops_behind_node))&set(all_borders))
        for i in next_to_max:
            adj_to_this_border_node = list(set(mapNetwork.get_neighbors(i))-set(my_territories))
            for j in adj_to_this_border_node: #find the most troops that are near this border
                if mapNetwork.get_node_troops(j) > min_troops_ahead: #this is max troops in front of border
                    min_troops_ahead = mapNetwork.get_node_troops(j)
                    troops_ahead_node = i

    else:
        for i in centre:
            if mapNetwork.get_node_troops(i) > max_troops_behind:
                max_troops_behind = mapNetwork.get_node_troops(i)
                troops_behind_node = i
        list_ahead_node = mapNetwork.shortest_path_to_border(my_territories, troops_behind_node)
        if list_ahead_node:
            troops_ahead_node = list_ahead_node[1]
        

    if troops_behind_node and troops_ahead_node:
        return game.move_fortify(query, troops_behind_node, troops_ahead_node, max_troops_behind - 1)
    else:
        return game.move_fortify_pass(query)





def main():
    # Get the game object, which will connect you to the engine and
    # track the state of the game.
    game = Game()
    bot_state = BotState()
    mapNetwork = MapNetwork()

    # Respond to the engine's queries with your moves.
    while True:
        # Get the engine's query (this will block until you receive a query).
        query = game.get_next_query()
        
        # Based on the type of query, respond with the correct move.
        def choose_move(query: QueryType) -> MoveType:
            match query:
                case QueryClaimTerritory() as q:
                    return handle_claim_territory(game, bot_state, q, mapNetwork)

                case QueryPlaceInitialTroop() as q:
                    return handle_place_initial_troop(game, bot_state, q, mapNetwork)

                case QueryRedeemCards() as q:
                    return handle_redeem_cards(game, bot_state, q)

                case QueryDistributeTroops() as q:
                    return handle_distribute_troops(game, bot_state, q, mapNetwork)

                case QueryAttack() as q:
                    return handle_attack(game, bot_state, q, mapNetwork)

                case QueryTroopsAfterAttack() as q:
                    return handle_troops_after_attack(game, bot_state, q, mapNetwork)

                case QueryDefend() as q:
                    return handle_defend(game, bot_state, q)

                case QueryFortify() as q:
                    return handle_fortify(game, bot_state, q, mapNetwork)
        
        # Send the move to the engine.
        game.send_move(choose_move(query))

if __name__ == "__main__":
    main()