from .entity import Entity

from enum import Enum

from .gpe import GeoPoliticalEntity
from .location import Location
from .organization import Organization
from .person import Person
from .species import Species
from .structure import Structure

class EntityTypes(Enum):
    GPE = GeoPoliticalEntity
    LOCATION = Location
    ORGANIZATION = Organization
    PERSON = Person
    SPECIES = Species
    STRUCTURE = Structure
    

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

