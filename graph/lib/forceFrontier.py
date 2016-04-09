# -*- coding: utf-8 -*-
"""
Method n°2 to find the frontier
Calculate a force layout and take the convex hull
"""
import networkx as nx
from scipy.spatial import ConvexHull
import numpy as np

class ForceFrontier:
    def __init__(self):
        pass

    def run(self, infected_graph):
        """
        Assumes that the nodes are identified by integers starting at 1
        """
        pos = nx.spring_layout(infected_graph)
        points = np.zeros((len(pos), 2))
        i = 0
        for p in pos:
            points[i] = pos[p]
            i += 1
            
        hull = ConvexHull(points)
        nodes = list(pos)
        return [nodes[p] for p in hull.vertices]

"""g = nx.Graph()
g.add_nodes_from([1,2,0])
g.add_edges_from([(1, 2), (2, 0), (1, 0)])
f = ForceFrontier()
print f.run(g)"""
