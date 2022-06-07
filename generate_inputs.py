from math import sqrt
import networkx as nx
from os import makedirs
from graph_types import *

class BarabasiAlbertGenerationException(nx.NetworkXError):
  def __init__(self, n, d, initial_type, *args, **kw):
    msg = f'Barabasi Albert graph with {n} nodes {d} density and initial {initial_type} graph is not possible.'
    exception_message = msg
    superinit = super().__init__
    superinit(self, exception_message, *args, **kw)

def m_star_1(n, d):
  return round((n - sqrt((1-2*d)*n**2+2*d*n)) / 2)

def m_star_2(n, d):
  return round((n + sqrt((1-2*d)*n**2+2*d*n)) / 2)

def m_complete(n, d):
  return round((2*n - 1 - sqrt((2*n-1)**2 - 4*d*n*(n+1))) / 2)

def generate_barabasi_albert(n, d, initial_graph_type, m_formula_index=None):
  assert initial_graph_type in ['star', 'complete']
  if initial_graph_type == 'star':
    assert m_formula_index in [1, 2]
    if d > 0.5 and n > 1 + 1/(2*d-1):
      raise BarabasiAlbertGenerationException(n, d, initial_graph_type)
    if m_formula_index == 1:
      if d < (n-0.5)/(n**2+n):
        raise BarabasiAlbertGenerationException(n, d, initial_graph_type)
      m = m_star_1(n, d)
    elif m_formula_index == 2:
      m = m_star_1(n, d)
    return nx.barabasi_albert_graph(n, m)
  elif initial_graph_type == 'complete':
    if n < (3 - d + sqrt(9-d*(9-d))) / 2*d:
      raise BarabasiAlbertGenerationException(n, d, initial_graph_type)
    m = m_complete(n, d)
    return nx.barabasi_albert_graph(n, m, None, nx.complete_graph(m))

def main(CURRENT_TYPE):
  n_list = [20, 50, 100, 150, 200]
  d_list = [0.1, 0.3, 0.5, 0.7, 0.9]
  niter = 5

  makedirs(f"inputs/{CURRENT_TYPE}", exist_ok=True)
  for i in range(niter):
    for n in n_list:
      for d in d_list:
        if CURRENT_TYPE == ERDOS_RENYI:
          G = nx.erdos_renyi_graph(n, d)
          nx.write_adjlist(G, f"inputs/{CURRENT_TYPE}/n{n}_d{d}_{i}.adjlist")
        elif CURRENT_TYPE == BARABASI_ALBERT:
          initial = 'star' #'complete'
          for edge_number_formula in [1, 2]:
            try:
              G = generate_barabasi_albert(n, d, initial, edge_number_formula)
              nx.write_adjlist(G, f"inputs/{CURRENT_TYPE}/n{n}_d{d}_{initial}_{edge_number_formula}_{i}.adjlist")
            except BarabasiAlbertGenerationException:
              pass
          initial = 'complete'
          try:
            G = generate_barabasi_albert(n, d, initial, edge_number_formula)
            nx.write_adjlist(G, f"inputs/{CURRENT_TYPE}/n{n}_d{d}_{initial}_{i}.adjlist")
          except BarabasiAlbertGenerationException:
            pass

if __name__ == "__main__":
  main(ERDOS_RENYI)
  main(BARABASI_ALBERT)
