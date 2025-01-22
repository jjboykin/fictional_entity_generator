from graph import Graph
from entity import Entity

class EntityGraph(Graph):

    def __init__(self) -> None:
        super().__init__()
        self.graph: dict = {Entity: set()}
        self.metadata: dict = {tuple[Entity, Entity]: dict()}
    
    def add(self, node: Entity) -> Entity:
        if not isinstance(node, Entity):
            raise TypeError("Node must be an instance of Entity")
        return self.add_node(node)

    def add_relationship(self, node1: Entity, node2:Entity, metadata1: dict = None, metadata2: dict = None) -> None:
        if not isinstance(node1, Entity) or not isinstance(node2, Entity):
            raise TypeError("Both nodes must be instances of Entity")
        
        self.add_pair(node1, node2, metadata1, metadata2)

    def add_node(self, node: Entity) -> Entity:
        if not isinstance(node, Entity):
            raise TypeError("Node must be an instance of Entity")
        
        existing_node = self.get_node_by_identifier(node)
        if existing_node:
            return existing_node  # Return the existing node

        self.graph[node] = set()
        return node

    def add_edge(self, node1: Entity, node2: Entity) -> None:
        if not isinstance(node1, Entity) or not isinstance(node2, Entity):
            raise TypeError("Both nodes must be instances of Entity")
        
        node1 = self.add_node(node1)
        node2 = self.add_node(node2)
        super().add_edge(node1, node2)

    def add_metadata(self, node1: Entity, node2: Entity, metadata: dict) -> None:
        if not isinstance(node1, Entity) or not isinstance(node2, Entity):
            raise TypeError("Both nodes must be instances of Entity")
        
        if metadata is not None:
            if (node1, node2) not in self.metadata:
                self.metadata[(node1, node2)] = metadata
            else:
                self.metadata[(node1, node2)].update(metadata)

    def add_metadata2(self, node1: Entity, node2: Entity, metadata1: dict = None, metadata2: dict = None) -> None:
        if not isinstance(node1, Entity) or not isinstance(node2, Entity):
            raise TypeError("Both nodes must be instances of Entity")
        
        if metadata1 is not None:
            if (node1, node2) not in self.metadata:
                self.add_metadata(node1, node2, metadata1)
        if metadata2 is not None:
            if (node2, node1) not in self.metadata:
                self.add_metadata(node2, node1, metadata2)

    def add_metadata_reciprocal(self, node1: Entity, node2: Entity, metadata: dict) -> None:
        if not isinstance(node1, Entity) or not isinstance(node2, Entity):
            raise TypeError("Both nodes must be instances of Entity")
        
        if metadata is not None:
            if (node1, node2) not in self.metadata:
                self.metadata[(node1, node2)] = metadata
            if (node2, node1) not in self.metadata:
                self.metadata[(node2, node2)] = metadata

    def add_pair(self, node1: Entity, node2: Entity, metadata1: dict = None, metadata2: dict = None) -> None:
        if not isinstance(node1, Entity) or not isinstance(node2, Entity):
            raise TypeError("Both nodes must be instances of Entity")
        
        node1 = self.add_node(node1)
        node2 = self.add_node(node2)
        
        if not self.edge_exists(node1, node2):
            self.add_edge(node1, node2)

        if metadata1 is not None:
            self.add_metadata(node1, node2, metadata1)

        if metadata2 is not None:
            self.add_metadata(node2, node1, metadata2)           

    def add_reciprocal_pair(self, node1: Entity, node2: Entity, metadata: dict = None) -> None:
        if not isinstance(node1, Entity) or not isinstance(node2, Entity):
            raise TypeError("Both nodes must be instances of Entity")
        
        node1 = self.add_node(node1)
        node2 = self.add_node(node2)
        
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

    def exists(self, node: Entity) -> bool:
        if not isinstance(node, Entity):
            raise TypeError("Node must be an instance of Entity")
        
        return self.get_node_by_identifier(node) is not None

    def edge_exists(self, node1: Entity, node2: Entity) -> bool:
        if not isinstance(node1, Entity) or not isinstance(node2, Entity):
            raise TypeError("Both nodes must be instances of Entity")
        
        if node1 in self.graph and node2 in self.graph:
            return (node2 in self.graph[node1]) and (node1 in self.graph[node2])
        return False
    
    def get_node(self, node: Entity) -> set:
        if not isinstance(node, Entity):
            raise TypeError("Node must be an instance of Entity")
        
        return self.graph[node]
    
    def get_node_by_identifier(self, node:Entity) -> Entity:
        for existing_node in self.graph.keys():
            # Assuming 'name' is the identifier
            if existing_node.name == node.name:  
                return existing_node
        return None
    
    def get_adjacent_nodes(self, node: Entity) -> list:
        if not isinstance(node, Entity):
            raise TypeError("Node must be an instance of Entity")
        
        return super().get_adjacent_nodes(node)
    
    def get_metadata(self, node: Entity) -> list:
        if not isinstance(node, Entity):
            raise TypeError("Node must be an instance of Entity")
        
        metadata = []
        for key, value in self.metadata.items():
            if node in key:
                metadata.append((key, value))
        return metadata
    
    def remove(self, node: Entity) -> None:
        if not isinstance(node, Entity):
            raise TypeError("Node must be an instance of Entity")
        
        if self.exists(node):
            del self.graph[node]
        for key, value in self.graph.items():
            if node in value:
                value.remove(node)
        for key, value in self.metadata.items():
            if node in key:
                del self.metadata[key]

    def remove_edge(self, node1: Entity, node2: Entity) -> None:
        if not isinstance(node1, Entity) or not isinstance(node2, Entity):
            raise TypeError("Both nodes must be instances of Entity")
        
        if self.exists(node1):
            self.graph[node1].remove(node2)
        if self.exists(node2):
            self.graph[node2].remove(node1)
        for key in self.metadata.items():
            if node1 in key:
                del self.metadata[key]
            if node2 in key:
                del self.metadata[key]

    