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
    species_traits: list[SpeciesAttributes] = field(default_factory=list)
    age_ranges: dict[str, tuple[int, int]] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
    
