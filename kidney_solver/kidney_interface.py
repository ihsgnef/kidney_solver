import argparse
import time
import random
import copy
import sys
import kidney_ndds
import kidney_ip
import kidney_utils
from dynamic_kidney_graph import DynamicKidneyGraph
from value_iteration import *

class KidneyInterface:

    def __init__(self, graph, cfg, formulation):
        self.digraph = graph
        self.cfg = cfg
        self.formulation = formulation

    def get_legal_actions(self):
        actions = self.solve_kep()
        cy = actions.cycles
        cycle_scores = actions.cycle_scores
        ch = actions.chains
        chain_scores = actions.chain_scores
        cycles = []
        for c in cy:
            cycles.append([self.digraph.digraph_id_name[x.id] for x in c])
        chains = []
        for c in ch:
            chain = [self.digraph.ndd_id_name[c.ndd_index]]
            chain += [self.digraph.digraph_id_name[x] for x in c.vtx_indices]
            chains.append(chain)
        return cycles, cycle_scores, chains, chain_scores

    def add_nodes(self, edges):
        vertices = self.digraph.get_vertices_from_edges(edges)
        if len(vertices) <=2:
            return edges
        v1 = vertices[-1]
        v2 = vertices[-2]
        add = []
        edges_copy = copy.deepcopy(edges)
        for edge in edges:
            src = edge[0]
            trg = edge[1]
            if src == v1 or src ==v2:
                if trg in self.digraph.digraph_name_id.keys():
                    add.append(edge)
                edges_copy.remove(edge)
            if trg == v1 or trg ==v2:
                if src in self.digraph.digraph_name_id.keys():
                    add.append(edge)
                edges_copy.remove(edge)

        self.digraph.add_digraph_edges(add)
        return edges_copy

    def remove_nodes(self):     
        keys = self.digraph.digraph_name_id.keys()
        v = []
        if(len(keys)>2):
            v.append(keys[0])
            v.append(keys[1])
            self.digraph.remove_digraph_vertices(v)
 
    def take_cycle(self, cycle):
        # cycle is a list of vertices
        self.digraph.remove_digraph_vertices(cycle)

    def take_chain(self, chain):

        # chain starts with a ndd and then digraph vertices
        self.digraph.remove_ndd_vertices(chain[:1])
        self.digraph.remove_digraph_vertices(chain[1:])

    def refresh(self):
        ndds = [value for key, value in self.digraph.ndds.items()]
        cfg = kidney_ip.OptConfig(self.digraph.digraph, ndds, args.cycle_cap, 
                              args.chain_cap, args.verbose,
                              args.timelimit, args.edge_success_prob, 
                              args.eef_alt_constraints,
                              args.lp_file, args.relax)
        return KidneyInterface(self.digraph, cfg, args.formulation) 



    def solve_kep(self, formulation='picef', use_relabelled=True):
    
        formulations = {
            "uef":  ("Uncapped edge formulation", kidney_ip.optimise_uuef),
            "eef": ("EEF", kidney_ip.optimise_eef),
            "eef_full_red": ("EEF with full reduction by cycle generation", 
                kidney_ip.optimise_eef_full_red),
            "hpief_prime": ("HPIEF'", kidney_ip.optimise_hpief_prime),
            "hpief_prime_full_red": ("HPIEF' with full reduction by cycle \
                    generation", kidney_ip.optimise_hpief_prime_full_red),
            "hpief_2prime": ("HPIEF''", kidney_ip.optimise_hpief_2prime),
            "hpief_2prime_full_red": ("HPIEF'' with full reduction by cycle \
                    generation", kidney_ip.optimise_hpief_2prime_full_red),
            "picef": ("PICEF", kidney_ip.optimise_picef),
            "cf":   ("Cycle formulation", kidney_ip.optimise_ccf)
        }
        
        if formulation in formulations:
            formulation_name, formulation_fun = formulations[formulation]
            if use_relabelled:
                opt_result = kidney_ip.optimise_relabelled(formulation_fun, 
                        self.cfg)
            else:
                opt_result = formulation_fun(self.cfg)
            kidney_utils.check_validity(opt_result, self.cfg.digraph,
                    self.cfg.ndds, self.cfg.max_cycle, self.cfg.max_chain)
            opt_result.formulation_name = formulation_name
            return opt_result
        else:
            raise ValueError("Unrecognised IP formulation name")


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Solve a kidney-exchange instance")
    parser.add_argument("cycle_cap", type=int,
            help="The maximum permitted cycle length")
    parser.add_argument("chain_cap", type=int,
            help="The maximum permitted number of edges in a chain")
    parser.add_argument("formulation",
            help="The IP formulation (uef, eef, eef_full_red, hpief_prime, \
                    hpief_2prime, hpief_prime_full_red, hpief_2prime_full_red,\
                    picef, cf)")
    parser.add_argument("--use-relabelled", "-r", required=False,
            action="store_true",
            help="Relabel vertices in descending order of in-deg + out-deg")
    parser.add_argument("--eef-alt-constraints", "-e", required=False,
            action="store_true",
            help="Use slightly-modified EEF constraints (ignored for other \
                    formulations)")
    parser.add_argument("--timelimit", "-t", required=False, default=None,
            type=float,
            help="IP solver time limit in seconds (default: no time limit)")
    parser.add_argument("--verbose", "-v", required=False,
            action="store_true",
            help="Log Gurobi output to screen and log file")
    parser.add_argument("--edge-success-prob", "-p", required=False,
            type=float, default=1.0,
            help="Edge success probability, for failure-aware matching. " +
                 "This can only be used with PICEF and cycle formulation.\
                         (default: 1)")
    parser.add_argument("--lp-file", "-l", required=False, default=None,
            metavar='FILE',
            help="Write the IP model to FILE, then exit.")
    parser.add_argument("--relax", "-x", required=False,
            action='store_true',
            help="Solve the LP relaxation.")
            
    args = parser.parse_args()
    args.formulation = args.formulation.lower()

    digraph_edges = []
    digraph_lines = open('example_data/input1').readlines()
    for line in digraph_lines:
        tokens = [x for x in line.split()]
        source = int(tokens[0])
        target = int(tokens[1])
        score = float(tokens[2])
        digraph_edges.append((source, target, score))

    ndd_edges = []
    ndd_lines = open('example_data/ndds1').readlines()
    for line in ndd_lines:
        tokens = [x for x in line.split()]
        source = int(tokens[0])
        target = int(tokens[1])
        score = float(tokens[2])
        ndd_edges.append((source, target, score))
    graph = DynamicKidneyGraph(digraph_edges, ndd_edges)
    ndds = [value for key, value in graph.ndds.items()]

    add_edges = []
    add_lines = open('example_data/input_add1').readlines()
    for line in add_lines:
        tokens = [x for x in line.split()]
        source = int(tokens[0])
        target = int(tokens[1])
        score = float(tokens[2])
        add_edges.append((source, target, score))

    cfg = kidney_ip.OptConfig(graph.digraph, ndds, args.cycle_cap, 
                              args.chain_cap, args.verbose,
                              args.timelimit, args.edge_success_prob, 
                              args.eef_alt_constraints,
                              args.lp_file, args.relax)
    interface = KidneyInterface(graph, cfg, args.formulation) 
    #interface = copy.deepcopy(interface1)
    



    for it in range(10):
        cycles, cycle_scores, chains, chain_scores = interface.get_legal_actions()
        #print " print chains", chains
       # print cycles, cycle_scores,chains, chain_scores
        value_iter = ValueIteratonSolver(interface, cycles, cycle_scores, chains, chain_scores, 0.9, 2, add_edges)
        cycle_action, chain_action = value_iter.choose_action()
        print "number of iter", it
        print 'cycle:', cycle_action, 'chain:', chain_action
        
        interface,add_edges = value_iter.transition(interface, cycle_action, chain_action,add_edges)

        #for i in interface.digraph.digraph.vs:
        #    print i.id
        


    