import random

from entity import Entity
from person import Person
from location import Location
from organization import Organization
from gpe import GeoPoliticalEntity

class EntityFactory:
    def __init__(self, entity_type):
        self.entity_type = entity_type

    def create_random_entity(self, **kwargs):
        #TODO: create_random_person function not yet implemented
        entity_type = self.entity_type
        
        return entity_type(**kwargs)
    
    def get_entity_type(self):
        return self.entity_type
