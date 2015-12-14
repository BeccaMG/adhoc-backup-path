# !/bin/python
# ##########################################################
# First implementation of the RIP algorithm to get familiar.
# ##########################################################

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import Queue


def generate_rip_graph(draw_flag):
    """
    Creates a weighted graph with a random number of nodes and weights. The graph is constructed using
    Barabasi-Albert algorithm with distance matrices in every node to use in the RIP algorithm

    :param draw_flag:
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
    n_graph = nx.barabasi_albert_graph(number_nodes, 2, seed=None)

    # Random weights
    weights = np.random.random_integers(low=low_edge, high=high_edge, size=n_graph.number_of_edges())
    for i, (n1, n2) in enumerate(n_graph.edges()):
        n_graph[n1][n2]['weight'] = weights[i]

    pos = nx.spring_layout(n_graph)

    # Add a distance matrix to all the nodes
    n = n_graph.number_of_nodes()
    for i in range(0, n):
        new_distance_matrix = np.zeros((n, n))
        new_distance_matrix[i].fill(-1)  # Fill with -1 me as destination
        n_graph.node[i]['distance_matrix'] = new_distance_matrix
        n_graph.node[i]['best_weights_vector'] = np.zeros(n)
        n_graph.node[i]['vectors_queue'] = Queue.Queue()

    n_graph.nodes(data=True)

    # ####################################
    # #             OPTIONAL             #                   
    # ####################################
    if draw_flag:
        
        # Labeling the edges with their weights
        edge_labels = {(n1, n2): network_graph[n1][n2]['weight'] for (n1, n2) in network_graph.edges()}
        # Drawing the graph
        nx.draw_networkx(n_graph, pos)
        nx.draw_networkx_edge_labels(n_graph, pos, edge_labels=edge_labels)
        plt.show()
        
    return n_graph


# First iteration of RIP algorithm: All the nodes add their neighbors and 
# weights to their distance matrix
def rip_first_iteration(G):
    for n, d in G.nodes(data=True):
        dm = d['distance_matrix']
        bwv = d['best_weights_vector']
        edges_from_n = G[n].items()
        # print "I am in node %d" % n
        for e, eattr in edges_from_n:
            w = eattr['weight']
            dm[e, e] = w
            bwv[e] = w
        #     print "My weight to %d is %d" % (e, w)
        # print "My matrix"
        # print dm
        # print "My vector"
        # print bwv
   
   
# WORKING ON IT !   
def rip_broadcasting(G):
    for n, d in G.nodes(data=True):
        bwv = d['best_weights_vector']        
        node_enqueue(G, n, bwv)
        # edges_from_n = G[n].items()
        # print "I am in node %d" % n
        # for e, eattr in edges_from_n:
        #     w = eattr['weight']
        #     distance_matrix[e,e] = w
            

# WORKING ON IT !
def node_enqueue(G, n, vector):
    print n, vector
    vq = G.node[n]['vectors_queue']    
    # for i in range(5):
    #     q.put(i)s
    # while not q.empty():
    #     print q.get()


if __name__ == '__main__':
    network_graph = generate_rip_graph(False)

    rip_first_iteration(network_graph)
    rip_broadcasting(network_graph)


    # Testing bellman-ford
    #pred, dist = nx.bellman_ford(network_graph, 1)
    #print sorted(pred.items())
    #print sorted(dist.items())


