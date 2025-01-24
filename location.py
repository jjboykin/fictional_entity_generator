from dataclasses import dataclass, field
from enum import Enum
from entity import Entity

class LocationType(Enum):
    # TODO: Establish possible location types
    TOWN = 1
    COUNTY = 2
    NATION = 3
    
class LocationAttributes(Enum):
    # TODO: Establish possible location attributes
    RESIDENTIAL = 1
    BUSINESS = 2
    INDUSTRIAL = 3

class TerrainAttributes(Enum):
    # TODO: Establish possible terrain attributes
    FOREST = 1
    MOUNTAIN = 2
    PLAINS = 3

class ClimateAttributes(Enum):
    # TODO: Establish possible climate attributes
    RAINY = 1
    TEMPERATE = 2
    ARTIC = 3

@dataclass(frozen=True, kw_only=True)
class Location(Entity):
    type: LocationType = field(default=LocationType.TOWN)
    #coordinates
    population: int = field(default=None)
    terrain: set[TerrainAttributes] = field(default=None)
    climate: set[ClimateAttributes] = field(default=None)
    #landmarks

    # Resources	ResourceID, LocationID, Type (water, ore, crops), Quantity, Quality
    # Infrastructure	InfrastructureID, LocationID, Type (roads, spaceports, trade hubs), Status

    def __post_init__(self):
        super().__post_init__()

    def __hash__(self):
        return hash((self.id, self.name, self.type)) 