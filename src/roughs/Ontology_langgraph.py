#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OWL-Exclusive RAG System using LangGraph
==========================================

This script demonstrates how to:
  1. Load an OWL ontology file using OWLready2.
  2. Extract each class’s details (name, parent(s), comment) and format them as text.
  3. Embed the texts and index them in an in-memory vector store.
  4. Build a simple Retrieval-Augmented Generation (RAG) pipeline using LangGraph,
     where a retrieval node searches the index and a generation node synthesizes an answer.
"""

import numpy as np
from owlready2 import get_ontology
import os


# ---------------------------
# Placeholder Embedding Function
# ---------------------------
def embed_text(text):
    """
    Replace this function with your real embedding model.
    For demonstration, we return a random 768-dimensional vector.
    """
    np.random.seed(abs(hash(text)) % (10 ** 8))  # Seed based on text for consistency
    return np.random.rand(768).tolist()


# ---------------------------
# Simple In-Memory Vector Store
# ---------------------------
class InMemoryVectorStore:
    def __init__(self):
        self.documents = {}  # Maps doc_id to content
        self.embeddings = {}  # Maps doc_id to embedding (as a NumPy array)

    def add_document(self, doc_id, content, embedding):
        self.documents[doc_id] = content
        self.embeddings[doc_id] = np.array(embedding)

    def similarity_search(self, query, top_k=3):
        query_embedding = np.array(embed_text(query))
        scores = {}
        for doc_id, emb in self.embeddings.items():
            # Compute cosine similarity
            denom = (np.linalg.norm(query_embedding) * np.linalg.norm(emb)) + 1e-10
            score = np.dot(query_embedding, emb) / denom
            scores[doc_id] = score
        # Sort doc_ids by similarity score (descending)
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        results = []
        for doc_id, score in sorted_docs:
            results.append({
                "id": doc_id,
                "content": self.documents[doc_id],
                "score": score
            })
        return results


# ---------------------------
# Load and Parse the OWL Ontology
# ---------------------------
def load_ontology(owl_file_path):
    """
    Load the ontology using OWLready2 and extract class information.
    Each class’s info includes its name, parent classes, and an optional comment.
    """
    ontology = get_ontology(owl_file_path).load()
    documents = []
    for cls in ontology.classes():
        class_info = f"Class: {cls.name}\n"
        if cls.is_a:
            # Gather parent class names (if available)
            parents = [parent.name for parent in cls.is_a if hasattr(parent, "name")]
            if parents:
                class_info += f"Parents: {', '.join(parents)}\n"
        if cls.comment:
            # Use the first comment (if exists)
            class_info += f"Comment: {cls.comment[0]}\n"
        documents.append({"id": cls.name, "content": class_info})
    return documents


# ---------------------------
# LangGraph Pipeline Setup
# ---------------------------
# We assume that LangGraph is installed and available.
# Replace these imports with your actual LangGraph package if necessary.
from langgraph.graph import START, StateGraph


# Define our application state as a simple dictionary.
class State(dict):
    """
    State for the LangGraph pipeline.
    Expected keys:
      - "query": user query (str)
      - "retrieved": list of retrieved document dicts
      - "answer": final answer (str)
    """
    pass


def retrieve_ontology_info(state: State):
    """
    Retrieve step: perform similarity search on the vector store using the query.
    """
    query = state["query"]
    results = vector_store.similarity_search(query)
    state["retrieved"] = results
    return state


import dotenv
dotenv.load_dotenv()
import openai
from openai import OpenAI
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

# ---------------------------
# Placeholder Embedding Function
# ---------------------------
def embed_text(text):
    """
    Replace this function with your real embedding model.
    For demonstration, we return a random 768-dimensional vector.
    """
    np.random.seed(abs(hash(text)) % (10 ** 8))  # Seed based on text for consistency
    return np.random.rand(768).tolist()


# ---------------------------
# Simple In-Memory Vector Store
# ---------------------------
class InMemoryVectorStore:
    def __init__(self):
        self.documents = {}  # Maps doc_id to content
        self.embeddings = {}  # Maps doc_id to embedding (as a NumPy array)

    def add_document(self, doc_id, content, embedding):
        self.documents[doc_id] = content
        self.embeddings[doc_id] = np.array(embedding)

    def similarity_search(self, query, top_k=3):
        query_embedding = np.array(embed_text(query))
        scores = {}
        for doc_id, emb in self.embeddings.items():
            # Compute cosine similarity
            denom = (np.linalg.norm(query_embedding) * np.linalg.norm(emb)) + 1e-10
            score = np.dot(query_embedding, emb) / denom
            scores[doc_id] = score
        # Sort doc_ids by similarity score (descending)
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        results = []
        for doc_id, score in sorted_docs:
            results.append({
                "id": doc_id,
                "content": self.documents[doc_id],
                "score": score
            })
        return results


# ---------------------------
# Load and Parse the OWL Ontology
# ---------------------------
def load_ontology(owl_file_path):
    """
    Load the ontology using OWLready2 and extract class information.
    Each class’s info includes its name, parent classes, and an optional comment.
    """
    ontology = get_ontology(owl_file_path).load()
    documents = []
    for cls in ontology.classes():
        class_info = f"Class: {cls.name}\n"
        if cls.is_a:
            # Gather parent class names (if available)
            parents = [parent.name for parent in cls.is_a if hasattr(parent, "name")]
            if parents:
                class_info += f"Parents: {', '.join(parents)}\n"
        if cls.comment:
            # Use the first comment (if exists)
            class_info += f"Comment: {cls.comment[0]}\n"
        documents.append({"id": cls.name, "content": class_info})
    return documents


# ---------------------------
# LangGraph Pipeline Setup
# ---------------------------
# Make sure LangGraph is installed.
from langgraph.graph import START, StateGraph


# Define our application state as a simple dictionary.
# Expected keys: "query", "retrieved", "answer"
class State(dict):
    pass


def initialize_state(state: State):
    """
    Initialization node: ensure the state contains all expected keys.
    This node returns a non-empty update, satisfying LangGraph's requirement.
    """
    updated_state = {
        "query": state.get("query", ""),
        "retrieved": state.get("retrieved", []),
        "answer": state.get("answer", "")
    }
    return updated_state


def retrieve_ontology_info(state: State):
    """
    Retrieval step: perform similarity search on the vector store using the query.
    """
    query = state["query"]
    results = vector_store.similarity_search(query)
    state["retrieved"] = results
    return {"retrieved": results}  # Return update for the 'retrieved' key


def generate_answer(state: State):
    """
    Generation step: combine retrieved document contents and simulate an LLM prompt.
    Replace the simulated LLM call with your actual model invocation.
    """
    context = "\n\n".join([doc["content"] for doc in state["retrieved"]])
    prompt = f"Given the following OWL ontology information:\n{context}\nAnswer the query: {state['query']}\n"
    # Simulate LLM invocation (replace with actual call)
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user",
             "content": prompt}
        ],
    )
    ans = resp.choices[0].message.content
    answer = f"Simulated answer based on retrieved ontology info for query: {state['query']} is answered: {ans}"
    state["answer"] = answer
    return {"answer": answer}


# Build the LangGraph state graph.
graph = (
    StateGraph(State)
    .add_sequence([initialize_state, retrieve_ontology_info, generate_answer])
    .add_edge(START, "initialize_state")
    .compile()
)

# ---------------------------
# Main Execution
# ---------------------------
if __name__ == "__main__":
    # Path to your OWL file (update this path accordingly)
    path = os.path.join(os.path.dirname(__file__), "..", "resources", "SOMA.owl")
    owl_file_path = path  # e.g., "ontologies/my_ontology.owl"

    # Load ontology and extract class documents
    documents = load_ontology(owl_file_path)

    # Initialize the vector store and add each document with its embedding
    vector_store = InMemoryVectorStore()
    for doc in documents:
        embedding = embed_text(doc["content"])
        vector_store.add_document(doc["id"], doc["content"], embedding)

    # Define a sample user query
    sample_query = "Which class is related to keyword - size of the object"
    state = {"query": sample_query}

    # Execute the LangGraph pipeline
    result = graph.invoke(state)
    print("Final Answer:")
    print(result["answer"])