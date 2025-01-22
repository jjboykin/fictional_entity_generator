from enum import Enum
from dataclasses import dataclass, field
from typing import Self

# This Enum should encompass option types for Person, Location, Organization, and GeoPoliticalEntity
class OptionTypes(Enum):
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
    SKILL = "Skill"
    SPECIALIZATION = "Specialization"
    TERRAIN = "Terrain"
    UNIQUE = "Unique Trait"

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