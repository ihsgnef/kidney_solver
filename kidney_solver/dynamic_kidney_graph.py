from kidney_digraph import *

class DynamicKidneyGraph:

    def __init__(self, edges):
        # edges is a list of (source, target, score)
        vertices = self.get_vertices_from_edges(edges)
        self.id_name = dict((i, v) for i, v in enumerate(vertices))
        self.name_id = dict((v, i) for i, v in enumerate(vertices))
        self.digraph = Digraph(len(self.name_id))
        for edge in edges:
            source, target, score = edge
            src = self.name_id[source]
            trg = self.name_id[target]
            if self.digraph.edge_exists(self.digraph.vs[src], 
                    self.digraph.vs[trg]):
                raise Exception('Duplicate edge!')
            self.digraph.add_edge(score, self.digraph.vs[src], 
                    self.digraph.vs[trg])
    
    def get_vertices_from_edges(self, edges):
        vertices = set([e[0] for e in edges])
        vertices.update([e[1] for e in edges])
        vertices = list(vertices)
        return vertices

    def reconstruct(self):
        new_graph = Digraph(len(self.name_id))
        for e in self.digraph.es:
            score = e.score
            src = new_graph.vs[e.src.id]
            trg = new_graph.vs[e.tgt.id]
            new_graph.add_edge(score, src, trg)
        self.digraph = new_graph

    def add_edges(self, edges):
        vertices = self.get_vertices_from_edges(edges)
        reconstruct = False
        for v in vertices:
            if v not in self.name_id:
                reconstruct = True
                self.name_id[v] = len(self.name_id)
                self.id_name[self.name_id[v]] = v
        if reconstruct:
            self.reconstruct()
        for edge in edges:
            source, target, score = edge
            src = self.name_id[source]
            trg = self.name_id[target]
            if self.digraph.edge_exists(self.digraph.vs[src], 
                    self.digraph.vs[trg]):
                raise Exception('Duplicate edge!')
            self.digraph.add_edge(score, self.digraph.vs[src], 
                    self.digraph.vs[trg])

    def remove_edges(self, edges):
        for edge in edges:
            if len(edge) == 2:
                source, target = edge
            elif len(edge) == 3:
                source, target, _ = edge
            src_id = self.name_id[source]
            trg_id = self.name_id[target]
            for e in self.digraph.es:
                if e.src.id == src_id and e.tgt.id == trg_id:
                    self.digraph.es.remove(e)
                    self.digraph.adj_mat[src_id][trg_id] = None
                    break

    def remove_vertices(self, vertices):
        id_name = dict()
        name_id = dict()
        for v in self.name_id.keys():
            if v not in vertices:
                name_id[v] = len(name_id)
                id_name[name_id[v]] = v
        new_graph = Digraph(len(name_id))
        for e in self.digraph.es:
            src = self.id_name[e.src.id]
            trg = self.id_name[e.tgt.id]
            if src in name_id and trg in name_id:
                src = new_graph.vs[name_id[src]]
                trg = new_graph.vs[name_id[trg]]
                new_graph.add_edge(e.score, src, trg)
        
        self.digraph = new_graph
        self.id_name = id_name
        self.name_id = name_id

