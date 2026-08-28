from crewai import Crew, Task, Process
from agents.research_agent import get_research_agent
from agents.analysis_agent import get_analysis_agent
from agents.review_agent import get_review_agent

class StudyCrew:
    def __init__(self, question, retrieved_context):
        self.question = question
        # Format the context for the agents
        if not retrieved_context:
            self.formatted_context = "No relevant context found in the uploaded documents."
        else:
            self.formatted_context = "\n\n".join([
                f"Source: {chunk.get('document', 'Unknown')} - Page: {int(chunk.get('page', 0))}\nContent: {chunk.get('text', '')}"
                for chunk in retrieved_context
            ])

        self.research_agent = get_research_agent()
        self.analysis_agent = get_analysis_agent()
        self.review_agent = get_review_agent()

    def run(self):
        # If no context was retrieved, short-circuit
        if self.formatted_context == "No relevant context found in the uploaded documents.":
            return {
                "final_answer": "I could not find sufficient information in the uploaded study material to answer this question.",
                "verification_status": "PASS",
                "sources": []
            }

        research_task = Task(
            description=(
                f"Question: {self.question}\n\n"
                f"Retrieved Context:\n{self.formatted_context}\n\n"
                "Extract relevant information from the context that helps answer the question. "
                "Include the source document and page number for each extracted fact. "
                "Do not invent information."
            ),
            expected_output="A structured list of facts and examples extracted from the context, including source metadata.",
            agent=self.research_agent
        )

        analysis_task = Task(
            description=(
                f"Based on the extracted research provided by the Research Agent, prepare a clear, academic answer "
                f"to the following question:\n{self.question}\n\n"
                "Ensure the answer is cohesive and strictly relies on the provided facts."
            ),
            expected_output="A well-written, academic answer to the user's question.",
            agent=self.analysis_agent
        )

        review_task = Task(
            description=(
                f"Verify the drafted answer provided by the Analysis Agent against the original retrieved context.\n"
                f"Original Context:\n{self.formatted_context}\n\n"
                f"Question:\n{self.question}\n\n"
                "Check for unsupported claims or hallucinations. If the answer is accurate and supported, "
                "conclude with 'VERIFICATION: PASS'. If there are issues, correct them and conclude with "
                "'VERIFICATION: NEEDS_REVISION'."
            ),
            expected_output="The final verified answer ending with a 'VERIFICATION: PASS' or 'VERIFICATION: NEEDS_REVISION' status.",
            agent=self.review_agent
        )

        crew = Crew(
            agents=[self.research_agent, self.analysis_agent, self.review_agent],
            tasks=[research_task, analysis_task, review_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        
        # Determine verification status
        final_result_text = str(result)
        verification_status = "PASS" if "VERIFICATION: PASS" in final_result_text.upper() else "NEEDS REVISION"
        
        # Clean up the final text a bit if it contains the verification string at the end
        if "VERIFICATION: PASS" in final_result_text.upper():
            # naive cleanup
            final_result_text = final_result_text.replace("VERIFICATION: PASS", "").strip()
        elif "VERIFICATION: NEEDS_REVISION" in final_result_text.upper():
            final_result_text = final_result_text.replace("VERIFICATION: NEEDS_REVISION", "").strip()
            
        return {
            "final_answer": final_result_text,
            "verification_status": verification_status
        }
