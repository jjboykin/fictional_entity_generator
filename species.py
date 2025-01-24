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

'''   
TODO: Implement age ranges for species 
if "young" == trait.lower():
    age = random.randint(1, 18)
    break
if "old" == trait.lower():
    age = random.randint(18, 100)
    break
if "middle-aged" == trait.lower():
    age = random.randint(30, 60)
    break
if "elderly" == trait.lower():
    age = random.randint(60, 100)
    break
if "child" == trait.lower():
    age = random.randint(1, 12)
    break
if "teen" == trait.lower():
    age = random.randint(13, 18)
    break
if "adult" == trait.lower():
    age = random.randint(18, 60)
    break
if "baby" == trait.lower():
    age = random.randint(0, 1)
    break
if "toddler" == trait.lower():
    age = random.randint(1, 3)
    break'''