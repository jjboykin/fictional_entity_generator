from dataclasses import dataclass, field
from enum import Enum

from .entity import Entity
from .entity_option import EntityOption, OptionTypes

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

        species_option: EntityOption = self.attributes[OptionTypes.RACE][0]
        object.__setattr__(self, "age_ranges", self.determine_age_ranges(species_option))

    def __hash__(self):
        return hash((self.id, self.name)) 
    
    def determine_age_ranges(self, race_attr: EntityOption) -> dict[str, tuple[int, int]]:
        """
        Determines the age ranges of the species based on the race/species trait

        args: string descriptor from the age trait 'EntityOption'

        base:   age_ranges = {
                    "young": (0, 21),
                    "old": (50, 100),
                    "middle-aged": (30, 50),
                    "elderly": (70, 100),
                    "child": (0, 15),
                    "teen": (13, 19),
                    "adult": (17, 60),
                    "baby": (0, 1),
                    "toddler": (1, 3)
                }

        returns: default or modified default age_range dictionary based on parameters of the species
        """
        
        
        min: int = 0
        max: int = 100
        new_min = race_attr.min
        new_max = race_attr.max
        
        if new_min:
            if new_max:
                min = new_min
                max = new_max
            else:
                min = new_min
        else:
            if new_max:
                max = new_max

        age_ranges = {
            "young": (min, max * 0.21),
            "old": (max * 0.5, max),
            "middle-aged": (max * 0.3, max * 0.5),
            "elderly": (max * .7, max),
            "child": (min, max * 0.15),
            "teen": (max * 0.13, max * 0.19),
            "adult": (max * 0.17, max * 0.6),
            "baby": (min, max * 0.01),
            "toddler": (max * 0.01, max * 0.03)
        }

        return age_ranges
