import sys
import networkx as nx
from collections import deque

class KidneyGraph:
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.edge_score = dict()
        self.ndd_vertices = set()
        self.shortest_paths = None

    def add_edge(self, score, source, target, ndd=False):
        self.graph.add_edge(source, target)
        self.edge_score[(source, target)] = score
        if ndd: self.ndd_vertices.add(source)

    def nodes(self):
        return self.graph.nodes()
    
    def edges(self):
        return self.graph.edges()
    
    def edge_score(self, source, target):
        return self.edge_score[(source, target)]

    def find_cycles(self, max_length):
        cycles = nx.simple_cycles(self.graph)
        cycles = [c for c in cycles if len(c) <= max_length]
        return cycles
    
    def edge_exists(self, source, target):
        return self.graph.has_edge(source, target)

    def induced_subgraph(self, vertices):
        return self.graph.subgraph(vertices)

    def out_edges(self, vertex):
        return self.graph.out_edges(vertex)
    
    def update_dists(self):
        self.shortest_paths = nx.shortest_path(self.graph)

    def is_ndd(self, vertex):
        return vertex in self.ndd_vertices


def read_digraph(lines):
    """Reads a digraph from an array of strings in the input format."""
    vtx_count, edge_count = [int(x) for x in lines[0].split()]
    digraph = KidneyGraph()
    for line in lines[1:edge_count+1]:
        tokens = [x for x in line.split()]
        src_id = int(tokens[0])
        tgt_id = int(tokens[1])
        if digraph.edge_exists(src_id, tgt_id):
            raise Exception("Duplicate edge {}, {}".format(src_id, tgt_id))
        score = float(tokens[2])
        digraph.add_edge(score, src_id, tgt_id)
    return digraph

if __name__ == '__main__':
    input_lines = [line for line in sys.stdin if len(line.strip()) > 0]
    n_digraph_edges = int(input_lines[0].split()[1])
    digraph_lines = input_lines[:n_digraph_edges + 2]
    kidney_graph = read_digraph(digraph_lines)
