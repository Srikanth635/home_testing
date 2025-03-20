from owlready2 import get_ontology, Ontology, ThingClass
from typing import List, Dict, Any

def load_ontology(file_path: str) -> Ontology:
    """Loads an OWL ontology from a file."""
    ontology = get_ontology(file_path).load()
    return ontology

def extract_classes(ontology: Ontology) -> List[ThingClass]:
    """Extracts all classes from the ontology."""
    return list(ontology.classes())

def extract_class_details(owl_class: ThingClass) -> Dict[str, Any]:
    """Extracts details of a single class, including subclasses and annotations."""
    details = {
        "name": owl_class.name,
        "iri": owl_class.iri,
        "subclasses": [subclass.name for subclass in owl_class.subclasses()],
        # "annotations": {annotation.property.name: str(annotation.value) for annotation in owl_class.get_annotations()},
        "comment": list(owl_class.comment)
    }
    return details

def extract_all_class_details(ontology: Ontology) -> List[Dict[str, Any]]:
    """Extracts details for all classes in the ontology."""
    classes = extract_classes(ontology)
    return [extract_class_details(cls) for cls in classes]

# Example usage:
if __name__ == "__main__":
    ontology = load_ontology("OWLs/SOMA.owl") # Ensure SOMA.owl is in the same path from current directory.

    classes = extract_classes(ontology)
    cls = classes[80]
    print(cls)

    class_details = extract_class_details(cls)
    # all_class_details = extract_all_class_details(ontology)
    print("*"*20)
    print(class_details)