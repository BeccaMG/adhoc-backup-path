# !/bin/python
# #################################################################
# RIP algorithm with backup path determined by the SECOND BEST COST
# #################################################################

# IMPORTANT, DOES NOT DETECT LOOPS

import network_graph as graph_gen
import networkx as nx
import numpy as np
import Queue
import sys
import heapq

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
        # #################################################################
        # The primary path
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

        # Control messages content
        n_graph.node[i]['best_weights_vector'] = new_best_weights_vector
        n_graph.node[i]['buffer_queue'] = Queue.Queue(maxsize=n)

        # #################################################################
        # The backup path
        # #################################################################

        new_path_matrix = [[]]  # A 2d array which will contain all possible paths to all nodes of the graph

        new_default_path = []
        for k in range(0, n):
            new_default_path.append('N/A')

        new_backup_path = np.empty(n)
        new_backup_path.fill(None)

        n_graph.node[i]['path_matrix'] = new_path_matrix
        n_graph.node[i]['primary_path'] = new_default_path
        n_graph.node[i]['backup_path_index'] = new_backup_path
        n_graph.node[i]['path_buffer_queue'] = Queue.Queue()

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
        pm = nattr['path_matrix']
        pp = nattr['primary_path']
        bwv[n] = 0
        pp[n] = []
        edges_from_n = G[n].items()  # Obtain all edges from node n
        # print "I am in node %d" % n
        for e, eattr in edges_from_n:  # For each edge-to-node e
            w = eattr['weight']
            dm[e, e] = w
            bwv[e] = w
            nhv[e] = e
            pm.append([e])
            pp[e] = [e]
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
        pm = nattr['path_matrix']
        pp = nattr['primary_path']
        edges_from_n = G[n].items()
        for e, eattr in edges_from_n:
            node_enqueue(G, e, n, bwv, pp)  # Pass the info to all its neighbors
            for path in pm:
                if e not in path:
                    path_enqueue(G, e, n, path)


# Enqueue on node to receive updates with redundancy
def path_enqueue(G, n1, n0, path):
    pbq = G.node[n1]['path_buffer_queue']
    path_to_enqueue = [n0]
    path_to_enqueue.extend(path)
    pbq.put(path_to_enqueue)
    # print "Node %d: Pair: %s" % (n1, pair_to_enqueue)


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
    # print "Node %d: Pair: %s" % (n1, pair_to_enqueue)


# Computes all the new distances after broadcast
def rip_update_distance_matrix(G):
    for n, nattr in G.nodes(data=True):
        dm = nattr['distance_matrix']
        nhv = nattr['default_next_hop']
        bwv = nattr['best_weights_vector']
        bq = nattr['buffer_queue']

        pm = nattr['path_matrix']
        pp = nattr['primary_path']
        bpi = nattr['backup_path_index']
        pbq = nattr['path_buffer_queue']

        while not bq.empty():
            element = bq.get()
            origin_node = element[0]
            received_vector = element[1]  # Received best distance vector from my neighbor
            received_path = element[2]
            distance_to_neighbor = dm[origin_node, origin_node]
            # print "Me envian %s desde %d con distancia %d" % (received_vector, origin_node, distance_to_neighbor)
            for i in range(0, len(bwv)):
                # Update the distance to the node via the neighbor
                if i != n:  # If it's not myself
                    old_distance = dm[i, origin_node]
                    new_distance = received_vector[i] + distance_to_neighbor
                    new_path = received_path[i]
                    # print "i: %d, n: %d, distance: %d" % (i, n, received_vector[i])
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

        while not pbq.empty():
            path = pbq.get()
            appended = False
            for i in range(0, len(pm)):
                if len(pm[i]) < len(path):
                    for j in range(0, len(pm[i])):
                        if pm[i][j] != path[j]:
                            break
                        if j == len(pm[i])-1:
                            pm[i] = path
                            appended = True
            if not (appended or path in pm):
                pm.append(path)

        print "I am in node %d" % n
        print "My matrix"
        print dm
        print "My vector"
        print bwv
        print "\n"


# def calculate_backup(G):
#     for n, nattr in G.nodes(data=True):
#         pm = nattr['path_matrix']
#         pp = nattr['primary_path']
#         bpi = nattr['backup_path_index']


if __name__ == '__main__':

    network_graph = generate_rip_graph(False, 4)

    rip_first_iteration(network_graph)

    while not convergence:
        rip_broadcast(network_graph)
        rip_update_distance_matrix(network_graph)

    # Comparing with bellman-ford for testing
    for n, nattr in network_graph.nodes(data=True):  # For each node n and attribute nattr
        # print "Our RIP:"
        # print "(%d,%s)" % (n, nattr['best_weights_vector'])
        # print "(%d,%s)" % (n, nattr['default_next_hop'])
        print "Node %d\n==============" % n
        for m in nattr['primary_path']:
                print "path = %s" % m

        # pred, dist = nx.bellman_ford(network_graph, n)
        # print "Bellman_ford:"
        # print sorted(dist.items())
        # print sorted(pred.items())
        # break

    graph_gen.draw_graph(network_graph)
