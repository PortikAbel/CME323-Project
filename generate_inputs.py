import networkx as nx
from graph_types import *
from numpy.random import normal

CURRENT_TYPE = BARABASI_ALBERT

def generate_barabasi_albert(n, d):
  m = min(n-1, round(normal(n*d, d)))
  return nx.barabasi_albert_graph(n, m)

generator = {
  ERDOS_RENYI: nx.erdos_renyi_graph,
  BARABASI_ALBERT: generate_barabasi_albert,
}

def main():
  n_list = [20, 50, 100, 150, 200]
  d_list = [0.1, 0.3, 0.5, 0.7, 0.9]
  niter = 5

  for i in range(niter):
    for n in n_list:
      for d in d_list:
        G = generator[CURRENT_TYPE](n, d)
        nx.write_adjlist(G, f"inputs/{CURRENT_TYPE}/n{n}_d{d}_{i}.adjlist")

if __name__ == "__main__":
  main()
