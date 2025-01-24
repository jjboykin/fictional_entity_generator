from entity import Entity

from static_options import EntityTypes

class EntityTracker:
    def __init__(self):
        self.entity_stack: list[Entity] = []

    def count(self, type: EntityTypes = None) -> int:
        if type:
            count:int = 0
            for i in range (0, len(self.entity_stack)):
                if type.value == self.entity_stack[i]:
                    count += 1
            return count
        else:
            return len(self.entity_stack)
        
    def add(self, entity: Entity) -> None:
        self.entity_stack.append(entity)

    def clear(self) -> None:
        self.entity_stack.clear()

