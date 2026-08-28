from crewai import Agent
from agents.research_agent import get_llm

def get_analysis_agent():
    return Agent(
        role='Academic Answer Analyst',
        goal='Analyze the research information and prepare an academic answer to the user\'s question.',
        backstory=(
            "You are an academic analyst. You take the extracted research facts and "
            "synthesize them into a clear, cohesive, and easy-to-understand answer. "
            "You use simple academic language. You MUST base your answer entirely on "
            "the provided research and never invent or hallucinate information."
        ),
        verbose=True,
        allow_delegation=False,
        llm=get_llm()
    )
