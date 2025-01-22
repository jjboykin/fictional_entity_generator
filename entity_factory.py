import random

from entity import Entity
from person import Person
from location import Location
from organization import Organization
from gpe import GeoPoliticalEntity

from entity_option import EntityOption, OptionTypes

class EntityFactory:
    def __init__(self, entity_type: Entity | str) -> None:
        """
        Initializes the EntityFactory with the desired entity type.

        args:
            entity_type: The type of entity to create (e.g., Person, Location, 
                         Organization, GeoPoliticalEntity) or the name of the class as a string.
        """
        if isinstance(entity_type, str):
            try:
                self.__entity_type: Entity = globals()[entity_type] 
            except KeyError:
                raise ValueError(f"Invalid entity type: {entity_type}")
        else:
            self.__entity_type: Entity = entity_type

        if not issubclass(self.__entity_type, Entity):
            raise TypeError(f"{self.__entity_type} does not inherit from Entity.")
        
        # Define applicable option types for each entity type
        if entity_type == Person:
            self.applicable_option_types = {
                OptionTypes.BACKGROUND: (1, 2),
                OptionTypes.FAMILY_NAME: (1, 1),
                OptionTypes.NAME: (1, 2),
                OptionTypes.NICKNAME: (0, 2),
                OptionTypes.PERSONALITY_TRAIT: (1, 3),
                OptionTypes.PHYSICAL_TRAIT: (1, 3),
                OptionTypes.PROFESSION: (1, 2),
                OptionTypes.RACE: (1, 1),
                OptionTypes.SPECIALIZATION: (0, 2),
                OptionTypes.SKILL: (1, 6),
                OptionTypes.UNIQUE: (0, 2)
            }
        elif entity_type == Location:
            self.applicable_option_types = {
                OptionTypes.NAME: (1, 2),
                OptionTypes.CLIMATE: (1, 1),
                OptionTypes.RESOURCES: (1, 2),
                OptionTypes.TERRAIN: (1, 2),
                OptionTypes.UNIQUE: (0, 2)
            }
        elif entity_type == Organization:
            self.applicable_option_types = {
                OptionTypes.NAME: (1, 2),
                OptionTypes.ROLE: (1, 2),
                OptionTypes.SPECIALIZATION: (0, 2),
                OptionTypes.UNIQUE: (0, 2)
            }
        elif entity_type == GeoPoliticalEntity:
            self.applicable_option_types = {
                OptionTypes.NAME: (1, 2),
                OptionTypes.UNIQUE: (0, 2)
            }
        else:
            self.applicable_option_types = {
                OptionTypes.NAME: (1, 2),
            }
            # Add more entity types and their applicable options as needed

    def create_random_entity(self, options: list[EntityOption]=None, **kwargs) -> Entity:
        """
        Creates a random instance of the specified entity type using parameters 
        obtained by randomly selecting appropriate categories of the option types passed in 
        to determine the values of the object's members and atrributes.

        args:
            options: A list of EntityOption objects to use for randomization.
            **kwargs: Additional keyword arguments to pass to the entity constructor.

        returns:
            An instance of the specified entity type.
        """
        if not issubclass(self.__entity_type, Entity):
            raise TypeError(f"{self.__entity_type} does not inherit from Entity.")
        
        entity_kwargs: dict[OptionTypes, list[str]]  = {}
 
        # Handle EntityOptions
        if options:
            # Determine the number of values to select for each option type
            option_counts: dict[OptionTypes, int] = {}
            for option in options:
                if option.type in self.applicable_option_types:
                    min_occurrences, max_occurrences = self.applicable_option_types[option.type]
                    option_counts[option.type] = random.randint(min_occurrences, max_occurrences)

        # Select random values for each option type
            for option_type, count in option_counts.items():
                selected_options = [opt for opt in options if opt.type == option_type]
                for _ in range(count):
                    selected_option = random.choices(selected_options, weights=[opt.weight for opt in selected_options], k=1)[0]
                    # Set the attribute value(s) on the entity
                    entity_kwargs[selected_option.type].append(selected_option.name)
                
        #Create the entity instance
        entity_kwargs.update(kwargs) 
        #entity = self.__entity_type(attributes=entity_kwargs, **kwargs)
        entity = self.__entity_type(attributes=entity_kwargs)
    
        return entity
    
    def get_entity_type(self):
        """
        Returns the class of Entity the EntityFactory is intialized to produce.

        returns:
            The class of the entity_type member variable.
        """
        return self.__entity_type
