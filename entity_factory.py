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
        
        self.__applicable_option_types = applicable_option_types
        self.__options_list = options_list

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
                if option.type in self.__applicable_option_types:
                    min_occurrences, max_occurrences = self.__applicable_option_types[option.type]
                    option_counts[option.type] = random.randint(min_occurrences, max_occurrences)
        
        # If OptionType.AGE is in option_counts, randomly generate the age trait first 
        if OptionTypes.AGE in option_counts.keys():
            option_type = OptionTypes.AGE
            entity_kwargs[option_type] = []
            selected_options = [opt for opt in self.__options_list if opt.type == option_type] 
            selected_option = random.choices(selected_options, weights=[opt.weight for opt in selected_options], k=1)[0]
            entity_kwargs[option_type].append(selected_option)
        
        # TODO: limit what else is generated based on that age
        # TODO: limit what else is generated based what is defined in mutually_exclusive (probably make this its own function)
            # Some names for certain sexes
            # Some names for certain races

        # Select random values for each option type
        for option_type, count in option_counts.items():
            selected_options = [opt for opt in self.__options_list if opt.type == option_type] 
            if option_type != OptionTypes.AGE:   # Don't process AGE a second time
                entity_kwargs[option_type] = []  # Initialize an empty list for each option type
                if selected_options:
                    for _ in range(count):
                        selected_option = random.choices(selected_options, weights=[opt.weight for opt in selected_options], k=1)[0]
                        entity_kwargs[option_type].append(selected_option)
                
        #Create the entity instance
        entity = self.__entity_type(attributes=entity_kwargs, applicable_option_types=self.__applicable_option_types, **kwargs)

        return entity
    
    def get_entity_type(self):
        """
        Returns the class of Entity the EntityFactory is intialized to produce.

        returns:
            The class of the entity_type member variable.
        """
        return self.__entity_type

    def get_applicable_option_types(self):
        """
        Returns the applicable option types for the EntityFactory.

        returns:
            The applicable_option_types member variable.
        """
        return self.__applicable_option_types

    def get_options_list(self):
        """
        Returns the options list for the EntityFactory.

        returns:
            The options_list member variable.
        """
        return self.__options_list   
