import networkx as nx
from heapq import heappop, heappush
from collections import defaultdict

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
        for node in range(0, 20):
            self.G.nodes[node]['troops'] = 10  

        for node in range(21,35):
            self.G.nodes[node]['troops'] = 3


    def find_path_to_cover_continent(self, start_node, continent):
        if start_node not in self.G.nodes or continent not in self.continents:
            raise ValueError("Invalid start node or continent")

        # Initialize Dijkstra's algorithm
        dist = defaultdict(lambda: float('inf'))
        dist[start_node] = 0
        previous = {}
        priority_queue = [(0, start_node)]  # (distance, node)

        # Dijkstra's algorithm
        while priority_queue:
            current_dist, current_node = heappop(priority_queue)

            if current_dist > dist[current_node]:
                continue

            for neighbor in self.G.neighbors(current_node):
                if self.G.nodes[neighbor]['owner'] == 'me' and neighbor != start_node:
                    continue  # Skip nodes owned by 'me' except the start node

                weight = self.G[current_node][neighbor].get('weight', 1)  # Assuming uniform weight for simplicity
                distance = current_dist + weight

                if distance < dist[neighbor]:
                    dist[neighbor] = distance
                    previous[neighbor] = current_node
                    heappush(priority_queue, (distance, neighbor))

        # Reconstruct path to cover the entire continent
        path = []
        current_node = max(self.continents[continent], key=lambda x: dist[x])

        while current_node != start_node:
            path.append(current_node)
            current_node = previous[current_node]

        path.append(start_node)
        path.reverse()

        return path, dist[max(self.continents[continent], key=lambda x: dist[x])]

# Example usage:
map_network = MapNetwork()

start_node = 30  # Example start node
continent = 'NA'  # Example continent to cover
path, troops_count = map_network.find_path_to_cover_continent(start_node, continent)
print("Path:", path)
print("Troops count:", troops_count)