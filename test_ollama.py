import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import Config
from crewai import Agent, Task, Crew
import requests

def test_ollama_directly():
    print("Testing Ollama direct connection...")
    try:
        response = requests.post(
            f"{Config.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": Config.OLLAMA_MODEL,
                "prompt": "What is the capital of France?",
                "stream": False
            }
        )
        if response.status_code == 200:
            print("Direct Ollama connection successful!")
            print("Response:", response.json().get('response'))
            return True
        else:
            print(f"Failed. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        return False

def test_crewai_ollama():
    print("\nTesting CrewAI with Ollama...")
    try:
        from agents.research_agent import get_llm
        llm = get_llm()
        
        test_agent = Agent(
            role='Test Agent',
            goal='Just say hello',
            backstory='A simple test agent',
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
        
        test_task = Task(
            description='Say "Hello, world!"',
            expected_output='A greeting',
            agent=test_agent
        )
        
        crew = Crew(agents=[test_agent], tasks=[test_task])
        result = crew.kickoff()
        print("CrewAI Test Successful. Result:", result)
    except Exception as e:
        print(f"Error testing CrewAI with Ollama: {e}")

if __name__ == "__main__":
    test_ollama_directly()
    test_crewai_ollama()
