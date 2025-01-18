class Graph:
    def __init__(self) -> None:
        self.graph: dict = {}

    def __repr__(self):
        return str(self.graph)
    
    def add_edge(self, u, v) -> None:
        if u in self.graph:
            self.graph[u].add(v)
        else:
            self.graph[u] = {v}
        if v in self.graph:
            self.graph[v].add(u)
        else:
            self.graph[v] = {u}

    def add_node(self, u) -> None:
        if u not in self.graph:
            self.graph[u] = set()

    def edge_exists(self, u, v) -> bool:
        if u in self.graph and v in self.graph:
            return (v in self.graph[u]) and (u in self.graph[v])
        return False
    
    def adjacent_nodes(self, node) -> list:
        return list(self.graph[node])

    def unconnected_vertices(self) -> list:
        unconnected = []
        for vertex, connections in self.graph.items():
            if not connections:
                unconnected.append(vertex)
        return unconnected
    
    def breadth_first_search(self, v) -> list:
        visited = []
        to_visit = []
        to_visit.append(v)
        while to_visit:
            s = to_visit.pop(0)
            visited.append(s)
            sorted_neighbors = sorted(self.graph[s])
            for neighbor in sorted_neighbors:
                if neighbor not in visited and neighbor not in to_visit:
                    to_visit.append(neighbor)
        return visited
    
    def depth_first_search(self, start_vertex) -> list:
        visited = []
        self.depth_first_search_r(visited, start_vertex)
        return visited

    def depth_first_search_r(self, visited, current_vertex) -> list:
        visited.append(current_vertex)
        sorted_neighbors = sorted(self.graph[current_vertex])
        for neighbor in sorted_neighbors:
            if neighbor not in visited:
                self.depth_first_search_r(visited, neighbor)

    def bfs_shortest_path(self, start, end) -> list:
        visited = []
        to_visit = [start]
        path = {start: None}
        while to_visit:
            current_vertex = to_visit.pop(0)
            visited.append(current_vertex)
            if current_vertex == end:
                path_list = []
                while current_vertex is not None:
                    path_list.append(current_vertex)
                    current_vertex = path[current_vertex]
                path_list.reverse()
                return path_list

            sorted_neighbors = sorted(self.graph[current_vertex])
            for neighbor in sorted_neighbors:
                if neighbor not in visited and neighbor not in to_visit:
                    to_visit.append(neighbor)
                    path[neighbor] = current_vertex
        return None
