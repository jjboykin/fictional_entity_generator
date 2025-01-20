from entity import Entity
from person import Person
from location import Location
from organization import Organization
from gpe import GeoPoliticalEntity
from entity_factory import EntityFactory
from static_options import EntityTypes

class EntityTracker:
    def __init__(self, entity_stack: list[EntityFactory]=None):
        self.entity_stack: list[EntityFactory] = entity_stack

    def count(self, type: EntityTypes=None) -> int:
        if type:
            count:int = 0
            for i in range (0, len(self.entity_stack)):
                if eval(type.value) == self.entity_stack[i].get_entity_type():
                    count += 1
            return count
        else:
            return len(self.entity_stack)