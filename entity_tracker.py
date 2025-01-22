from entity import Entity

from static_options import EntityTypes

class EntityTracker:
    def __init__(self):
        self.entity_stack: list[Entity] = []

    def count(self, type: EntityTypes=None) -> int:
        if type:
            count:int = 0
            for i in range (0, len(self.entity_stack)):
                if eval(type.value) == self.entity_stack[i]:
                    count += 1
            return count
        else:
            return len(self.entity_stack)