import logging
from logging.handlers import RotatingFileHandler

from graph import Graph
from person import Person

def main():
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

    enities = Graph()
    person_a = Person(first_name="Harry", last_name="Potter", description=None, age=11)
    person_b = Person(first_name="James", last_name="Potter", description=None)
    person_c = Person(first_name="Lily", last_name="Potter", description=None)

    person_d = Person(first_name="Sirius", last_name="Black", description=None)
    person_e = Person(first_name="Hermione", last_name="Granger", description=None)
    person_f = Person(first_name="Daphne", last_name="Greengrass", description=None)

    person_x = Person(first_name="Draco", last_name="Malfoy", description=None)
    person_y = Person(first_name="Lucius", last_name="Malfoy", description=None)
    person_z = Person(first_name="Tom", last_name="Riddle", description=None)

    enities.add_edge(person_a, person_b)
    enities.add_edge(person_a, person_c)
    enities.add_edge(person_b, person_c)

    enities.add_edge(person_a, person_e)
    enities.add_edge(person_a, person_f)
    enities.add_edge(person_a, person_d)
    enities.add_edge(person_b, person_d)

    enities.add_edge(person_x, person_y)
    enities.add_edge(person_x, person_z)
    enities.add_edge(person_y, person_z)
    enities.add_edge(person_a, person_z)
    enities.add_edge(person_a, person_x)
    enities.add_edge(person_a, person_y)

    print(enities.graph[person_e])
    #print(enities)

if __name__ == "__main__":
    main()