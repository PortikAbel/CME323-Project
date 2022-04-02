import networkx as nx

def generate(n, d, index):
  G = nx.erdos_renyi_graph(n,d)
  nx.write_adjlist(G, "inputs/ER_n{0}_d{1}_{2}.adjlist".format(n, d, index))

def main():
  n_list = [20, 50, 100, 150, 200]
  d_list = [0.1, 0.3, 0.5, 0.7, 0.9]
  niter = 5

  for i in range(niter):
    for n in n_list:
      for d in d_list:
        generate(n, d, i)

if __name__ == "__main__":
  main()
