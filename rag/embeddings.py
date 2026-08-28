from langchain_community.embeddings import OllamaEmbeddings
import sys
import os

# Allow overriding from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# Initialize globally to avoid recreating it
_embeddings = None

def get_embedding_model():
    global _embeddings
    if _embeddings is None:
        _embeddings = OllamaEmbeddings(
            model="nomic-embed-text", 
            base_url=Config.OLLAMA_BASE_URL
        )
    return _embeddings

def generate_embeddings(text):
    """
    Generates embedding for a single string.
    Returns a list of floats.
    """
    model = get_embedding_model()
    return model.embed_query(text)

def generate_embeddings_batch(texts):
    """
    Generates embeddings for a batch of strings.
    Returns a list of lists of floats.
    """
    model = get_embedding_model()
    return model.embed_documents(texts)
