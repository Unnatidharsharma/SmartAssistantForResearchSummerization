import streamlit as st

def initialize_session_state():
    """Initialize session state variables"""
    if 'document_processed' not in st.session_state:
        st.session_state.document_processed = False
    
    if 'document_content' not in st.session_state:
        st.session_state.document_content = ""
    
    if 'document_chunks' not in st.session_state:
        st.session_state.document_chunks = []
    
    if 'document_summary' not in st.session_state:
        st.session_state.document_summary = ""
    
    if 'document_name' not in st.session_state:
        st.session_state.document_name = ""
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'challenge_questions' not in st.session_state:
        st.session_state.challenge_questions = None
    
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = None
    
    if 'evaluations' not in st.session_state:
        st.session_state.evaluations = None

def validate_openai_key():
    """Check if OpenAI API key is available"""
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        st.stop()
    return api_key

def format_text_for_display(text: str, max_length: int = 500) -> str:
    """Format text for display with truncation if needed"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + "..."

def clean_filename(filename: str) -> str:
    """Clean filename for display"""
    import re
    # Remove file extension and clean up
    name = re.sub(r'\.[^.]*$', '', filename)
    # Replace underscores and hyphens with spaces
    name = re.sub(r'[_-]', ' ', name)
    # Capitalize first letter of each word
    return ' '.join(word.capitalize() for word in name.split())
