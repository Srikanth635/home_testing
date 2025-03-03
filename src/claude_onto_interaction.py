import rdflib
from rdflib import RDF, RDFS, OWL
import nltk
import json
nltk.download('punkt_tab')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple, Optional
import operator
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
import dotenv
dotenv.load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


class OWLOntologyQuerySystem:
    def __init__(self, ontology_path: str):
        """
        Initialize the OWL ontology query system with the path to the OWL file.

        Args:
            ontology_path: Path to the OWL ontology file
        """
        # Download required NLTK resources
        try:
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('stopwords')
            nltk.download('wordnet')
            nltk.download('punkt')

        # Initialize NLP components
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

        # Load the ontology
        self.g = rdflib.Graph()
        self.g.parse(ontology_path)
        print(f"Loaded ontology with {len(self.g)} triples")

        # Extract all classes and their comments
        self.classes = self._extract_classes_with_comments()
        print(f"Extracted {len(self.classes)} classes with comments")

        # Create a TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer()
        self._build_vectorizer()

    def _extract_classes_with_comments(self) -> Dict[str, Dict]:
        """
        Extract all classes from the ontology along with their comments and parent-child relationships.

        Returns:
            A dictionary mapping class URIs to their metadata including comments and relationships
        """
        classes = {}

        # Get all classes
        for class_uri in self.g.subjects(RDF.type, OWL.Class):
            class_info = {
                'uri': str(class_uri),
                'label': self._get_label(class_uri),
                'comment': self._get_comment(class_uri),
                'parents': [],
                'children': []
            }
            classes[str(class_uri)] = class_info

        # Build parent-child relationships
        for class_uri, parent_uri in self.g.subject_objects(RDFS.subClassOf):
            if str(class_uri) in classes and str(parent_uri) in classes:
                classes[str(class_uri)]['parents'].append(str(parent_uri))
                classes[str(parent_uri)]['children'].append(str(class_uri))

        return classes

    def _get_label(self, uri) -> str:
        """Get the rdfs:label for a URI, or the local name if no label exists."""
        for label in self.g.objects(uri, RDFS.label):
            return str(label)
        # If no label, use the local name (after the # or the last /)
        local_name = str(uri).split('#')[-1] if '#' in str(uri) else str(uri).split('/')[-1]
        return local_name

    def _get_comment(self, uri) -> str:
        """Get the rdfs:comment for a URI, or an empty string if none exists."""
        for comment in self.g.objects(uri, RDFS.comment):
            return str(comment)
        return ""

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text by tokenizing, removing stopwords, and lemmatizing.

        Args:
            text: The input text to preprocess

        Returns:
            Preprocessed text
        """
        tokens = word_tokenize(text.lower())
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if
                  token.isalnum() and token not in self.stop_words]
        return " ".join(tokens)

    def _build_vectorizer(self):
        """Build the TF-IDF vectorizer using class comments."""
        processed_comments = []
        for class_info in self.classes.values():
            if class_info['comment']:
                processed_comments.append(self._preprocess_text(class_info['comment']))
            else:
                processed_comments.append(self._preprocess_text(class_info['label']))

        self.comment_vectors = self.vectorizer.fit_transform(processed_comments)
        self.class_uris = list(self.classes.keys())

    def match_query_to_classes(self, query: str, top_n: int = 5) -> List[Dict]:
        """
        Match a natural language query to the most relevant classes in the ontology.

        Args:
            query: Natural language query
            top_n: Number of top matches to return

        Returns:
            List of dictionaries containing matched classes and their relevance scores
        """
        # Preprocess the query
        processed_query = self._preprocess_text(query)

        # Vectorize the query
        query_vector = self.vectorizer.transform([processed_query])

        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.comment_vectors).flatten()

        # Get the top N matches
        top_indices = np.argsort(similarities)[-top_n:][::-1]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include if there's some similarity
                class_uri = self.class_uris[idx]
                class_info = self.classes[class_uri]
                results.append({
                    'uri': class_uri,
                    'label': class_info['label'],
                    'comment': class_info['comment'],
                    'score': float(similarities[idx])
                })

        return results

    def get_class_hierarchy(self, class_uri: str, direction: str = 'children', depth: int = 2, visited=None) -> Dict:
        if visited is None:
            visited = set()
        if class_uri in visited:
            return {"error": f"Cycle detected at {class_uri}"}

        visited.add(class_uri)
        class_info = self.classes.get(class_uri, None)
        if not class_info:
            return {"error": f"Class {class_uri} not found"}

        result = {
            'uri': class_uri,
            'label': class_info['label'],
            'comment': class_info['comment']
        }

        if depth > 0:
            relations = []
            related_uris = class_info['children'] if direction == 'children' else class_info['parents']
            for related_uri in related_uris:
                relations.append(self.get_class_hierarchy(related_uri, direction, depth - 1, visited))

            if relations:
                result[direction] = relations

        return result

    def get_class_hierarchy_old(self, class_uri: str, direction: str = 'children', depth: int = 2) -> Dict:
        """
        Get the hierarchy (children or parents) for a specific class.

        Args:
            class_uri: URI of the class
            direction: 'children' or 'parents'
            depth: How many levels to traverse

        Returns:
            Dictionary representing the class hierarchy
        """
        if class_uri not in self.classes:
            return {"error": f"Class {class_uri} not found"}

        class_info = self.classes[class_uri]
        result = {
            'uri': class_uri,
            'label': class_info['label'],
            'comment': class_info['comment']
        }

        if depth > 0:
            relations = []
            related_uris = class_info['children'] if direction == 'children' else class_info['parents']

            for related_uri in related_uris:
                relations.append(self.get_class_hierarchy(related_uri, direction, depth - 1))

            if relations:
                result[direction] = relations

        return result

    def analyze_class_specificity(self, query: str, initial_matches: List[Dict]) -> List[Dict]:
        """
        Analyze the specificity of matched classes by looking at their hierarchies.
        Refines matches by checking if children classes are more specific matches.

        Args:
            query: The original query string
            initial_matches: Initial matched classes

        Returns:
            Refined list of matches with potentially more specific classes
        """
        processed_query = self._preprocess_text(query)
        query_vector = self.vectorizer.transform([processed_query])

        refined_matches = []

        for match in initial_matches:
            class_uri = match['uri']
            class_info = self.classes[class_uri]

            # Check if any children are more specific matches
            best_match = match

            for child_uri in class_info['children']:
                child_info = self.classes[child_uri]
                child_comment = child_info['comment'] if child_info['comment'] else child_info['label']
                processed_child_comment = self._preprocess_text(child_comment)

                child_vector = self.vectorizer.transform([processed_child_comment])
                child_similarity = cosine_similarity(query_vector, child_vector).flatten()[0]

                if child_similarity > best_match['score']:
                    best_match = {
                        'uri': child_uri,
                        'label': child_info['label'],
                        'comment': child_info['comment'],
                        'score': float(child_similarity),
                        'parent': {
                            'uri': class_uri,
                            'label': class_info['label']
                        }
                    }

            refined_matches.append(best_match)

        # Sort by score
        refined_matches.sort(key=operator.itemgetter('score'), reverse=True)
        return refined_matches

    def describe_class(self, class_uri: str) -> Dict:
        """
        Get a detailed description of a class including its comments, parents and children.

        Args:
            class_uri: URI of the class

        Returns:
            Dictionary with class details
        """
        if class_uri not in self.classes:
            return {"error": f"Class {class_uri} not found"}

        class_info = self.classes[class_uri]

        parent_classes = []
        for parent_uri in class_info['parents']:
            parent_info = self.classes[parent_uri]
            parent_classes.append({
                'uri': parent_uri,
                'label': parent_info['label']
            })

        child_classes = []
        for child_uri in class_info['children']:
            child_info = self.classes[child_uri]
            child_classes.append({
                'uri': child_uri,
                'label': child_info['label']
            })

        return {
            'uri': class_uri,
            'label': class_info['label'],
            'comment': class_info['comment'],
            'parents': parent_classes,
            'children': child_classes
        }

# Create LangChain tools and agent for the RAG system
def create_ontology_rag_system(ontology_path: str, model_name: str = "gpt-4o"):
    """
    Create a RAG system using LangChain to query the ontology.

    Args:
        ontology_path: Path to the OWL ontology file
        model_name: Name of the LLM model to use

    Returns:
        AgentExecutor that can be used to query the ontology
    """
    # Initialize the ontology system
    ontology_system = OWLOntologyQuerySystem(ontology_path)

    # eval(input_str.split("|")[1])
    # Create tools
    tools = [
        Tool(
            name="SearchOntology",
            func=lambda query: str(ontology_system.match_query_to_classes(query)),
            description="Searches the ontology for classes matching a natural language query. Returns a list of potential matching classes with their scores."
        ),
        Tool(
            name="AnalyzeClassSpecificity",
            func=lambda input_str: str(ontology_system.analyze_class_specificity(
                input_str.split("|")[0],
                [ontology_system.classes[uri] for uri in input_str.split("|")[1].split(",") if uri in ontology_system.classes]
            )),
            description="Analyzes if children classes are more specific matches to the query. Input format: 'query|list_of_matches'"
        ),
        Tool(
            name="GetClassHierarchy",
            func=lambda input_str: str(ontology_system.get_class_hierarchy(
                input_str.split("|")[0],
                input_str.split("|")[1],
                int(json.loads(input_str.split("|")[2]))
            )),
            description="Gets the hierarchy (children or parents) for a specific class. Input format: 'class_uri|direction|depth' where direction is 'children' or 'parents'"
        ),
        Tool(
            name="DescribeClass",
            func=lambda class_uri: str(ontology_system.describe_class(class_uri)),
            description="Gets detailed information about a specific class including its description, parents, and children"
        )
    ]

    # Create the LLM
    llm = ChatOpenAI(openai_api_key= OPENAI_API_KEY,model_name=model_name,temperature=0.1)

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
            You are an ontology expert assistant. You help users find relevant classes in an OWL ontology by understanding their natural language queries.
            You have access to tools that can search the ontology and analyze the class hierarchy.

            When a user asks a question, follow these steps:
            1. Use SearchOntology to find initial matching classes
            2. Use AnalyzeClassSpecificity to check if children classes are more specific matches
            3. Use GetClassHierarchy or DescribeClass to get more information if needed
            4. Present the most relevant classes to the user in a clear format
            """),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    # Create the agent
    agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"])
            }
            | prompt
            | llm.bind_functions(tools)
            | OpenAIFunctionsAgentOutputParser()
    )

    # Create the agent executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return agent_executor, ontology_system

# Example usage
def main():

    ontology_path = os.path.join(os.path.dirname(__file__), "..", "resources", "SOMA.owl")
    print(f"ontology path: {ontology_path}")

    # Create the agent
    agent, ontology_system = create_ontology_rag_system(ontology_path)

    # Example query
    result = agent.invoke({"input": "What classes are related to object sharpness?"})
    print(result["output"])

    # Or use the ontology system directly
    matches = ontology_system.match_query_to_classes("What classes are related to object sharpness?")
    refined_matches = ontology_system.analyze_class_specificity("What classes are related to object sharpness?", matches)

    for match in refined_matches[:3]:
        print(f"Class: {match['label']}")
        print(f"Description: {match['comment']}")
        print(f"Relevance: {match['score']:.2f}")
        print("-" * 50)


if __name__ == "__main__":
    main()