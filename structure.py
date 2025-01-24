from dataclasses import dataclass, field
from enum import Enum
from entity import Entity

class StructureAttributes(Enum):
    # TODO: Establish possible structure attributes
    RESIDENTIAL = 1
    BUSINESS = 2
    INDUSTRIAL = 3
    MARTIAL = 5
    MAGICAL = 6
    ORNAMENTAL = 7

@dataclass(frozen=True, kw_only=True)
class Structure(Entity):
    attributes: dict[StructureAttributes, bool] = field(default=None)
    
    def __post_init__(self):
        super().__post_init__()

    def __hash__(self):
        return hash((self.id, self.name)) 