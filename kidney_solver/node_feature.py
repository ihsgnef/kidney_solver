
class NodeFeatures:

	 def __init__(self, graph, vx):
	 	self.graph = graph
	 	self.indegree = 0
	 	self.outdegree = 0
	 	self.vx = vx
	 	self.wait_time = 0

	 	self.calculate_degrees()



	 def calculate_degrees(self):
	 	incoming =0
	 	outgoing =0
	 	for other_v in self.graph.get_digraph_vertices():
	 		if self.graph.digraph_edge_exists(other_v, self.vx):
	 			incoming += 1
	 	outgoing = len(self.graph.get_digraph_edges(self.vx))

	 	self.indegree = incoming
	 	self.outdegree = outgoing



	 def create_dictionary(self):
	 	feature_dict = dict()
	 	feature_dict['node_indegree'] = self.indegree
	 	feature_dict['node_outdegree'] = self.outdegree
	 	return feature_dict


	 def update_wait_time(self):
	 	self.wait_time = self.wait_time + 1

