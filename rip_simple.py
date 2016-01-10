# !/bin/python
# ##########################################################
# First implementation of the RIP algorithm to get familiar.
# ##########################################################

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import Queue
import sys


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
    #number_nodes = 3
    n_graph = nx.barabasi_albert_graph(number_nodes, 2, seed=None)

    # Random weights
    weights = np.random.random_integers(low=low_edge, high=high_edge, size=n_graph.number_of_edges())
    for i, (n1, n2) in enumerate(n_graph.edges()):
        n_graph[n1][n2]['weight'] = weights[i]

    pos = nx.spring_layout(n_graph)

    # Add a distance matrix, a best weights vector and a queue to all the nodes
    n = n_graph.number_of_nodes()
    for i in range(0, n):
        new_distance_matrix = np.empty((n, n))
        new_distance_matrix.fill(sys.maxint)
        new_distance_matrix[i].fill(-1)  # Fill with -1 me as destination
        new_distance_matrix[:,i] = -1  # Fill with -1 me as path
        new_best_weights_vector = np.empty(n)
        new_best_weights_vector.fill(sys.maxint)
        n_graph.node[i]['distance_matrix'] = new_distance_matrix
        n_graph.node[i]['best_weights_vector'] = new_best_weights_vector
        n_graph.node[i]['vectors_queue'] = Queue.Queue(maxsize=n)

    n_graph.nodes(data=True)

    # ####################################
    # #             OPTIONAL             #                   
    # ####################################
    if draw_flag:
        
        # Labeling the edges with their weights
        edge_labels = {(n1, n2): n_graph[n1][n2]['weight'] for (n1, n2) in n_graph.edges()}
        # Drawing the graph
        nx.draw_networkx(n_graph, pos)
        nx.draw_networkx_edge_labels(n_graph, pos, edge_labels=edge_labels)
        plt.show()
        
    return n_graph


# First iteration of RIP algorithm: All the nodes add their neighbors and 
# weights to their distance matrix
def rip_first_iteration(G):
    for n, nattr in G.nodes(data=True): # For each node n and attribute nattr
        dm = nattr['distance_matrix']
        bwv = nattr['best_weights_vector']
        bwv[n] = 0
        edges_from_n = G[n].items() # Obtain all edges from node n
        #print "I am in node %d" % n
        for e, eattr in edges_from_n: # For each edge-to-node e
            w = eattr['weight']
            dm[e, e] = w
            bwv[e] = w
            #print "My weight to %d is %d" % (e, w)
        #print "My matrix"
        #print dm
        #print "My vector"
        #print bwv
   
   
# Pass the best distances vectors (or best weights vectors to all the neighbors)
def rip_broadcast(G):
    for n, nattr in G.nodes(data=True):
        bwv = nattr['best_weights_vector']  
        edges_from_n = G[n].items()
        for e, eattr in edges_from_n:
            node_enqueue(G, e, n, bwv) # Pass the info to all its neighbors
            
# Enqueue on node to receive updates with redundancy
def node_enqueue(G, n1, n0, vector):
    vq = G.node[n1]['vectors_queue']
    pair_to_enqueue = n0, vector
    vq.put(pair_to_enqueue)
    #print "Node %d: Pair: %s" % (n1, pair_to_enqueue)
 
 
# Computes all the new distances after broadcast
def rip_update_distance_matrix(G):
    for n, nattr in G.nodes(data=True):
        dm = nattr['distance_matrix']
        bwv = nattr['best_weights_vector']
        vq = nattr['vectors_queue']
        while not vq.empty():
            element = vq.get()
            origin_node = element[0]
            vector = element[1] # Received best distance vector from my neighbor
            distance_to_neighbor = dm[origin_node, origin_node]
            #print "Me envian %s desde %d con distancia %d" % (vector, origin_node, distance_to_neighbor)
            for i in range(0, len(bwv)):
                # Update the distance to the node via the neighbor
                if (i != n): # If it's not myself
                    new_distance = vector[i] + distance_to_neighbor
                    #print "i: %d, n: %d, distance: %d" % (i, n, vector[i])
                    dm[i, origin_node] = new_distance
                    # Compute if it is the best distance
                    if new_distance < bwv[i]:
                        bwv[i] = new_distance
        
        #print "I am in node %d" % n
        #print "My matrix"
        #print dm
        #print "My vector"
        #print bwv
        #print "\n"            


if __name__ == '__main__':
    network_graph = generate_rip_graph(True)

    rip_first_iteration(network_graph)
    
    # TODO: Think about a stop condition!!!! - repeat every 30 seconds
    rip_broadcast(network_graph)
    rip_update_distance_matrix(network_graph)
    rip_broadcast(network_graph)
    rip_update_distance_matrix(network_graph)
    rip_broadcast(network_graph)
    rip_update_distance_matrix(network_graph)
    rip_broadcast(network_graph)
    rip_update_distance_matrix(network_graph)


    # Comparing with bellman-ford for testing
    for n, nattr in network_graph.nodes(data=True): # For each node n and attribute nattr
        print "Our RIP:"
        print "(%d,%s)" % (n, nattr['best_weights_vector'])
        
        pred, dist = nx.bellman_ford(network_graph, n)
        #print sorted(pred.items())
        print "Bellman_ford:"
        print sorted(dist.items())


