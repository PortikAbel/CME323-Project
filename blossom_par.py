from unittest import result
import networkx as nx
import numpy as np
import copy
from multiprocessing import Pool
from functools import partial
import time

from utils import dist_to_root, generate_random_graph

def find_maximum_matching(G: nx.Graph, M: nx.Graph):
    P = finding_aug_path(G, M)
    if P == []: #Base Case
        return M
    else: #Augment P to M

        ##Add the alternating edges of P to M
        for i in range(0, len(P)-2,2): ######## could be parallelized
            M.add_edge(P[i], P[i+1])
            M.remove_edge(P[i+1], P[i+2])
        M.add_edge(P[-2], P[-1])
        return find_maximum_matching(G, M)

def par_is_in_tree(Forest, v):
    for tree_number, tree_in  in enumerate(Forest):  ######## could be parallelized
        if tree_in.has_node(v) == True:
            return tree_number
    return -1

def finding_aug_path(G: nx.Graph, M: nx.Graph, Blossom_stack: list[int] = []) -> list[int]:
    Forest: list[nx.Graph] = [] #Storing the Forest as list of graphs

    unmarked_edges = list(set(G.edges()) - set(M.edges()))
    Forest_nodes = []
    ## we need a map from v to the tree
    tree_to_root = {} # key=idx of tree in forest, val=root
    root_to_tree = {} # key=root, val=idx of tree in forest
        
    ##List of exposed vertices - ROOTS OF TREES
    exp_vertex = list(set(G.nodes()) - set(M.nodes()))
    
    counter = 0
    #List of trees with the exposed vertices as the roots
    for v in exp_vertex:  ######## could be parallelized
        temp = nx.Graph()
        temp.add_node(v)
        Forest.append(temp)
        Forest_nodes.append(v)

        #link each root to its tree
        tree_to_root[counter] = v
        root_to_tree[v] = counter
        counter = counter + 1

    
    for v in Forest_nodes:  
        tree_num_of_v = par_is_in_tree(Forest, v)
        root_of_v = tree_to_root[tree_num_of_v]

        pool = Pool(processes = 4)
        edge_data = list(G.edges(v))
        # Feed the function all global args
        partial_edge_function = partial(edge_function,G,M,Forest,unmarked_edges,tree_to_root,tree_num_of_v,root_of_v,v,Blossom_stack)
        #PARALLEL LOOP!
        temp = pool.map(partial_edge_function, edge_data)
        pool.terminate()

        for case, result in temp: ######## could be parallelized
            if case == 2 or case == 3:
                return result
        # Not CASE 2 or 3
        ## check for blossoms of 3-length
        for case, result in temp: ######## could be parallelized
            if case == 1 and G.has_edge(v, result[1]):
                #contract len 3 blossom
                w = result[0]                
                blossom = [v, w, result[1], v]
                return par_blossom_recursion(G, M, blossom, w, Blossom_stack)

        for case, result in temp:
            if case == 1:
                Forest[tree_num_of_v].add_edge(v,result[0])
                Forest[tree_num_of_v].add_edge(*result)
                Forest_nodes.append(result[1])
                
    return [] #Empty Path
    
def par_lift_blossom(blossom, aug_path, v_B):
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
        based_blossom = blossom[base_idx:] + blossom[:base_idx+1]
    else:
        based_blossom = blossom

    # CHECK IF BLOSSOM IS ENDPT
    if L_stem == [] or R_stem == []:
        if L_stem != []:
            if G.has_edge(base, L_stem[-1]):
                # CASE 1:
                # Chuck the blossom. 
                return L_stem + [base]
            else:
                # CASE 2:
                # find where Lstem is connected
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
                    # assert(i < len(based_blossom)-1)
                    if G.has_edge(based_blossom[i],R_stem[0]):
                        # make sure we're adding the even part to lifted path
                        if i%2 == 0: # same dir path
                            lifted_blossom = based_blossom[:i+1]
                            print(lifted_blossom)
                        else: # opposite dir path
                            lifted_blossom = list(reversed(based_blossom))[:-i]
                    i += 1
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
                            # print(lifted_blossom)
                        else: # opposite dir path
                            lifted_blossom = list(reversed(based_blossom))[:-i]
                            # print(lifted_blossom)
                    i += 1
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
                return L_stem + list((lifted_blossom)) + R_stem

def par_blossom_recursion(G, M, blossom, w, Blossom_stack):
    # contract blossom into single node w
    contracted_G = copy.deepcopy(G)
    contracted_M = copy.deepcopy(M)
    for node in blossom[0:len(blossom)-1]:
        if node != w:
            contracted_G = nx.contracted_nodes(contracted_G, w, node, self_loops=False)
            if node in contracted_M.nodes(): 
                edge_rm = list(M.edges(node))[0] #this will be exactly one edge
                contracted_M.remove_node(node)
                contracted_M.remove_node(edge_rm[1])
                # assert(len(list(contracted_M.nodes()))%2 == 0)
    # add blossom to our stack
    Blossom_stack.append(w)

    # recurse
    aug_path = finding_aug_path(contracted_G, contracted_M, Blossom_stack)

    # check if blossom exists in aug_path 
    v_B = Blossom_stack.pop()
    if (v_B in aug_path):
        return par_lift_blossom(blossom, aug_path, v_B)
    else: # blossom is not in aug_path
        return aug_path

def edge_function(G,M,Forest,unmarked_edges,tree_to_root,tree_num_of_v,root_of_v,v,Blossom_stack,e):
    e2 = (e[1],e[0]) #the edge in the other order
    if (e!=[] and (e in unmarked_edges or e2 in unmarked_edges)):
        w = e[1] # the other vertex of the unmarked edge

        tree_num_of_w = par_is_in_tree(Forest, v)

        if tree_num_of_w == -1:
            ## w is matched, so add e and w's matched edge to F
            Forest[tree_num_of_v].add_edge(e[0],e[1]) # edge {v,w} 
            # Note: we don't add w to forest nodes b/c it's odd dist from root
            # assert(M.has_node(w))
            edge_w = list(M.edges(w))[0] # get edge {w,x}
            return (1,edge_w) ## store to add to forest after parallel for

        else: ## w is in Forest
            root_of_w = tree_to_root[tree_num_of_w]
            tree_of_w = Forest[tree_num_of_w]
            if dist_to_root(w,root_of_w,Forest[tree_num_of_w])%2 == 0:
                if (tree_num_of_v != tree_num_of_w):
                    ##Shortest path from root(v)--->v-->w---->root(w)
                    path_in_v = nx.shortest_path(Forest[tree_num_of_v], source = root_of_v, target = v)
                    path_in_w = nx.shortest_path(Forest[tree_num_of_w], source = w, target = root_of_w)
                    return (2,path_in_v + path_in_w)
                else: ##Contract the blossom
                    # create blossom
                    blossom = nx.shortest_path(tree_num_of_w, source=v, target=w)
                    blossom.append(v)
                    return (3, par_blossom_recursion(G, M, blossom, w, Blossom_stack))
            else:   #CASE 4
                return (4,0)     

if __name__ == '__main__':
    n_list = [20, 50, 100, 150, 200]
    d_list = [0.3, 0.5, 0.7, 0.9]
    niter = 5

    results = np.ndarray((len(d_list),len(n_list)))
    results.fill(0)
    
    for i in range(niter):
        iter_start = time.time()
        print("starting round ", i)
        for n in n_list:
            for d in d_list:
                print("\t starting n=",n,"d=",d)
                G = generate_random_graph(n,d)
                M = nx.Graph()
                Blossom_stack = []
                a = time.time()
                MM = find_maximum_matching(G, M)
                b = time.time()
                results[d_list.index(d)][n_list.index(n)] += b - a
                print("\t\tTook ", b-a)
        iter_end = time.time()
        print("Iteration ", i, " took ", iter_end - iter_start)

    results /= float(niter)
    print("final matrix: ",results)
    np.save("results/par_results", results)

    
    sparse_results = np.ndarray((1,len(n_list)))
    sparse_results.fill(0)
    for i in range(niter):
        print("starting iteration ", i)
        iter_start = time.time()
        for n in n_list:
            print("\t with n =",n)
            G = generate_random_graph(n,0.1)
            M = nx.Graph()
            a = time.time()
            MM = find_maximum_matching(G, M)
            b = time.time()
            sparse_results[0][n_list.index(n)] += b - a
            print("\t\ttook ", b-a)
        iter_end = time.time()
        print("Iteration ", i, " took ", iter_end - iter_start)
    
    sparse_results /= float(niter)
    print(sparse_results)
    np.save("results/sparse_par_results", sparse_results)



                    
                            
        