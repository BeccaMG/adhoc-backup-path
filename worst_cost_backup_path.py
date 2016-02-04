# !/bin/python
# ###########################################################
# RIP algorithm with backup path determined by the WORST COST
# ###########################################################

# IMPORTANT, DOES NOT DETECT LOOPS

import networkx as nx
import network_graph as graph_gen
import numpy as np
import Queue
import sys
import heapq

convergence = False

def generate_rip_graph(draw_flag, size):
    """
    :param draw_flag:
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
        new_backup_next_hop_vector = np.empty(n)
        new_backup_next_hop_vector.fill(None)
        
        n_graph.node[i]['distance_matrix'] = new_distance_matrix
        n_graph.node[i]['default_next_hop'] = new_default_next_hop_vector
        n_graph.node[i]['backup_next_hop'] = new_backup_next_hop_vector
        
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

        for e, eattr in edges_from_n:  # For each edge-to-node e
            w = eattr['weight']
            dm[e, e] = w
            bwv[e] = w
            nhv[e] = e


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
            received_vector = element[1] # Received best distance vector from my neighbor
            distance_to_neighbor = dm[origin_node, origin_node]

            for i in range(0, len(bwv)):
                # Update the distance to the node via the neighbor
                if i != n:  # If it's not myself
                    old_distance = dm[i, origin_node]                    
                    new_distance = received_vector[i] + distance_to_neighbor

                    if new_distance < old_distance:
                        dm[i, origin_node] = new_distance
                        global convergence
                        convergence = False

                    # Compute if it is the best distance
                    if new_distance < bwv[i]:
                        bwv[i] = new_distance
                        nhv[i] = origin_node
                        global convergence
                        convergence = False
                        
                        
# WORST COST
def set_backup_next_hop(G):
    for n, nattr in G.nodes(data=True):  # For each node n and attribute nattr
        dm = nattr['distance_matrix']
        nhv = nattr['default_next_hop']
        bnhv = nattr['backup_next_hop']
        
        for i in range(0, G.number_of_nodes()):
            if i != n:
                array = np.array(dm[i,:])  # This destination in the distance matrix
                worst_distance = np.max(array[array < sys.maxint])
                result = np.where(array == worst_distance)[0]
                bnhv[i] = result[0]
                
                # If unluckily there is just one different from infinity or two with same distance
                if bnhv[i] == nhv[i] and len(result) <= 1:
                    bnhv[i] = None
                elif bnhv[i] == nhv[i]:
                    bnhv[i] = result[1]                 
        



if __name__ == '__main__':    
    
    network_graph = generate_rip_graph(False, 6)
    np.set_printoptions(precision=1)

    rip_first_iteration(network_graph)

    while not convergence:
        rip_broadcast(network_graph)
        rip_update_distance_matrix(network_graph)
        
    set_backup_next_hop(network_graph)

    #Comparing with bellman-ford for testing
    for n, nattr in network_graph.nodes(data=True):  # For each node n and attribute nattr
        print n
        print nattr['distance_matrix']
        print nattr['best_weights_vector']
        print nattr['default_next_hop']
        print nattr['backup_next_hop']

        print "\n"
        
        #for i in range(0, network_graph.number_of_nodes()):
            #print "All shortest (%d,%d)" % (n, i)
            #print ([p for p in nx.all_shortest_paths(network_graph,source=n,weight='weight')])

    graph_gen.draw_graph(network_graph)

