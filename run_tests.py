from os import makedirs, path
import networkx as nx
import numpy as np
import time
from os import getpid

from blossom_seq import find_maximum_matching as find_mm_seq
from blossom_par import find_maximum_matching as find_mm_par
from graph_types import *

def measure_runtimes_on_graph(filename):
  G = nx.read_adjlist(filename)
  M = nx.Graph()

  a = time.time()
  find_mm_seq(G, M)
  b = time.time()
  seq_result = b - a

  M = nx.Graph()
  pid = getpid()

  a = time.time()
  find_mm_par(pid, G, M)
  b = time.time()
  par_result = b - a

  return seq_result, par_result

def main(CURRENT_TYPE, type_suffix=''):
  assert type_suffix in ['', '_star_1', '_star_2', '_complete']
  assert (CURRENT_TYPE==ERDOS_RENYI and type_suffix=='') or (CURRENT_TYPE==BARABASI_ALBERT and type_suffix!='')

  n_list = [20, 50, 100, 150, 200]
  d_list = [0.1, 0.3, 0.5, 0.7, 0.9]
  niter = 5

  makedirs("results", exist_ok=True)
  seq_results_path_no_ext = f"results/{CURRENT_TYPE}{type_suffix}_seq"
  seq_results_path = seq_results_path_no_ext + '.npy'
  if path.exists(seq_results_path):
    seq_results = np.load(seq_results_path)
  else:
    seq_results = np.zeros((len(d_list),len(n_list),niter))
  
  par_results_path_no_ext = f"results/{CURRENT_TYPE}{type_suffix}_par"
  par_results_path = par_results_path_no_ext + '.npy'
  if path.exists(par_results_path):
    par_results = np.load(par_results_path)
  else:
    par_results = np.zeros((len(d_list),len(n_list),niter))
  
  for i in range(niter):
    iter_start = time.time()
    print("starting round ", i)
    for n in n_list:
      for d in d_list:
        filename = f"inputs/{CURRENT_TYPE}/n{n}_d{d}{type_suffix}_{i}.adjlist"
        if path.exists(filename):
          seq_result, par_result = measure_runtimes_on_graph(filename)
          
          seq_results[d_list.index(d)][n_list.index(n)][i] = seq_result
          par_results[d_list.index(d)][n_list.index(n)][i] = par_result
          print(f"\tsequential test with n={n} d={d} took ", seq_result)
          print(f"\tparallel test with n={n} d={d} took ", par_result)
        else:
          print(f'\tFile does not exists on path: {filename}')
          seq_results[d_list.index(d)][n_list.index(n)][i] = -1
          par_results[d_list.index(d)][n_list.index(n)][i] = -1
    iter_end = time.time()
    np.save(seq_results_path_no_ext, seq_results)
    np.save(par_results_path_no_ext, par_results)
    print(f"Iteration {i} took {iter_end - iter_start}")

  print("final sequential matrix: ", seq_results)
  print("final parallel matrix: ", par_results)
  
if __name__ == '__main__':
  # main(ERDOS_RENYI)
  main(BARABASI_ALBERT, '_star_1')
  main(BARABASI_ALBERT, '_star_2')
  main(BARABASI_ALBERT, '_complete')