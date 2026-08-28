from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys

from config import Config
from rag.pdf_processor import extract_text_from_pdf
from rag.text_chunker import chunk_text
from rag.pinecone_manager import PineconeManager
from services.qa_service import QAService

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize global services
qa_service = None
try:
    qa_service = QAService()
except Exception as e:
    print(f"Warning: QAService initialization failed: {e}")

pm = None
try:
    pm = PineconeManager()
except Exception as e:
    print(f"Warning: PineconeManager initialization failed: {e}")

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed.'}), 400

    if not pm:
        return jsonify({'error': 'Pinecone vector database is not configured. Cannot process uploads.'}), 500

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        file.save(filepath)
        
        # 1. Extract text
        pages_data = extract_text_from_pdf(filepath)
        if not pages_data:
            return jsonify({'error': 'No extractable text found in PDF. It might be scanned/image-based.'}), 400
            
        # 2. Chunk text
        chunks_data = chunk_text(pages_data, filename)
        
        # 3. Generate Embeddings & Upsert to Pinecone
        pm.upsert_chunks(chunks_data)
        
        return jsonify({
            'message': 'Document processed successfully.',
            'chunks_created': len(chunks_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'An error occurred while processing the PDF: {str(e)}'}), 500
    finally:
        # Optionally clean up the uploaded file to save space
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    if not data or 'question' not in data:
        return jsonify({'error': 'Question is required.'}), 400
        
    question = data['question']
    if not question.strip():
        return jsonify({'error': 'Question cannot be empty.'}), 400
        
    if not qa_service:
        return jsonify({'error': 'QA Service is not initialized. Check configurations.'}), 500

    try:
        result = qa_service.ask_question(question, top_k=3)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
