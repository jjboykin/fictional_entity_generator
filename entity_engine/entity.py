import uuid
from dataclasses import dataclass, field
from enum import Enum

from .entity_option import OptionTypes

class RelationshipType(Enum):
    IS_A = 0
    CHILD = 1
    PARENT = 2
    SPOUSE = 3
    FRIEND = 4
    ALLY = 5
    ENEMY = 6
    COUSIN = 6
    CRUSH = 8
    RIVAL = 9
    MENTOR = 10
    STUDENT = 11
    EMPLOYER = 12
    EMPLOYEE = 13
    PARTNER = 14
    ASSOCIATE = 15
    ACQUAINTANCE = 16
    NEIGHBOR = 17
    ROOMMATE = 18
    TEAMMATE = 19
    CLASSMATE = 20
    COLLEAGUE = 21
    SUPERIOR = 22
    SUBORDINATE = 23
    GUILDMATE = 24

@dataclass(frozen=True, kw_only=True)
class Entity():
    id: uuid.UUID = field(default=None)
    name: str = field(init=False)
    notes: str = field(default=None)
    attributes: dict[OptionTypes, list[str]] = field(default_factory=dict)
    applicable_option_types: dict[OptionTypes, tuple[int, int]] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "id", uuid.uuid4())

        if OptionTypes.NAME in self.attributes:
            object.__setattr__(self, "name", self.attributes[OptionTypes.NAME][0])

    def __hash__(self):
        return hash((self.id, self.name)) 

