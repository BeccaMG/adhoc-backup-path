#!/usr/bin/python
# ####################################################
# Generator of a RIP graph with backup path structures
# ####################################################

# IMPORTANT, DOES NOT DETECT LOOPS

import second_best_cost_backup_path as sbp
import worst_cost_backup_path as wbp
import rip_graph_generator as rip_gen
import networkx as nx
import random
import math

def reduce_edges(graph, reduced_graph, percentage):
    number_of_edges_to_delete = int(math.ceil(graph.number_of_edges()*1.0*percentage/100))
    edges_to_delete = random.sample(reduced_graph.edges(), number_of_edges_to_delete)
    reduced_graph.remove_edges_from(edges_to_delete)
    # Being awesome
    #edges_to_delete.extend([(y,x) for (x,y) in edges_to_delete])
    return edges_to_delete


def detect_affected_paths(primary_paths, deleted_edges):    
    s1 = set(deleted_edges)
    src_dest = []
    for path in primary_paths:
        chunk = [(path[i],path[i+1]) for i in range(0, len(path)-1)]  # Awesome chunking
        s2 = set(chunk)
        interception = s1&s2
        if len(interception) != 0:
            print "Detected affected path: %s" % path
            src_dest.append((path[0],path[-1]))
            
    return src_dest
            
            
def check_backup_strategy(graph, source, destination):
    current_node = source
    TTL = graph.number_of_nodes()
    while (current_node != destination and TTL >= 0):
        nhv = graph.node[current_node]['default_next_hop']
        next_hop = nhv[destination]
        print "I am in node %d and to go to %d I should use %d" % (current_node,destination,next_hop)
        if graph.has_edge(current_node, next_hop):
            current_node = next_hop
            TTL = TTL-1
        else:
            bhv = graph.node[current_node]['backup_next_hop']            
            next_hop = bhv[destination]
            if (next_hop != None and graph.has_edge(current_node, next_hop)):
                current_node = next_hop
                TTL = TTL-1
            else:
                print "BIG FAIL"
                break;
    
    if TTL < 0:
        print "BIG FAIL"
    

if __name__ == '__main__':

    print "******** STARTING SMALL EXPERIMENT ********"
    small_network_graph = rip_gen.generate_rip_graph(10)    

    print "\nSetting SECOND BEST COST backup strategy..."
    sbp.second_best_cost_backup_path(small_network_graph)    
    reduced_graph = small_network_graph.subgraph(small_network_graph.nodes())
    deleted_edges = reduce_edges(small_network_graph, reduced_graph, 5)
    print deleted_edges
    
    primary_paths = []
    for k,v in nx.shortest_path(small_network_graph).iteritems():
        for n,m in v.iteritems():
            if len(m) > 1:
                primary_paths.append(m)
            
    #print primary_paths
    
    ap = detect_affected_paths(primary_paths, deleted_edges)
    print ap
    
    global fail_count
    global success_count
    for (s,d) in ap:
        check_backup_strategy(reduced_graph, s, d)
        #break
    
    
    print "First graph: %s " % small_network_graph
    rip_gen.draw_graph(small_network_graph)
    print "Second graph: %s " % reduced_graph
    #rip_gen.draw_graph(reduced_graph)
    
    print "Setting WORST BEST COST backup strategy..."
    #wbp.worst_cost_backup_path(small_network_graph)

    


    
    print "\n\n******** STARTING MEDIUM EXPERIMENT ********"
    medium_network_graph = rip_gen.generate_rip_graph(50)
    print "\n\n******** STARTING BIG EXPERIMENT ********"
    big_network_graph = rip_gen.generate_rip_graph(100)
    
    #for n, nattr in small_network_graph.nodes(data=True):  # For each node n and attribute nattr
        #print n
        #print nattr['distance_matrix']
        #print nattr['best_weights_vector']
        #print nattr['default_next_hop']
        #print nattr['backup_next_hop']

        #print "\n"
    #print nx.shortest_path(small_network_graph)
    #rip_gen.draw_graph(network_graph)
