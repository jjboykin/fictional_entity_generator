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
    parser.add_argument('-f', '--file', type=str, help='Path to an input file containing object attribute options. Input file formats: csv, json')
    parser.add_argument('--save_config', type=bool, help='Saves the passed configuration')
    parser.add_argument('--reset_config', type=bool, help='Resets saved configuration to default')

    parser.add_argument('-out', '--output', type=str, default='screen', help='Output mode: screen, file, both')
    parser.add_argument('--outfile_format', type=str, default='md', help='Output file format: md, csv, html')
        
    parser.add_argument('-p', '--person', type=int, default=1, help='Specifies how many person objects to generate')
    parser.add_argument('-l', '--location', type=int, default=0, help='Specifies how many location objects to generate')
    parser.add_argument('-o', '--organization', type=int, default=0, help='Specifies how many organization objects to generate')
    parser.add_argument('-gpe', '--geopolitical', type=int, default=0, help='Specifies how many geopolitical entity objects to generate')
    
    parser.add_argument('--load', type=str, help='Name of a saved object file to load')
    parser.add_argument('--save', type=str, help='Name to save the generated object file to')

    # Parse arguments
    args = parser.parse_args()

    # Access parsed arguments
    print(f"Command line args: {args}") # TODO: Keep this but change to logging

    if args.save_config and args.reset_config:
        # TODO: Add logging
        raise Exception ("Save config and reset config flags are mutually exclusive.")

    '''Setup Config File Parsing'''

    # Read config file (if it exists)
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Update config with command line arguments
    if 'main' not in config:
        config['main'] = {}
    if 'objects' not in config:
        config['objects'] = {}
        
    if args.output:
        config['main']['output'] = args.output
    if args.outfile_format:
        config['main']['outfile_format'] = args.outfile_format

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

    # Use the options
    print(f"Config file args:")
    for key, value in config['main'].items():
        print(f"{key}={value}")

    for key, value in config['objects'].items():
        print(f"{key}={value}")

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
    #person: Person = factory.create_random_entity(first_name="Naruto", last_name="Uzumaki", description="The next Hokage, dattebayo!")
    person: Person = factory.create_random_entity()
    return person

if __name__ == "__main__":
    main()