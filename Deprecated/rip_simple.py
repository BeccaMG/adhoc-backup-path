#!/bin/python
# ##########################################
# First implementation of the RIP algorithm.
# ##########################################

# IMPORTANT, DOES NOT DETECT LOOPS

import network_graph as graph_gen
import networkx as nx
import numpy as np
import Queue
import sys

convergence = False


def generate_rip_graph(draw_flag, size):
    """
    :param draw_flag: boolean indicating whether the graph should be drawn or not
    :param size: Integer indicating the size of the graph to be generated
    :return n_graph: the generated graph
    """
    n_graph = graph_gen.generate_graph(size)

    # Add a distance matrix, a best weights vector and a queue to all the nodes
    n = n_graph.number_of_nodes()

    for i in range(0, n):
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

        # Control messages content
        n_graph.node[i]['best_weights_vector'] = new_best_weights_vector
        n_graph.node[i]['buffer_queue'] = Queue.Queue(maxsize=n)

    n_graph.nodes(data=True)

    if draw_flag:
        graph_gen.draw_graph(n_graph)

    return n_graph


# First iteration of RIP algorithm: All the nodes add their neighbors and
# weights to their distance matrix
def rip_first_iteration(G):
    for n, nattr in G.nodes(data=True):  # For each node n and attribute nattr
        dm = nattr['distance_matrix']
        nhv = nattr['default_next_hop']
        bwv = nattr['best_weights_vector']
        bwv[n] = 0
        edges_from_n = G[n].items()  # Obtain all edges from node n
        # print "I am in node %d" % n
        for e, eattr in edges_from_n:  # For each edge-to-node e
            w = eattr['weight']
            dm[e, e] = w
            bwv[e] = w
            nhv[e] = e
            # print "My weight to %d is %d" % (e, w)
            # print "My matrix"
            # print dm
            # print "My vector"
            # print bwv


# Pass the best distances vectors (or best weights vectors to all the neighbors)
def rip_broadcast(G):
    global convergence
    convergence = True
    for n, nattr in G.nodes(data=True):
        bwv = nattr['best_weights_vector']
        edges_from_n = G[n].items()
        for e, eattr in edges_from_n:
            node_enqueue(G, e, n, bwv)  # Pass the info to all its neighbors


# Enqueue on node to receive updates with redundancy
def node_enqueue(G, n1, n0, vector):
    bq = G.node[n1]['buffer_queue']
    pair_to_enqueue = n0, vector
    bq.put(pair_to_enqueue)
    # print "Node %d: Pair: %s" % (n1, pair_to_enqueue)


# Computes all the new distances after broadcast
def rip_update_distance_matrix(G):
    for n, nattr in G.nodes(data=True):
        dm = nattr['distance_matrix']
        nhv = nattr['default_next_hop']
        bwv = nattr['best_weights_vector']
        bq = nattr['buffer_queue']

        while not bq.empty():
            element = bq.get()
            origin_node = element[0]
            received_vector = element[1]  # Received best distance vector from my neighbor
            distance_to_neighbor = dm[origin_node, origin_node]
            # print "Me envian %s desde %d con distancia %d" % (received_vector, origin_node, distance_to_neighbor)
            for i in range(0, len(bwv)):
                # Update the distance to the node via the neighbor
                if i != n:  # If it's not myself
                    old_distance = dm[i, origin_node]
                    new_distance = received_vector[i] + distance_to_neighbor
                    # print "i: %d, n: %d, distance: %d" % (i, n, received_vector[i])
                    if new_distance < old_distance:
                        dm[i, origin_node] = new_distance
                        global convergence
                        convergence = False
                    # Compute if it is the best distance
                    if new_distance < bwv[i]:
                        bwv[i] = new_distance
                        # print "Encontre una mejor distancia a %d desde %d con distancia %d" % (i, origin_node, new_distance)
                        nhv[i] = origin_node
                        global convergence
                        convergence = False

        print "I am in node %d" % n
        print "My matrix"
        print dm
        print "My vector"
        print bwv
        print "\n"


def rip_simple(size):

    net_graph = generate_rip_graph(False, size)

    rip_first_iteration(net_graph)

    while not convergence:
        rip_broadcast(net_graph)
        rip_update_distance_matrix(net_graph)

    return net_graph

if __name__ == '__main__':

    # network_graph = generate_rip_graph(False, 4)
    #
    # rip_first_iteration(network_graph)
    #
    # while not convergence:
    #     rip_broadcast(network_graph)
    #     rip_update_distance_matrix(network_graph)

    network_graph = rip_simple(100)

    # Comparing with bellman-ford for testing
    for n, nattr in network_graph.nodes(data=True):  # For each node n and attribute nattr
        print "Our RIP:"
        print "(%d,%s)" % (n, nattr['best_weights_vector'])
        print "(%d,%s)" % (n, nattr['default_next_hop'])

        pred, dist = nx.bellman_ford(network_graph, n)
        print "Bellman_ford:"
        print sorted(dist.items())
        print sorted(pred.items())
        break

    graph_gen.draw_graph(network_graph)
