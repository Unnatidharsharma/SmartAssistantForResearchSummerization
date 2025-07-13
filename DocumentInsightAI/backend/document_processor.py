import PyPDF2
import io
import re
from typing import List

class DocumentProcessor:
    """Handles document processing and text extraction"""
    
    def extract_text(self, uploaded_file) -> str:
        """Extract text from uploaded PDF or TXT file"""
        try:
            if uploaded_file.type == "application/pdf":
                return self._extract_pdf_text(uploaded_file)
            elif uploaded_file.type == "text/plain":
                return self._extract_txt_text(uploaded_file)
            else:
                raise ValueError(f"Unsupported file type: {uploaded_file.type}")
        except Exception as e:
            raise Exception(f"Failed to extract text from document: {str(e)}")
    
    def _extract_pdf_text(self, pdf_file) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Failed to read PDF: {str(e)}")
        
        if not text.strip():
            raise Exception("No text could be extracted from the PDF")
        
        return text.strip()
    
    def _extract_txt_text(self, txt_file) -> str:
        """Extract text from TXT file"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin1', 'cp1252']
            content = txt_file.read()
            
            for encoding in encodings:
                try:
                    if isinstance(content, bytes):
                        text = content.decode(encoding)
                    else:
                        text = content
                    return text.strip()
                except UnicodeDecodeError:
                    continue
            
            raise Exception("Could not decode text file with any supported encoding")
        except Exception as e:
            raise Exception(f"Failed to read TXT file: {str(e)}")
    
    def chunk_text(self, text: str, chunk_size: int = 2000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for better processing"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to end at a sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 200 characters
                sentence_ends = [m.end() for m in re.finditer(r'[.!?]\s+', text[end-200:end])]
                if sentence_ends:
                    end = start + chunk_size - 200 + sentence_ends[-1]
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for better AI processing"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with processing
        text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', '', text)
        
        # Ensure proper sentence spacing
        text = re.sub(r'\.(?=[A-Z])', '. ', text)
        
        return text.strip()