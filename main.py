import os, sys, datetime
import argparse, configparser
import magic, mimetypes
import pickle, logging
from logging.handlers import RotatingFileHandler

from static_options import InputOptionsFileFormat, OutputResultsFileFormat, OutputMode, EntityTypes

from graph import Graph
from entity_option import EntityOption, OptionTypes
from entity_factory import EntityFactory
from entity_tracker import EntityTracker
from person import Person
from location import Location
from organization import Organization
from gpe import GeoPoliticalEntity

from tests.test_graph import *

def main():
    """
    A program to generate fictional entities (people, places, organisations, and the connections between them) 
    at random based on user specified parameters against either the default dictionaries of attributes or one 
    passed to the program at runtime. 
    """

    '''Setup Method Scope Variables'''
    input_file_formats: str = ", ".join([format.value for format in InputOptionsFileFormat])
    results_output_file_formats: str = ", ".join([format.value for format in OutputResultsFileFormat])
    results_output_modes: str = ", ".join([format.value for format in OutputMode])
    results_output_mode: OutputMode = OutputMode.CONSOLE
    results_outfile_format: OutputResultsFileFormat = OutputResultsFileFormat.MD
    results_output_file_path: str = get_datetime_filename("results", get_extension_from_mime(results_outfile_format.value))
    object_output_file_path: str = None
    object_input_file_path: str = None
    input_file_path: str = None 
    entity_stack: list[EntityFactory] = []
    tracker: EntityTracker = EntityTracker(entity_stack)
    entities: Graph = Graph()
    random_options: list[EntityOption] = []

    '''Setup Logging'''
    logger = logging.getLogger(__name__)
    
    #Create logging handlers
    console_handler = logging.StreamHandler()
    rotating_file_handler = RotatingFileHandler("app.log", maxBytes=2000)

    #Set handler logging levels
    console_handler.setLevel(logging.WARNING)
    rotating_file_handler.setLevel(logging.ERROR)

    logging_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(logging_format)
    rotating_file_handler.setFormatter(logging_format)

    logger.addHandler(console_handler)
    logger.addHandler(rotating_file_handler)

    '''Setup Command Line Argument Parsing'''
    parser = argparse.ArgumentParser(description='Description of your program')

    # Add arguments
    parser.add_argument('-f', '--file', type=str, help=f'Path to an input file containing object attribute options. Input file formats: {input_file_formats}')
    parser.add_argument('--save_config', type=bool, help='Saves the passed configuration')
    parser.add_argument('--reset_config', type=bool, help='Resets saved configuration to default')

    parser.add_argument('-out', '--output', type=str, default=f'{results_output_mode.value}', help=f'Output mode: {results_output_modes}')
    parser.add_argument('--outfile_format', type=str, default=f'{results_outfile_format.value}', help=f'Output file formats: {results_output_file_formats}')
    parser.add_argument('--outfile_name', type=str, help='Name to save the results file to')
        
    parser.add_argument('-p', '--person', type=int, default=1, help='Specifies how many person objects to generate')
    parser.add_argument('-l', '--location', type=int, default=0, help='Specifies how many location objects to generate')
    parser.add_argument('-o', '--organization', type=int, default=0, help='Specifies how many organization objects to generate')
    parser.add_argument('-gpe', '--geopolitical', type=int, default=0, help='Specifies how many geopolitical entity objects to generate')
    
    # TODO: Add autosave option that when "on" keeps the load and save options in its own [autosave] section of the config
    parser.add_argument('--load', type=str, help='Name of a saved object file to load')
    parser.add_argument('--save', type=str, help='Name to save the generated object file to')

    # Parse arguments
    args = parser.parse_args()

    # Access parsed arguments
    if args.save_config and args.reset_config:
        e = Exception ("Save config and reset config flags are mutually exclusive.")
        logger.error(f"Exception: {e}")
        raise e

    if args.reset_config:
        # Write the config with defaults before reading
        defaults: dict = {}
        for action in args._actions:
            if action.default is not None:
                defaults[action.dest] = action.default
        reset_config(defaults)

    '''Setup Config File Parsing'''

    # Read config file (if it exists)
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Update config with command line arguments
    if 'main' not in config:
        config['main'] = {}
    if 'objects' not in config:
        config['objects'] = {}
    # Write updated config to file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    # Main arguments in config
    if args.output:
        if is_valid_results_output_mode(args.output):
            config['main']['output'] = args.output
            results_output_mode = OutputMode(args.output)
        else:
            w = Exception ("Invalid output mode parameter; continuing with configured option.")
            logger.warning(f"Exception: {w}")
            if config['main']['output']:
                if is_valid_results_output_mode(config['main']['output']):
                    results_output_mode = OutputMode(config['main']['output'])
                else:
                    w = Exception ("Invalid configured output mode; continuing with default option.")
                    logger.warning(f"Exception: {w}")
            else:
                w = Exception ("No configured output mode; continuing with default option.")
                logger.warning(f"Exception: {w}")
    
    if args.outfile_format:
        if is_valid_results_outfile_format(args.outfile_format):
            config['main']['outfile_format'] = args.outfile_format
            results_outfile_format = OutputResultsFileFormat(args.outfile_format)
        else:
            w = Exception ("Invalid outfile format; continuing with configured option.")
            logger.warning(f"Exception: {w}")
            if config['main']['outfile_format']:
                if is_valid_results_outfile_format(config['main']['outfile_format']):
                    results_outfile_format = OutputResultsFileFormat(config['main']['outfile_format'])
                else:
                    w = Exception ("Invalid configured outfile format; continuing with default option.")
                    logger.warning(f"Exception: {w}")
            else:
                w = Exception ("No configured outfile format; continuing with default option.")
                logger.warning(f"Exception: {w}")

    # Main arguments NOT in config
    if args.file:
        input_file_path = args.file
        if is_valid_input_options_file(input_file_path):
            try:
                read_input_options_file(input_file_path)
            except Exception as e:
                logger.error(f"Error: {e}")
                return None
        else:
            w = Exception ("Invalid input file format; continuing with standard options.")
            logger.warning(f"Exception: {w}")

    if args.outfile_name:
        # Parse args.outfile_name and strip extension (if any) from file name
        temp_file_name: str =  os.path.splitext(args.outfile_name)[0]
        file_format: str = get_extension_from_mime(results_outfile_format.value)
        # Append chosen format file extension and assign to variable
        results_output_file_path = f"{temp_file_name}.{file_format}"
        
    if args.save:
        object_output_file_path = get_datetime_filename("objects", "pkl")

    if args.load:
        object_input_file_path = args.load
        # TODO: Load existing objects into memory before generating anymore

    # Object arguments in config
    has_commandline_object_args: bool = False
    if args.person:
        has_commandline_object_args = True
        config['objects']['person'] = str(args.person)
        for i in range(0, args.person):
            factory: EntityFactory = EntityFactory(Person)
            entity_stack.append(factory)

    if args.location:
        has_commandline_object_args = True
        config['objects']['location'] = str(args.location)
        for i in range(0, args.location):
            factory: EntityFactory = EntityFactory(Location)
            entity_stack.append(factory)

    if args.organization:
        has_commandline_object_args = True
        config['objects']['organization'] = str(args.organization)
        for i in range(0, args.organization):
            factory: EntityFactory = EntityFactory(Organization)
            entity_stack.append(factory)
        
    if args.geopolitical:
        has_commandline_object_args = True
        config['objects']['geopolitical'] = str(args.geopolitical)
        for i in range(0, args.geopolitical):
            factory: EntityFactory = EntityFactory(GeoPoliticalEntity)
            entity_stack.append(factory)
    
    if args.save_config:
        # Write updated config to file
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    '''
    print(f"Config file args:")
    for key, value in config['main'].items():
        print(f"{key}={value}")

    for key, value in config['objects'].items():
        print(f"{key}={value}")
    '''

    # Use the options
    '''Setup Text Menu Interface for Program Operation and Testing'''
    use_commandline_interface: bool = True
    menu_page = "main"

    while use_commandline_interface:
        choice = generate_menu(entities, tracker, menu_page)

        if choice.upper() == "X":
            sys.exit("Exiting the program.")
        if choice.upper() == "T":
            menu_page = "test"
        if choice.upper() == "M":
            menu_page = "main"

        match menu_page:
            case "main":
                if choice == "1":
                    menu_page = "entity_create"
                elif choice == "2":
                    menu_page = "entity_view"
                elif choice == "3":
                    # TODO: Process entities stack
                    menu_page = "main"
                elif choice == "4":
                    menu_page = "config"
                elif choice == "5":
                    # TODO: Save Generated Entities to Object File
                    save_object_data(entities, f"entity_{object_output_file_path}")
                    save_object_data(random_options, f"option_{object_output_file_path}")
                elif choice == "6":
                    # TODO: Load Previously Generated Entities
                    pass
                elif choice == "7":
                    # TODO: Export Generated Entities
                    pass
            case "test":
                if choice == "1":
                    test_graph_with_person()
                    input("Press any key to continue...")
                elif choice == "2":
                    person = create_random_person()
                    print(person)
                    input("Press any key to continue...")
                else:
                    print("Invalid choice. Please try again.")
            case "entity_create":
                if choice == "1":
                    pass
                elif choice == "2":
                    pass
                elif choice == "3":
                    pass
                elif choice == "4":
                    pass
                else:
                    print("Invalid choice. Please try again.")
            case "entity_view":
                if choice == "1":
                    pass
                elif choice == "2":
                    pass
                elif choice == "3":
                    pass
                elif choice == "4":
                    pass
                elif choice == "5":
                    pass
                else:
                    print("Invalid choice. Please try again.")
            case "config":
                if choice == "1":
                    pass
                elif choice == "2":
                    pass
                else:
                    print("Invalid choice. Please try again.")
            case _:
                pass
        
def generate_menu(entities: Graph, tracker: EntityTracker, page: str=None) -> str:
    print("")
    print("==============================" + "< Fictional Entity Generator >" + "==============================" + "\n")

    print(f"Entities Created: {entities.count()}\t| "
        f"Person= {entities.count(EntityTypes.PERSON)}; "
        f"Location= {entities.count(EntityTypes.LOCATION)}; " 
        f"Organization= {entities.count(EntityTypes.ORGANIZATION)}; "
        f"Geopolitical= {entities.count(EntityTypes.GPE)}")

    if tracker.entity_stack:
        print(f"Entities Queued:  {tracker.count()}\t| "
            f"Person= {tracker.count(EntityTypes.PERSON)}; "
            f"Location= {tracker.count(EntityTypes.LOCATION)}; " 
            f"Organization= {tracker.count(EntityTypes.ORGANIZATION)}; "
            f"Geopolitical= {tracker.count(EntityTypes.GPE)}\n")
        
    if not page:
        generate_menu_main(entities, tracker)
    else:
        match page:
            case "main":
                generate_menu_main(entities, tracker)
            case "test":
                generate_menu_test(entities, tracker)
            case "entity_create":
                generate_menu_entity_create(entities, tracker)
            case "entity_view":
                generate_menu_entity_view(entities, tracker)
            case "config":
                generate_menu_config(entities, tracker)
            case _:
                generate_menu_main(entities, tracker)

    print("\nT. Run Tests")
    print("")
    if not page == "main":
        print("M. Main Menu")
    print("X. Exit")

    return input("\nEnter your choice: ")

def generate_menu_config(entities: Graph, tracker: EntityTracker) -> None:
    print(f"------------------------------------------------------------------------------------------\n")
    print("Configuration Menu:\n")
    print("1. Save Current Parameters to Configuration")
    print("2. Reset Configuration")

def generate_menu_entity_create(entities: Graph, tracker: EntityTracker) -> None:
    print(f"------------------------------------------------------------------------------------------\n")
    print("Create Entity Menu:\n")
    print("1. Person")
    print("2. Location")
    print("3. Organization")
    print("4. Geopolitical Entity")

def generate_menu_entity_view(entities: Graph, tracker: EntityTracker) -> None:
    print(f"------------------------------------------------------------------------------------------\n")
    print("View Entity Menu:\n")
    print("1. Person")
    print("2. Location")
    print("3. Organization")
    print("4. Geopolitical Entity")
    print("5. All")

def generate_menu_main(entities: Graph, tracker: EntityTracker) -> None:
    print(f"------------------------------------------------------------------------------------------\n")
    print("Main Menu:\n")
    print("1. Queue New Entities")
    print("2. View Created Entities")
    print("3. Process Queued Entities")
    print("4. Edit Configuration Parameters")
    print("5. Save Generated Entities to Object File")
    print("6. Load Previously Generated Entities")
    print("7. Export Generated Entities")

def generate_menu_test(entities: Graph, tracker: EntityTracker) -> None:
    print(f"------------------------------------------------------------------------------------------\n")
    print("Test Menu:\n")
    print("1. Test Graph with Person objects")
    print("2. Create Random Person")


def is_valid_input_options_file(input_file_path) -> bool:
    if os.path.exists(input_file_path):
        mime = magic.from_file(input_file_path, mime = True)
    else:
        raise FileNotFoundError (f"Input options file not found at {input_file_path}.")
    return mime in InputOptionsFileFormat
        
def read_input_options_file(input_file_path):
    # TODO: Read input_options_file into table objects
    pass

def is_valid_results_output_mode(results_output_mode) -> bool:
    return results_output_mode in OutputMode

def is_valid_results_outfile_format(results_outfile_format) -> bool:
    return results_outfile_format in OutputResultsFileFormat

def get_datetime_filename(file_type: str, file_format: str) -> str:
    # Get current date and time
    now = datetime.datetime.now()

    # Format the date and time as a string
    formatted_datetime = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Create a filename with the formatted date and time
    return f"{file_type}_{formatted_datetime}.{file_format}"

def get_extension_from_mime(mime_type):
    try:
        magic_instance = magic.Magic(mime=True)
        file_type = magic_instance.from_buffer(mime_type)
        extension = mimetypes.guess_extension(file_type)
        return extension
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error: {e}")
        return None

def reset_config(defaults: dict) -> None:
    if os.path.exists("config.ini"):
        os.remove("config.ini")
    
     # Read config file (if it exists)
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Update config with default arguments
    if 'main' not in config:
        config['main'] = {}
    if 'objects' not in config:
        config['objects'] = {}

    config['main']['output'] = defaults.output
    config['main']['outfile_format'] = defaults.outfile_format
    config['objects']['person'] = str(defaults.person)

    # Write updated config to file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def save_object_data(data, file_path: str) -> None:
    """Save object data to pickle """

    # Open a file in binary write mode
    with open(file_path, "wb") as file:
        # Dump the object to the file
        pickle.dump(data, file)

def create_random_person() -> Person:
    print(f"Executing {create_random_person.__name__}...") 
    logger = logging.getLogger(__name__)
    logger.error(f"Executing {create_random_person.__name__}...")
    
    # Create an instance of the factory
    factory = EntityFactory(Person)

    # Generate random entities
    person: Person = factory.create_random_entity(first_name="Naruto", last_name="Uzumaki", description="The next Hokage, dattebayo!")
    #person: Person = factory.create_random_entity()
    return person

if __name__ == "__main__":
    main()