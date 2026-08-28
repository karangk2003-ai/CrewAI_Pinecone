from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid
import os

def chunk_text(pages_data, filename):
    """
    Takes a list of pages and splits them into chunks.
    Returns a list of chunks with metadata.
    """
    # Use a reasonable chunk size and overlap
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
    )

    chunks_data = []
    for page_data in pages_data:
        page_num = page_data['page']
        text = page_data['text']
        
        # Split text into chunks
        chunks = text_splitter.split_text(text)
        
        for i, chunk_text in enumerate(chunks):
            chunk_id = f"{os.path.basename(filename)}_p{page_num}_c{i}_{uuid.uuid4().hex[:6]}"
            chunks_data.append({
                "chunk_id": chunk_id,
                "document": os.path.basename(filename),
                "page": page_num,
                "text": chunk_text
            })
            
    return chunks_data
