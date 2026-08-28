import os
import sys

# Allow overriding from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.pinecone_manager import PineconeManager
from rag.embeddings import generate_embeddings

class Retriever:
    def __init__(self):
        try:
            self.pm = PineconeManager()
        except Exception as e:
            print(f"Warning: Could not initialize PineconeManager: {e}")
            self.pm = None

    def search(self, query, top_k=5):
        """
        Searches Pinecone for the top_k most relevant chunks for a given query.
        Returns a list of dictionaries containing metadata.
        """
        if not self.pm:
            raise Exception("PineconeManager is not initialized.")
            
        query_embedding = generate_embeddings(query)
        
        results = self.pm.index.query(
            namespace=self.pm.namespace,
            vector=query_embedding,
            top_k=top_k,
            include_values=False,
            include_metadata=True
        )
        
        retrieved_chunks = []
        for match in results.matches:
            if match.metadata:
                retrieved_chunks.append(match.metadata)
                
        return retrieved_chunks
