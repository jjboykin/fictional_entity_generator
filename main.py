import os, sys, datetime, csv, json, mimetypes, random
import argparse, configparser, logging
import magic, pickle

from logging.handlers import RotatingFileHandler

from static_options import InputOptionsFileFormat, OutputResultsFileFormat, OutputMode, EntityTypes

from entity import Entity
from entity_graph import EntityGraph
from entity_option import EntityOption, OptionTypes, EntityOptionListFlag
from entity_factory import EntityFactory
from entity_tracker import EntityTracker
from species import Species
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
    input_file_path: str = None

    results_output_file_formats: str = ", ".join([format.value for format in OutputResultsFileFormat])
    results_output_modes: str = ", ".join([format.value for format in OutputMode])
    results_output_mode: OutputMode = OutputMode.CONSOLE
    results_outfile_format: OutputResultsFileFormat = OutputResultsFileFormat.MD
    results_output_file_path: str = get_datetime_filename("results", get_extension_from_mime(results_outfile_format.value))
    
    object_output_file_path: str = None
    object_input_file_path: str = None
    
    persons_to_queue: int = 1
    locations_to_queue: int = 0
    organizations_to_queue: int = 0
    gpes_to_queue: int = 0

    is_config_updated: bool = False
    is_results_output_mode_updated: bool = False
    is_results_outfile_format_updated: bool = False
    is_persons_to_queue_updated: bool = False

    tracker: EntityTracker = EntityTracker()
    entities: EntityGraph = EntityGraph()

    options_list: list[EntityOption] = get_default_options_list()

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


    '''Setup Config File Parsing'''
    # Read config file (if it exists)
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Add missing default sections to config
    if 'main' not in config:
        config['main'] = {}
        is_config_updated = True
    else:
        # Get `main` section parameters
        if 'output' in config['main']:
            if is_valid_results_output_mode(config['main']['output']):
                results_output_mode = OutputMode(config['main']['output'])
                is_results_output_mode_updated = True
            else:
                w = Exception ("Invalid configured output mode; continuing with default option.")
                logger.warning(f"Exception: {w}")
        else:
            w = Exception ("No configured output mode; continuing with default option.")
            logger.warning(f"Exception: {w}")

        if 'outfile_format' in config['main']:
            if is_valid_results_outfile_format(config['main']['outfile_format']):
                results_outfile_format = OutputResultsFileFormat(config['main']['outfile_format'])
                is_results_outfile_format_updated = True
            else:
                w = Exception ("Invalid configured output mode; continuing with default option.")
                logger.warning(f"Exception: {w}")
        else:
            w = Exception ("No configured output mode; continuing with default option.")
            logger.warning(f"Exception: {w}")
        
    if 'objects' not in config:
        config['objects'] = {}
        is_config_updated = True
    else:
        # Get `objects` section parameters
        if 'person' in config['objects']:
            value, is_valid = is_valid_config_value(config['objects']['person'], int)
            if is_valid:
                persons_to_queue = value
                is_persons_to_queue_updated = True
            else:
                w = Exception ("Invalid configured output mode; continuing with default option.")
                logger.warning(f"Exception: {w}")
        else:
            w = Exception ("No configured output mode; continuing with default option.")
            logger.warning(f"Exception: {w}")

        if 'location' in config['objects']:
            value, is_valid = is_valid_config_value(config['objects']['location'], int)
            if is_valid:
                locations_to_queue = value
            else:
                w = Exception ("Invalid configured output mode; continuing with default option.")
                logger.warning(f"Exception: {w}")
        else:
            w = Exception ("No configured output mode; continuing with default option.")
            logger.warning(f"Exception: {w}")
        
        if 'organization' in config['objects']:
            value, is_valid = is_valid_config_value(config['objects']['organization'], int)
            if is_valid:
                organizations_to_queue = value
            else:
                w = Exception ("Invalid configured output mode; continuing with default option.")
                logger.warning(f"Exception: {w}")
        else:
            w = Exception ("No configured output mode; continuing with default option.")
            logger.warning(f"Exception: {w}")

        if 'geopolitical' in config['objects']:
            value, is_valid = is_valid_config_value(config['objects']['geopolitical'], int)
            if is_valid:
                gpes_to_queue = value
            else:
                w = Exception ("Invalid configured output mode; continuing with default option.")
                logger.warning(f"Exception: {w}")
        else:
            w = Exception ("No configured output mode; continuing with default option.")
            logger.warning(f"Exception: {w}")

    if is_config_updated:
        # Write initial updated config back to file, if needed
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        is_config_updated = False

    '''Setup Command Line Argument Parsing'''
    parser = argparse.ArgumentParser(description='Description of your program')

    # Add arguments
    parser.add_argument('-f', '--file', type=str, help=f'Path to an input file containing object attribute options. Input file formats: {input_file_formats}')
    parser.add_argument('--save_config', type=bool, help='Saves the passed configuration')
    parser.add_argument('--reset_config', type=bool, help='Resets saved configuration to default')

    if is_results_output_mode_updated:
        parser.add_argument('-out', '--output', type=str, help=f'Output mode: {results_output_modes}')
    else:
        parser.add_argument('-out', '--output', type=str, default=f'{results_output_mode.value}', help=f'Output mode: {results_output_modes}')

    if is_results_outfile_format_updated:        
        parser.add_argument('--outfile_format', type=str, help=f'Output file formats: {results_output_file_formats}')
    else:
        parser.add_argument('--outfile_format', type=str, default=f'{results_outfile_format.value}', help=f'Output file formats: {results_output_file_formats}')

    parser.add_argument('--outfile_name', type=str, help='Name to save the results file to')

    if is_persons_to_queue_updated:        
        parser.add_argument('-p', '--person', type=int, help='Specifies how many person objects to generate')
    else:
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

    # Main arguments in config
    if args.output:
        value = str(args.output)
        if is_valid_results_output_mode(value):
            config['main']['output'] = value
            results_output_mode = OutputMode(value)
            is_config_updated = True
        else:
            w = Exception ("Invalid output mode parameter; continuing with configured option.")
            logger.warning(f"Exception: {w}")
    
    if args.outfile_format:
        value = str(args.outfile_format)
        if is_valid_results_outfile_format(value):
            config['main']['outfile_format'] = value
            results_outfile_format = OutputResultsFileFormat(value)
            is_config_updated = True
        else:
            w = Exception ("Invalid outfile format; continuing with configured option.")
            logger.warning(f"Exception: {w}")

    # Main arguments NOT in config
    if args.file:
        input_file_path = args.file
        if is_valid_input_options_file(input_file_path):
            try:
                # TODO: Create an import file to test the options list with
                read_input_options_file(input_file_path, options_list)
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
        value, is_valid = is_valid_config_value(args.person, int)
        if is_valid:
            persons_to_queue = value
            config['objects']['person'] = str(persons_to_queue)
            is_config_updated = True
    for i in range(0, persons_to_queue):
        tracker.entity_stack.append(Person)

    if args.location:
        has_commandline_object_args = True
        value, is_valid = is_valid_config_value(args.location, int)
        if is_valid:
            locations_to_queue = value
            config['objects']['location'] = str(locations_to_queue)
            is_config_updated = True
    for i in range(0, locations_to_queue):
        tracker.entity_stack.append(Location)

    if args.organization:
        has_commandline_object_args = True
        value, is_valid = is_valid_config_value(args.organization, int)
        if is_valid:
            organizations_to_queue = value
            config['objects']['organization'] = str(organizations_to_queue)
            is_config_updated = True
    for i in range(0, organizations_to_queue):
        tracker.entity_stack.append(Organization)
        
    if args.geopolitical:
        has_commandline_object_args = True
        value, is_valid = is_valid_config_value(args.geopolitical, int)
        if is_valid:
            gpes_to_queue = value
            config['objects']['geopolitical'] = str(gpes_to_queue)
            is_config_updated = True
    for i in range(0, gpes_to_queue):
        tracker.entity_stack.append(GeoPoliticalEntity)
    
    if args.save_config and is_config_updated:
        # Write updated config to file
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    # Process entities stack populated by command line or config parsing 
    # by popping off the top factory and creating an entity that is added to the graph
    process_entities_stack(entities, tracker, options_list)

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
                    process_entities_stack(entities, tracker, options_list)
                    menu_page = "main"
                elif choice == "4":
                    menu_page = "config"
                elif choice == "5":
                    # Save Generated Entities to Object File
                    save_object_data(entities, f"entity_{object_output_file_path}")
                    save_object_data(options_list, f"option_{object_output_file_path}")
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
                    person = create_random_person(entities, options_list)
                    input("Press any key to continue...")
                else:
                    print("Invalid choice. Please try again.")
            case "entity_create":
                if choice == "1":
                    num_person = input("How many Person entities would you like to create? ")
                    for i in range(0, int(num_person)):
                        tracker.entity_stack.append(Person)
                elif choice == "2":
                    num_location = input("How many Location entities would you like to create? ")
                    for i in range(0, int(num_location)):
                        tracker.entity_stack.append(Location)
                elif choice == "3":
                    num_org = input("How many Organization entities would you like to create? ")
                    for i in range(0, int(num_org)):
                        tracker.entity_stack.append(Organization)
                elif choice == "4":
                    num_gpe = input("How many Geopolitical entities would you like to create? ")
                    for i in range(0, int(num_gpe)):
                        tracker.entity_stack.append(GeoPoliticalEntity)
                else:
                    print("Invalid choice. Please try again.")
            case "entity_view":
                if choice == "1":
                    print(f"------------------------------------------------------------------------------------------\n")
                    for entity in entities.graph.keys():
                        if isinstance(entity, Person):
                            display_person(entity)
                            print("------------------------------")
                elif choice == "2":
                    for entity in entities.graph.keys():
                        if isinstance(entity, Location):
                            display_location(entity)
                            print("------------------------------")
                elif choice == "3":
                    for entity in entities.graph.keys():
                        if isinstance(entity, Organization):
                            display_organization(entity)
                            print("------------------------------")
                elif choice == "4":
                    for entity in entities.graph.keys():
                        if isinstance(entity, GeoPoliticalEntity):
                            display_gpe(entity)
                            print("------------------------------")
                elif choice == "5":
                    for entity in entities.graph.keys():
                        display_entity(entity)
                        print("------------------------------")
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

def get_default_options_list() -> list[EntityOption]:
    """
    Returns an EntityOptions list populated with the hardcoded default options

    returns:
        list[EntityOption]: A list of EntityOption objects.
    """
    default_options_list: list[EntityOption] = []
    try:
        # Load the default options list from the hardcoded default options
        default_options_list = [
            # Age
            EntityOption(name="Young", type=OptionTypes.AGE, description="A child, adolescent, or early adult"),
            EntityOption(name="Old", type=OptionTypes.AGE, description="Elderly or advanced in years"),
            EntityOption(name="Middle-aged", type=OptionTypes.AGE, description="Between young and old"),
            EntityOption(name="Adult", type=OptionTypes.AGE, description="Mature and fully grown"),
            EntityOption(name="Teen", type=OptionTypes.AGE, description="Adolescent or young adult"),
            EntityOption(name="Baby", type=OptionTypes.AGE, description="Infant or very young child"),
            EntityOption(name="Toddler", type=OptionTypes.AGE, description="Young child learning to walk"),

            # Background
            EntityOption(name="Academic", type=OptionTypes.BACKGROUND, description="Educated and scholarly"),
            EntityOption(name="Apprentice", type=OptionTypes.BACKGROUND, description="Learned a trade from a master"),
            EntityOption(name="Aristocrat", type=OptionTypes.BACKGROUND, description="Born into privilege and wealth"),
            EntityOption(name="Criminal", type=OptionTypes.BACKGROUND, description="Life of petty or grand theft"),
            EntityOption(name="Entertainer", type=OptionTypes.BACKGROUND, description="Musicians, actors, dancers, etc."),
            EntityOption(name="Explorer", type=OptionTypes.BACKGROUND, description="Traveled extensively"),
            EntityOption(name="Far Traveler", type=OptionTypes.BACKGROUND, description="From a distant land"),
            EntityOption(name="Folk Hero", type=OptionTypes.BACKGROUND, description="Champion of the common people"),
            EntityOption(name="Guild Artisan", type=OptionTypes.BACKGROUND, description="Member of a skilled guild"),
            EntityOption(name="Hermit", type=OptionTypes.BACKGROUND, description="Lived in seclusion for an extended period"),
            EntityOption(name="Noble", type=OptionTypes.BACKGROUND, description="Of high social standing"),
            EntityOption(name="Outlaw", type=OptionTypes.BACKGROUND, description="A fugitive from justice"),
            EntityOption(name="Pirate", type=OptionTypes.BACKGROUND, description="Life of piracy and plunder"),
            EntityOption(name="Sage", type=OptionTypes.BACKGROUND, description="Dedicated to the pursuit of knowledge"),
            EntityOption(name="Sailor", type=OptionTypes.BACKGROUND, description="Life at sea"),
            EntityOption(name="Soldier", type=OptionTypes.BACKGROUND, description="Served in a military or paramilitary force"),
            EntityOption(name="Spy", type=OptionTypes.BACKGROUND, description="Trained in espionage and subterfuge"),
            EntityOption(name="Urbanite", type=OptionTypes.BACKGROUND, description="Grew up in a large city"),
            EntityOption(name="Wanderer", type=OptionTypes.BACKGROUND, description="Traveled extensively with no fixed abode"),
            EntityOption(name="Zealot", type=OptionTypes.BACKGROUND, description="Fanatically devoted to a cause or deity"),

            # Climate
            EntityOption(name="Temperate", type=OptionTypes.CLIMATE, description="Mild weather with four distinct seasons"),
            EntityOption(name="Tropical", type=OptionTypes.CLIMATE, description="Hot and humid year-round"),
            EntityOption(name="Arid", type=OptionTypes.CLIMATE, description="Hot and dry with little rainfall"),
            EntityOption(name="Tundra", type=OptionTypes.CLIMATE,  description="Frigid and icy with short summers"),
            EntityOption(name="Subarctic", type=OptionTypes.CLIMATE, description="Long, cold winters and short, cool summers"),
            EntityOption(name="Mediterranean", type=OptionTypes.CLIMATE, description="Warm, dry summers and mild, wet winters"),
            EntityOption(name="Highland", type=OptionTypes.CLIMATE, description="Cool summers and cold, snowy winters"),
            EntityOption(name="Oceanic", type=OptionTypes.CLIMATE, description="Mild temperatures and frequent precipitation"),
            EntityOption(name="Continental", type=OptionTypes.CLIMATE, description="Large variations in temperature between summer and winter"),
            EntityOption(name="Tropical Monsoon", type=OptionTypes.CLIMATE, description="Hot and humid with distinct wet and dry seasons"),

            # Family Name
            EntityOption(name="Stoneshield", type=OptionTypes.FAMILY_NAME, description="Strong and defensive"),
            EntityOption(name="Whisperwind", type=OptionTypes.FAMILY_NAME, description="Agile and stealthy"),
            EntityOption(name="Silverflow", type=OptionTypes.FAMILY_NAME, description="Magical and arcane"),
            EntityOption(name="Everflame", type=OptionTypes.FAMILY_NAME, description="Passionate and fiery"),
            EntityOption(name="Greenhaven", type=OptionTypes.FAMILY_NAME, description="Nature-connected and nurturing"),
            EntityOption(name="Stormbringer", type=OptionTypes.FAMILY_NAME, description="Powerful and destructive"),
            EntityOption(name="Brightwood", type=OptionTypes.FAMILY_NAME, description="Optimistic and hopeful"),
            EntityOption(name="Shadowheart", type=OptionTypes.FAMILY_NAME, description="Mysterious and secretive"),
            EntityOption(name="Moonsilver", type=OptionTypes.FAMILY_NAME, description="Elusive and mystical"),
            EntityOption(name="Goldforge", type=OptionTypes.FAMILY_NAME, description="Skilled artisans and crafters"),

            # Name
            EntityOption(name="Anya", type=OptionTypes.NAME),
            EntityOption(name="Elora", type=OptionTypes.NAME),
            EntityOption(name="Kael", type=OptionTypes.NAME),
            EntityOption(name="Bron", type=OptionTypes.NAME),
            EntityOption(name="Gwyn", type=OptionTypes.NAME),
            EntityOption(name="Zara", type=OptionTypes.NAME),
            EntityOption(name="Krog", type=OptionTypes.NAME),
            EntityOption(name="Lysander", type=OptionTypes.NAME),
            EntityOption(name="Seraphina", type=OptionTypes.NAME),
            EntityOption(name="Orion", type=OptionTypes.NAME),

            # Nickname
            EntityOption(name="The Swift", type=OptionTypes.NICKNAME, description="Known for speed and agility"),
            EntityOption(name="The Silent", type=OptionTypes.NICKNAME, description="Known for stealth and cunning"),
            EntityOption(name="The Wise", type=OptionTypes.NICKNAME, description="Known for intelligence and wisdom"),
            EntityOption(name="The Strong", type=OptionTypes.NICKNAME, description="Known for physical strength and power"),
            EntityOption(name="The Bold", type=OptionTypes.NICKNAME, description="Known for courage and bravery"),
            EntityOption(name="The Wanderer", type=OptionTypes.NICKNAME, description="Known for their travels and explorations"),
            EntityOption(name="The Healer", type=OptionTypes.NICKNAME, description="Known for their healing abilities"),
            EntityOption(name="The Shadow", type=OptionTypes.NICKNAME, description="Known for their mysterious nature"),
            EntityOption(name="The Jester", type=OptionTypes.NICKNAME, description="Known for their wit and humor"),
            EntityOption(name="The Scholar", type=OptionTypes.NICKNAME, description="Known for their vast knowledge"),

            # Personality Trait
            EntityOption(name="Brave", type=OptionTypes.PERSONALITY_TRAIT, description="Courageous and fearless"),
            EntityOption(name="Compassionate", type=OptionTypes.PERSONALITY_TRAIT, description="Kind and caring towards others"),
            EntityOption(name="Curious", type=OptionTypes.PERSONALITY_TRAIT, description="Eager to learn and explore"),
            EntityOption(name="Determined", type=OptionTypes.PERSONALITY_TRAIT, description="Resolute and unwavering in their goals"),
            EntityOption(name="Dishonest", type=OptionTypes.PERSONALITY_TRAIT, description="Untrustworthy and deceitful"),
            EntityOption(name="Greedy", type=OptionTypes.PERSONALITY_TRAIT, description="Driven by a desire for wealth and power"),
            EntityOption(name="Impatient", type=OptionTypes.PERSONALITY_TRAIT, description="Easily frustrated and restless"),
            EntityOption(name="Jealous", type=OptionTypes.PERSONALITY_TRAIT, description="Envious of others' success"),
            EntityOption(name="Loyal", type=OptionTypes.PERSONALITY_TRAIT, description="Faithful and devoted to their friends and allies"),
            EntityOption(name="Suspicious", type=OptionTypes.PERSONALITY_TRAIT, description="Distrustful and wary of others"),

            # Physical Trait
            EntityOption(name="Agile", type=OptionTypes.PHYSICAL_TRAIT, description="Nimble and quick"),
            EntityOption(name="Delicate Features", type=OptionTypes.PHYSICAL_TRAIT, description="Graceful and refined appearance"),
            EntityOption(name="Scarred Face", type=OptionTypes.PHYSICAL_TRAIT, description="A visible mark from a past injury"),
            EntityOption(name="Unusual Hair Color", type=OptionTypes.PHYSICAL_TRAIT, description="Unique hair color, such as silver or purple"),
            EntityOption(name="Missing Limb", type=OptionTypes.PHYSICAL_TRAIT, description="Lost a limb due to injury or accident"),
            EntityOption(name="Tall", type=OptionTypes.PHYSICAL_TRAIT, description="Taller than average"),
            EntityOption(name="Short", type=OptionTypes.PHYSICAL_TRAIT, description="Shorter than average"),
            EntityOption(name="Piercing Eyes", type=OptionTypes.PHYSICAL_TRAIT, description="Intense and penetrating eyes"),
            EntityOption(name="Distinctive Voice", type=OptionTypes.PHYSICAL_TRAIT, description="A unique and memorable voice"),

            # Profession
            EntityOption(name="Blacksmith", type=OptionTypes.PROFESSION, description="Crafts weapons and armor"),
            EntityOption(name="Farmer", type=OptionTypes.PROFESSION, description="Cultivates crops and raises livestock"),
            EntityOption(name="Hunter", type=OptionTypes.PROFESSION, description="Provides food for the community through hunting"),
            EntityOption(name="Merchant", type=OptionTypes.PROFESSION, description="Trades goods and services"),
            EntityOption(name="Scholar", type=OptionTypes.PROFESSION, description="Studies knowledge and teaches others"),
            EntityOption(name="Soldier", type=OptionTypes.PROFESSION, description="Protects the community from threats"),
            EntityOption(name="Fisherman", type=OptionTypes.PROFESSION, description="Provides food by fishing in local waters"),
            EntityOption(name="Woodcutter", type=OptionTypes.PROFESSION, description="Provides lumber for construction and other uses"),
            EntityOption(name="Cook", type=OptionTypes.PROFESSION, description="Prepares food for the community"),
            EntityOption(name="Herbalist", type=OptionTypes.PROFESSION, description="Collects and uses medicinal plants"),

            # Relationship
            EntityOption(name="Spouse", type=OptionTypes.RELATIONSHIP, description="Married to another individual"),
            EntityOption(name="Sibling", type=OptionTypes.RELATIONSHIP, description="Brother or sister"),
            EntityOption(name="Parent", type=OptionTypes.RELATIONSHIP, description="Has children"),
            EntityOption(name="Child", type=OptionTypes.RELATIONSHIP, description="Has parents"),
            EntityOption(name="Friend", type=OptionTypes.RELATIONSHIP, description="Close companion"),
            EntityOption(name="Rival", type=OptionTypes.RELATIONSHIP, description="Competitor or enemy"),
            EntityOption(name="Mentor", type=OptionTypes.RELATIONSHIP, description="Provides guidance and training"),
            EntityOption(name="Apprentice", type=OptionTypes.RELATIONSHIP, description="Learns from a mentor"),
            EntityOption(name="Enemy", type=OptionTypes.RELATIONSHIP, description="An active opponent"),
            EntityOption(name="Ally", type=OptionTypes.RELATIONSHIP, description="A trusted friend and supporter"),

            # Race
            EntityOption(name="Human", type=OptionTypes.RACE, description="Common and adaptable race"),
            EntityOption(name="Elf", type=OptionTypes.RACE, description="Longevity and connection to nature"),
            EntityOption(name="Dwarf", type=OptionTypes.RACE, description="Sturdy and resilient, skilled in mining and crafting"),
            EntityOption(name="Orc", type=OptionTypes.RACE, description="Strong and warlike, often misunderstood"),
            EntityOption(name="Goblin", type=OptionTypes.RACE, description="Small and mischievous, known for trickery"),
            EntityOption(name="Halfling", type=OptionTypes.RACE, description="Small and agile, known for luck and charm"),
            EntityOption(name="Dragonborn", type=OptionTypes.RACE, description="Powerful and draconic heritage"),
            EntityOption(name="Gnome", type=OptionTypes.RACE, description="Small and inventive, skilled in magic and technology"),
            EntityOption(name="Tiefling", type=OptionTypes.RACE, description="Demonic heritage, often associated with magic"),
            EntityOption(name="Aarakocra", type=OptionTypes.RACE, description="Bird-like humanoids, skilled in flight"),

            # Resources
            EntityOption(name="Gold", type=OptionTypes.RESOURCES, description="Valuable currency"),
            EntityOption(name="Land", type=OptionTypes.RESOURCES, description="Property and territory"),
            EntityOption(name="Food", type=OptionTypes.RESOURCES, description="Supplies for sustenance"),
            EntityOption(name="Water", type=OptionTypes.RESOURCES, description="Access to clean water sources"),
            EntityOption(name="Wood", type=OptionTypes.RESOURCES, description="Lumber for construction and other uses"),
            EntityOption(name="Iron", type=OptionTypes.RESOURCES, description="Metal for tools and weapons"),
            EntityOption(name="Stone", type=OptionTypes.RESOURCES, description="Building materials and tools"),
            EntityOption(name="Magic", type=OptionTypes.RESOURCES, description="Access to magical power or items"),
            EntityOption(name="Influence", type=OptionTypes.RESOURCES, description="Political power and connections"),
            EntityOption(name="Knowledge", type=OptionTypes.RESOURCES, description="Access to information and learning"),

            # Role
            EntityOption(name="Leader", type=OptionTypes.ROLE, description="Guides and directs others"),
            EntityOption(name="Guardian", type=OptionTypes.ROLE, description="Protects and defends others"),
            EntityOption(name="Artisan", type=OptionTypes.ROLE, description="Creates and crafts valuable items"),
            EntityOption(name="Scholar", type=OptionTypes.ROLE, description="Seeks and shares knowledge"),
            EntityOption(name="Explorer", type=OptionTypes.ROLE, description="Seeks adventure and discovery"),
            EntityOption(name="Rogue", type=OptionTypes.ROLE, description="Operates in secrecy and cunning"),
            EntityOption(name="Mystic", type=OptionTypes.ROLE, description="Possesses magical abilities"),
            EntityOption(name="Warrior", type=OptionTypes.ROLE, description="A skilled combatant"),
            EntityOption(name="Diplomat", type=OptionTypes.ROLE, description="Negotiates and resolves conflicts"),
            EntityOption(name="Healer", type=OptionTypes.ROLE, description="Provides medical care and healing"),

            #Sex
            EntityOption(name="Male", type=OptionTypes.SEX),
            EntityOption(name="Female", type=OptionTypes.SEX),
            #EntityOption(name="Intersex", type=OptionTypes.SEX),

            #Skill
            EntityOption(name="Acrobatics", type=OptionTypes.SKILL, description="Balance, agility, tumbling"),
            EntityOption(name="Animal Handling", type=OptionTypes.SKILL, description="Interact with animals"),
            EntityOption(name="Athletics", type=OptionTypes.SKILL, description="Strength or dexterity-based feats of physical exertion"),
            EntityOption(name="Deception", type=OptionTypes.SKILL, description="Tricking or deceiving others"),
            EntityOption(name="Diplomacy", type=OptionTypes.SKILL, description="Persuasion and social interaction"),
            EntityOption(name="Insight", type=OptionTypes.SKILL, description="Detect lies and hidden meanings"),
            EntityOption(name="Intimidation", type=OptionTypes.SKILL, description="Frighten or coerce others"),
            EntityOption(name="Investigation", type=OptionTypes.SKILL, description="Gather information and solve mysteries"),
            EntityOption(name="Medicine", type=OptionTypes.SKILL, description="Treat injuries and diseases"),
            EntityOption(name="Nature", type=OptionTypes.SKILL, description="Knowledge of the natural world"),
            EntityOption(name="Perception", type=OptionTypes.SKILL, description="Notice hidden things"),
            EntityOption(name="Performance", type=OptionTypes.SKILL, description="Entertain others with music, dance, or acting"),
            EntityOption(name="Persuasion", type=OptionTypes.SKILL, description="Influence others through charm and reason"),
            EntityOption(name="Religion", type=OptionTypes.SKILL, description="Knowledge of deities, faiths, and religious lore"),
            EntityOption(name="Sleight of Hand", type=OptionTypes.SKILL, description="Dexterity, sleight of hand, and quick thinking"),
            EntityOption(name="Stealth", type=OptionTypes.SKILL, description="Move quietly and unseen"),
            EntityOption(name="Survival", type=OptionTypes.SKILL, description="Survive in the wilderness"),


            # Terrain
            EntityOption(name="Forest", type=OptionTypes.TERRAIN, description="Densely wooded area"),
            EntityOption(name="Mountain", type=OptionTypes.TERRAIN, description="High, rocky terrain"),
            EntityOption(name="Desert", type=OptionTypes.TERRAIN, description="Dry, sandy landscape"),
            EntityOption(name="Swamp", type=OptionTypes.TERRAIN, description="Wetlands with stagnant water"),
            EntityOption(name="Plains", type=OptionTypes.TERRAIN, description="Flat, grassy land"),
            EntityOption(name="Coast", type=OptionTypes.TERRAIN, description="Land bordering the sea"),
            EntityOption(name="Tundra", type=OptionTypes.TERRAIN, description="Treeless Arctic or subarctic region"),
            EntityOption(name="Jungle", type=OptionTypes.TERRAIN, description="Dense tropical rainforest"),
            EntityOption(name="Cave", type=OptionTypes.TERRAIN, description="Natural underground cavity"),
            EntityOption(name="Volcano", type=OptionTypes.TERRAIN, description="Mountain with an opening that erupts lava"),

             # Type 
            EntityOption(name="Village", type=OptionTypes.TYPE, description="Small community of people"),
            EntityOption(name="City", type=OptionTypes.TYPE, description="Large urban center"),
            EntityOption(name="Castle", type=OptionTypes.TYPE, description="Fortified residence of a noble"),
            EntityOption(name="Temple", type=OptionTypes.TYPE, description="Place of worship"),
            EntityOption(name="Tavern", type=OptionTypes.TYPE, description="Place to eat, drink, and socialize"),
            EntityOption(name="Market", type=OptionTypes.TYPE, description="Place for buying and selling goods"),
            EntityOption(name="Library", type=OptionTypes.TYPE, description="Place for storing and accessing books"),
            EntityOption(name="Forest", type=OptionTypes.TYPE, description="Densely wooded area"),
            EntityOption(name="Cave", type=OptionTypes.TYPE, description="Natural underground cavity"),
            EntityOption(name="Ruins", type=OptionTypes.TYPE, description="Remains of an ancient civilization"),

            # Unique Trait
            EntityOption(name="Sixth Sense", type=OptionTypes.UNIQUE, description="An uncanny ability to predict danger"),
            EntityOption(name="Animal Companion", type=OptionTypes.UNIQUE, description="A loyal animal companion"),
            EntityOption(name="Magical Affinity", type=OptionTypes.UNIQUE, description="A natural talent for magic"),
            EntityOption(name="Precognition", type=OptionTypes.UNIQUE, description="The ability to foresee future events"),
            EntityOption(name="Regeneration", type=OptionTypes.UNIQUE, description="The ability to heal quickly"),
            EntityOption(name="Superhuman Strength", type=OptionTypes.UNIQUE, description="Exceptional physical strength"),
            EntityOption(name="Telepathy", type=OptionTypes.UNIQUE, description="The ability to read minds"),
            EntityOption(name="Shape-shifting", type=OptionTypes.UNIQUE, description="The ability to change one's appearance"),
            EntityOption(name="Invisibility", type=OptionTypes.UNIQUE, description="The ability to become invisible"),
            EntityOption(name="Elemental Control", type=OptionTypes.UNIQUE, description="The ability to control a specific element (e.g., fire, water)")
        ]
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error: {e}")
    return default_options_list

def is_valid_input_options_file(input_file_path:str) -> bool:
    if os.path.exists(input_file_path):
        mime = magic.from_file(input_file_path, mime = True)
    else:
        raise FileNotFoundError (f"Input options file not found at {input_file_path}.")
    return mime in InputOptionsFileFormat
        
def read_input_options_file(input_file_path: str, options_list: list[EntityOption], flag:str = EntityOptionListFlag.ADD) -> None:
    """
    Reads input options from a CSV or JSON file and populates the `options_list`
    with `EntityOption` instances.

    args:
        input_file_path: Path to the input options file.

    raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file format is invalid or the data cannot be parsed.
    """
    # TODO: Change read_input_options_file function to load and save the random 
    # options into the options list from the default or passed file, using a flag 
    # to determine whether to add to or override the default options list.  
    
    if flag == EntityOptionListFlag.OVERRIDE:
        options_list: list[EntityOption] = []
    elif not options_list:
        options_list: list[EntityOption] = []
    
    try:
        if input_file_path.endswith(".csv"):
            with open(input_file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        #Parse row data from the CSV file to the local EntityOption member variables
                        option_type = OptionTypes[row['type']]
                        option_name = row['name']
                        description = row.get('description', ''),
                        weight = float(row.get('weight', 1.0)),
                        min = int(row.get('min', 1))
                        max = int(row.get('max', 1))

                        exclusive_options: list[EntityOption] = []
                        if 'exclusive' in row and row['exclusive']:
                            for exclusive_option in row['exclusive'].split(','):
                                # Search for the exclusive option in the global options list 
                                existing_exclusive_option_index = index_in_options_list(EntityOption(name=exclusive_option), options_list)
                                if existing_exclusive_option_index is not None:
                                    exclusive_options.append(options_list[existing_exclusive_option_index])
                                else:
                                    exclusive_options.append(EntityOption(name=exclusive_option))

                        requirements: list[str] = []
                        if 'requirements' in row and row['requirements']:
                            requirements = row['requirements'].split(',')

                        specializations: list[EntityOption] = []
                        if 'specializations' in row and row['specializations']:
                            for specialization in row['specializations'].split(','):
                                # Search for the specialization option in the global options list 
                                existing_specialization_index = index_in_options_list(EntityOption(name=specialization, type=OptionTypes.SPECIALIZATION), options_list)
                                if existing_specialization_index is not None:
                                    specializations.append(options_list[existing_specialization_index])
                                else:
                                    specializations.append(EntityOption(name=specialization, type=OptionTypes.SPECIALIZATION))
                        
                        # Find or create the EntityOption in the options_list using the local member variables
                        upsert_entity_option(EntityOption(
                            type = option_type,
                            name = option_name,
                            description = description,
                            weight = weight,
                            min = min,
                            max = max,
                            mutually_exclusive = exclusive_options,
                            requirements = requirements,
                            specilizations = specializations
                            )
                        )
                    except KeyError as e:
                        logger = logging.getLogger(__name__)
                        err_msg = f"Invalid CSV header: {e}"
                        logger.error(err_msg)
                        raise ValueError(err_msg)
                    except ValueError as e:
                        logger = logging.getLogger(__name__)
                        err_msg = f"Invalid data in CSV: {e}"
                        logger.error(err_msg)
                        raise ValueError(err_msg)

        elif input_file_path.endswith(".json"):
            with open(input_file_path, 'r') as file:
                data = json.load(file)
                for option_data in data:
                    try:
                        #Parse row data from the CSV file to the local EntityOption member variables
                        option_type = OptionTypes[option_data['type']]
                        option_name = option_data['name']
                        description = option_data.get('description', '')
                        weight = float(option_data.get('weight', 1.0))
                        min = int(option_data.get('min', 1))
                        max = int(option_data.get('max', 1))

                        exclusive_options: list[EntityOption] = []
                        if 'exclusive' in option_data:
                            for exclusive_option in option_data.get('exclusive', []):
                                # Search for the exclusive option in the global options list 
                                existing_exclusive_option_index = index_in_options_list(EntityOption(name=exclusive_option), options_list)
                                if existing_exclusive_option_index is not None:
                                    exclusive_options.append(options_list[existing_exclusive_option_index])
                                else:
                                    exclusive_options.append(EntityOption(name=exclusive_option))

                        requirements: list[str] = option_data.get('requirements', [])

                        specializations: list[EntityOption] = []
                        if 'specializations' in option_data:
                            for specialization in option_data.get('specializations', []):
                                # Search for the specialization option in the global options list 
                                existing_specialization_index = index_in_options_list(EntityOption(name=specialization, type=OptionTypes.SPECIALIZATION), options_list)
                                if existing_specialization_index is not None:
                                    specializations.append(options_list[existing_specialization_index])
                                else:
                                    specializations.append(EntityOption(name=specialization, type=OptionTypes.SPECIALIZATION))

                        # Find or create the EntityOption in the options_list using the local member variables
                        upsert_entity_option(EntityOption(
                            type = option_type,
                            name = option_name,
                            description = description,
                            weight = weight,
                            min = min,
                            max = max,
                            mutually_exclusive = exclusive_options,
                            requirements = requirements,
                            specilizations = specializations
                            )
                        )
                    except KeyError as e:
                        logger = logging.getLogger(__name__)
                        err_msg = f"Invalid JSON data: {e}"
                        logger.error(err_msg)
                        raise ValueError(err_msg)
                    except ValueError as e:
                        logger = logging.getLogger(__name__)
                        err_msg = f"Invalid data in JSON: {e}"
                        logger.error(err_msg)
                        raise ValueError(err_msg)

        else:
            logger = logging.getLogger(__name__)
            err_msg = f"Unsupported file format: {input_file_path}"
            logger.error(err_msg)
            raise ValueError(err_msg)

    except FileNotFoundError as e:
        raise FileNotFoundError(f"Input options file not found at {input_file_path}.")

def index_in_options_list(option: EntityOption, options_list: list[EntityOption]) -> int:
    # Find the index of the existing option in the options_list
    if option.name is not None and option.type is not None:
        try:
            existing_option_index = next(i for i, opt in enumerate(options_list) 
                                        if opt.type == option.type and opt.name == option.name)
        except StopIteration:
            existing_option_index = None
    elif option.name is not None:
        try:
            existing_option_index = next(i for i, opt in enumerate(options_list) 
                                        if opt.name == option.name)
        except StopIteration:
            existing_option_index = None
    else:
        existing_option_index = None
    return existing_option_index

def upsert_entity_option(option: EntityOption, options_list: list[EntityOption]) -> None:
    option_type: OptionTypes = option.type
    option_name: str = option.name
    description: str = option.description
    weight: float = option.weight
    min: int = option.min
    max: int = option.max
    exclusive_options: list[EntityOption] = option.mutually_exclusive
    requirements: list[str] = option.requirements
    specializations: list[EntityOption] = option.specilizations

    existing_option_index = index_in_options_list(EntityOption(name=option_name, type=option_type), options_list)

    if existing_option_index is not None:
        existing_option = options_list[existing_option_index]
        # Update existing option with new values 
        existing_option.description = description
        existing_option.weight = weight
        existing_option.min = min
        existing_option.max = max
        existing_option.mutually_exclusive.extend(exclusive_options)
        existing_option.requirements += requirements
        existing_option.specilizations.extend(specializations)
        # Save it back to the existing option in the options_list
        options_list[existing_option_index] = existing_option
    else:   
        # Append new EntityOption to the options_list
        options_list.append(option)

def is_valid_results_output_mode(results_output_mode) -> bool:
    value, is_valid = is_valid_config_value(results_output_mode, str)
    if is_valid:
        return value in OutputMode
    return is_valid

def is_valid_results_outfile_format(results_outfile_format) -> bool:
    value, is_valid = is_valid_config_value(results_outfile_format, str)
    if is_valid:
        return value in OutputResultsFileFormat
    return is_valid

def get_datetime_filename(file_type: str, file_format: str) -> str:
    # Get current date and time
    now = datetime.datetime.now()

    # Format the date and time as a string
    formatted_datetime = now.strftime("%Y-%m-%d_%H-%M-%S")

    file_format = file_format.strip(".")

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

def is_valid_config_value(value, type) -> tuple[str | int | float | bool, bool]:
    try:
        cast_value = type(value)
        return cast_value, isinstance(cast_value, type)
    except ValueError:
        return None, False

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

def create_random_person(entities: EntityGraph, options_list: list[EntityOption]) -> Person:
    logger = logging.getLogger(__name__)
    logger.warning(f"Executing {create_random_person.__name__}...")
    
    applicable_option_types = {
        OptionTypes.AGE: (1, 1),
        OptionTypes.BACKGROUND: (1, 2),
        OptionTypes.FAMILY_NAME: (1, 1),
        OptionTypes.NAME: (1, 2),
        OptionTypes.NICKNAME: (0, 2),
        OptionTypes.PERSONALITY_TRAIT: (1, 3),
        OptionTypes.PHYSICAL_TRAIT: (1, 3),
        OptionTypes.PROFESSION: (1, 2),
        OptionTypes.RACE: (1, 1),
        OptionTypes.ROLE: (0, 3),
        OptionTypes.RELATIONSHIP: (1, 10),
        OptionTypes.SEX: (1, 1),
        OptionTypes.SPECIALIZATION: (0, 2),
        OptionTypes.SKILL: (1, 6),
        OptionTypes.UNIQUE: (0, 2)
    }

    # Create an instance of the factory
    factory: EntityFactory = EntityFactory(Person, applicable_option_types, options_list)
    logger.warning(f"Factory will create entities of type: {factory.get_entity_type()}")

    # Generate random person entity
    person: Person = factory.create_random_entity(options_list)
    species: EntityOption = person.attributes[OptionTypes.RACE][0]
    logger.warning(f"Person {person.id}: {person.name}, age={person.age}, species={species} sex={person.sex}")
    #logger.warning(f"Attributes of created Person: {person.attributes}")
    entities.add(person)

    return person

def create_random_location(entities: EntityGraph, options_list: list[EntityOption]) -> Location:
    logger = logging.getLogger(__name__)
    logger.warning(f"Executing {create_random_location.__name__}...")
    
    applicable_option_types = {
        OptionTypes.NAME: (1, 1),
        OptionTypes.TYPE: (1, 1),
        OptionTypes.CLIMATE: (1, 1),
        OptionTypes.RESOURCES: (1, 2),
        OptionTypes.TERRAIN: (1, 2),
        OptionTypes.UNIQUE: (0, 2)
    }

    # Create an instance of the factory
    factory: EntityFactory = EntityFactory(Location, applicable_option_types, options_list)
    logger.warning(f"Factory will create entities of type: {factory.get_entity_type()}")

    # Generate random entities
    location: Location = factory.create_random_entity(options_list)
    logger.warning(f"Attributes of created Location: {location.attributes}")
    entities.add(location)

    return location

def create_random_organization(entities: EntityGraph, options_list: list[EntityOption]) -> Organization:
    logger = logging.getLogger(__name__)
    logger.warning(f"Executing {create_random_organization.__name__}...")
    
    applicable_option_types = {
        OptionTypes.NAME: (1, 1),
        OptionTypes.TYPE: (1, 1),
        OptionTypes.RELATIONSHIP: (0, 5),
        OptionTypes.ROLE: (1, 2),
        OptionTypes.SPECIALIZATION: (0, 2),
        OptionTypes.UNIQUE: (0, 2)
    }

    # Create an instance of the factory
    factory: EntityFactory = EntityFactory(Organization, applicable_option_types, options_list)
    logger.warning(f"Factory will create entities of type: {factory.get_entity_type()}")

    # Generate random entities
    organization: Organization = factory.create_random_entity(options_list)
    logger.warning(f"Attributes of created Organization: {organization.attributes}")
    entities.add(organization)

    return organization

def create_random_gpe(entities: EntityGraph, options_list: list[EntityOption]) -> GeoPoliticalEntity:
    logger = logging.getLogger(__name__)
    logger.warning(f"Executing {create_random_gpe.__name__}...")
    
    applicable_option_types = {
        OptionTypes.NAME: (1, 1),
        OptionTypes.RELATIONSHIP: (0, 10),
        OptionTypes.TYPE: (1, 1),
        OptionTypes.UNIQUE: (0, 2)
    }
    
    # Create an instance of the factory
    factory: EntityFactory = EntityFactory(GeoPoliticalEntity, applicable_option_types, options_list)
    logger.warning(f"Factory will create entities of type: {factory.get_entity_type()}")

    # Generate random entities
    location = create_random_location(entities, options_list)
    organization = create_random_organization(entities, options_list)
    gpe: GeoPoliticalEntity = factory.create_random_entity(options_list, location= location, organization= organization)
    logger.warning(f"Attributes of created Location: {gpe.attributes}")
    entities.add(gpe)

    # TODO: Add relationship between location and orgranization and gpe to graph
    
    return gpe

def display_person(person: Person) -> None:
    species: EntityOption = person.attributes[OptionTypes.RACE][0]
    print(f"Person {person.id}: {person.name}, age={person.age}, species={species} sex={person.sex}")
    print(f"Attributes of created Person: {person.attributes}")

def display_location(location: Location) -> None:
    print(f"Location {location.id}: {location.name}")
    print(f"Attributes of created Location: {location.attributes}")

def display_organization(organization: Organization) -> None:
    print(f"Organization {organization.id}: {organization.name}")
    print(f"Attributes of created Organization: {organization.attributes}")

def display_gpe(gpe: GeoPoliticalEntity) -> None:
    print(f"Geopolitical {gpe.id}: {gpe.name}")
    print(f"Attributes of created Geopolitical: {gpe.attributes}")

def display_entity(entity: Entity) -> None:
    print(f"Entity {entity.id}: {entity.name}")
    print(f"Attributes of created Entity: {entity.attributes}")

def process_entities_stack(entities: EntityGraph, tracker: EntityTracker, options_list: list[EntityOption]) -> None:
    """
    Processes the tracker's entity stack by popping the top entity class off and creating a random instance 
    of an entity using the passed in options list and adding it to the graph for each entity type within 
    until the stack is empty.

    args:
        entities: An instance of the EntityGraph class to add the created entities to.
        tracker: An instance of the EntityTracker class to manage the entity stack.
        options: A list of EntityOption objects to use for randomization.

    returns:
        none
    """
    # TODO: Evalute the necessary relationships to other entities and add them to the graph as well if they are not already present
    while tracker.entity_stack:
        entity_type = tracker.entity_stack.pop()
        if entity_type == Person:    
            person = create_random_person(entities, options_list)
            
        elif entity_type == Location:
            location = create_random_location(entities, options_list)
            
        elif entity_type == Organization:
            organization = create_random_organization(entities, options_list)
            
        elif entity_type == GeoPoliticalEntity:
            gpe = create_random_gpe(entities, options_list)
            
        else:
            raise TypeError(f"Invalid entity type: {entity_type}")

if __name__ == "__main__":
    main()