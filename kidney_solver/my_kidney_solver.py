from my_kidney_graph import *
from my_kidney_ip import *

if __name__ == '__main__':
    input_lines = [line for line in sys.stdin if len(line.strip()) > 0]
    n_digraph_edges = int(input_lines[0].split()[1])
    digraph_lines = input_lines[:n_digraph_edges + 2]
    d = read_digraph(digraph_lines)
    cycles = d.find_cycles(3)
    # solution = optimize_picef(kidney_graph, 3, 0, 0.9, None, False)
    # solution.display()
