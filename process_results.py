import numpy as np 
import matplotlib.pyplot as plt
from graph_types import *

SEQ = 'seq'
PAR = 'par'

def load_result(graph_type, algo_type):
  return np.load(f'results/{graph_type}_{algo_type}.npy')

def main():
  n_list = [20, 50, 100, 150, 200]
  d_list = [0.1, 0.3, 0.5, 0.7, 0.9]
  n_rows = len(d_list)
  n_cols = 2
  n_boxes = len(n_list)

  for fig_index, graph_type in enumerate([ERDOS_RENYI, BARABASI_ALBERT]):
    fig = plt.figure(fig_index)
    fig.suptitle(graph_type)
    axs = fig.subplots(n_rows, n_cols)

    for column_index, algo_type in enumerate([SEQ, PAR]):
      result = load_result(graph_type, algo_type)
      for row_index, result_by_density in enumerate(result):
        ax = axs[row_index][column_index]
        ax.boxplot(result_by_density)
        ax.set_title(f'{algo_type}: {d_list[row_index]}')
        ax.set_yscale('log')
        ax.set_xticks(list(range(1, n_boxes+1)))
        ax.set_xticklabels(n_list)

  plt.show()

if __name__ == "__main__":
  main()