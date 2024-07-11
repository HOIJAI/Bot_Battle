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
        # Step 1: Calculate degree for each node
        node_degrees = {node: degree for node, degree in nx.degree(self.G)}

        # Step 2: Filter nodes where owner is None
        nodes_with_owner_none = [node for node in self.G.nodes if self.G.nodes[node].get('owner') is None]

        # Step 3: Sort nodes by degree in descending order
        sorted_nodes = sorted(nodes_with_owner_none, key=lambda node: node_degrees[node], reverse=True)

        # Step 4: Find nodes with the minimum links (border nodes)
        if not nodes_with_owner_none:
            return []  # Return empty list if there are no nodes with owner as None
        
        min_degree = min(node_degrees[node] for node in nodes_with_owner_none)
        border_nodes = [node for node in nodes_with_owner_none if node_degrees[node] == min_degree]

        # Step 5: Find nexus nodes that are connected to border nodes
        nexus_connected_to_border = []

        for nexus_node in sorted_nodes:
            connected_to_border = [node for node in self.G.neighbors(nexus_node) if node in border_nodes]
            if connected_to_border:
                nexus_connected_to_border.append((nexus_node, connected_to_border))

        # Step 6: Verify that most connections between nexus and border nodes are owner=None
        valid_nexus_nodes = []

        for nexus, connected_border in nexus_connected_to_border:
            count_owner_none = sum(1 for neighbor in connected_border if self.G.nodes[neighbor].get('owner') is None)
            if count_owner_none / len(connected_border) >= 0.8:  # Adjust threshold as needed
                valid_nexus_nodes.append(nexus)

        return valid_nexus_nodes

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
    
    def check_my_ownership(self):
        results = []
        for continent, nodes in self.continents.items():
            owner_count = {'me': 0}  # Initialize owner count for 'me'
            for node in nodes:
                owner = self.G.nodes[node]['owner']
                if owner == 'me':
                    owner_count['me'] += 1

            if owner_count['me'] / len(nodes) >= 0.75:
                results.append((continent, 'me'))

        return results
    
    #get the 5 nodes closest
    def get_5cluster(self):
        nodes_owned_by_me = self.nodes_with_same_owner('me')
        #Calculate clustering coefficients for these nodes
        clustering_coeffs = {}
        for i in nodes_owned_by_me:
            clustering_coeffs[i] = nx.clustering(self.G, nodes=i)

        #Find the top 5 nodes with the highest clustering coefficients
        sorted_nodes = sorted(clustering_coeffs.items(), key=lambda x: x[1], reverse=True)
        top_5_nodes = [node for node, _ in sorted_nodes[:5]]

        return top_5_nodes #list
    
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

    #when poking a continent, look for the minimum land I can take without spending much troops
    def find_min_troop_adjacent_node(self, continent, owner): #find the most number of my troops in the adjacent
        min_enemies_troops = float('inf')
        enemy_node = None
        my_node = None
        
        # Get the list of nodes in the continent
        continent_nodes = self.continents[continent]
        
        # Identify nodes in the continent owned by 'me'
        nodes_owned_by_me = self.nodes_with_same_owner('me')
        
        for node in nodes_owned_by_me:
            adj = self.G.neighbors(node)
            for i in adj:
                if self.get_node_owner(i) == owner and i in continent_nodes:
                    if self.get_node_troops(i)<min_enemies_troops:
                        min_enemies_troops = self.get_node_troops(i)
                        enemy_node = i
                        my_node = node
                    
        if my_node != None and enemy_node != None:
            return [my_node, enemy_node]
        else:
            return None #need to check if my_node == None

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
        curr_nexus = random.sample(nexus_list, 1)[0]
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
        elif len(available) + claimed <= 2:
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
    
    cluster = mapNetwork.get_5cluster()
    centre = mapNetwork.get_centre()
    # We will place troops along the territories on our border/cluster if no nexus.
    border_territories = list(set(cluster)-set(centre))

    min_troops_territory=None
    border_territory_models = [game.state.territories[x] for x in border_territories]
   
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
    outer_border = list(set(my_territories) - set(cluster))
    outer_models = [game.state.territories[x] for x in outer_border]
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
    

    # 1. Check if any player owns >75% of a continent, only attack one of them at a time
    continent_owned = mapNetwork.check_ownership() #e.g.[('NA', '0')]
    if continent_owned:
        for i in continent_owned:
            # Find adjacent to min enemy node and attack if conditions met
            out = mapNetwork.find_min_troop_adjacent_node(i[0], i[1])
            if out:
                my_closet_node, node_to_attack = out
                if total_troops - mapNetwork.get_node_troops(node_to_attack)*2 >= total_troops//4:
                    distributions[my_closet_node] += mapNetwork.get_node_troops(node_to_attack)
                    total_troops -= mapNetwork.get_node_troops(node_to_attack)
            break
    
    # 2. Implement logic for troop distribution around nexus, bridges, etc.
        # Placeholder logic for securing continents or strategic locations
    border_territories = game.state.get_all_border_territories(
        game.state.get_territories_owned_by(game.state.me.player_id)
    )

    if len(border_territories) >=3:
        border_territories = random.sample(border_territories, 1)[:3]
    
    troops_per_territory = total_troops // len(border_territories)
    leftover_troops = total_troops % len(border_territories)

    for territory in border_territories:
        distributions[territory] += troops_per_territory

    # The leftover troops will be put some territory (we don't care)
    distributions[random.sample(border_territories, 1)[0]] += leftover_troops
    
    return game.move_distribute_troops(query, distributions)

# handlers/handle_troops_after_attack/sample.py


def handle_troops_after_attack(game: Game, bot_state: BotState, query: QueryTroopsAfterAttack) -> MoveTroopsAfterAttack:
    """After conquering a territory in an attack, you must move troops to the new territory."""

    # First we need to get the record that describes the attack, and then the move that specifies
    # which territory was the attacking territory.
    record_attack = cast(RecordAttack, game.state.recording[query.record_attack_id])
    move_attack = cast(MoveAttack, game.state.recording[record_attack.move_attack_id])

    # We will always move the maximum number of troops we can.
    return game.move_troops_after_attack(query, game.state.territories[move_attack.attacking_territory].troops - 1)


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


def handle_fortify(game: Game, bot_state: BotState, query: QueryFortify) -> Union[MoveFortify, MoveFortifyPass]:
    """At the end of your turn, after you have finished attacking, you may move a number of troops between
    any two of your territories (they must be adjacent)."""

    # We will never fortify.
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
                    return handle_troops_after_attack(game, bot_state, q)

                case QueryDefend() as q:
                    return handle_defend(game, bot_state, q)

                case QueryFortify() as q:
                    return handle_fortify(game, bot_state, q)
        
        # Send the move to the engine.
        game.send_move(choose_move(query))

if __name__ == "__main__":
    main()