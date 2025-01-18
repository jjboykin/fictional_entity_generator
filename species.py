from dataclasses import dataclass, field
from enum import Enum
from entity import Entity

class SpeciesAttributes(Enum):
    # TODO: Establish possible species attributes
    LAND_NATIVE = 1
    AQUATIC_NATIVE = 2
    AMPHIBIOUS = 3
    HAS_WINGS = 4
    CAN_FLY = 5

@dataclass(frozen=True, kw_only=True)
class Species(Entity):
    attributes: dict[SpeciesAttributes, bool] = field(default=None)
    
