import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.retriever import Retriever
from crew.study_crew import StudyCrew

class QAService:
    def __init__(self):
        try:
            self.retriever = Retriever()
        except Exception as e:
            print(f"Warning: QA service could not initialize retriever: {e}")
            self.retriever = None

    def ask_question(self, question, top_k=3):
        if not self.retriever:
            raise Exception("Retriever (Pinecone) is not configured correctly.")
            
        # 1. Retrieve Context
        try:
            retrieved_context = self.retriever.search(question, top_k=top_k)
        except Exception as e:
            raise Exception(f"Error during retrieval: {e}")

        # 2. Run CrewAI Workflow
        crew = StudyCrew(question, retrieved_context)
        try:
            result = crew.run()
        except Exception as e:
            raise Exception(f"Error during CrewAI execution: {e}")

        # Extract unique sources
        sources = []
        seen = set()
        for chunk in retrieved_context:
            doc = chunk.get('document', 'Unknown')
            page = chunk.get('page', 0)
            identifier = f"{doc} - Page {int(page)}"
            if identifier not in seen:
                seen.add(identifier)
                sources.append(identifier)
                
        # Only attach sources if there's an actual answer from context
        if not retrieved_context:
            sources = []

        result['sources'] = sources
        return result
