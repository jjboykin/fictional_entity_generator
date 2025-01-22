from dataclasses import dataclass, field
from species import Species

@dataclass(frozen=True, kw_only=True)
class Person(Species):
    name: str = field(init=False)
    first_name: str = field(default=None)
    last_name: str = field(default=None)
    age: int = field(default=None)

    # TODO: Pull name, first_name, last_name, and age from attributes in post_init

    def __post_init__(self):
        
        # Only run this check if the first_name and last_name attributes are not found in the attributes dictionary
        #if not self.first_name or not self.last_name:
        #    raise ValueError("First and last name are required fields")
        
        super().__post_init__()
        
        object.__setattr__(self, "name", f"{self.first_name} {self.last_name}")