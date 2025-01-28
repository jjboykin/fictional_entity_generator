from dataclasses import dataclass, field
from enum import Enum
from entity import Entity
#from entity_option import EntityOption, OptionTypes

class OrganizationType(Enum):
    GUILD = 1
    RELIGION = 2
    CORPORATION = 3
    MILITARY = 4
    SCHOOL = 5
    GOVERNMENT = 6

class OrganizationAttributes(Enum):
    POLITICAL = 1
    SOCIAL = 2
    ECONOMIC = 3
    RELIGIOUS = 4
    ACADEMIC = 5
    TRADE = 6
    CRIMINAL = 7
    TECHNOLOGICAL = 8
    MAGICAL = 9 

@dataclass(frozen=True, kw_only=True)
class Organization(Entity):
    type: OrganizationType = field(default=OrganizationType.GOVERNMENT)
    #leader: Person - connected by graph
    members: int = field(default=None)
    attributes: set[OrganizationAttributes] = field(default=None)
    #headquarters: LocationID - connected by graph
    
    # Policies	PolicyID, OrganizationID, Name, Type (taxation, trade, military), Impact (social/environmental/etc.)
    # Factions	FactionID, OrganizationID, Name, Alignment, PowerLevel
    # Relations	RelationID, OrganizationID1, OrganizationID2, Type (ally/rival/enemy), Status

    def __post_init__(self):
        super().__post_init__()

    def __hash__(self):
        return hash((self.id, self.name, self.type)) 