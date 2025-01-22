import random

from entity import Entity
from entity_option import EntityOption, OptionTypes

class EntityFactory:
    def __init__(self, entity_type: Entity | str, applicable_option_types: dict[OptionTypes, tuple[int, int]], options_list: list[EntityOption]) -> None:
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
                raise TypeError(f"Invalid entity type: {entity_type}")
        else:
            self.__entity_type: Entity = entity_type

        if not issubclass(self.__entity_type, Entity):
            raise TypeError(f"{self.__entity_type} does not inherit from Entity.")
        
        self.applicable_option_types = applicable_option_types
        self.options_list = options_list

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
        
        entity_kwargs: dict[OptionTypes, list[EntityOption]]  = {}
 
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
                selected_options = [opt for opt in self.options_list if opt.type == option_type]  # Use options_list here
                entity_kwargs[option_type] = []  # Initialize an empty list for each option type
                if selected_options:
                    for _ in range(count):
                        selected_option = random.choices(selected_options, weights=[opt.weight for opt in selected_options], k=1)[0]
                        entity_kwargs[option_type].append(selected_option)
                
        #Create the entity instance
        #entity_kwargs.update(kwargs) 
        #entity = self.__entity_type(attributes=entity_kwargs, **kwargs)
        entity = self.__entity_type(attributes=entity_kwargs, applicable_option_types=self.applicable_option_types, **kwargs)

        return entity
    
    def get_entity_type(self):
        """
        Returns the class of Entity the EntityFactory is intialized to produce.

        returns:
            The class of the entity_type member variable.
        """
        return self.__entity_type
