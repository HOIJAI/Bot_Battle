import networkx as nx
from collections import defaultdict, deque
import heapq
# import matplotlib.pyplot as plt

# Create an empty graph
G = nx.Graph()

# Add nodes from 0 to 41
G.add_nodes_from(list(range(42)), troops = 0, owner = None)

# Add edges
G.add_edges_from([(0,1),(0,5),(0,21)])
G.add_edges_from([(1,5),(1,6),(1,8)])
G.add_edges_from([(2,8),(2,3),(2,30)])
G.add_edges_from([(3,2),(3,8),(3,6),(3,7)])
G.add_edges_from([(4,5),(4,6),(4,7),(4,10)])
G.add_edges_from([(5,0),(5,1),(5,6),(5,4)])
G.add_edges_from([(6,1),(6,5),(6,4),(6,7),(6,3),(6,8)])
G.add_edges_from([(7,3),(7,4),(7,6)])
G.add_edges_from([(9,10),(9,11),(9,12),(9,15)])
G.add_edges_from([(10,4),(10,9),(10,12)])
G.add_edges_from([(11,12),(11,9),(11,15),(11,13),(11,14)])
G.add_edges_from([(12,10),(12,9),(12,11),(12,14)])
G.add_edges_from([(13,11),(13,14),(13,15),(13,34)])
G.add_edges_from([(14,12),(14,11),(14,13),(14,16),(14,22)])
G.add_edges_from([(15,9),(15,11),(15,13),(15,36)])
G.add_edges_from([(16,14),(16,26),(16,17),(16,18),(16,22)])
G.add_edges_from([(17,16),(17,18),(17,26),(17,25),(17,23),(17,24)])
G.add_edges_from([(18,16),(18,17),(18,22),(18,24)])
G.add_edges_from([(19,25),(19,21),(19,23),(19,27)])
G.add_edges_from([(20,23),(20,21)])
G.add_edges_from([(21,27),(21,20),(21,19)])
G.add_edges_from([(24,17),(24,18),(24,40)])
G.add_edges_from([(25,26),(25,27),(25,19),(25,17)])
G.add_edges_from([(28,29),(28,31)])
G.add_edges_from([(29,30),(29,36),(29,31),(29,28)])
G.add_edges_from([(30,2),(30,31),(30,29)])
G.add_edges_from([(32,36),(32,33),(32,37)])
G.add_edges_from([(33,34),(33,35),(33,32),(33,37)])
G.add_edges_from([(34,36),(34,13),(34,33)])
G.add_edges_from([(35,37),(35,33)])
G.add_edges_from([(38,39),(38,41)])
G.add_edges_from([(39,41)])
G.add_edges_from([(40,24),(40,41),(40,39)])


NA = [8, 3, 2, 6, 1, 0, 7, 5, 4]
SA = [30, 31, 29, 28]
EU = [14, 11, 10, 9, 12, 15, 13]
AF = [35, 32, 34, 33, 36, 37]
AS = [19, 23, 24, 21, 20, 26, 16, 22, 25, 17, 18, 27]
AU = [40, 41, 39, 38]

continents = {'NA': NA, 'SA': SA, 'EU': EU, 'AF': AF, 'AS': AS, 'AU': AU}

for group, nodes in continents.items():
    for node in nodes:
        G.nodes[node]['group'] = group


    def set_troops_and_owners(node_data: Dict[int, Dict[str, int]]):
        for node, data in node_data.items():
            if node in G:
                G.nodes[node]['troops'] = data.get('troops', 0)
                G.nodes[node]['owner'] = data.get('owner', None)

    def find_border_nodes(my_nodes: List[int]) -> List[int]:
        border_nodes = []
        for node in my_nodes:
            for neighbor in G.neighbors(node):
                if G.nodes[neighbor]['owner'] != 'me':
                    border_nodes.append(node)
                    break
        return border_nodes

    def find_optimal_path(start_node: int, target_nodes: List[int]) -> List[int]:
        min_heap = [(G.nodes[start_node]['troops'], start_node, [start_node])]
        visited = set()
        
        while min_heap:
            current_troops, current_node, path = heapq.heappop(min_heap)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            if all(node in visited for node in target_nodes):
                return path
            
            for neighbor in G.neighbors(current_node):
                if neighbor not in visited:
                    total_troops = current_troops + G.nodes[neighbor]['troops']
                    heapq.heappush(min_heap, (total_troops, neighbor, path + [neighbor]))
        
        return []

    def calculate_optimal_paths(my_nodes: List[int]) -> List[Tuple[str, List[int], int]]:
        border_nodes = find_border_nodes(my_nodes)
        optimal_paths = []
        
        for continent, nodes in continents.items():
            continent_nodes = set(nodes)
            best_path = None
            min_troops = float('inf')
            
            for border_node in border_nodes:
                path = find_optimal_path(border_node, list(continent_nodes))
                if path:
                    path_troops = sum(G.nodes[node]['troops'] for node in path)
                    if path_troops < min_troops:
                        min_troops = path_troops
                        best_path = path
            
            if best_path:
                optimal_paths.append((continent, best_path, min_troops))
        
        optimal_paths.sort(key=lambda x: x[2])
        return optimal_paths

