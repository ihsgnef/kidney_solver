import copy

NO_CYCLES = 1
NO_CHAINS = 2
NO_ACTION = 3
HAVE_CY_CH = 0


class ValueIteratonSolver:

  def __init__(self, interface, cycles, cycle_scores, chains, chain_scores, discount, iteration, add_edges):
    self.interface = interface

    self.cycles = cycles
    self.cycle_scores = cycle_scores
    self.chains = chains
    self.chain_scores = chain_scores
    self.discount = discount
    self.values = dict()
    self.iteration = iteration
    self.add_edges = add_edges


  def get_reward(self, cycle, chain):
  	return self.cycle_scores[cycle] + self.chain_scores[chain]


  def get_greedy_action(self, cycles, cycle_scores, chains, chain_scores):
  	#print cycles
    reward = 0 
    cycle = []
    chain = []

    if len(cycle_scores)>0:
      max_cycle = max(cycle_scores)
      cycle = cycles[cycle_scores.index(max_cycle)]
      reward += max_cycle
    if len(chain_scores)>0:
      max_chain = max(chain_scores)
      chain = chains[chain_scores.index(max_chain)]
      reward += max_chain
    return cycle, chain, reward

  def remove_possible_action(self, cycles, chains, cycle, chain, cycle_scores, chain_scores, removed_nodes ):
    if len(cycles)>0:
      cycle_scores.remove(cycle_scores[cycles.index(cycle)])
      cycles.remove(cycle)
      for cy in cycles:
        for vx in cy:
          if vx in removed_nodes and cy in cycles:
            cycle_scores.remove(cycle_scores[cycles.index(cy)])
            cycles.remove(cy)
            break


    if len(chains)>0:
      chain_scores.remove(chain_scores[chains.index(chain)])
      chains.remove(chain)
      for ch in chains:
        for vx in ch:
          if vx in removed_nodes:
            if ch in chains:
              chain_scores.remove(chain_scores[chains.index(ch)])
              chains.remove(ch)
              break

    return cycles, chains, cycle_scores, chain_scores







  def get_future_reward(self, cycle, chain):
    future_reward = 0
    new_interface = copy.deepcopy(self.interface)
    new_cycles = list(self.cycles)
    new_chains = list(self.chains)
    new_cycle_scores = list(self.cycle_scores)
    new_chain_scores = list(self.chain_scores)
    new_interface, new_add_edges, removed_nodes = self.transition(new_interface, cycle, chain, self.add_edges)
    decay_discount = self.discount
    new_cycles, new_chains, new_cycle_scores, new_chain_scores = self.remove_possible_action(new_cycles, new_chains, cycle, chain, new_cycle_scores, new_chain_scores, removed_nodes)


 
    for it in range(self.iteration):
      cycle_action, chain_action, highest_reward = self.get_greedy_action(new_cycles, new_cycle_scores, new_chains, new_chain_scores)
      future_reward = future_reward + decay_discount * highest_reward
      new_interface, new_add_edges, removed_nodes = self.transition(new_interface, cycle_action, chain_action, new_add_edges)
      new_cycles, new_chains, new_cycle_scores, new_chain_scores = self.remove_possible_action(new_cycles, new_chains, cycle_action, chain_action, new_cycle_scores, new_chain_scores, removed_nodes)
      decay_discount = decay_discount * self.discount

    new_cycles, new_cycle_scores, new_chains, new_chain_scores = new_interface.get_legal_actions()
    action_cycle, action_chain, highest_reward = self.get_greedy_action(new_cycles, new_cycle_scores, new_chains, new_chain_scores)
    future_reward = future_reward + decay_discount * highest_reward




    return future_reward



  def get_values(self):
    

    if len(self.chains) == 0 and len(self.cycles) ==0:
      return NO_ACTION


    if len(self.chains) == 0:
      for cycle_action in range(len(self.cycles)):
        reward = self.cycle_scores[cycle_action]
        future_reward = self.get_future_reward(self.cycles[cycle_action], [])
        q_value = reward + future_reward
        ss =  str(cycle_action)
        self.values[ss] = q_value
      return NO_CHAINS

    if len(self.cycles) ==0:
      for chain_action in range(len(self.chains)):
        reward = self.chain_scores[chain_action]
        future_reward = self.get_future_reward([], self.chains[chain_action])
        q_value = reward + future_reward
        ss =  str(chain_action)
        self.values[ss] = q_value
      return NO_CYCLES

    for cycle_action in range(len(self.cycles)):
      for chain_action in range(len(self.chains)):
        #print cycle_action
        reward = self.get_reward(cycle_action, chain_action)
        future_reward = self.get_future_reward(self.cycles[cycle_action], self.chains[chain_action])
        q_value = reward + future_reward
        ss =  str(cycle_action) + '+' + str(chain_action)
       # print ss

        self.values[ss] = q_value


    return HAVE_CY_CH









  def choose_action(self):
    res = self.get_values()
    if res ==HAVE_CY_CH:
      action = max(self.values, key=lambda p: self.values[p])
      cycle_action, chain_action = action.split('+')
      cycle_action = int(cycle_action)
      chain_action = int(chain_action)
      return self.cycles[cycle_action], self.chains[chain_action]
    elif res == NO_CHAINS:
      action = max(self.values, key=lambda p: self.values[p])
      return self.cycles[int(action)], [] 
    elif res == NO_CYCLES:
      action = max(self.values, key=lambda p: self.values[p])
      return [], self.chains[int(action)]
    else:
      return [], []





  def transition(self, new_interface, cycles, chains, add_edges):
    #for chain in chains:
    #print cycles
    new_add_edges = new_interface.add_nodes(add_edges)
    #new_interface =  new_interface.refresh()
    if len(cycles) >0:
      new_interface.take_cycle(cycles)
    if len(chains) >0:
      new_interface.take_chain(chains)

    #for cycle in cycles:
    removed_nodes = new_interface.remove_nodes()
    new_interface =  new_interface.refresh()
    return new_interface, new_add_edges, removed_nodes











  



