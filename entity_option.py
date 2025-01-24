from enum import Enum
from dataclasses import dataclass, field
from typing import Self

# This Enum should encompass option types for Person, Location, Organization, and GeoPoliticalEntity
class OptionTypes(Enum):
    AGE = "Age"
    BACKGROUND = "Background"
    CLIMATE = "Climate"
    FAMILY_NAME = "Family Name"
    NAME = "Name"
    NICKNAME = "Nickname"
    PERSONALITY_TRAIT = "Personality Trait"
    PHYSICAL_TRAIT = "Physical Trait"
    PROFESSION = "Profession"
    RELATIONSHIP = "Relationship"
    RACE = "Race"
    RESOURCES = "Resources"
    ROLE = "Role"
    SEX = "Sex"
    SKILL = "Skill"
    SPECIALIZATION = "Specialization"
    TERRAIN = "Terrain"
    TYPE = "Type"
    UNIQUE = "Unique Trait"
    
class EntityOptionListFlag(Enum):
    ADD = "add"
    OVERRIDE = "override"

# This dataclass should be used to define options for Person, Location, Organization, and GeoPoliticalEntity <Entity> types
@dataclass(kw_only=True)
class EntityOption:
    name: str
    type: OptionTypes
    description: str = field(default=None)
    min: int = field(default=None)
    max: int = field(default=None)
    weight: float = field(default=10.0)
    mutually_exclusive: list[Self] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    specilizations: list[Self] = field(default_factory=list)

    def __post_init__(self):
        if self.min and self.max:
            if self.min > self.max:
                raise ValueError(f"Min value {self.min} cannot be greater than max value {self.max}")
        if self.weight < 0:
            raise ValueError(f"Weight cannot be negative: {self.weight}")
        if self.weight > 100:
            raise ValueError(f"Weight cannot be greater than 100: {self.weight}")
        
    def __eq__(self, other: Self):
        return self.name == other.name and self.type == other.type

    def __hash__(self):
        return hash((self.name, self.type))
    
    def __str__(self):
        return f"{self.name}"
    
    def __repr__(self):
        return f"{self.name}"
    
    def __lt__(self, other: Self):
        return self.weight < other.weight
    
    def __gt__(self, other: Self):
        return self.weight > other.weight
    
    def __le__(self, other: Self):
        return self.weight <= other.weight
    
    def __ge__(self, other: Self):
        return self.weight >= other.weight
    
    def __ne__(self, other: Self):    
        return self.name != other.name or self.type != other.type
    