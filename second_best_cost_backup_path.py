# !/bin/python
# #################################################################
# RIP algorithm with backup path determined by the SECOND BEST COST
# #################################################################

# IMPORTANT, DOES NOT DETECT LOOPS

import rip_graph_generator as rip_gen

import numpy as np
import Queue
import sys
import heapq


# SECOND BEST COST
def second_best_cost_backup_path(G):
    for n, nattr in G.nodes(data=True):  # For each node n and attribute nattr
        dm = nattr['distance_matrix']
        nhv = nattr['default_next_hop']
        bnhv = nattr['backup_next_hop']

        for i in range(0, G.number_of_nodes()):
            if i != n:
                array = np.array(dm[i, :])
                second_best_distance = heapq.nsmallest(3, array)[-1]  # At least 3 nodes

                if second_best_distance < sys.maxint:
                    result = np.where(array == second_best_distance)[0]  # Find the position in the array
                    bnhv[i] = result[0]

                    # If unluckily there are two with the smallest cost
                    if bnhv[i] == nhv[i]:
                        bnhv[i] = result[1]


if __name__ == '__main__':

    network_graph = rip_gen.generate_rip_graph(False, 6)
    
    np.set_printoptions(precision=1)
    
    second_best_cost_backup_path(network_graph)

    # Comparing with bellman-ford for testing
    for n, nattr in network_graph.nodes(data=True):  # For each node n and attribute nattr
        print n
        print nattr['distance_matrix']
        print nattr['best_weights_vector']
        print nattr['default_next_hop']
        print nattr['backup_next_hop']

        print "\n"

        # for i in range(0, network_graph.number_of_nodes()):
        # print "All shortest (%d,%d)" % (n, i)
        # print ([p for p in nx.all_shortest_paths(network_graph,source=n,weight='weight')])

    rip_gen.draw_graph(network_graph)
