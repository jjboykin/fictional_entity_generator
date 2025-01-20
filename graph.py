class Graph:
    def __init__(self) -> None:
        self.graph: dict = {}
        self.metadata: dict = {}

    def __repr__(self):
        return str(self.graph) + str(self.metadata)
    
    def add_edge(self, node1, node2) -> None:
        if node1 in self.graph:
            self.graph[node1].add(node2)
        else:
            self.graph[node1] = {node2}
        if node2 in self.graph:
            self.graph[node2].add(node1)
        else:
            self.graph[node2] = {node1}

    def add_node(self, node) -> None:
        if node not in self.graph:
            self.graph[node] = set()
    
    def add_metadata(self, node1, node2, metadata: dict) -> None:
        if metadata is not None:
            if (node1, node2) not in self.metadata:
                self.metadata[(node1, node2)] = metadata

    def add_metadata2(self, node1, node2, metadata1: dict = None, metadata2: dict = None) -> None:
        if metadata1 is not None:
            if (node1, node2) not in self.metadata:
                self.add_metadata(node1, node2, metadata1)
        if metadata2 is not None:
            if (node2, node1) not in self.metadata:
                self.add_metadata(node2, node1, metadata2)

    def add_metadata_reciprocal(self, node1, node2, metadata: dict) -> None:
        if metadata is not None:
            if (node1, node2) not in self.metadata:
                self.metadata[(node1, node2)] = metadata
            if (node2, node1) not in self.metadata:
                self.metadata[(node2, node2)] = metadata

    def add(self, node1, node2, metadata1: dict = None, metadata2: dict = None) -> None:
        if node1 not in self.graph:
            self.add_node(node1)

        if node2 not in self.graph:
            self.add_node(node2)
        
        if not self.edge_exists(node1, node2):
            self.add_edge(node1, node2)

        if metadata1 is not None:
            self.add_metadata(node1, node2, metadata1)

        if metadata2 is not None:
            self.add_metadata(node2, node1, metadata2)           

    def add_reciprocal(self, node1, node2, metadata: dict = None) -> None:
        if node1 not in self.graph:
            self.add_node(node1)

        if node2 not in self.graph:
            self.add_node(node2)
        
        if not self.edge_exists(node1, node2):
            self.add_edge(node1, node2)

        if metadata is not None:
            self.add_metadata_reciprocal(node1, node2, metadata)

    def count(self, type=None) -> int:
        if type:
            count:int = 0
            for i in range (0, len(self.graph)):
                if eval(type.value) == self.graph[i]:
                    count += 1
            return count
        else:
            return len(self.graph)

    def edge_exists(self, node1, node2) -> bool:
        if node1 in self.graph and node2 in self.graph:
            return (node2 in self.graph[node1]) and (node1 in self.graph[node2])
        return False
    
    def get_adjacent_nodes(self, node) -> list:
        return list(self.graph[node])
    
    def get_metadata(self, node) -> list:
        metadata = []
        for key, value in self.metadata.items():
            if node in key:
                metadata.append((key, value))
        return metadata

    def unconnected_nodes(self) -> list:
        unconnected = []
        for node, connections in self.graph.items():
            if not connections:
                unconnected.append(node)
        return unconnected
    
    def breadth_first_search(self, node) -> list:
        visited = []
        to_visit = []
        to_visit.append(node)
        while to_visit:
            s = to_visit.pop(0)
            visited.append(s)
            sorted_neighbors = sorted(self.graph[s])
            for neighbor in sorted_neighbors:
                if neighbor not in visited and neighbor not in to_visit:
                    to_visit.append(neighbor)
        return visited
    
    def depth_first_search(self, start_node) -> list:
        visited = []
        self.depth_first_search_r(visited, start_node)
        return visited

    def depth_first_search_r(self, visited, current_node) -> list:
        visited.append(current_node)
        sorted_neighbors = sorted(self.graph[current_node])
        for neighbor in sorted_neighbors:
            if neighbor not in visited:
                self.depth_first_search_r(visited, neighbor)

    def bfs_shortest_path(self, start, end) -> list:
        visited = []
        to_visit = [start]
        path = {start: None}
        while to_visit:
            current_node = to_visit.pop(0)
            visited.append(current_node)
            if current_node == end:
                path_list = []
                while current_node is not None:
                    path_list.append(current_node)
                    current_node = path[current_node]
                path_list.reverse()
                return path_list

            sorted_neighbors = sorted(self.graph[current_node])
            for neighbor in sorted_neighbors:
                if neighbor not in visited and neighbor not in to_visit:
                    to_visit.append(neighbor)
                    path[neighbor] = current_node
        return None
