import os
import sys

# Ensure correct path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.pdf_processor import extract_text_from_pdf
from rag.text_chunker import chunk_text
from rag.pinecone_manager import PineconeManager
from services.qa_service import QAService

def run_e2e():
    print("--- STARTING E2E PIPELINE VERIFICATION ---")
    
    # 1. PDF
    pdf_path = "test_dummy.pdf"
    if not os.path.exists(pdf_path):
        print("Creating dummy PDF for E2E...")
        from pypdf import PdfWriter
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with open(pdf_path, 'wb') as f:
            writer.write(f)

    try:
        print("1. Extracting text from PDF...")
        pages_data = extract_text_from_pdf(pdf_path)
        
        # Manually inject some text since blank page has no text
        pages_data = [{'page': 1, 'text': 'Machine learning is a field of study that gives computers the ability to learn without being explicitly programmed.'}]
        
        print("2. Chunking text...")
        chunks_data = chunk_text(pages_data, "test_dummy.pdf")
        
        print("3. Connecting to Pinecone...")
        pm = PineconeManager()
        
        print("4. Upserting Embeddings to Pinecone...")
        pm.upsert_chunks(chunks_data)
        
        print("5. Initializing QA Service (Retrieval + CrewAI Agents)...")
        qa = QAService()
        
        print("6. Asking Question: 'What is machine learning?'")
        result = qa.ask_question("What is machine learning?")
        
        print("\n--- FINAL VERIFIED ANSWER ---")
        print(result.get("final_answer"))
        print("\nVerification Status:", result.get("verification_status"))
        print("Sources:", result.get("sources"))
        
    except Exception as e:
        print("\n[PIPELINE STOPPED] An error occurred:", str(e))
        print("Note: If this is a ValueError regarding PINECONE_API_KEY, you must provide your real API key in the .env file.")

if __name__ == '__main__':
    run_e2e()
