# !/bin/python
# ###########################################################
# RIP algorithm with backup path determined by the WORST COST
# ###########################################################

# IMPORTANT, DOES NOT DETECT LOOPS

import rip_graph_generator as rip_gen
import networkx as nx

import numpy as np
import Queue
import sys
import heapq

                        
# WORST COST
def worst_cost_backup_path(G):
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
    
    network_graph = rip_gen.generate_rip_graph(False, 6)
    
    np.set_printoptions(precision=1)
    
    worst_cost_backup_path(network_graph)

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

    rip_gen.draw_graph(network_graph)
