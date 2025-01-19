import os, sys, datetime
import argparse, configparser
import magic, mimetypes
import pickle, logging
from logging.handlers import RotatingFileHandler

from static_options import InputOptionsFileFormat, OutputResultsFileFormat, OutputMode

from graph import Graph
from entity_factory import EntityFactory
from person import Person

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
    
    # TODO: Add autosave option later that when on does keep the load and save options in its own [autosave] section of the config
    parser.add_argument('--load', type=str, help='Name of a saved object file to load')
    parser.add_argument('--save', type=str, help='Name to save the generated object file to')

    # Parse arguments
    args = parser.parse_args()

    # Access parsed arguments
    if args.save_config and args.reset_config:
        # TODO: Add logging for config flag conflict
        raise Exception ("Save config and reset config flags are mutually exclusive.")

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
            # TODO: log error ("Invalid output mode.") but continue with config option
            if config['main']['output']:
                if is_valid_results_output_mode(config['main']['output']):
                    results_output_mode = OutputMode(config['main']['output'])
                else:
                    # TODO: log error ("Invalid configured output mode.") but continue with default option
                    pass
            else:
                # TODO: log error ("No configured output mode.") but continue with default option
                pass
    
    if args.outfile_format:
        if is_valid_results_outfile_format(args.outfile_format):
            config['main']['outfile_format'] = args.outfile_format
            results_outfile_format = OutputResultsFileFormat(args.outfile_format)
        else:
            # TODO: log error ("Invalid outfile format.") but continue with config option
            if config['main']['outfile_format']:
                if is_valid_results_outfile_format(config['main']['outfile_format']):
                    results_outfile_format = OutputResultsFileFormat(config['main']['outfile_format'])
                else:
                    # TODO: log error ("Invalid configured outfile format.") but continue with default option
                    pass
            else:
                # TODO: log error ("No configured outfile format.") but continue with default option
                pass

    # Main arguments NOT in config
    if args.file:
        input_file_path = args.file
        if is_valid_input_options_file(input_file_path):
            # TODO: Handle file read into table object memory
            read_input_options_file(input_file_path)
        else:
            # TODO: log error ("Invalid input file format.") but continue with standard options
            pass

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
    if args.person:
        config['objects']['person'] = str(args.person)
    if args.location:
        config['objects']['location'] = str(args.location)
    if args.organization:
        config['objects']['organization'] = str(args.organization)
    if args.geopolitical:
        config['objects']['geopolitical'] = str(args.geopolitical)
    
    if args.save_config:
        # Write updated config to file
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    #print(f"Config file args:")
    for key, value in config['main'].items():
        print(f"{key}={value}")

    for key, value in config['objects'].items():
        print(f"{key}={value}")

    # Use the options
    '''Setup Text Menu Interface for Program Operation and Testing'''
    use_commandline_interface: bool = True

    while use_commandline_interface:
        print("\nMenu:")
        print("1. Test Graph with Person objects")
        print("2. Create Random Person")
        print("3. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            test_graph_with_person()
        elif choice == "2":
            person = create_random_person()
            print(person)
        elif choice == "3":
            sys.exit("Exiting the program.")
        else:
            print("Invalid choice. Please try again.")

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
        print(f"Error: {e}")
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

def create_random_person() -> Person:
    print(f"Executing {create_random_person.__name__}...") # TODO: Log execution of create_random_person function
    # Create an instance of the factory
    factory = EntityFactory([Person])

    # Generate random entities
    #person: Person = factory.create_random_entity(first_name="Naruto", last_name="Uzumaki", description="The next Hokage, dattebayo!")
    person: Person = factory.create_random_entity()
    return person

if __name__ == "__main__":
    main()