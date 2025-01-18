import os, sys
import argparse, configparser
import logging
from logging.handlers import RotatingFileHandler

from tests.test_graph import *

from entity_factory import EntityFactory

from graph import Graph
from person import Person
from entity import RelationshipType

def main():
    """
    A program to generate fictional entities (people, places, organisations, and the connections between them) 
    at random based on user specified parameters against either the default dictionaries of attributes or one 
    passed to the program at runtime. 
    """

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
    parser.add_argument('-f', '--file', help='Path to the input file')
    parser.add_argument('-v', '--verbose', help='Increase output verbosity', action='store_true')
    parser.add_argument('--option1', type=str, help='Option 1 description')
    parser.add_argument('--option2', type=int, default=10, help='Option 2 description')

    # Parse arguments
    args = parser.parse_args()

    # Access parsed arguments
    print(f"Command line args: {args.file}") # TODO: Keep this but change to logging
    if args.verbose:
        print('Verbose mode enabled') # TODO: Keep this but change to logging

    '''Setup Config File Parsing'''

    # Read config file (if it exists)
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Update config with command line arguments
    if 'main' not in config:
        config['main'] = {}
    if args.option1:
        config['main']['option1'] = args.option1
    if args.option2:
        config['main']['option2'] = str(args.option2)

    # Write updated config to file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    # Use the options
    print(f"Config file args:")
    print("Option 1:", config['main'].get('option1'))
    print("Option 2:", config['main'].getint('option2'))

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

def create_random_person() -> Person:
    print(f"Executing {create_random_person.__name__}...") # TODO: Make this logging
    # Create an instance of the factory
    factory = EntityFactory([Person])

    # Generate random entities
    person: Person = factory.create_random_entity(first_name="Naruto", last_name="Uzumaki", description="The next Hokage, dattebayo!")
    return person

if __name__ == "__main__":
    main()