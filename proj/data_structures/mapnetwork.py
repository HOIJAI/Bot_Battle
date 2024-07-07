import networkx as nx

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
        # Calculate degree for each node
        node_degrees = {node: degree for node, degree in nx.degree(self.G)}

        # Filter nodes where owner is None
        nodes_with_owner_none = [node for node in self.G.nodes if self.G.nodes[node]['owner'] is None]

        # Sort nodes by degree in descending order
        nexus_nodes = sorted(nodes_with_owner_none, key=lambda node: node_degrees[node], reverse=True)

        # Find nodes (border_nodes) with the minimum links (owner=None)
        min_degree = min(node_degrees[node] for node in nodes_with_owner_none)
        border_nodes = [node for node in nodes_with_owner_none if node_degrees[node] == min_degree]

        # Find nexus nodes that are connected to border nodes
        nexus_connected_to_border = []

        for nexus_node in nexus_nodes:
            connected_to_border = [node for node in self.G.neighbors(nexus_node) if node in border_nodes]
            if connected_to_border:
                nexus_connected_to_border.append((nexus_node, connected_to_border))

        # Verify that most connections between nexus and border nodes are owner=None
        valid_nexus_nodes = []

        for nexus, connected_border in nexus_connected_to_border:
            count_owner_none = sum(1 for neighbor in connected_border if self.G.nodes[neighbor]['owner'] is None)
            if count_owner_none / len(connected_border) >= 0.8:  # Adjust threshold as needed
                valid_nexus_nodes.append(nexus)

        return(valid_nexus_nodes)

    #get the properties of the territory, num = num of troops, owner = owned by who
    def get_node_property(self, node, property_name):
        return self.G.nodes[node].get(property_name, None)

    #get adjacent territories
    def get_neighbors(self, node):
        return list(self.G.neighbors(node))

    #get number of territories linked to a node
    def get_num_connections(self, node):
        return list(self.G.adj[node])

    #get the number of territories owned by the owner
    def nodes_with_same_owner(self, owner):
        return [node for node, data in self.G.nodes(data=True) if data.get('owner') == owner]
    
    #get the player who got the most territories in specific continents (>70% of owning the entire continent):
    def check_ownership(self, continent):
        results = {}
        for continent, nodes in self.continents.items():
            owner_count = {}
            for node in nodes:
                owner = self.G.nodes[node]['owner']
                if owner:
                    if owner not in owner_count:
                        owner_count[owner] = 0
                    owner_count[owner] += 1
            for owner, count in owner_count.items():
                if count / len(nodes) > 0.7:
                    results[continent] = owner
        return results