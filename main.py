import logging
from logging.handlers import RotatingFileHandler

from graph import Graph
from person import Person
from entity import RelationshipType

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

    entities: Graph = Graph()
    person_a: Person = Person(first_name="Harry", last_name="Potter", description=None, age=11)
    person_b: Person = Person(first_name="James", last_name="Potter", description=None)
    person_c: Person = Person(first_name="Lily", last_name="Potter", description=None)

    person_d: Person = Person(first_name="Sirius", last_name="Black", description=None)
    person_e: Person = Person(first_name="Hermione", last_name="Granger", description=None)
    person_f: Person = Person(first_name="Daphne", last_name="Greengrass", description=None)

    person_g: Person = Person(first_name="Aberforth", last_name="Dumbledore", description=None)
    person_h: Person = Person(first_name="Poppy", last_name="Pomfrey", description=None)

    person_i: Person = Person(first_name="Dudley", last_name="Dursley", description=None)
    person_j: Person = Person(first_name="Cho", last_name="Chang", description=None)
    
    person_x: Person = Person(first_name="Draco", last_name="Malfoy", description=None)
    person_y: Person = Person(first_name="Lucius", last_name="Malfoy", description=None)
    person_z: Person = Person(first_name="Tom", last_name="Riddle", description=None)

    entities.add_edge(person_a, person_b)
    entities.add_edge(person_a, person_c)
    entities.add_edge(person_b, person_c)

    entities.add_edge(person_a, person_e)
    entities.add_edge(person_a, person_f)
    entities.add_edge(person_a, person_d)
    entities.add_edge(person_b, person_d)

    entities.add_edge(person_x, person_y)
    entities.add_edge(person_x, person_z)
    entities.add_edge(person_y, person_z)
    entities.add_edge(person_a, person_z)
    entities.add_edge(person_a, person_x)
    entities.add_edge(person_a, person_y)

    entities.add_node(person_g)
    entities.add_node(person_h)

    entities.add_metadata(person_a, person_b, metadata={"type": RelationshipType.CHILD, "details": "Harry looks strikingly like his father."})
    entities.add_metadata(person_b, person_a, metadata={"type": RelationshipType.PARENT, "details": "James never got to see Harry grow up."})
    entities.add_metadata(person_b, person_c, metadata={"type": RelationshipType.SPOUSE})
    entities.add_metadata(person_c, person_b, metadata={"type": RelationshipType.SPOUSE})
    entities.add_metadata_reciprocal(person_b, person_d, metadata={"type": RelationshipType.FRIEND})
    entities.add_metadata2(person_a, person_e, metadata1={"type": RelationshipType.FRIEND}, metadata2={"type": RelationshipType.CRUSH})

    entities.add(person_a, person_i, metadata1={"type": RelationshipType.COUSIN}, metadata2={"type": RelationshipType.COUSIN})
    entities.add(person_a, person_j, metadata1={"type": RelationshipType.CRUSH})

    print(f"Connections for {person_a.name}: ")
    for entity in entities.get_adjacent_nodes(person_a):
        print(f"{entity}")

    print(f"---------------------------------")
    print(f"Metadata for {person_a.name}: ")
    for key, value in entities.get_metadata(person_a): 
        print(f"{key[0].name}->{key[1].name}: {value}")

    print(f"---------------------------------")
    print(f"All Metadata: ")
    for key, value in entities.metadata.items():
        print(f"{key[0].name}->{key[1].name}: {value}")

    print(f"---------------------------------")
    print(f"Unconnected nodes: ")
    print(entities.unconnected_nodes())

if __name__ == "__main__":
    main()