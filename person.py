from dataclasses import dataclass, field
from species import Species, SpeciesAttributes

@dataclass(frozen=True, kw_only=True)
class Person(Species):
    name: str = field(init=False)
    first_name: str
    last_name: str
    age: int = field(default=None)
    attributes: dict[SpeciesAttributes, bool] = field(default=None)

    def __post_init__(self):
        if not self.first_name or not self.last_name:
            raise ValueError("First and last name are required fields")
        
        object.__setattr__(self, "name", f"{self.first_name} {self.last_name}")