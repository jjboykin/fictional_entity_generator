import uuid
from dataclasses import dataclass, field

@dataclass(frozen=True, kw_only=True)
class Entity():
    id: uuid.UUID = uuid.uuid4()
    name: str
    description: str