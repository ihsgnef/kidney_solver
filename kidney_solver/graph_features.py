import count_cycles_and_chains

MAX_CYCLE = 3
MAX_CHAIN = 3

#GraphFeatures accepts a DynamicKidneyGraph and generates features for the graph, which it returns as dictionary.
#USAGE: GraphFeatures(dynamicGraph).create_dictionary()
class GraphFeatures:

    def __init__(self, graph):
        self.graph = graph #graph is of type DynamicKidneyGraph
        #these are the features that will be generated for the graph
        self.indegrees = 0
        self.outdegrees = 0
        self.high_outdegree = 0
        self.high_indegree = 0
        self.centrality = 0 # ~~~How would one do this without networkx?~~~
        self.num_vertices = len(self.graph.get_digraph_vertices())
        self.num_cycles = sum(self.calculate_cycles()) # can break this up by amount of each length of cycle as well
        self.num_chains =  0#self.calculate_chains() # ~~~ need to update to calculate_chains when ndd issue resolved~~~

        #populate the features
        self.calculate_degrees()

        #kidney related features will be added later i.e
        # num of AB donors, location similarlity of donors+recipients, insurance similarity, etc.

    #finds avg and max edges of vertex in the graph
    def calculate_degrees(self):

        avg_incoming =  0. #~~~float so decimal values aren't lost, or perhaps int would be better~~~
        avg_outgoing = 0.
        max_incoming = 0
        max_outgoing = 0

        #go through each vertex and calculate number of edges ~~~ how can I access edges from vertex? ~~~
        for v in self.graph.get_digraph_vertices():
            # calculate in-bound vertices for each vertex
            incoming = 0
            for other_v in self.graph.get_digraph_vertices():
                try:
                    if self.graph.digraph_edge_exists(other_v, v):
                        incoming += 1
                except:
                    pass
            outgoing = len(self.graph.get_digraph_edges(v)) #calculate out-bound
            avg_incoming += incoming
            avg_outgoing += outgoing
            if incoming > max_incoming:
                max_incoming = incoming
            if outgoing > max_outgoing:
                max_outgoing = outgoing

        #set object variables to average and max
        if len(self.graph.get_digraph_vertices()) > 0:
            self.indegrees = avg_incoming/ len(self.graph.get_digraph_vertices())
            self.outdegrees = avg_outgoing / len(self.graph.get_digraph_vertices())

        self.high_indegree = max_incoming
        self.high_outdegree = max_outgoing

    def calculate_cycles(self):
        return count_cycles_and_chains.count_cycles(self.graph.digraph, MAX_CYCLE)

    def calculate_chains(self):
        return count_cycles_and_chains.count_chains(self.graph.digraph, self.graph.get_ndds(), MAX_CHAIN)

    #~~~How to do this~~~
    def calculate_centrality(self):
        pass

    def create_dictionary(self, graph_flag=True):
        feature_dict = dict()

        #enumerating variables for flexibility in the future
        #~~~SHOULD THIS BE CONVERTED INTO A LIST OF FEATURES WHERE FEAT 1 = indegrees, FEAT 2= out, etc...~~~
        if graph_flag:
            feature_dict['indegrees'] = self.indegrees
            feature_dict['outdegrees'] = self.outdegrees
            #feature_dict['centrality'] = self.centrality  ~~~not yet implemented
            feature_dict['max_in'] = self.high_indegree
            feature_dict['max_out'] = self.high_outdegree
            feature_dict['num_vertices'] = self.num_vertices
            feature_dict['num_cycles'] = self.num_cycles
            feature_dict['num_chains'] = self.num_chains

        #if kidney_flag...

        return feature_dict