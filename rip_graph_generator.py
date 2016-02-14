#!/usr/bin/python
# ####################################################
# Generator of a RIP graph with backup path structures
# ####################################################

# IMPORTANT, DOES NOT DETECT LOOPS

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import Queue
import sys
import heapq


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


def rip_graph(size):
    """
    :param draw_flag: boolean indicating whether the graph should be drawn or not
    :param size: Integer indicating the size of the graph to be generated
    :return n_graph: the generated graph
    """
    n_graph = generate_graph(size)

    # Add a distance matrix, a best weights vector and a queue to all the nodes
    n = n_graph.number_of_nodes()

    for i in range(0, n):
        # #################################################################
        # ##################     The primary path       ###################
        # #################################################################
        new_distance_matrix = np.empty((n, n))
        new_distance_matrix.fill(sys.maxint)
        new_distance_matrix[i].fill(-1)  # Fill with -1 me as destination
        new_distance_matrix[:, i] = -1  # Fill with -1 me as path

        new_best_weights_vector = np.empty(n)
        new_best_weights_vector.fill(sys.maxint)

        new_default_next_hop_vector = np.empty(n)
        new_default_next_hop_vector.fill(None)        

        n_graph.node[i]['distance_matrix'] = new_distance_matrix
        n_graph.node[i]['default_next_hop'] = new_default_next_hop_vector
        
        
        # #################################################################
        # ###################       The backup path     ###################
        # #################################################################
        new_backup_next_hop_vector = np.empty(n)
        new_backup_next_hop_vector.fill(None)
        new_default_path = []
        new_backup_path = []
        
        for k in range(0, n):
            new_default_path.append('N/A')
            new_backup_path.append('N/A')

        n_graph.node[i]['backup_next_hop'] = new_backup_next_hop_vector
        n_graph.node[i]['primary_path'] = new_default_path
        n_graph.node[i]['backup_path'] = new_backup_path
        
        
        # Control messages content
        n_graph.node[i]['best_weights_vector'] = new_best_weights_vector
        n_graph.node[i]['buffer_queue'] = Queue.Queue(maxsize=n)
        
        global convergence
        convergence = False

    n_graph.nodes(data=True)

    return n_graph


# First iteration of RIP algorithm: All the nodes add their neighbors and
# weights to their distance matrix
def rip_first_iteration(G):
    for n, nattr in G.nodes(data=True):  # For each node n and attribute nattr
        dm = nattr['distance_matrix']
        nhv = nattr['default_next_hop']
        bwv = nattr['best_weights_vector']
        pp = nattr['primary_path']
        bwv[n] = 0
        pp[n] = []
        
        edges_from_n = G[n].items()  # Obtain all edges from node n
        
        for e, eattr in edges_from_n:  # For each edge-to-node e
            w = eattr['weight']
            dm[e, e] = w
            bwv[e] = w
            nhv[e] = e
            pp[e] = [e]


# Pass the best distances vectors (or best weights vectors to all the neighbors)
def rip_broadcast(G):
    global convergence
    convergence = True
    for n, nattr in G.nodes(data=True):
        bwv = nattr['best_weights_vector']
        pp = nattr['primary_path']
        edges_from_n = G[n].items()
        for e, eattr in edges_from_n:
            node_enqueue(G, e, n, bwv, pp)  # Pass the info to all its neighbors


# Enqueue on node to receive updates with redundancy
def node_enqueue(G, n1, n0, vector, path):
    bq = G.node[n1]['buffer_queue']
    path_to_enq = []
    for (i, p) in enumerate(path):
        if p != 'N/A':
            path_to_enq.append([n0])
            path_to_enq[i].extend(p)
        else:
            path_to_enq.append(p)
    to_enqueue = n0, vector, path_to_enq
    bq.put(to_enqueue)


# Computes all the new distances after broadcast
def rip_update_distance_matrix(G):
    for n, nattr in G.nodes(data=True):
        dm = nattr['distance_matrix']
        nhv = nattr['default_next_hop']
        bwv = nattr['best_weights_vector']
        bq = nattr['buffer_queue']
        pp = nattr['primary_path']

        while not bq.empty():
            element = bq.get()
            origin_node = element[0]
            received_vector = element[1]  # Received best distance vector from my neighbor
            received_path = element[2]
            distance_to_neighbor = dm[origin_node, origin_node]
            
            for i in range(0, len(bwv)):
                # Update the distance to the node via the neighbor
                if i != n:  # If it's not myself
                    old_distance = dm[i, origin_node]
                    new_distance = received_vector[i] + distance_to_neighbor
                    new_path = received_path[i]
                    
                    if new_distance < old_distance:
                        dm[i, origin_node] = new_distance
                        global convergence
                        convergence = False
                        
                    # Compute if it is the best distance
                    if new_distance < bwv[i]:
                        bwv[i] = new_distance
                        pp[i] = new_path
                        nhv[i] = origin_node
                        global convergence
                        convergence = False


def generate_rip_graph(size):
    
    network_graph = rip_graph(size)
    
    rip_first_iteration(network_graph)
    
    while not convergence:
        rip_broadcast(network_graph)
        rip_update_distance_matrix(network_graph)
        
    return network_graph


if __name__ == '__main__':

    network_graph = generate_rip_graph(10)

    # Comparing with bellman-ford for testing
    for n, nattr in network_graph.nodes(data=True):  # For each node n and attribute nattr
        print "Our RIP:"
        print "(%d,%s)" % (n, nattr['best_weights_vector'])
        print "(%d,%s)" % (n, nattr['default_next_hop'])

        pred, dist = nx.bellman_ford(network_graph, n)
        print "Bellman_ford:"
        print sorted(dist.items())
        print sorted(pred.items())
        #break
        
    draw_graph(network_graph)