from .graph import Graph

class WeightedDirectedGraph(Graph):
    def __init__(self):
        self.graph = {}  # Dictionary where keys are nodes and values are lists of connected edges

    def add_edge(self, source, target, weight, **metadata):
        """
        Adds a directed edge from source to target with a given weight and optional metadata. 
        """
        if source not in self.graph:
            self.graph[source] = []
        self.graph[source].append((target, weight, metadata))

    def get_edges(self, node):
        """
        Returns a list of edges (target, weight, metadata) connected to a given node.
        """
        return self.graph.get(node, [])

    def get_weight(self, source, target):
        """
        Returns the weight of the edge between source and target.
        """
        for edge in self.graph.get(source, []):
            if edge[0] == target:
                return edge[1]
        return None  # Edge not found
    
    def get_metadata(self, source, target):
        """
        Returns the metadata associated with the edge between source and target.
        """
        for edge in self.graph.get(source, []):
            if edge[0] == target:
                return edge[2]
        return None  # Edge not found
    
    