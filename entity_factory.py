import random

from entity import Entity
from person import Person
from location import Location
from organization import Organization
from gpe import GeoPoliticalEntity

class EntityFactory:
    def __init__(self, entity_types):
        self.entity_types = entity_types

    def create_random_entity(self, **kwargs):
        entity_type = random.choice(self.entity_types)
        return entity_type(**kwargs)
