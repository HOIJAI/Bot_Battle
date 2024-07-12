import networkx as nx
from collections import defaultdict, deque
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
G.add_edges_from([(34,36),(34,13),(34,33), (34,22)])
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

# G.nodes[5]['owner'] = '0'
# G.nodes[1]['owner'] = '0'
# G.nodes[6]['owner'] = '0'
# G.nodes[2]['owner'] = '0'
G.nodes[30]['owner'] = '0'
G.nodes[31]['owner'] = '0'
G.nodes[29]['owner'] = '0'
G.nodes[26]['owner'] = '0'
G.nodes[35]['owner'] = '0'
G.nodes[24]['owner'] = '0'
G.nodes[38]['owner'] = '0'
G.nodes[40]['owner'] = '0'
G.nodes[41]['owner'] = '0'
G.nodes[39]['owner'] = '0'

for i in range(1, 40):
    G.nodes[i]['troops'] = 10




# def find_most_clustered_nodes():
#     clustered_nodes = [node for node in G.nodes() if len(list(G.neighbors(node))) >= 4]
#     clustered_nodes_sorted = sorted(clustered_nodes, key=lambda node: len(list(G.neighbors(node))), reverse=True)
#     return clustered_nodes_sorted

# k = find_most_clustered_nodes()
# print(k)
my_territories = [node for node in G.nodes if G.nodes[node]['owner'] == '0']

def bridges_list():
    # Find nodes connected to another continent
    connected_to_another_continent = []
    for u, v in G.edges():
        if G.nodes[u]['group'] != G.nodes[v]['group']:
            connected_to_another_continent.append(u)
            connected_to_another_continent.append(v)

    connected_to_another_continent = list(set(connected_to_another_continent))
    return connected_to_another_continent

def nexus():
    nodes_with_none_owner = [n for n, attr in G.nodes(data=True) if attr.get('owner') is None]
    
    # Calculate the number of nodes in each continent
    continent_node_counts = {continent: len(nodes) for continent, nodes in continents.items()}
    
    node_scores = []
    
    for node in nodes_with_none_owner:
        node_degree = G.degree(node) # type: ignore
        continent = G.nodes[node].get('group')
        continent_size = continent_node_counts[continent]

        surrounding_none_owner_count = 0
        surrounding_low_link_count = 0
        
        for neighbor in G.neighbors(node):
            neighbor_degree = G.degree[neighbor] # type: ignore
            if G.nodes[neighbor].get('owner') is None:
                surrounding_none_owner_count += 1
            surrounding_low_link_count += neighbor_degree
        
        # Score calculation: prioritize few links of surrounding nodes -> most owner = none -> many links of this node
        score = -1 * surrounding_low_link_count + 3 * surrounding_none_owner_count + node_degree
        
        bridges = bridges_list()
        continent_bridges = [bridge for bridge in bridges if G.nodes[bridge]['group'] == continent]
        # Adjust the score based on the continent size (fewer nodes in continent means higher score)
        score_adjustment = 1/(continent_size + 3*len(continent_bridges)) #more continent = bad, more bridges = bad
        score *= score_adjustment
        
        node_scores.append((node, score))
    
    sorted_nodes = sorted(node_scores, key=lambda x: x[1], reverse=True)
    return [node for node, score in sorted_nodes]

def calculate_enemy_troops_by_continent():
    enemy_troops_by_continent = {continent: 0 for continent in   continents}
    territories_owned_by_others = {continent: 0 for continent in   continents}

    for continent, nodes in   continents.items():
        total_troops = 0
        owned_by_others = 0
        for node in nodes:
            if   G.nodes[node].get('owner') != '0':
                total_troops +=   G.nodes[node].get('troops', 0)
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

    return sorted_continents

def calculate_continent_groups(territories_list):
    con = list(  continents.keys())
    continent_groups = {}

    for continent in con:
        continent_territories = set(  continents[continent])
        my_continent_territories = set(territories_list) & continent_territories
        portion = len(my_continent_territories) / len(continent_territories)
        
        # # Calculate the total troops in my territories for this continent
        # total_troops = sum(  G.nodes[node]['troops']/len(continent_territories) for node in my_continent_territories)
        
        # Combine portion and total troops into a single score, for example by adding them
        score = portion #+ total_troops
        
        continent_groups[continent] = score

    # Sort by the combined score in descending order
    sorted_continent_groups = sorted(continent_groups.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_continent_groups

def find_border_nodes(group):
    border_nodes = []
    for node in group:
        for neighbor in G.neighbors(node):
            if neighbor not in group:
                border_nodes.append(node)
                break
    return border_nodes

def shortest_path_to_border(group, start_node):
    if start_node not in group:
        return None

    border_nodes = find_border_nodes(group)
    shortest_path = None

    for border_node in border_nodes:
        path = nx.shortest_path(G, source=start_node, target=border_node)
        if shortest_path is None or len(path) < len(shortest_path):
            shortest_path = path

    return shortest_path


m = calculate_continent_groups(my_territories)
n = nexus()
print(n)