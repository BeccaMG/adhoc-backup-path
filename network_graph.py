import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def generate_graph():
    """
    Creates a weighted graph with a random number of nodes and weights. The graph is constructed using
    Barabasi-Albert algorithm.

    :return n_graph: the generated graph
    """

    # Minimum and Maximum number of nodes in the generated graph
    min_nodes = 3
    max_nodes = 5

    # Lowest and highest possible values for the edges' weights
    low_edge = 1
    high_edge = 10

    # Create the graph with 2 edges added to any new node and random number of
    # nodes in [min, max] using Barabasi-Albert
    number_nodes = np.random.randint(min_nodes, max_nodes)
    # number_nodes = 3
    n_graph = nx.barabasi_albert_graph(number_nodes, 2, seed=None)

    # Random weights
    weights = np.random.random_integers(low=low_edge, high=high_edge, size=n_graph.number_of_edges())
    for i, (n1, n2) in enumerate(n_graph.edges()):
        n_graph[n1][n2]['weight'] = weights[i]

    return n_graph


def draw_graph(n_graph):
    pos = nx.spring_layout(n_graph)
    # Labeling the edges with their weights
    edge_labels = {(n1, n2): n_graph[n1][n2]['weight'] for (n1, n2) in n_graph.edges()}
    # Drawing the graph
    nx.draw_networkx(n_graph, pos)
    nx.draw_networkx_edge_labels(n_graph, pos, edge_labels=edge_labels)
    plt.show()