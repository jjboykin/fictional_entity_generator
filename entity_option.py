from enum import Enum
from entity import Entity
from species import Species
from person import Person
from location import Location
from organization import Organization
from gpe import GeoPoliticalEntity

class OptionTypes(Enum):
    RELATIONSHIP = "Relationship"

class EntityOption:
    option_type: OptionTypes

    def __init__(self):
        pass