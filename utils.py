# -*- coding: utf-8 -*-
"""
Created on Mon May  9 11:03:08 2016

@author: sagarvare
"""

import networkx as nx
import numpy as np

def dist_to_root(point,root,Graph):
    path = nx.shortest_path(Graph, source = point, target = root)
    return (len(path)-1)


def generate_random_graph(n,density=0.5):
    ## n - number of nodes
    ## d - "density" of the graph [0,1]
    graph = nx.Graph()
    for i in range(n):
        for j in range(i+1,n):
            if np.random.uniform() < density:
                graph.add_edge(i,j)
    return graph 
