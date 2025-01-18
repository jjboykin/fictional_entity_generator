import uuid
from dataclasses import dataclass, field
from enum import Enum

class RelationshipType(Enum):
    CHILD = 1
    PARENT = 2
    SPOUSE = 3
    FRIEND = 4
    ALLY = 5
    ENEMY = 6
    COUSIN = 6
    CRUSH = 8


@dataclass(frozen=True, kw_only=True)
class Entity():
    id: uuid.UUID = field(default=None)
    name: str
    description: str = field(default=None)

    def __post_init__(self):
        object.__setattr__(self, "id", uuid.uuid4())