import networkx as nx
import copy

from utils import dist_to_root

def seq_is_in_tree(Forest: nx.DiGraph, v: int) -> int:
    for tree_number, tree_in  in enumerate(Forest): 
        if tree_in.has_node(v) == True:
            return tree_number
    return -1

def seq_lift_blossom(blossom, aug_path, v_B, G, M):
    ##Define the L_stem and R_stem
    L_stem = aug_path[0:aug_path.index(v_B)]
    R_stem = aug_path[aug_path.index(v_B)+1:]
    lifted_blossom = [] #stores the path within the blossom to take
    
    # Find base of blossom
    i = 0
    base = None
    base_idx = -1
    blossom_ext = blossom + [blossom[1]] 
    while base == None and i < len(blossom) - 1:
        if not(M.has_edge(blossom[i],blossom[i+1])):
            if not(M.has_edge(blossom[i+1],blossom_ext[i+2])): 
                base = blossom[i+1]
                base_idx = i+1
            else:
                i += 2
        else:
            i += 1
    # if needed, create list of blossom nodes starting at base
    if blossom[0] != base:
        base_idx = blossom.index(base)
        based_blossom = blossom[base_idx:] + blossom[1:base_idx+1]
    else:
        based_blossom = blossom

    # CHECK IF BLOSSOM IS ENDPT
    if L_stem == [] or R_stem == []:
        if L_stem != []:
            if G.has_edge(base, L_stem[-1]):
                # CASE 1:
                # Chuck the blossom
                return L_stem + [base]
            else:
                # CASE 2:
                # find where Lstem is connected
                i = 1
                while (lifted_blossom == []):
                    #assert(i < len(based_blossom)-1)
                    if G.has_edge(based_blossom[i],L_stem[-1]):
                        # make sure we're adding the even part to lifted path
                        if i%2 == 0: # same dir path
                            lifted_blossom = list(reversed(based_blossom))[-i-1:] ####################
                        else: # opposite dir path
                            lifted_blossom = based_blossom[i:]##########################
                    i += 1
                assert len(lifted_blossom) % 2 == 1
                return L_stem + lifted_blossom

        else:
            if G.has_edge(base, R_stem[0]):
                # CASE 1:
                # Chuck the blossom. 
                return [base] + R_stem
            else:
                # CASE 2:
                # find where R_stem is connected
                i = 1
                while (lifted_blossom == []):
                    #assert(i < len(based_blossom)-1)
                    if G.has_edge(based_blossom[i],R_stem[0]):
                        # make sure we're adding the even part to lifted path
                        if i%2 == 0: # same dir path
                            lifted_blossom = based_blossom[:i+1]
                        else: # opposite dir path
                            lifted_blossom = list(reversed(based_blossom))[:-i]
                    i += 1
                assert len(lifted_blossom) % 2 == 1
                return lifted_blossom + R_stem

    else: # blossom is in the middle
        # LIFT the blossom
        # check if L_stem attaches to base
        if M.has_edge(base, L_stem[-1]):
            # find where right stem attaches
            if G.has_edge(base, R_stem[0]):
                # blossom is useless
                return L_stem + [base] + R_stem
            else:
                # blossom needs to be lifted
                i = 1
                while (lifted_blossom == []):
                    # assert(i < len(based_blossom)-1)
                    if G.has_edge(based_blossom[i],R_stem[0]):
                        # make sure we're adding the even part to lifted path
                        if i%2 == 0: # same dir path
                            lifted_blossom = based_blossom[:i+1] 
                        else: # opposite dir path
                            lifted_blossom = list(reversed(based_blossom))[:-i]
                    i += 1
                assert len(lifted_blossom) % 2 == 1
                return L_stem + lifted_blossom + R_stem
        else: 
            # R stem to base is in matching
            # assert(M.has_edge(base, R_stem[0]))
            # check where left stem attaches
            if G.has_edge(base, L_stem[-1]):
                # blossom is useless
                return L_stem + [base] + R_stem
            else:
                # blossom needs to be lifted
                i = 1
                while (lifted_blossom == []):
                    # assert(i < len(based_blossom)-1)
                    if G.has_edge(based_blossom[i],L_stem[-1]):
                        # make sure we're adding the even part to lifted path
                        if i%2 == 0: # same dir path
                            lifted_blossom = list(reversed(based_blossom))[-i-1:] 
                        else: # opposite dir path
                            lifted_blossom = based_blossom[i:] 
                    i += 1
                assert len(lifted_blossom) % 2 == 1
                return L_stem + lifted_blossom + R_stem

def seq_blossom_recursion(G, M, F, v, w):
    # base of the blossom
    b = nx.lowest_common_ancestor(F, v, w)
    # create blossom
    blossom = nx.shortest_path(F, source=b, target=w) + list(reversed(nx.shortest_path(F, source=b, target=v)))

    # assert(len(blossom)%2 == 0)
    # contract blossom into single node b
    contracted_G = copy.deepcopy(G)
    contracted_M = copy.deepcopy(M)
    for node in blossom[:-1]:
        if node != b:
            contracted_G = nx.contracted_nodes(contracted_G, b, node, self_loops=False)
            contracted_M = nx.contracted_nodes(contracted_M, b, node, self_loops=False)

    # recurse
    aug_path = finding_aug_path(contracted_G, contracted_M)

    # check if blossom exists in aug_path 
    if (b in aug_path):
        return seq_lift_blossom(blossom, aug_path, b, G, M)
    else: # blossom is not in aug_path
        return aug_path

def finding_aug_path(G: nx.Graph, M: nx.Graph) -> list[int]:
    Forest: list[nx.DiGraph] = [] #Storing the Forest as list of graphs

    unmarked_edges = list(set(G.edges()) - set(M.edges()))
    Forest_nodes = []
    ## we need a map from v to the tree
    tree_to_root = {} # key=idx of tree in forest, val=root
    root_to_tree = {} # key=root, val=idx of tree in forest
        
    ##List of exposed vertices - ROOTS OF TREES
    exp_vertex = list(set(G.nodes()) - set(M.nodes()))
    
    #List of trees with the exposed vertices as the roots
    for i, v in enumerate(exp_vertex):  
        temp = nx.DiGraph()
        temp.add_node(v)
        Forest.append(temp)
        Forest_nodes.append(v)

        #link each root to its tree
        tree_to_root[i] = v
        root_to_tree[v] = i

    
    for v in Forest_nodes:
        tree_num_of_v = seq_is_in_tree(Forest, v)
        tree_of_v = Forest[tree_num_of_v]
        root_of_v = tree_to_root[tree_num_of_v]

        for e in G.edges(v):
            e2 = (e[1],e[0]) #the edge in the other order
            if (e!=[] and (e in unmarked_edges or e2 in unmarked_edges)):
                w = e[1] # the other vertex of the unmarked edge

                ## check if w in F
                tree_num_of_w = seq_is_in_tree(Forest, w)
                
                if tree_num_of_w == -1:
                    ## w is matched, so add e and w's matched edge to F
                    tree_of_v.add_edge(*e) # edge {v,w}
                    # Note: we don't add w to forest nodes b/c it's odd dist from root
                    #assert(M.has_node(w))
                    edge_w = list(M.edges(w))[0] # get edge {w,x}
                    tree_of_v.add_edge(*edge_w) # add edge{w,x}
                    Forest_nodes.append(edge_w[1]) ## add {x} to the list of forest nodes

                else: ## w is in Forest
                    root_of_w = tree_to_root[tree_num_of_w]
                    tree_of_w = Forest[tree_num_of_w]
                    if dist_to_root(w,root_of_w,tree_of_w)%2 == 0:
                        if (tree_num_of_v != tree_num_of_w):
                            ##Shortest path from root(v)--->v-->w---->root(w)
                            path_in_v = nx.shortest_path(tree_of_v, source = root_of_v, target = v)
                            path_in_w = nx.shortest_path(tree_of_w, source = root_of_w, target = w)
                            return path_in_v + list(reversed(path_in_w))
                        else: ##Contract the blossom
                            return seq_blossom_recursion(G, M, tree_of_w, v, w)
                    # if odd, do nothing.
    ##IF Nothing is Found
    return [] ##Empty Path

def find_maximum_matching(G: nx.Graph, M: nx.Graph):
    P = finding_aug_path(G, M)
    if P == []:#Base Case
        return M
    #Augment P to M
    ##Add the alternating edges of P to M
    for i in range(0, len(P)-2,2): 
        M.add_edge(P[i], P[i+1])
        M.remove_edge(P[i+1], P[i+2])
    M.add_edge(P[-2], P[-1])
    return find_maximum_matching(G, M)

