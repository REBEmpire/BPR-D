#!/usr/bin/env python3
"""
Hybrid GraphRAG Injector Prototype
Author: Jules
Date: 2026-02-19
Description: A simple hybrid retriever combining Vector Search (mocked) and Graph Traversal.
"""

import networkx as nx
import random
from typing import List, Dict, Any

# Mock numpy if not available
try:
    import numpy as np
except ImportError:
    class MockNumpy:
        def random(self):
            class Rand:
                def rand(self, n):
                    return [random.random() for _ in range(n)]
            return Rand()
    np = MockNumpy()

class HybridRetriever:
    """
    A simple hybrid retriever combining Vector Search (mocked) and Graph Traversal.
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        self.vector_store = {}  # Mock vector store: {doc_id: embedding}
        self.doc_content = {}   # {doc_id: text}

    def add_document(self, doc_id: str, content: str, entities: List[str]):
        """Ingests a document: updates vector store AND graph."""
        # 1. Vector Store Update (Mock)
        try:
            embedding = np.random.rand(128) # Mock embedding
        except:
             embedding = [0.1] * 128
        self.vector_store[doc_id] = embedding
        self.doc_content[doc_id] = content

        # 2. Graph Update (Dynamic)
        self.graph.add_node(doc_id, type='document', content=content[:50])
        for entity in entities:
            self.graph.add_node(entity, type='entity')
            self.graph.add_edge(doc_id, entity, relation='mentions')
            # Connect entities if they appear in same doc (simple co-occurrence)
            for other_entity in entities:
                if entity != other_entity:
                    self.graph.add_edge(entity, other_entity, relation='co-occurs')

        print(f"Ingested {doc_id} with entities {entities}. Graph size: {self.graph.number_of_nodes()} nodes.")

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """Hybrid retrieval: Vector sim + Graph neighborhood."""
        # 1. Vector Search (Mock - just return random docs for demo)
        # In real impl, query_embedding = embed(query)
        # relevant_docs = vector_search(query_embedding)
        relevant_docs = list(self.doc_content.keys())[:top_k]

        # 2. Graph Expansion
        expanded_context = set(relevant_docs)
        for doc_id in relevant_docs:
            if doc_id in self.graph:
                # Get neighbors (entities)
                neighbors = list(self.graph.neighbors(doc_id))
                for neighbor in neighbors:
                    # Get nodes connected to these entities (2-hop)
                    # predecessors of an entity could be documents OR other entities
                    potential_docs = list(self.graph.predecessors(neighbor))
                    for potential in potential_docs:
                        # Only add if it's a document and not the original one
                        if potential in self.doc_content and potential != doc_id:
                            expanded_context.add(potential)

        results = []
        for doc_id in list(expanded_context)[:top_k*2]: # Return expanded set
             content = self.doc_content.get(doc_id)
             if content:
                 results.append(content)

        return results

if __name__ == "__main__":
    print("Initializing Hybrid Retriever...")
    retriever = HybridRetriever()
    retriever.add_document("doc1", "Elon Musk discusses AI safety.", ["Elon Musk", "AI Safety"])
    retriever.add_document("doc2", "OpenAI releases new model.", ["OpenAI", "AI Model"])
    retriever.add_document("doc3", "Elon Musk sues OpenAI.", ["Elon Musk", "OpenAI"])

    # Query for "Elon Musk" should retrieve doc1 AND doc3 (direct),
    # and potentially doc2 (via OpenAI connection in graph)
    print("\nRetrieving for 'Elon Musk':")
    results = retriever.retrieve("Elon Musk")
    print(f"Retrieved {len(results)} documents.")
    for res in results:
        print(f"- {res}")
