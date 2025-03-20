from owlready2 import *

def load_ontology(file_path):
    """Loads an ontology from a given file path."""
    onto = get_ontology(file_path).load()
    return onto

def get_concept_by_name(onto, concept_name):
    """Returns a concept by name (case-insensitive) as a Thing instance."""
    for concept in onto.classes():
        if concept.name.lower() == concept_name.lower():
            return concept
    return None

def get_subclasses(onto, concept_name):
    """Returns a list of subclasses for a given concept."""
    concept = get_concept_by_name(onto, concept_name)
    if concept:
        return list(concept.subclasses())
    return []

def get_all_subclasses(onto, concept_or_name):
    """
    Retrieves all subclasses (direct and indirect) of a given concept or concept name.

    Args:
        onto: The loaded ontology.
        concept_or_name: The concept object or its name (string).

    Returns:
        A list of all subclasses.
    """
    if isinstance(concept_or_name, str):
        concept = get_concept_by_name(onto, concept_or_name)
        if not concept:
            return []
    else:
        concept = concept_or_name

    all_subclasses = set()
    to_process = [concept]

    while to_process:
        current = to_process.pop(0)
        for subclass in current.subclasses():
            if subclass not in all_subclasses:
                all_subclasses.add(subclass)
                to_process.append(subclass)

    return list(all_subclasses)

def add_concept(onto, concept_name, parent_concept_name=None):
    """Adds a new concept to the ontology."""
    if get_concept_by_name(onto, concept_name):
      return None

    if parent_concept_name:
        parent_concept = get_concept_by_name(onto, parent_concept_name)
        if parent_concept:
            new_concept = types.new_class(concept_name, (parent_concept,))
        else:
            new_concept = types.new_class(concept_name, (Thing,))
    else:
        new_concept = types.new_class(concept_name, (Thing,))

    onto.imported_ontologies.append(new_concept.namespace.ontology)
    return new_concept

def add_object_property(onto, property_name, domain_concept_name=None, range_concept_name=None):
    """Adds a new object property to the ontology, with optional domain and range."""
    if get_concept_by_name(onto, property_name):
      return None
    new_property = types.new_class(property_name, (ObjectProperty,))
    if domain_concept_name:
        domain_concept = get_concept_by_name(onto, domain_concept_name)
        if domain_concept:
            new_property.domain.append(domain_concept)
    if range_concept_name:
        range_concept = get_concept_by_name(onto, range_concept_name)
        if range_concept:
            new_property.range.append(range_concept)

    onto.imported_ontologies.append(new_property.namespace.ontology)
    return new_property

def add_triple(onto, subject_concept_name, property_name, object_concept_name):
    """Adds a triple (subject, property, object) to the ontology."""
    subject_concept = get_concept_by_name(onto, subject_concept_name)
    property_concept = get_concept_by_name(onto, property_name)
    object_concept = get_concept_by_name(onto, object_concept_name)

    if subject_concept and property_concept and object_concept:
        subject_instance = subject_concept()
        setattr(subject_instance, property_name, [object_instance])
        onto.instances.append(subject_instance)
        return True
    return False

# Example Usage (assuming you have an ontology file "my_ontology.owl"):
# Create a dummy ontology for demonstration.
def create_dummy_ontology(file_path):
    onto = get_ontology(file_path)
    with onto:
        class Animal(Thing): pass
        class Mammal(Animal): pass
        class Dog(Mammal): pass
        class Cat(Mammal): pass
        class has_pet(ObjectProperty): pass
        has_pet.domain = [Animal]
        has_pet.range = [Animal]
    onto.save(file_path)


if __name__ == "__main__":
    # Example Usage
    ontology_file = "OWLs/SOMA.owl"
    # create_dummy_ontology(ontology_file)
    onto = load_ontology(ontology_file)

    # # Get concept by name
    action_concept = get_concept_by_name(onto, "physicaltask")
    print(f"Concept Action: {action_concept}, type: {type(action_concept)}")
    #
    # # Get subclasses
    action_subclasses = get_subclasses(onto, action_concept.name)
    print(f"Subclasses of Action: {action_subclasses}")

    action_subclasses = get_all_subclasses(onto, action_concept.name)
    print(f"length: {len(action_subclasses)}")
    print(f"All Subclasses of Action: {action_subclasses}")

    # # Get concept by name
    action_concept = get_concept_by_name(onto, "motion")
    print(f"Concept Action: {action_concept}, type: {type(action_concept)}")
    #
    # # Get subclasses
    action_subclasses = get_subclasses(onto, action_concept.name)
    print(f"Subclasses of Action: {action_subclasses}")

    action_subclasses = get_all_subclasses(onto, action_concept.name)
    print(f"length: {len(action_subclasses)}")
    print(f"All Subclasses of Action: {action_subclasses}")

    #
    # # Add a new concept
    # new_concept = add_concept(onto, "GoldenRetriever", "Dog")
    # print(f"New concept GoldenRetriever: {new_concept}")
    #
    # # Add object property
    # new_property = add_object_property(onto, "eats", "Dog", "Cat")
    # print(f"New object property eats: {new_property}")
    #
    # # add triple
    # add_triple(onto, "Dog", "has_pet", "Cat")
    #
    # #Save the ontology
    # onto.save(ontology_file)