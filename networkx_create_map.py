import networkx as nx
# import matplotlib.pyplot as plt

# Create an empty graph
G = nx.Graph()

# Add nodes from 0 to 41
G.add_nodes_from(list(range(42)), num = 0, owner = None)

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

# Find nodes connected to another continent
connected_to_another_continent = []

for u, v in G.edges():
    if G.nodes[u]['group'] != G.nodes[v]['group']:
        connected_to_another_continent.append(u)
        connected_to_another_continent.append(v)

connected_to_another_continent = list(set(connected_to_another_continent))

print("Nodes connected to another continent:", connected_to_another_continent)



# # Calculate degree for each node
# node_degrees = {node: degree for node, degree in nx.degree(G)}

# # Filter nodes where owner is None
# nodes_with_owner_none = [node for node in G.nodes if G.nodes[node]['owner'] is None]

# # Find nodes with the least links (owner=None)
# min_degree = min(node_degrees[node] for node in nodes_with_owner_none)
# nodes_with_min_degree = [node for node in nodes_with_owner_none if node_degrees[node] == min_degree]

# print("Nodes with the least links (owner=None):", nodes_with_min_degree)

# # Find nodes (owner=None) next to those with the least links
# neighbors_with_most_links = []

# for node in nodes_with_min_degree:
#     neighbors = list(G.neighbors(node))
#     neighbors_degrees = [(neighbor, node_degrees[neighbor]) for neighbor in neighbors if G.nodes[neighbor]['owner'] is None]
#     neighbors_sorted_by_degree = sorted(neighbors_degrees, key=lambda x: x[1], reverse=True)
#     if neighbors_sorted_by_degree:
#         neighbors_with_most_links.append(neighbors_sorted_by_degree[0][0])


# Calculate degree for each node
node_degrees = {node: degree for node, degree in nx.degree(G)}

# Filter nodes where owner is None
nodes_with_owner_none = [node for node in G.nodes if G.nodes[node]['owner'] is None]

# Sort nodes by degree in descending order
nexus_nodes = sorted(nodes_with_owner_none, key=lambda node: node_degrees[node], reverse=True)

print("Nodes sorted by degree (owner=None):", nexus_nodes)

# Find nodes (border_nodes) with the minimum links (owner=None)
min_degree = min(node_degrees[node] for node in nodes_with_owner_none)
border_nodes = [node for node in nodes_with_owner_none if node_degrees[node] == min_degree]

print("Border nodes (owner=None) with the minimum links:", border_nodes)

# Find nexus nodes that are connected to border nodes
nexus_connected_to_border = []

for nexus_node in nexus_nodes:
    connected_to_border = [node for node in G.neighbors(nexus_node) if node in border_nodes]
    if connected_to_border:
        nexus_connected_to_border.append((nexus_node, connected_to_border))

print("Nexus nodes connected to border nodes:", nexus_connected_to_border)

# Verify that most connections between nexus and border nodes are owner=None
valid_nexus_nodes = []

for nexus, connected_border in nexus_connected_to_border:
    count_owner_none = sum(1 for neighbor in connected_border if G.nodes[neighbor]['owner'] is None)
    if count_owner_none / len(connected_border) >= 0.5:  # Adjust threshold as needed
        valid_nexus_nodes.append(nexus)

print("Valid nexus nodes with most links to owner=None border nodes:", valid_nexus_nodes)
# useful functions
# print(list(G.nodes)) #all the nodes in a list
# print(list(G.edges)) #list of tuples of connections

# G.nodes[1]['num']=2
# G.nodes[1]['owner']='me'
# print(G.nodes[1]['num'])
# print(G.nodes[1]['owner'])
# print(G.nodes[1]['group'])
# print(G.nodes.data())

# print(G.degree[1]) #same as len(list(G.adj[1]))
# print(list(G.adj[1]))#get how many connections there are and its nodes
# print(len(list(G[1]))) #same as adj[1]
 #get how many connections there are
# pos = nx.spring_layout(G)
# # Draw nodes
# plt.figure(figsize=(12, 12))
# nx.draw_networkx_nodes(G, pos, node_size=500, node_color="skyblue")

# # Draw edges
# nx.draw_networkx_edges(G, pos, edge_color="gray")

# # Draw labels
# nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")

# # Display the plot
# plt.title("NetworkX Graph with Spring Layout")
# plt.axis("off")  # Turn off axis labels
# plt.show()
