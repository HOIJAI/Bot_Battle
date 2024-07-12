import networkx as nx
import heapq

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

        # Define the continents with their respective territories
        self.continents = {
            'NA': [8, 3, 2, 6, 1, 0, 7, 5, 4],
            'SA': [30, 31, 29, 28],
            'EU': [14, 11, 10, 9, 12, 15, 13],
            'AF': [35, 32, 34, 33, 36, 37],
            'AS': [19, 23, 24, 21, 20, 26, 16, 22, 25, 17, 18, 27],
            'AU': [40, 41, 39, 38]
        }

        # Initialize graph nodes with group, owner, and troops attributes
        for group, nodes in self.continents.items():
            for node in nodes:
                self.G.add_node(node, group=group, owner=None, troops=0)

    def set_troops_and_owners(self, node_data):
        for node, data in node_data.items():
            if node in self.G:
                self.G.nodes[node]['troops'] = data.get('troops', 0)
                self.G.nodes[node]['owner'] = data.get('owner', None)

    def find_border_nodes(self, my_territories):
        border_nodes = []
        for node in my_territories:
            for neighbor in self.G.neighbors(node):
                if self.G.nodes[neighbor].get('owner') != 'me':
                    border_nodes.append(node)
                    break
        return border_nodes

    def optimal_path_to_continent(self, border_nodes, target_continent):
        min_heap = []
        visited = set()
        target_nodes = set(self.continents[target_continent])
        continent_coverage = set()
        optimal_path = None

        for start_node in border_nodes:
            heapq.heappush(min_heap, (0, 0, start_node, [start_node], set([start_node])))

        while min_heap:
            enemy_count, enemy_troops, current_node, path, coverage = heapq.heappop(min_heap)

            if current_node in visited:
                continue

            visited.add(current_node)
            coverage.add(current_node)

            if coverage >= target_nodes:
                if optimal_path is None or (enemy_count, enemy_troops) < optimal_path[:2]:
                    optimal_path = (enemy_count, enemy_troops, path)
                continue

            for neighbor in self.G.neighbors(current_node):
                if neighbor not in visited and neighbor not in coverage:
                    new_enemy_count = enemy_count + (1 if self.G.nodes[neighbor].get('owner') != 'me' else 0)
                    new_enemy_troops = enemy_troops + (self.G.nodes[neighbor]['troops'] if self.G.nodes[neighbor].get('owner') != 'me' else 0)
                    heapq.heappush(min_heap, (new_enemy_count, new_enemy_troops, neighbor, path + [neighbor], coverage | set([neighbor])))

        return optimal_path[2] if optimal_path else None

    def find_optimal_continent_paths(self, my_territories):
        border_nodes = self.find_border_nodes(my_territories)
        continent_paths = {}

        for continent in self.continents.keys():
            path = self.optimal_path_to_continent(border_nodes, continent)
            if path:
                continent_paths[continent] = path

        sorted_continents = sorted(continent_paths.items(), key=lambda x: (len(x[1]), sum(self.G.nodes[node]['troops'] for node in x[1] if self.G.nodes[node].get('owner') != 'me')))
        
        return sorted_continents

# Example usage
map_network = MapNetwork()

# Set the number of troops and owner for specific nodes
for i in range(1,12):
    map_network.G.nodes[i]['owner'] = 'me'
# for i in range(18,21):
#     G.nodes[i]['owner'] = 'me'
for i in range(1,20):
    map_network.G.nodes[i]['troops'] = 10
for i in range(25,40):
    map_network.G.nodes[i]['troops'] = 20

my_nodes = [node for node in map_network.G.nodes if map_network.G.nodes[node]['owner'] == 'me']

print(map_network.find_optimal_continent_paths(my_nodes))
