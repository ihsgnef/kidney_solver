from kidney_digraph import *
from kidney_ndds import *

class DynamicKidneyGraph:

    def __init__(self, digraph_edges, ndd_edges):
        # edges is a list of (source, target, score)
        vertices = self.get_vertices_from_edges(digraph_edges)
        self.digraph_id_name = dict((i, v) for i, v in enumerate(vertices))
        self.digraph_name_id = dict((v, i) for i, v in enumerate(vertices))
        self.digraph = Digraph(len(self.digraph_name_id))
        for edge in digraph_edges:
            source, target, score = edge
            src = self.digraph_name_id[source]
            trg = self.digraph_name_id[target]
            if self.digraph.edge_exists(self.digraph.vs[src], 
                    self.digraph.vs[trg]):
                raise Exception('Duplicate edge!')
            self.digraph.add_edge(score, self.digraph.vs[src], 
                    self.digraph.vs[trg])
        ndds = [e[0] for e in ndd_edges]
        self.ndds = dict((i, Ndd()) for i, v in enumerate(ndds))
        self.ndd_id_name = dict((i, v) for i, v in enumerate(ndds))
        self.ndd_name_id = dict((v, i) for i, v in enumerate(ndds))
        for edge in ndd_edges:
            source, target, score = edge
            src = self.ndd_name_id[source]
            trg = self.digraph.vs[self.digraph_name_id[target]]
            self.ndds[src].add_edge(NddEdge(trg, score))
    
    def get_vertices_from_edges(self, digraph_edges):
        vertices = set([e[0] for e in digraph_edges])
        vertices.update([e[1] for e in digraph_edges])
        return list(vertices)

    def add_digraph_edges(self, digraph_edges):
        vertices = self.get_vertices_from_edges(digraph_edges)
        new_vertices = []
        for v in vertices:
            if v not in self.digraph_name_id:
                new_vertices.append(v)
                self.digraph_name_id[v] = len(self.digraph_name_id)
                self.digraph_id_name[self.digraph_name_id[v]] = v
        for i in range(len(self.digraph.vs)):
            self.digraph.adj_mat[i] += [None] * len(new_vertices)
        new_vs = [Vertex(self.digraph_name_id[i]) for i in new_vertices]
        self.digraph.vs += new_vs
        self.digraph.adj_mat += [[None] * len(self.digraph.vs) for _ in
                range(len(new_vs))]

        for edge in digraph_edges:
            source, target, score = edge
            src = self.digraph_name_id[source]
            trg = self.digraph_name_id[target]
            src_v = self.digraph.vs[src]
            trg_v = self.digraph.vs[trg]
            if self.digraph.adj_mat[src][trg] is not None:
                raise Exception('Duplicate')
            self.digraph.add_edge(score, src_v, trg_v)

    def add_ndd_edges(self, ndd_edges):
        ndds = [e[0] for e in ndd_edges]
        for v in ndds:
            if v not in self.ndd_name_id:
                nid = len(self.ndd_name_id)
                self.ndd_name_id[v] = nid
                self.ndd_id_name[nid] = v
                self.ndds[nid] = Ndd()
        for edge in ndd_edges:
            source, target, score = edge
            src = self.ndd_name_id[source]
            trg = self.digraph.vs[self.digraph_name_id[target]]
            self.ndds[src].add_edge(NddEdge(trg, score))

    def remove_digraph_edges(self, digraph_edges):
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

    def remove_ndd_vertices(self, vertices):
        for v in vertices:
            self.ndds.pop(self.ndd_name_id[v])
