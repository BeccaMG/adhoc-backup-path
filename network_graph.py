import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def generate_graph(size):
    """
    Creates a weighted graph with size number of nodes and random weights. 
    The graph is constructed using Barabasi-Albert algorithm.
    :param size:
    :returns n_graph: the generated graph
    """

    # Lowest and highest possible values for the edges' weights
    low_edge = 1
    high_edge = 10

    # Create a Barabasi-Albert graph with the passed size and
    # 2 edges added to any new node
    n_graph = nx.barabasi_albert_graph(size, 2, seed=None)

    # Random weights with values between low_edge and high_edge
    weights = np.random.random_integers(low=low_edge, high=high_edge, size=n_graph.number_of_edges())
    for i, (n1, n2) in enumerate(n_graph.edges()):
        n_graph[n1][n2]['weight'] = weights[i]

    return n_graph


def draw_graph(n_graph):
    """
    Prints the graph to the terminal with the edges labelled by their weights
    :param n_graph:
    """
    pos = nx.spring_layout(n_graph)
    # Labeling the edges with their weights
    edge_labels = {(n1, n2): n_graph[n1][n2]['weight'] for (n1, n2) in n_graph.edges()}
    # Drawing the graph
    nx.draw_networkx(n_graph, pos)
    nx.draw_networkx_edge_labels(n_graph, pos, edge_labels=edge_labels)
    plt.show()
