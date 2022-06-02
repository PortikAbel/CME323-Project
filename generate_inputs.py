import networkx as nx
from os import makedirs
from graph_types import *

def generate_barabasi_albert(n, d):
  m = round((n*(n-1)*d) / (2*(n+1)))
  return nx.barabasi_albert_graph(n, m)

generator = {
  ERDOS_RENYI: nx.erdos_renyi_graph,
  BARABASI_ALBERT: generate_barabasi_albert,
}

def main(CURRENT_TYPE):
  n_list = [20, 50, 100, 150, 200]
  d_list = [0.1, 0.3, 0.5, 0.7, 0.9]
  niter = 5

  makedirs(f"inputs/{CURRENT_TYPE}", exist_ok=True)
  for i in range(niter):
    for n in n_list:
      for d in d_list:
        G = generator[CURRENT_TYPE](n, d)
        nx.write_adjlist(G, f"inputs/{CURRENT_TYPE}/n{n}_d{d}_{i}.adjlist")

if __name__ == "__main__":
  main(ERDOS_RENYI)
  main(BARABASI_ALBERT)
