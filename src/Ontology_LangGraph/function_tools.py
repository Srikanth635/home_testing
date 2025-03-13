from typing import List, Dict, Any
from ontology_parser import *

class OntologyTools:
    def __init__(self, ontology_file_path: str):
        self.ontology = load_ontology(ontology_file_path)
        self.class_details = extract_all_class_details(self.ontology)

    def find_relevant_classes(self, query: str) -> List[Dict[str, Any]]:
        """Finds classes relevant to the user query."""
        relevant_classes = []
        query_lower = query.lower()
        for class_detail in self.class_details:
            if query_lower in class_detail["name"].lower():
                relevant_classes.append(class_detail)
            else:
                # for annotation_value in class_detail["annotations"].values():
                #     if query_lower in str(annotation_value).lower():
                #         relevant_classes.append(class_detail)
                for comment_value in class_detail["comment"]:
                    if query_lower in str(comment_value).lower():
                        relevant_classes.append(class_detail)
        return relevant_classes