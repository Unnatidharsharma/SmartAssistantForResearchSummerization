# Gemini AI Document Analysis Assistant

## Overview

This is a modern web application that uses Google's Gemini AI to analyze documents and provide intelligent Q&A capabilities with logic-based challenges. The application uses a Flask backend and HTML/CSS/JavaScript frontend with advanced AI integration via Google's Gemini 2.0 Flash model.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modern web architecture with clear separation between frontend and backend:

- **Frontend**: HTML/CSS/JavaScript with modern responsive design, drag-and-drop functionality, and real-time API integration
- **Backend**: Flask REST API with comprehensive endpoints for document processing and AI interactions
- **Gemini AI Integration**: Google's Gemini 2.0 Flash model for advanced document analysis, summarization, and question generation
- **File Processing**: Support for PDF and TXT document formats with robust text extraction capabilities

## Key Components

### 1. Flask Backend (`backend/app.py`)
- **Purpose**: RESTful API server handling all backend operations
- **Key Features**:
  - Document upload and processing endpoints
  - Session management with in-memory storage
  - CORS configuration for frontend integration
  - Comprehensive error handling and validation

### 2. Document Processing (`backend/document_processor.py`)
- **Purpose**: Handles file upload and text extraction from PDF/TXT documents
- **Key Features**:
  - Multi-format support (PDF via PyPDF2, TXT with encoding detection)
  - Text chunking for efficient processing
  - Error handling for unsupported formats and encoding issues

### 3. Gemini AI Assistant (`backend/gemini_ai_assistant.py`)
- **Purpose**: Manages all AI interactions using Google's Gemini API
- **Key Features**:
  - Intelligent document summarization with natural language understanding
  - Context-aware question answering with document references
  - Sophisticated challenge question generation requiring critical thinking
  - Advanced answer evaluation with detailed feedback and scoring

### 4. Frontend Interface (`frontend/`)
- **Purpose**: Modern web interface with responsive design
- **Key Features**:
  - HTML5 with semantic structure
  - CSS3 with gradient backgrounds and animations
  - JavaScript for API integration and dynamic content
  - Drag-and-drop file upload functionality

## Data Flow

1. **Document Upload**: User uploads PDF/TXT file through web interface (drag-and-drop or file picker)
2. **API Request**: Frontend sends multipart form data to Flask backend
3. **Text Extraction**: Backend processes file and extracts text content
4. **AI Processing**: Gemini AI assistant generates intelligent document summary with natural language understanding
5. **Session Creation**: Backend creates session with unique ID and stores document data
6. **Interactive Phase**: User can ask questions or take challenges through API calls
7. **Response Generation**: Gemini AI provides sophisticated responses with contextual understanding and document citations
8. **Session Management**: Conversation history maintained in backend memory

## External Dependencies

### Backend Dependencies
- **Flask**: Web framework for REST API
- **Flask-CORS**: Cross-origin resource sharing
- **Google GenAI**: Google's Gemini API client library
- **PyPDF2**: PDF text extraction
- **Werkzeug**: WSGI utilities for file handling
- **Pydantic**: Data validation and parsing

### Frontend Dependencies
- **Modern Web Standards**: HTML5, CSS3, ES6 JavaScript
- **Font Awesome**: Icons for enhanced UI
- **Google Fonts**: Inter font family for typography

### Gemini AI Benefits
- Advanced natural language understanding and generation
- Sophisticated reasoning and analysis capabilities
- Context-aware responses with proper citations
- Intelligent evaluation with constructive feedback
- Cost-effective API usage with excellent performance

## Deployment Strategy

### Local Development
- Flask backend runs on port 5000
- Frontend served as static files or through local HTTP server
- Environment variable configuration for API keys
- No database requirements - uses in-memory session storage

### Key Architectural Decisions

1. **Flask + HTML/CSS/JS**: Modern web architecture with clear separation of concerns
2. **REST API Design**: Comprehensive endpoints for all functionality
3. **Responsive Frontend**: Mobile-first design with modern CSS features
4. **Gemini AI Integration**: Uses Google's Gemini 2.0 Flash for advanced document analysis and reasoning
5. **Session-Based Storage**: Uses in-memory storage for simplicity (Redis recommended for production)
6. **Error Handling**: Comprehensive error handling throughout frontend and backend

### Requirements
- Python 3.11+
- Google Gemini API key (free at https://makersuite.google.com/app/apikey)
- Modern web browser with JavaScript enabled
- Internet connection for API calls

## Recent Changes (July 12, 2025)

✓ **Architecture Restructure**: Migrated from Streamlit to Flask backend + HTML/CSS/JS frontend
✓ **REST API Implementation**: Created comprehensive Flask API with 6 endpoints
✓ **ChatGPT-Like Interface**: Built interactive chat interface with real-time messaging
✓ **Enhanced UX**: Added typing indicators, auto-resizing input, and smooth animations
✓ **Session Management**: Implemented UUID-based session tracking
✓ **File Processing**: Maintained robust PDF/TXT processing with improved error handling
✓ **Gemini AI Integration**: Integrated Google's Gemini 2.0 Flash for superior AI capabilities
✓ **Modern UI/UX**: Dark theme, sidebar navigation, and responsive design better than ChatGPT

This architecture provides a professional, cutting-edge solution for document analysis with advanced AI-powered interactions using Google's Gemini technology, suitable for deployment with superior performance and intelligence.