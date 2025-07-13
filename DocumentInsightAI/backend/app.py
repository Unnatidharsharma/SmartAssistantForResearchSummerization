from flask import Flask, request, jsonify, session, send_from_directory, render_template_string
from flask_cors import CORS
import os
import json
import uuid
import tempfile
from werkzeug.utils import secure_filename
from document_processor import DocumentProcessor
from gemini_ai_assistant import GeminiAIAssistant

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.secret_key = os.urandom(24)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize processors
doc_processor = DocumentProcessor()
ai_assistant = GeminiAIAssistant()

# In-memory storage for demo (in production, use Redis or database)
document_sessions = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/demo')
def demo():
    """Serve the demo page"""
    return send_from_directory('../frontend', 'demo.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Backend is running"})

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """Upload and process document"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create a temporary file-like object
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        file.save(temp_file.name)
        temp_file.close()  # <-- Close the file before using or deleting it
        
        # Create a file-like object that mimics Streamlit's uploaded file
        class FileWrapper:
            def __init__(self, path, filename):
                self.name = filename
                self.type = file.content_type
                self._path = path
            def read(self):
                with open(self._path, "rb") as f:
                    return f.read()
        
        file_wrapper = FileWrapper(temp_file.name, file.filename)
        
        # Extract text
        text_content = doc_processor.extract_text(file_wrapper)
        
        # Generate summary
        summary = ai_assistant.generate_summary(text_content)
        
        # Store document session
        document_sessions[session_id] = {
            'filename': file.filename,
            'content': text_content,
            'summary': summary,
            'conversation_history': [],
            'challenge_questions': None,
            'user_answers': [],
            'evaluations': []
        }
        
        # Clean up temp file
        os.unlink(temp_file.name)
        
        return jsonify({
            "session_id": session_id,
            "filename": file.filename,
            "summary": summary,
            "message": "Document processed successfully"
        })
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Answer questions about the document"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        question = data.get('question')
        
        if not session_id or session_id not in document_sessions:
            return jsonify({"error": "Invalid session ID"}), 400
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        doc_session = document_sessions[session_id]
        
        # Get answer
        answer, justification = ai_assistant.answer_question(
            question,
            doc_session['content'],
            doc_session['conversation_history']
        )
        
        # Add to conversation history
        doc_session['conversation_history'].append((question, answer, justification))
        
        return jsonify({
            "question": question,
            "answer": answer,
            "justification": justification
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to answer question: {str(e)}"}), 500

@app.route('/api/generate-questions', methods=['POST'])
def generate_questions():
    """Generate challenge questions"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id or session_id not in document_sessions:
            return jsonify({"error": "Invalid session ID"}), 400
        
        doc_session = document_sessions[session_id]
        
        # Generate questions
        questions = ai_assistant.generate_challenge_questions(doc_session['content'])
        
        # Store questions
        doc_session['challenge_questions'] = questions
        doc_session['user_answers'] = [""] * len(questions)
        doc_session['evaluations'] = [None] * len(questions)
        
        return jsonify({
            "questions": questions
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to generate questions: {str(e)}"}), 500

@app.route('/api/evaluate-answer', methods=['POST'])
def evaluate_answer():
    """Evaluate user's answer to challenge question"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        question_index = data.get('question_index')
        user_answer = data.get('answer')
        
        if not session_id or session_id not in document_sessions:
            return jsonify({"error": "Invalid session ID"}), 400
        
        doc_session = document_sessions[session_id]
        
        if not doc_session['challenge_questions'] or question_index >= len(doc_session['challenge_questions']):
            return jsonify({"error": "Invalid question index"}), 400
        
        question = doc_session['challenge_questions'][question_index]
        
        # Evaluate answer
        evaluation = ai_assistant.evaluate_answer(
            question,
            user_answer,
            doc_session['content']
        )
        
        # Store evaluation
        doc_session['evaluations'][question_index] = evaluation
        doc_session['user_answers'][question_index] = user_answer
        
        return jsonify({
            "evaluation": evaluation,
            "question_index": question_index
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to evaluate answer: {str(e)}"}), 500

@app.route('/api/conversation-history', methods=['GET'])
def get_conversation_history():
    """Get conversation history for a session"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id or session_id not in document_sessions:
            return jsonify({"error": "Invalid session ID"}), 400
        
        doc_session = document_sessions[session_id]
        
        return jsonify({
            "conversation_history": doc_session['conversation_history'],
            "challenge_questions": doc_session['challenge_questions'],
            "user_answers": doc_session['user_answers'],
            "evaluations": doc_session['evaluations']
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get conversation history: {str(e)}"}), 500

@app.route('/api/reset-session', methods=['POST'])
def reset_session():
    """Reset challenge questions for a session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id or session_id not in document_sessions:
            return jsonify({"error": "Invalid session ID"}), 400
        
        doc_session = document_sessions[session_id]
        doc_session['challenge_questions'] = None
        doc_session['user_answers'] = []
        doc_session['evaluations'] = []
        
        return jsonify({"message": "Session reset successfully"})
        
    except Exception as e:
        return jsonify({"error": f"Failed to reset session: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)