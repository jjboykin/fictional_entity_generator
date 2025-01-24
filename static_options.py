from enum import Enum
from person import Person
from location import Location
from organization import Organization
from gpe import GeoPoliticalEntity

class InputOptionsFileFormat(Enum):
    CSV = "text/csv"
    JSON = "application/json" 

class OutputResultsFileFormat(Enum):
    CSV = "text/csv"
    JSON = "application/json" 
    MD = "text/markdown"
    HTML = "text/html"

class OutputMode(Enum):
    CONSOLE = "console"
    FILE = "file"
    CONSOLE_AND_FILE = "cf"
    #GUI = "gui"
    #GUI_AND_FILE = "gf"
    ALL = "all"

class EntityTypes(Enum):
    PERSON = Person
    LOCATION = Location
    ORGANIZATION = Organization
    GPE = GeoPoliticalEntity