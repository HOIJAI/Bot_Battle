import networkx as nx
import heapq
from typing import List, Dict, Tuple

# Create an empty graph
G = nx.Graph()

# Add nodes from 0 to 41 with default attributes
G.add_nodes_from(range(42), troops=0, owner=None)

# Add edges between nodes
edges = [
    (0, 1), (0, 5), (0, 21), (1, 5), (1, 6), (1, 8), (2, 8), (2, 3), (2, 30),
    (3, 2), (3, 8), (3, 6), (3, 7), (4, 5), (4, 6), (4, 7), (4, 10), (5, 0),
    (5, 1), (5, 6), (5, 4), (6, 1), (6, 5), (6, 4), (6, 7), (6, 3), (6, 8),
    (7, 3), (7, 4), (7, 6), (9, 10), (9, 11), (9, 12), (9, 15), (10, 4),
    (10, 9), (10, 12), (11, 12), (11, 9), (11, 15), (11, 13), (11, 14),
    (12, 10), (12, 9), (12, 11), (12, 14), (13, 11), (13, 14), (13, 15),
    (13, 34), (14, 12), (14, 11), (14, 13), (14, 16), (14, 22), (15, 9),
    (15, 11), (15, 13), (15, 36), (16, 14), (16, 26), (16, 17), (16, 18),
    (16, 22), (17, 16), (17, 18), (17, 26), (17, 25), (17, 23), (17, 24),
    (18, 16), (18, 17), (18, 22), (18, 24), (19, 25), (19, 21), (19, 23),
    (19, 27), (20, 23), (20, 21), (21, 27), (21, 20), (21, 19), (24, 17),
    (24, 18), (24, 40), (25, 26), (25, 27), (25, 19), (25, 17), (28, 29),
    (28, 31), (29, 30), (29, 36), (29, 31), (29, 28), (30, 2), (30, 31),
    (30, 29), (32, 36), (32, 33), (32, 37), (33, 34), (33, 35), (33, 32),
    (33, 37), (34, 36), (34, 13), (34, 33), (34, 22), (35, 37), (35, 33),
    (38, 39), (38, 41), (39, 41), (40, 24), (40, 41), (40, 39)
]

G.add_edges_from(edges)

# Define continents with their respective nodes
continents = {
    'NA': [8, 3, 2, 6, 1, 0, 7, 5, 4],
    'SA': [30, 31, 29, 28],
    'EU': [14, 11, 10, 9, 12, 15, 13],
    'AF': [35, 32, 34, 33, 36, 37],
    'AS': [19, 23, 24, 21, 20, 26, 16, 22, 25, 17, 18, 27],
    'AU': [40, 41, 39, 38]
}

# Assign continent groups to nodes
for group, nodes in continents.items():
    for node in nodes:
        G.nodes[node]['group'] = group

import time


# def find_optimal_paths_to_continents(my_nodes):
#     # Cache for memoization
#     memo = {}

#     def dijkstra_with_troops(start: int, target_continent):
#         if (start, tuple(target_continent)) in memo:
#             return memo[(start, tuple(target_continent))]
        
#         pq = [(0, 0, start, [start])]
#         visited = set()
        
#         while pq:
#             total_troops, total_nodes, current, path = heapq.heappop(pq)
            
#             if current in visited:
#                 continue
#             visited.add(current)
            
#             if current in target_continent:
#                 result = (total_troops, total_nodes, path)
#                 memo[(start, tuple(target_continent))] = result
#                 return result
            
#             for neighbor in G.neighbors(current):
#                 if neighbor not in visited:
#                     troops = G.nodes[neighbor]['troops']
#                     new_total_troops = total_troops + (troops if G.nodes[neighbor]['owner'] != 'me' else 0)
#                     new_path = path + [neighbor]
#                     heapq.heappush(pq, (new_total_troops, total_nodes + 1, neighbor, new_path))
        
#         result = (float('inf'), float('inf'), [])
#         memo[(start, tuple(target_continent))] = result
#         return result

#     results = []

#     for continent_name, continent_nodes in continents.items():
#         optimal_troops = float('inf')
#         optimal_nodes = float('inf')
#         optimal_path = []

#         for my_node in my_nodes:
#             troops, nodes, path = dijkstra_with_troops(my_node, continent_nodes)
#             if (troops, nodes) < (optimal_troops, optimal_nodes):
#                 optimal_troops = troops
#                 optimal_nodes = nodes
#                 optimal_path = path
        
#         results.append([continent_name, optimal_path, optimal_troops])
    
#     for i in results:
#         continent_name = i[0]
#         path = i[1]
#         if path:
#             continent_nodes = continents[continent_name]
#             continents_troops = sum(G.nodes[node]['troops'] for node in continent_nodes if G.nodes[node]['owner'] != 'me')
#             i[2] += continents_troops - (G.nodes[path[-1]]['troops'] if G.nodes[path[-1]]['owner'] != 'me' else 0)
    
#     return sorted(results, key=lambda x: (x[2], len(x[1])))


def find_optimal_paths_to_continents(my_nodes):
    # Cache for memoization
    memo = {}

    def dijkstra_with_troops(start_nodes, target_continent):
        target_set = set(target_continent)
        pq = [(0, 0, start, [start]) for start in start_nodes]
        heapq.heapify(pq)
        visited = {}
        
        while pq:
            total_troops, total_nodes, current, path = heapq.heappop(pq)
            
            if current in visited and visited[current] <= total_troops:
                continue
            visited[current] = total_troops
            
            if current in target_set:
                memo[(tuple(start_nodes), tuple(target_continent))] = (total_troops, total_nodes, path)
                return total_troops, total_nodes, path
            
            for neighbor in G.neighbors(current):
                if neighbor not in visited or total_troops < visited[neighbor]:
                    troops = G.nodes[neighbor]['troops']
                    new_total_troops = total_troops + (troops if G.nodes[neighbor]['owner'] != 'me' else 0)
                    new_path = path + [neighbor]
                    heapq.heappush(pq, (new_total_troops, total_nodes + 1, neighbor, new_path))
        
        result = (float('inf'), float('inf'), [])
        memo[(tuple(start_nodes), tuple(target_continent))] = result
        return result

    results = []

    for continent_name, continent_nodes in continents.items():
        if (tuple(my_nodes), tuple(continent_nodes)) in memo:
            optimal_troops, optimal_nodes, optimal_path = memo[(tuple(my_nodes), tuple(continent_nodes))]
        else:
            optimal_troops, optimal_nodes, optimal_path = dijkstra_with_troops(my_nodes, continent_nodes)
        
        results.append([continent_name, optimal_path, optimal_troops])
    
    for i in results:
        continent_name = i[0]
        path = i[1]
        if path:
            continent_nodes = continents[continent_name]
            continents_troops = sum(G.nodes[node]['troops'] for node in continent_nodes if G.nodes[node]['owner'] != 'me')
            i[2] += continents_troops - (G.nodes[path[-1]]['troops'] if G.nodes[path[-1]]['owner'] != 'me' else 0)
    
    return sorted(results, key=lambda x: (x[2], len(x[1])))


# def find_optimal_paths_to_continents(G: nx.Graph, my_nodes: List[int], continents: Dict[str, List[int]]):
#     def dijkstra_with_troops(start: int, target_continent: List[int]) -> Tuple[int, int, List[int]]:
#         pq = [(0, 0, start, [start])]  # Priority queue with (total troops, total nodes, current node, path)
#         visited = set()
        
#         while pq:
#             total_troops, total_nodes, current, path = heapq.heappop(pq)
            
#             if current in visited:
#                 continue
#             visited.add(current)
            
#             if current in target_continent:
#                 return total_troops, total_nodes, path
            
#             for neighbor in G.neighbors(current):
#                 if neighbor not in visited:
#                     troops = G.nodes[neighbor]['troops']
#                     new_total_troops = total_troops + (troops if G.nodes[neighbor]['owner'] != 'me' else 0)
#                     new_path = path + [neighbor]
#                     heapq.heappush(pq, (new_total_troops, total_nodes + 1, neighbor, new_path)) # type: ignore
        
#         return float('inf'), float('inf'), []  # type: ignore # In case there's no valid path

#     results = []
    
#     for continent_name, continent_nodes in continents.items():
#         optimal_troops = float('inf')
#         optimal_nodes = float('inf')
#         optimal_path = []
        
#         for my_node in my_nodes:
#             troops, nodes, path = dijkstra_with_troops(my_node, continent_nodes)
#             if (troops, nodes) < (optimal_troops, optimal_nodes):
#                 optimal_troops = troops
#                 optimal_nodes = nodes
#                 optimal_path = path
        
#         results.append([continent_name, optimal_path, optimal_troops])
    
#     for name, nodes in continents.items():
#         continents_troops = sum([G.nodes[node]['troops'] for node in nodes if G.nodes[node]['owner'] != 'me'])
#         for i in results:
#             if i[0] == name:
#                 i[2] += continents_troops
#                 if len(i[1])>1:
#                     i[2] -= G.nodes[i[1][-1]]['troops'] #repeated
#                 # i[2] += G.nodes[i[1][0]]['troops']
    
#     return sorted(results, key=lambda x: (x[2], len(x[1])))  # Sort by the total troops required and path length
#     # e.g[['NA', [0], -10], ['SA', [2, 30], 40], ['EU', [4, 10], 70],...

# Example node ownership and troops assignment

# G.nodes[11]['owner'] = 'me'
# G.nodes[15]['owner'] = 'me'
# G.nodes[13]['owner'] = 'me'
# G.nodes[14]['owner'] = 'me'
# G.nodes[10]['owner'] = 'me'
# G.nodes[9]['owner'] = 'me'
# G.nodes[12]['owner'] = 'me'
for i in range(35,39):
    G.nodes[i]['owner'] = 'me'
G.nodes[32]['owner'] = 'me'
G.nodes[33]['owner'] = 'me'

for i in range(42):
    G.nodes[i]['troops'] = 10
# G.nodes[10]['troops'] = 1
# G.nodes[9]['troops'] = 1
# G.nodes[12]['troops'] = 1
# G.nodes[15]['troops'] = 3
# G.nodes[13]['troops'] = 4
# G.nodes[11]['troops'] = 3

# Path should skip nodes with high troops like 14 and 16 from my nodes to AU
my_nodes = [node for node in G.nodes if G.nodes[node]['owner'] == 'me']

# Find optimal paths
start = time.process_time()
optimal_paths = find_optimal_paths_to_continents (my_nodes)
end = time.process_time()

print(optimal_paths, 12000*(end-start))
