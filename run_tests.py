import networkx as nx
import numpy as np
import time

from blossom_seq import find_maximum_matching as find_mm_seq
from blossom_par import find_maximum_matching as find_mm_par
from graph_types import *

def main(CURRENT_TYPE):
  n_list = [20, 50, 100, 150, 200]
  d_list = [0.1, 0.3, 0.5, 0.7, 0.9]
  niter = 5

  seq_results = np.zeros((len(d_list),len(n_list)))
  par_results = np.zeros((len(d_list),len(n_list)))
  
  for i in range(niter):
      iter_start = time.time()
      print("starting round ", i)
      for n in n_list:
          for d in d_list:
              G = nx.read_adjlist(f"inputs/{CURRENT_TYPE}/n{n}_d{d}_{i}.adjlist")
              M = nx.Graph()

              print(f"\t starting sequential test with n={n} d={d}")
              a = time.time()
              find_mm_seq(G, M)
              b = time.time()
              
              seq_results[d_list.index(d)][n_list.index(n)] += b - a
              print("\t\tTook ", b-a)

              M = nx.Graph()

              print(f"\t starting parallel test with n={n} d={d}")
              a = time.time()
              find_mm_par(G, M)
              b = time.time()
              
              par_results[d_list.index(d)][n_list.index(n)] += b - a
              print("\t\tTook ", b-a)
      iter_end = time.time()
      print(f"Iteration {i} took {iter_end - iter_start}")

  seq_results /= float(niter)
  par_results /= float(niter)
  print("final sequential matrix: ", seq_results)
  print("final parallel matrix: ", par_results)
  np.save(f"results/{CURRENT_TYPE}_seq", par_results)
  np.save(f"results/{CURRENT_TYPE}_par", par_results)

if __name__ == '__main__':
  main(ERDOS_RENYI)
  main(BARABASI_ALBERT)