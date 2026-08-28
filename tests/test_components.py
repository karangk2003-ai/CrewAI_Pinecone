import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.pdf_processor import extract_text_from_pdf
from rag.text_chunker import chunk_text
from rag.embeddings import generate_embeddings
from pypdf import PdfWriter

class TestComponents(unittest.TestCase):
    def setUp(self):
        # Create a dummy PDF for testing
        self.test_pdf = 'test_dummy.pdf'
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with open(self.test_pdf, 'wb') as f:
            writer.write(f)
            
    def tearDown(self):
        if os.path.exists(self.test_pdf):
            os.remove(self.test_pdf)

    def test_pdf_validation(self):
        # Test non-existent file
        with self.assertRaises(FileNotFoundError):
            extract_text_from_pdf('non_existent.pdf')
            
        # Test invalid extension
        with self.assertRaises(ValueError):
            extract_text_from_pdf('test.txt')

    def test_text_chunking(self):
        dummy_pages = [
            {'page': 1, 'text': 'This is a test document. ' * 100} # 2500 chars
        ]
        chunks = chunk_text(dummy_pages, 'dummy.pdf')
        self.assertTrue(len(chunks) > 1)
        self.assertIn('chunk_id', chunks[0])
        self.assertIn('text', chunks[0])
        self.assertIn('page', chunks[0])

    def test_embeddings(self):
        text = "Hello world"
        embedding = generate_embeddings(text)
        self.assertEqual(len(embedding), 384)

if __name__ == '__main__':
    unittest.main()
