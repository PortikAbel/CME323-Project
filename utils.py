import networkx as nx

def dist_to_root(point,root,Graph):
    path = nx.shortest_path(Graph, source = root, target = point)
    return (len(path)-1)

