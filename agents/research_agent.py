from crewai import Agent, LLM
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def get_llm():
    return LLM(model=f"ollama/{Config.OLLAMA_MODEL}", base_url=Config.OLLAMA_BASE_URL)

def get_research_agent():
    return Agent(
        role='Study Material Research Specialist',
        goal='Find and organize relevant information from the retrieved document context.',
        backstory=(
            "You are an expert researcher. Your job is to examine retrieved document "
            "snippets and extract the most relevant facts, definitions, and examples "
            "to answer the user's question. You only use the provided context. "
            "You always preserve document and page metadata when extracting facts."
        ),
        verbose=True,
        allow_delegation=False,
        llm=get_llm()
    )
