from dataclasses import dataclass, field
from species import Species
from entity_option import OptionTypes

@dataclass(frozen=True, kw_only=True)
class Person(Species):
    name: str = field(init=False)
    given_name: str = field(default=None)
    family_name: str = field(default=None)
    age: int = field(default=None)

    def __post_init__(self):
        super().__post_init__()

        if OptionTypes.NAME in self.attributes:
            object.__setattr__(self, "given_name", self.attributes[OptionTypes.NAME][0])
        if OptionTypes.FAMILY_NAME in self.attributes:
            object.__setattr__(self, "family_name", self.attributes[OptionTypes.FAMILY_NAME][0])

        if not self.given_name or not self.family_name:
            raise ValueError("First and last name are required fields")   
            
        object.__setattr__(self, "name", f"{self.given_name} {self.family_name}")