import argparse
import time
import sys
import kidney_ndds
import kidney_ip
import kidney_utils
from dynamic_kidney_graph import DynamicKidneyGraph

class KidneyInterface:

    def __init__(self, cfg, formulation):
        self.digraph = cfg.digraph
        self.cfg = cfg
        self.formulation = formulation

    def get_legal_actions(self):
        actions = self.solve_kep()
        cycles = actions.cycles
        cycle_scores = actions.cycle_scores
        chains = actions.chains
        chain_scores = actions.chain_scores
        return actions

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
    digraph_lines = open('example_data/input').readlines()
    for line in digraph_lines:
        tokens = [x for x in line.split()]
        source = int(tokens[0])
        target = int(tokens[1])
        score = float(tokens[2])
        digraph_edges.append((source, target, score))

    ndd_edges = []
    ndd_lines = open('example_data/ndds').readlines()
    for line in ndd_lines:
        tokens = [x for x in line.split()]
        source = int(tokens[0])
        target = int(tokens[1])
        score = float(tokens[2])
        ndd_edges.append((source, target, score))
    graph = DynamicKidneyGraph(digraph_edges, ndd_edges)
    ndds = [value for key, value in graph.ndds.items()]

    cfg = kidney_ip.OptConfig(graph.digraph, ndds, args.cycle_cap, 
                              args.chain_cap, args.verbose,
                              args.timelimit, args.edge_success_prob, 
                              args.eef_alt_constraints,
                              args.lp_file, args.relax)
    interface = KidneyInterface(cfg, args.formulation) 
    actions = interface.get_legal_actions()
    actions.display()
