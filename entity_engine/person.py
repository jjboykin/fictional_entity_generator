import random
from dataclasses import dataclass, field
from enum import Enum

from .species import Species
from .entity_option import EntityOption, OptionTypes

@dataclass(frozen=True, kw_only=True)
class Person(Species):
    given_name: str = field(default=None)
    middle_names: str = field(default=None)
    family_name: str = field(default=None)
    age: int = field(default=None)
    sex: str = field(default=None)

    def __post_init__(self):
        super().__post_init__()

        if OptionTypes.NAME in self.attributes:
            object.__setattr__(self, "given_name", self.attributes[OptionTypes.NAME][0])

            middle_name = ""
            for i in range (1, len(self.attributes[OptionTypes.NAME])):
                middle_name = f"{self.attributes[OptionTypes.NAME][i]} "
            middle_name = middle_name.strip()
            object.__setattr__(self, "middle_name", middle_name)
        
        if OptionTypes.FAMILY_NAME in self.attributes:
            object.__setattr__(self, "family_name", self.attributes[OptionTypes.FAMILY_NAME][0])

        if not self.given_name or not self.family_name:
            raise ValueError("First and last name are required fields")   
            
        object.__setattr__(self, "name", f"{self.given_name} {self.family_name}")

        if OptionTypes.AGE in self.attributes:
            age_option: EntityOption = self.attributes[OptionTypes.AGE][0]
            object.__setattr__(self, "age", self.determine_age(age_option.name))

        if OptionTypes.SEX in self.attributes:
            object.__setattr__(self, "sex", self.attributes[OptionTypes.SEX][0])
    
    def __hash__(self):
        return hash((self.id, self.name)) 

    def determine_age(self, trait: str) -> int:
        """
        Determines the age of the person based on the age trait

        args: string descriptor from the age trait 'EntityOption'

        returns: randomly generated age within the parameter of the species and attributes
        """
        age: int = 17
        min: int = 0
        max: int = 100
        if self.age_ranges:
            print(self.age_ranges)
            new_min, new_max = self.age_ranges[trait.lower()]
        
        if new_min:
            if new_max:
                min = int(new_min)
                max = int(new_max)
            else:
                min = int(new_min)
        else:
            if new_max:
                max = int(new_max)

        age = random.randint(min, max)

        return age
