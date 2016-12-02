from kidney_digraph import *
from kidney_ndds import *

class DynamicKidneyGraph:

    def __init__(self, digraph_edges, ndd_edges):
        '''
        Initialize a kidney graph.
        Args:
            digraph_edges: list of [source, target, score]
            ndd_edges: list of [ndd source, digraph target, score]
        '''
        new_vertices = self._get_vertices_from_edges(digraph_edges)
        self.digraph_id_name = dict((i, v) for i, v in enumerate(new_vertices))
        self.digraph_name_id = dict((v, i) for i, v in enumerate(new_vertices))
        self.digraph = Digraph(len(self.digraph_name_id))
        for edge in digraph_edges:
            source, target, score = edge
            source = self.digraph_name_id[source]
            target = self.digraph_name_id[target]
            if self.digraph.edge_exists(self.digraph.vs[source], 
                                        self.digraph.vs[target]):
                raise Exception('Duplicate edge!')
            self.digraph.add_edge(score, self.digraph.vs[source],
                                         self.digraph.vs[target])

        new_ndds = [e[0] for e in ndd_edges]
        self.ndds = dict((i, Ndd()) for i, v in enumerate(new_ndds))
        self.ndd_id_name = dict((i, v) for i, v in enumerate(new_ndds))
        self.ndd_name_id = dict((v, i) for i, v in enumerate(new_ndds))
        for edge in ndd_edges:
            source, target, score = edge
            source = self.ndd_name_id[source]
            target = self.digraph.vs[self.digraph_name_id[target]]
            self.ndds[source].add_edge(NddEdge(target, score))

    def get_digraph_vertices(self):
        '''
        Get the list of digraph vertices in names.
        '''
        return self.digraph_name_id.keys()

    def get_ndds(self):
        '''
        Get the list of ndds in names.
        '''
        return self.ndd_name_id.keys()


    def digraph_edge_exists(self, source, target):
        '''
        Given names of the source and target vertices, check if edge exists.
        '''
        source = self.digraph_name_id[source]
        source = self.digraph_name_id[target]
        return self.digraph.edge_exists(self.digraph.vs[src], 
                                        self.digraph.vs[trg])

    def ndd_edge_exists(self, source, target):
        '''
        Given the names of source ndd and target vertex, check if edge exists.
        '''
        source = self.ndd_name_id[source]
        source_ndd = self.ndds[source]
        target = self.digraph_name_id[target]
        target_vertex = self.digraph.vs[target]
        for edge in source_ndd.edges:
            if edge.target_v == target_vertex:
                return True
        return False

    def get_digraph_edges(self, source):
        '''
        Get all out-going edges from a vertex given its name.
        Return: a list of (target vertex name, score)
        '''
        source = self.digraph.vs[self.digraph_name_id[source]]
        edge_list = []
        for edge in source.edges:
            target = self.digraph_id_name[edge.tgt.id]
            score = edge.score
            edge_list.append((target, score))
        return edge_list


    def get_ndd_edges(self, source):
        '''
        Get all out-going edges from a ndd given its name.
        Return: a list of (target vertex name, score)
        '''
        source = self.ndds[self.ndd_name_id[source]]
        edge_list = []
        for edge in source.edges:
            target = self.digraph_id_name[edge.target_v.id]
            score = edge.score
            edge_list.append((target, score))
        return edge_list

    def add_digraph_edges(self, digraph_edges):
        '''
        Add edges to digraph, with potential new vertices.
        Args:
            digraph_edges: list of [source, target, score]
        '''
        vertices = self._get_vertices_from_edges(digraph_edges)
        new_vertices = []
        for v in vertices:
            if v not in self.digraph_name_id:
                new_vertices.append(v)
                self.digraph_name_id[v] = len(self.digraph_name_id)
                self.digraph_id_name[self.digraph_name_id[v]] = v
        # expand the adjacent matrix
        for i in range(len(self.digraph.vs)):
            self.digraph.adj_mat[i] += [None] * len(new_vertices)
        new_vs = [Vertex(self.digraph_name_id[i]) for i in new_vertices]
        self.digraph.vs += new_vs
        self.digraph.adj_mat += [[None] * len(self.digraph.vs) for _ in
                range(len(new_vs))]

        for edge in digraph_edges:
            source, target, score = edge
            source = self.digraph_name_id[source]
            target = self.digraph_name_id[target]
            source_v = self.digraph.vs[source]
            target_v = self.digraph.vs[target]
            if self.digraph.adj_mat[source][target] is not None:
                raise Exception('Duplicate')
            self.digraph.add_edge(score, source_v, target_v)

    def add_ndd_edges(self, ndd_edges):
        '''
        Add edges to digraph, with potential new ndds but no new vertices.
        Args:
            ndd_edges: list of [source, target, score]
        '''
        ndds = [e[0] for e in ndd_edges]
        for v in ndds:
            if v not in self.ndd_name_id:
                nid = len(self.ndd_name_id)
                self.ndd_name_id[v] = nid
                self.ndd_id_name[nid] = v
                self.ndds[nid] = Ndd()
        for edge in ndd_edges:
            source, target, score = edge
            source = self.ndd_name_id[source]
            target = self.digraph.vs[self.digraph_name_id[target]]
            self.ndds[source].add_edge(NddEdge(target, score))

    def remove_digraph_edges(self, digraph_edges):
        '''
        Remove a set of edges from the digraph.
        '''
        for edge in digraph_edges:
            if len(edge) == 2:
                source, target = edge
            elif len(edge) == 3:
                source, target, _ = edge
            src_id = self.digraph_name_id[source]
            trg_id = self.digraph_name_id[target]
            for e in self.digraph.es:
                if e.src.id == src_id and e.tgt.id == trg_id:
                    self.digraph.es.remove(e)
                    self.digraph.adj_mat[src_id][trg_id] = None
                    break

    def remove_ndd_edges(self, ndd_edges):
        '''
        Remove a set of ndd edges.
        '''
        for edge in ndd_edges:
            if len(edge) == 2:
                source, target = edge
            elif len(edge) == 3:
                source, target, _ = edge
            src = self.ndd_name_id[source]
            trg = self.digraph.vs[self.digraph_name_id[target]]
            for e in self.ndds[src].edges:
                if e.target_v == trg:
                    self.ndds[src].edges.remove(e)
                    break

    def remove_digraph_vertices(self, vertices):
        '''
        Remove vertices from the graph, and all connecting edges.
        Graph is reconstructed in the method.
        '''
        digraph_id_name = dict()
        digraph_name_id = dict()
        for v in self.digraph_name_id.keys():
            if v not in vertices:
                digraph_name_id[v] = len(digraph_name_id)
                digraph_id_name[digraph_name_id[v]] = v
        new_graph = Digraph(len(digraph_name_id))
        for e in self.digraph.es:
            src = self.digraph_id_name[e.src.id]
            trg = self.digraph_id_name[e.tgt.id]
            if src in digraph_name_id and trg in digraph_name_id:
                src = new_graph.vs[digraph_name_id[src]]
                trg = new_graph.vs[digraph_name_id[trg]]
                new_graph.add_edge(e.score, src, trg)
        for vid, v in self.ndds.items():
            edges = []
            for e in v.edges:
                trg_name = self.digraph_id_name[e.target_v.id]
                if trg_name in digraph_name_id:
                    trg_id = digraph_name_id[trg_name]
                    edges.append(NddEdge(new_graph.vs[trg_id], e.score))
            v.edges = edges
        
        self.digraph = new_graph
        self.digraph_id_name = digraph_id_name
        self.digraph_name_id = digraph_name_id

    def remove_ndd_vertices(self, ndds):
        '''
        Remove a set of ndds.
        '''
        for ndd in ndds:
            self.ndds.pop(self.ndd_name_id[ndd])

    def _get_vertices_from_edges(self, digraph_edges):
        '''
        Helper to get all the vertices in a set of edges.
        '''
        vertices = set([e[0] for e in digraph_edges])
        vertices.update([e[1] for e in digraph_edges])
        return list(vertices)
    
    def find_cycles(self, max_length):
        cycles_vertices = [c for c in self.digraph.generate_cycles(max_length)]
        cycles_names = []
        for cycle in cycles_vertices:
            cycles_names.append([self.digraph_id_name[x.id] for x in cycle])
        return cycles_names
