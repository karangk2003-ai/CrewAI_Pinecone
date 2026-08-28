from pypdf import PdfReader
import os

def extract_text_from_pdf(file_path):
    """
    Extracts text from a PDF file page by page.
    Returns a list of dictionaries: [{'page': 1, 'text': '...'}, ...]
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    if not file_path.lower().endswith('.pdf'):
        raise ValueError(f"File {file_path} is not a PDF")

    pages_data = []
    try:
        reader = PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                text = text.strip()
                if text:
                    pages_data.append({
                        "page": i + 1,
                        "text": text
                    })
    except Exception as e:
        raise Exception(f"Error reading PDF {file_path}: {str(e)}")
        
    return pages_data
