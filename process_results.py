from sys import argv
import numpy as np 
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
from graph_types import *

SEQ = 'seq'
PAR = 'par'

def load_result(graph_type, algo_type):
  return np.load(f'results/{graph_type}_{algo_type}.npy')

def main(graph_type, seq_par_separated):
  n_list = ['20', '50', '100', '150', '200']
  d_list = ['0.1', '0.3', '0.5', '0.7', '0.9']
  n_boxes = len(n_list)

  fig = plt.figure()
  fig.suptitle(graph_type)
  if seq_par_separated:
    axs = fig.subplots(1, 3)
    axs[0].sharey(axs[1])
  else:
    axs = fig.subplots(1, 2)

  result = []
  for algo_type in [SEQ, PAR]:
    result.append(load_result(graph_type, algo_type))

  def redraw_results_with_density(d):
    for column_index, algo_type in enumerate([SEQ, PAR]):
      ax = axs[column_index]
      ax.set_yscale('linear')
      ax.cla()
      ax.boxplot(result[column_index][d_list.index(d)])
      ax.set_yscale('log')
      ax.set_title(f'{algo_type}: d={d}')
      ax.set_xticks(list(range(1, n_boxes+1)))
      ax.set_xticklabels(n_list)
      plt.draw()

  def redraw_result_comparision_with_density(d):
    ax = axs[0]
    ax.set_yscale('linear')
    ax.cla()
    ax.boxplot(result[0][d_list.index(d)] / result[1][d_list.index(d)])
    ax.set_yscale('log')
    ax.set_title(f'(sequential runtime) / (parallel runtime): d={d}')
    ax.set_xticks(list(range(1, n_boxes+1)))
    ax.set_xticklabels(n_list)
    plt.draw()

  if seq_par_separated:
    redraw_results_with_density(d_list[0])
    radio_button = RadioButtons(axs[2], d_list)
    radio_button.on_clicked(redraw_results_with_density)
  else:
    redraw_result_comparision_with_density(d_list[0])
    radio_button = RadioButtons(axs[1], d_list)
    radio_button.on_clicked(redraw_result_comparision_with_density)

  plt.show()

if __name__ == "__main__":
  if len(argv) < 3:
    print('Missing arguments')
    print(f'Usage: {argv[0]} er|ba  sep|comp')
    exit()

  if 'er' == argv[1]:
    graph_type = ERDOS_RENYI
  elif 'ba' == argv[1]:
    graph_type = BARABASI_ALBERT
  else:
    print(f'Usage: {argv[0]} er|ba  sep|comp')
    exit()

  if 'sep' == argv[2]:
    separated = True
  elif 'comp' == argv[2]:
    separated = False
  else:
    print(f'Usage: {argv[0]} er|ba sep|comp')
    exit()

  main(graph_type, separated)