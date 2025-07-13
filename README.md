# Gemini AI Document Analysis Assistant

A modern web application that uses Google's Gemini AI to analyze documents and provide intelligent Q&A capabilities with logic-based challenges.

## Features

- **Document Upload**: Support for PDF and TXT files
- **Gemini AI Analysis**: Uses Google's Gemini 2.0 Flash for advanced document processing
- **Two Interaction Modes**:
  - **Ask Anything**: Free-form Q&A with document-grounded responses
  - **Challenge Me**: Logic-based questions with AI evaluation
- **Modern UI**: Clean, responsive interface built with HTML, CSS, and JavaScript
- **REST API**: Flask backend with comprehensive endpoints

## Architecture

### Backend (Flask)
- **Flask API**: RESTful endpoints for document processing and AI interactions
- **Document Processing**: PDF and TXT text extraction with chunking
- **Gemini AI Integration**: Advanced language model for analysis, summarization, and evaluation
- **Session Management**: In-memory storage for document sessions

### Frontend (HTML/CSS/JavaScript)
- **Responsive Design**: Modern UI with gradient backgrounds and animations
- **Interactive Elements**: Drag-and-drop file upload, real-time Q&A
- **Dynamic Content**: Live conversation history and challenge evaluations
- **API Integration**: Fetch-based communication with Flask backend

## Setup Instructions

### Prerequisites
- Python 3.11+
- Google Gemini API key (free at https://makersuite.google.com/app/apikey)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd document-analysis-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install flask flask-cors pypdf2 werkzeug google-genai
   ```

3. **Set up Gemini API key**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

4. **Run the backend**
   ```bash
   cd backend
   python app.py
   ```

5. **Open the frontend**
   - Open `frontend/index.html` in your web browser
   - Or serve it through a local HTTP server:
     ```bash
     cd frontend
     python -m http.server 8000
     ```

## API Endpoints

### POST /api/upload
Upload and process a document (PDF/TXT)

**Request**: Multipart form data with file
**Response**: 
```json
{
  "session_id": "uuid",
  "filename": "document.pdf",
  "summary": "Document summary...",
  "message": "Document processed successfully"
}
```

### POST /api/ask
Ask questions about the document

**Request**:
```json
{
  "session_id": "uuid",
  "question": "What are the main findings?"
}
```

**Response**:
```json
{
  "question": "What are the main findings?",
  "answer": "The main findings are...",
  "justification": "This is supported by..."
}
```

### POST /api/generate-questions
Generate challenge questions

**Request**:
```json
{
  "session_id": "uuid"
}
```

**Response**:
```json
{
  "questions": [
    "Question 1...",
    "Question 2...",
    "Question 3..."
  ]
}
```

### POST /api/evaluate-answer
Evaluate user's answer to challenge question

**Request**:
```json
{
  "session_id": "uuid",
  "question_index": 0,
  "answer": "User's answer..."
}
```

**Response**:
```json
{
  "evaluation": {
    "score": 8,
    "feedback": "Good answer but...",
    "justification": "Based on paragraph 2..."
  }
}
```

## Project Structure

```
├── backend/
│   ├── app.py              # Flask application
│   ├── ai_assistant.py     # OpenAI integration
│   └── document_processor.py # Document processing
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── styles.css          # Styling
│   └── script.js           # JavaScript logic
├── README.md               # This file
└── replit.md              # Project documentation
```

## Data Flow

1. **Document Upload**: User uploads PDF/TXT through frontend
2. **Text Extraction**: Backend processes file and extracts text
3. **AI Processing**: OpenAI generates document summary
4. **Interactive Phase**: User can ask questions or take challenges
5. **Response Generation**: AI provides grounded responses with justifications
6. **Session Management**: Conversation history maintained in memory

## Key Features

### Document Processing
- Multi-format support (PDF, TXT)
- Robust text extraction with error handling
- Text chunking for efficient processing
- Encoding detection for TXT files

### Gemini AI Integration
- Google's Gemini 2.0 Flash model for advanced language understanding
- Intelligent document summarization and analysis
- Context-aware question answering with citations
- Advanced answer evaluation with constructive feedback

### User Experience
- Drag-and-drop file upload
- Real-time loading indicators
- Responsive design for mobile devices
- Smooth animations and transitions
- Error handling with user-friendly messages

## Security & Best Practices

- File type validation
- File size limits (16MB)
- Secure filename handling
- API key protection
- CORS configuration
- Error handling throughout

## Deployment

### Local Development
- Backend runs on port 5000
- Frontend can be served statically or through local server
- Environment variables for API keys

### Production Considerations
- Use Redis or database for session storage
- Implement authentication and authorization
- Add rate limiting
- Use HTTPS
- Configure proper CORS origins
- Add logging and monitoring

## License

This project is licensed under the MIT License.
