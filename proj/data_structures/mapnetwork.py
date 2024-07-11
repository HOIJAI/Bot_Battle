import networkx as nx
import heapq
from risk_helper.game import Game

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
            score_adjustment = 1 / continent_size
            score *= score_adjustment
            
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
        
        # Adjust the troops count based on the number of territories owned by others
        adjusted_enemy_troops = {continent: troops / territories_owned_by_others[continent] for continent, troops in filtered_enemy_troops.items() if territories_owned_by_others[continent] > 0}
        
        # Sort the continents based on the adjusted enemy troops in ascending order
        sorted_continents = sorted(adjusted_enemy_troops.items(), key=lambda x: x[1])

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
    
    def update_mapnetwork(self, game: Game):
        player_list = list(range(5))
        myId = game.state.me.player_id

        for value in game.state.territories.values():
            if value.occupier in player_list:
                self.set_node_owner(value.territory_id, 'me' if value.occupier == myId else str(value.occupier))
                self.set_node_troops(value.territory_id, value.troops)
