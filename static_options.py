from enum import Enum

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