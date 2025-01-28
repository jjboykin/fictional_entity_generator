from dataclasses import dataclass, field
from entity import Entity
from location import Location
from organization import Organization
from structure import Structure
#from entity_option import EntityOption, OptionTypes

@dataclass(frozen=True, kw_only=True)
class GeoPoliticalEntity(Entity):
    location: Location
    organization: Organization

    # Structures tied to both the location and organization (e.g., military bases, trade offices).
    facilities: set[Structure] = field(default=None)
    
    allies: set[Entity] = field(default=None)
    enemies: set[Entity] = field(default=None)
    
    #Events
    
    # Key Metrics
    # For Locations: Population growth, resource exploitation, environmental changes.
    # For Organizations: Influence, stability, conflicts, and alliances.

    def __post_init__(self):
        super().__post_init__()

    def __hash__(self):
        return hash((self.id, self.name)) 
