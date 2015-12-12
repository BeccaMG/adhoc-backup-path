# !/bin/python
# First implementation of the RIP algorithm to get familiar.
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

network_graph = nx.Graph()
# Choosing random number of nodes between 5 and 15
number_nodes = np.random.randint(5, 15)

network_graph.add_node(0, table=[])

# Creating a random graph wih barabasi-albert with
network_graph = nx.barabasi_albert_graph(number_nodes, 2, seed=None)
# Assigning random weights to the edges
weights = np.random.random_integers(low=1, high=10, size=len(network_graph.edges()))
for i, (n1, n2) in enumerate(network_graph.edges()):
    network_graph[n1][n2]['weight'] = weights[i]

pos = nx.spring_layout(network_graph)

for i in range(0, len(network_graph.nodes())):
    network_graph.node[i]['Table'] = [[] for x in range(0, len(network_graph.neighbors(i)))]
    network_graph.nodes(data=True)

print network_graph.nodes(data=True)

# Labelling the edges with their weights
edge_labels = {(n1, n2): network_graph[n1][n2]['weight'] for (n1, n2) in network_graph.edges()}

# Testing bellman-ford
pred, dist = nx.bellman_ford(network_graph, 1)
print sorted(pred.items())
print sorted(dist.items())

# Drawing the graph
nx.draw_networkx(network_graph, pos)
nx.draw_networkx_edge_labels(network_graph, pos, edge_labels=edge_labels)
plt.show()
