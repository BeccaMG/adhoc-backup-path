# !/bin/python
# #######################################################################
# RIP algorithm with backup path determined by the least overlapping path
# #######################################################################

import rip_graph_generator as rip_gen
import network_graph as graph_gen
import networkx as nx
import numpy as np
import sys


def least_overlapping_backup_path(G):
    for n, nattr in G.nodes(data=True):
        pp = nattr['primary_paths']
        bp = nattr['backup_paths']
        bnh = nattr['backup_next_hop']
        print "\nCalculating Node = %d" % n
        for m, mattr in G.nodes(data=True):
            if m == n:
                pp.append([])
                bp.append([])
                bnh[m] = None
            else:
                ppx = nx.shortest_path(G, source=n, target=m)
                pp.append(ppx)
                pm = nx.all_simple_paths(G, source=n, target=m)
                # random.shuffle(pm)
                bp.append(get_single_backup(ppx, pm))
                bnh[m] = (bp[m][1])
                sys.stdout.write('.')
                # print "Path Matrix of %d to %d = %s" % (n, m, pm)
            # print "Primary_path of %d to %d = %s" % (n, m, pp[m])
            # print "Backup_path of %d to %d = %s" % (n, m, bp[m])
            # print "Backup_next_hop of %d to %d = %.0f" % (n, m, bnh[m])

        nattr['primary_paths'] = pp
        nattr['backup_paths'] = bp
        nattr['backup_next_hop'] = bnh


def get_single_backup(primary_path, path_matrix):
    # primary_path.extend([(y, x) for (x, y) in primary_path])
    chunk = [(primary_path[i], primary_path[i+1]) for i in range(0, len(primary_path)-1)]
    s2 = set(chunk)
    overlap = sys.maxint
    backup = []
    for path in path_matrix:
        chunk = [(path[i], path[i+1]) for i in range(0, len(path)-1)]
        s1 = set(chunk)
        intersection = s1 & s2
        if len(intersection) < overlap:
            overlap = len(intersection)
            backup = path
            if overlap == 0:
                return backup

    return backup


if __name__ == '__main__':
    network_graph = rip_gen.generate_rip_graph(6)

    np.set_printoptions(precision=1)

    least_overlapping_backup_path(network_graph)

    # Comparing with bellman-ford for testing

    graph_gen.draw_graph(network_graph)
