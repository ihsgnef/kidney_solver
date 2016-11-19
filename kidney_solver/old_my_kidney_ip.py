from gurobipy import *

class OptSolution(object):
    """An optimal solution for a kidney-exchange problem instance.
    
    Data members:
        ip_model: The Gurobi Model object
        cycles: A list of cycles in the optimal solution, each represented
            as a list of vertices
        chains: A list of chains in the optimal solution, each represented
            as a Chain object
        total_score: The total score of the solution
    """

    def __init__(self, ip_model, cycles, chains, digraph, edge_success_prob=1):
        self.ip_model = ip_model
        self.cycles = cycles
        self.chains = chains
        self.digraph = digraph
        self.total_score = (sum(c.score for c in chains) +
                sum(failure_aware_cycle_score(c, digraph, edge_success_prob) for c in cycles))
        self.edge_success_prob = edge_success_prob

    def display(self):
        """Print the optimal cycles and chains to standard output."""

        print "cycle_count: {}".format(len(self.cycles))
        print "chain_count: {}".format(len(self.chains))
        print "cycles:"
        # cs is a list of cycles, with each cycle represented as a list of vertex IDs
        # cs = [[v.id for v in c] for c in self.cycles]
        cs = self.cycles
        # Put the lowest-indexed vertex at the start of each cycle
        for i in range(len(cs)):
            min_index_pos = cs[i].index(min(cs[i]))
            cs[i] = cs[i][min_index_pos:] + cs[i][:min_index_pos]
        # Sort the cycles
        cs.sort()
        for c in cs:
            print "\t".join(str(v_id) for v_id in c)
        print "chains:"
        for c in self.chains:
            print str(c.ndd_index) + "\t" + "\t".join(str(v) for v in c.vtx_indices)

    def relabelled_copy(self, old_to_new_vertices, new_digraph):
        """Create a copy of the solution with vertices relabelled.

        If the solution was found on a relabelled copy of the instance digraph, this
        method can be used to transform the solution back to the original digraph. Each
        Vertex v in the OptSolution on which this method is called is replaced in the
        returned copy by old_to_new_vertices[v.id].
        """

        relabelled_cycles = [[old_to_new_vertices[v.id] for v in c] for c in self.cycles]
        relabelled_chains = [Chain(c.ndd_index,
                                   [old_to_new_vertices[i].id for i in c.vtx_indices],
                                   c.score)
                             for c in self.chains]
        return OptSolution(self.ip_model, relabelled_cycles, relabelled_chains,
                           new_digraph, self.edge_success_prob)

def create_ip_model(time_limit, verbose):
    m = Model("kidney-mip")
    if not verbose:
        m.params.outputflag = 0
    m.params.mipGap = 0
    if time_limit is not None:
        m.params.timelimit = time_limit
    return m

def failure_aware_cycle_score(cycle, graph, edge_success_prob):
    l = len(cycle)
    score = sum(graph.edge_score[(cycle[i], cycle[(i+1)%l])] for i in range(l))
    score *= edge_success_prob**l
    return score

def optimize_picef(graph, max_cycle, max_chain, edge_success_prob=1.0,
        time_limit=None, verbose=False):
    m = create_ip_model(time_limit, verbose)
    m.params.method = 2
    cycles = graph.find_cycles(max_cycle)
    cycle_vars = [m.addVar(vtype=GRB.BINARY) for _ in cycles]
    m.update()

    vtx_to_vars = [[] for _ in graph.nodes()]
    
    edge_vars = dict()
    v_grb_vars_in = dict()
    v_grb_vars_out = dict()

    if max_chain > 0:
        for v in graph.nodes():
            v_grb_vars_in[v] = [[] for i in range(max_chain - 1)]
            v_grb_vars_out[v] = [[] for i in range(max_chain - 1)]
        for ndd in graph.ndd_vertices:
            ndd_edge_vars = []
            for e in graph.out_edges(ndd):
                edge_var = m.addVar(vtype=GRB.BINARY)
                edge_vars[e.eid] = edge_var
                ndd_edge_vars.append(edge_var)
                vtx_to_vars[e.target].append(edge_var)
                if max_chain > 1:
                    v_grb_vars_in[e.target][0].append(edge_var)
            m.update()
            m.addConstr(quicksum(ndd_edge_vars) <= 1)

    dist_from_ndd = dict()
    for v in graph.nodes():
        if graph.is_ndd(v):
            continue
        sd = 9999999
        for ndd in graph.ndd_vertices:
            if ndd not in graph.shortest_paths:
                continue
            if v in graph.shortest_paths[ndd]:
                d = min([len(x) for x in graph.shortest_paths[ndd][v]])
                sd = d if d < sd else sd
        dist_from_ndd[v] = sd
    
    e_grb_vars = dict()
    e_grb_var_positions = dict()
    for e in graph.edges():
        if graph.is_ndd(e[0]):
            continue
        e_grb_vars[e] = []
        e_grb_var_positions[e] = []
        for i in range(max_chain - 1):
            if dist_from_ndd[e[0]] <= i + 1:
                edge_var = m.addVar(vtype=GRB.BINARY)
                e_grb_vars[e].append(edge_var)
                e_grb_var_positions.append(i + 1)
                vtx_to_vars[e.target].append(edge_var)
                v_grb_vars_out[e[0]][i].append(edge_var)
                if i < max_chain - 2:
                    e_grb_vars[e.target][i + 1].append(edge_var)
    m.update()

    for i in range(max_chain - 1):
        for v in graph.nodes():
            m.addConstr(quicksum(v_grb_vars_in[v][i]) >= \
                    quicksum(v_grb_vars_out[v][i]))

    for i, c in enumerate(cycles):
        for v in c:
            vtx_to_vars[v].append(cycle_vars[i])

    for i in vtx_to_vars:
        if len(i) > 0:
            m.addConstr(quicksum(i) <= 1)

    if max_chain == 0:
        obj_expr = quicksum(failure_aware_cycle_score(c, graph,
            edge_success_prob) * var for c, var in zip(cycles, cycle_vars))
    else:
        obj_expr = (quicksum(failure_aware_cycle_score(c, graph,
            edge_success_prob) * var for c, var in zip(cycles, cycle_vars)) +
            quicksum(graph.edge_score[e] * edge_success_prob * edge_vars[e]
                for ndd in graph.ndd_vertices for e in graph.out_edges(ndd)) +
            quicksum(graph.edge_score[e] * edge_success_prob ** (pos + 1) * var
                for e in graph.edges() for var, pos in zip(e_grb_vars[e],
                    e_grb_var_positions[e])))

    m.setObjective(obj_expr, GRB.MAXIMIZE)
    m.optimize()

    return OptSolution(ip_model=m,
                       cycles=[c for c, v in zip(cycles, cycle_vars) if v.x > 0.5],
                       chains=[] if max_chain==0 else kidney_utils.get_optimal_chains(
                            cfg.digraph, cfg.ndds, cfg.edge_success_prob),
                       digraph=graph,
                       edge_success_prob=edge_success_prob)
