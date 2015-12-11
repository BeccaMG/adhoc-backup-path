#!/bin/python
# First implementation of the RIP algorithm to get familiar.

import networkx as nx
import matplotlib.pyplot as plt

network_graph = nx.Graph()
H = nx.path_graph(10)
network_graph.add_nodes_from(H)

#nx.path_graph(10, create_using = nx.DiGraph())
network_graph.add_weighted_edges_from([(1,2,4),(1,3,4),(2,4,4),(3,4,1)])
pred, dist = nx.bellman_ford(network_graph, 1)

pos = nx.spring_layout(network_graph)
#nx.draw_networkx_edge_labels(network_graph,pos)

print sorted(pred.items())
print sorted(dist.items())

nx.draw_networkx(network_graph, pos)
plt.show()