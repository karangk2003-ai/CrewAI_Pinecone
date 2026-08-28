import os
import sys
from pinecone import Pinecone, ServerlessSpec

# Allow overriding from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from rag.embeddings import generate_embeddings_batch

class PineconeManager:
    def __init__(self):
        if not Config.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY is not set.")
        self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        self.index_name = Config.PINECONE_INDEX_NAME
        self.namespace = Config.PINECONE_NAMESPACE
        self._ensure_index_exists()
        self.index = self.pc.Index(self.index_name)

    def _ensure_index_exists(self):
        existing_indexes = [index_info["name"] for index_info in self.pc.list_indexes()]
        if Config.PINECONE_INDEX_NAME not in self.pc.list_indexes().names():
            print(f"Creating Pinecone index '{Config.PINECONE_INDEX_NAME}'...")
            self.pc.create_index(
                name=Config.PINECONE_INDEX_NAME,
                dimension=768,  # nomic-embed-text dimension
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )

    def upsert_chunks(self, chunks_data):
        """
        Takes a list of chunks, generates embeddings for them, and upserts them to Pinecone.
        """
        if not chunks_data:
            return

        texts = [chunk['text'] for chunk in chunks_data]
        embeddings = generate_embeddings_batch(texts)

        vectors = []
        for i, chunk in enumerate(chunks_data):
            vector = {
                "id": chunk["chunk_id"],
                "values": embeddings[i],
                "metadata": {
                    "text": chunk["text"],
                    "document": chunk["document"],
                    "page": chunk["page"],
                    "chunk_id": chunk["chunk_id"]
                }
            }
            vectors.append(vector)

        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch, namespace=self.namespace)
