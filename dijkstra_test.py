import networkx as nx

# Assuming you have a graph G with nodes containing 'troops' and 'owner' attributes, and edges without weight

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

def shortest_path_with_least_troops_sum(G, start_node, continent_nodes):
    def troops_sum_weight(u, v, data):
        # Custom weight function: sum of troops along the path
        return data.get('troops', 0)

    # Exclude nodes owned by 'me' from consideration
    def exclude_me(node):
        return G.nodes[node].get('owner') != 'me'

    # Filter nodes in the continent by excluding nodes owned by 'me'
    continent_nodes_filtered = [node for node in continent_nodes if exclude_me(node)]

    # Find shortest path using Dijkstra's algorithm with custom weight function
    path = nx.shortest_path(G, source=start_node, weight=troops_sum_weight)

    # Filter path to include only nodes in the continent and exclude nodes owned by 'me'
    path_filtered = [node for node in path if node in continent_nodes_filtered]

    return path_filtered

def find_easiest_path_to_continent(G, start_node, continent_nodes):
    # Create a copy of the graph with edges containing no troops
    H = G.copy()
    for u, v in H.edges():
        H[u][v]['weight'] = 0  # Assuming weight of edges is zero (no troops)

    # Filter nodes to exclude 'me'
    continent_nodes = [node for node in H.nodes() if H.nodes[node].get('owner') != 'me']
    
    # Use Dijkstra's algorithm to find the shortest path based on troop sum
    shortest_path = nx.dijkstra_path(H, source=start_node, target=continent_nodes[0], weight='weight')
    
    # Calculate troops needed
    troops_needed = sum(H.nodes[node].get('troops', 0) for node in shortest_path)  # type: ignore # Exclude start node
    
    return shortest_path, troops_needed

# Example usage:
# Assuming G is your NetworkX graph and start_node is the starting node in a different continent
# and continent_nodes is a list of nodes in the continent you want to pass through
start_node = 2  # Replace with actual starting node
continent_nodes = continents['AF']
for node in range(10, 20):
    G.nodes[node]['troops'] = 10  

for node in range(21,35):
    G.nodes[node]['troops'] = 3# Replace with actual continent nodes

result_path, troops_needed = find_easiest_path_to_continent(G, start_node, continent_nodes)
print("Easiest Path:", result_path)
print("Troops Needed:", troops_needed)