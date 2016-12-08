import copy
import random
from util import Counter
import statistics


NO_CYCLES = 1
NO_CHAINS = 2
NO_ACTION = 3
HAVE_CY_CH = 0



class ValueIteratonSolver:
    def __init__(self, interface, cycles, cycle_scores, chains, chain_scores, discount, curr_iter, weight, add_edges):
        self.interface = interface
        self.cycles = cycles
        self.cycle_scores = cycle_scores
        self.chains = chains
        self.chain_scores = chain_scores
        self.discount = discount
        self.iter = curr_iter
        self.weight = weight
        self.add_edges = add_edges
        self.alpha = 0.2


    def rescale(self, features):
        mean = statistics.mean(features.values())
        std = statistics.stdev(features.values())
        for fea in features.keys():
            features[fea] = (features[fea] - mean )/ std 
        return features



    def extract_features(self, vx):
        graph_features = self.interface.get_graph_features()
        node_features = self.interface.get_node_features(vx)
        graph_features.update(node_features)

        graph_features = self.rescale(graph_features)

        return graph_features



    def get_qvalue(self, vx):
        value = 0
        features = self.extract_features(vx)
        for fea in features.keys():
            value = value + self.weight[fea] * features[fea]
            #print "ssss"
            #print self.weight[fea]
            #print fea
            #print features[fea]
            #raw_input()
        return value

    def transition(self, new_interface, cycles, chains, add_edges):
        new_add_edges = new_interface.add_nodes(add_edges)
        for cycle in cycles:
            new_interface.take_cycle(cycle)
        for chain in chains:
            new_interface.take_chain(chain)
        removed_nodes = new_interface.remove_nodes(self.iter)
        new_interface =  new_interface.refresh()
        return new_interface, self.weight, new_add_edges, removed_nodes



    def update(self, q_value, vx):
        new_interface = copy.deepcopy(self.interface)
        features = self.extract_features(vx)
        new_interface, ww, new_add_edges, removed_nodes = self.transition(new_interface, [], [], self.add_edges )
        new_cycles, new_cycle_scores, new_chains, new_chain_scores = new_interface.get_legal_actions()
        score =0
        for cycle in new_cycles:
            if vx in cycle:
                score = new_cycle_scores[new_cycles.index(cycle)]/len(cycle)
                break
        for chain in new_chains:
            if vx in chain[1:]:
                score = new_chain_scores[new_chains.index(chain)]/len(chain)
                break
        correction = self.discount * score - q_value
        for fea in features.keys():
            self.weight[fea] = self.weight[fea] + self.alpha * correction* features[fea]





    def choose_action(self):
    	cycle_list = []
    	chain_list = []
    	for cycle in self.cycles:
            is_remove = 0
            for vx in cycle:
                immed_reward = self.cycle_scores[self.cycles.index(cycle)] * 1.0 / len(cycle)

                future_reward = self.get_qvalue(vx)
                #print "feature reward", future_reward
                #print "immed reward", immed_reward
                self.update(future_reward, vx)
                if immed_reward > future_reward:
                    is_remove = is_remove + 1
                elif immed_reward == future_reward:
                    is_remove = is_remove + 0
                else:
                    is_remove = is_remove - 1

            if is_remove ==len(cycle):
                cycle_list.append(cycle)

    	for chain in self.chains:
            is_remove = 0
            for vx in chain[1:]:
                immed_reward = self.chain_scores[self.chains.index(chain)] * 1.0 / len(chain)
                future_reward = self.get_qvalue(vx)
                self.update(future_reward, vx)
                if immed_reward > future_reward:
                    is_remove = is_remove + 1
                elif immed_reward == future_reward:
                    is_remove = is_remove + 0
                else:
                    is_remove = is_remove - 1
            #print is_remove
            if is_remove == len(chain)-1:
                chain_list.append(chain)

        return cycle_list, chain_list
    			







