from sys import argv
import numpy as np 
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
from graph_types import *

SEQ = 'seq'
PAR = 'par'

def load_result(folder_name, graph_type, algo_type):
  return np.load(f'results/{folder_name}/{graph_type}_{algo_type}.npy')

def main(graph_type):
  n_list = ['20', '50', '100', '150', '200']
  d_list = ['0.1', '0.3', '0.5', '0.7', '0.9']
  n_boxes = len(n_list)

  result_map = []
  for algo_type in [SEQ, PAR]:
    result_map.append(load_result('using_map', graph_type, algo_type))
  result_imap_unordered = []
  for algo_type in [SEQ, PAR]:
    result_imap_unordered.append(load_result('imap_unordered', graph_type, algo_type))
  result_proc_lim = []
  for algo_type in [SEQ, PAR]:
    result_proc_lim.append(load_result('process_limitation', graph_type, algo_type))

  if graph_type == ERDOS_RENYI:
    graph_type_text = 'Erdős-Rényi modellű'
  elif graph_type == BARABASI_ALBERT + '_star_1':
    graph_type_text = 'Barabási-Albert modellű, csillaggráfból (m=m_1) induló'
  elif graph_type == BARABASI_ALBERT + '_star_2':
    graph_type_text = 'Barabási-Albert modellű, csillaggráfból (m=m_2) induló'
  elif graph_type == BARABASI_ALBERT + '_complete':
    graph_type_text = 'Barabási-Albert modellű, teljes gráfból induló'

  for i, result in enumerate([result_map, result_imap_unordered, result_proc_lim]):
    fig = plt.figure(i)
    fig.suptitle(graph_type)
    axs = fig.subplots(1, 4)
    axs[0].sharey(axs[1])

    for i_n, n in enumerate(n_list):
      table = [
        '\\begin{table}[H]',
        '\t\\centering',
        '\t\\begin{tabular}{| c || c | c | c |}',
        '\t\t\\hline',
        '\t\td & szekvenciális futási idő & párhuzamos futási idő & arány \\\\',
        '\t\t\\hline\\hline'
      ]
      for i_d, d in enumerate(d_list):
        table.append(f'\t\t{d} & {np.mean(result[0][i_d][i_n]):.3f} & {np.mean(result[1][i_d][i_n]):.3f} & {np.mean(result[0][i_d][i_n] / result[1][i_d][i_n]):.3f} \\\\')
        table.append('\t\t\\hline')
      table.append('\t\\end{tabular}')

      table.append(f'\t\\caption{{futási idők n={n} csúcsú {graph_type_text} véletlengráfokon}}')
      table.append(f'\t\\label{{table:v{i+1}_{graph_type}_n{n}}}')
      table.append('\\end{table}')
      with open(f'results/tables/v{i+1}_{graph_type}_n{n}.tex', 'w', encoding='utf-8') as fout:
        fout.write('\n'.join(table))

    def redraw_results_with_density(d):
      for column_index, algo_type in enumerate([SEQ, PAR]):
        ax = axs[column_index]
        ax.set_yscale('linear')
        ax.cla()
        ax.boxplot(result[column_index][d_list.index(d)].transpose())
        ax.set_yscale('log')
        ax.set_title(f'{algo_type}: d={d}')
        ax.set_xticks(list(range(1, n_boxes+1)))
        ax.set_xticklabels(n_list)
      ax = axs[2]
      ax.set_yscale('linear')
      ax.cla()
      ax.boxplot((result[0][d_list.index(d)] / result[1][d_list.index(d)]).transpose())
      ax.set_yscale('log')
      ax.set_title(f'seq/par: d={d}')
      ax.set_xticks(list(range(1, n_boxes+1)))
      ax.set_xticklabels(n_list)

      plt.draw()

    redraw_results_with_density(d_list[0])
    axs[3].set_title('Select density')
    radio_button = RadioButtons(axs[3], d_list)
    radio_button.on_clicked(redraw_results_with_density)

  plt.show()

if __name__ == "__main__":
  usage = f'''Usage: {argv[0]} graph_type'''
  if len(argv) < 2:
    print('Missing arguments')
    print(usage)
    exit()

  if 'er' == argv[1]:
    graph_type = ERDOS_RENYI
  elif 'ba-s1' == argv[1]:
    graph_type = BARABASI_ALBERT + '_star_1'
  elif 'ba-s2' == argv[1]:
    graph_type = BARABASI_ALBERT + '_star_2'
  elif 'ba-c' == argv[1]:
    graph_type = BARABASI_ALBERT + '_complete'
  else:
    print(usage)
    exit()

  main(graph_type)
