import streamlit as st
import os
from document_processor import DocumentProcessor
from ai_assistant import AIAssistant
from utils import initialize_session_state

def main():
    st.set_page_config(
        page_title="GenAI Document Analysis Assistant",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 GenAI Document Analysis Assistant")
    st.markdown("Upload a document and interact with it through AI-powered Q&A and logic challenges.")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 Document Upload")
        uploaded_file = st.file_uploader(
            "Choose a document", 
            type=['pdf', 'txt'],
            help="Upload a PDF or TXT file for analysis"
        )
        
        if uploaded_file is not None:
            if st.button("Process Document", type="primary"):
                process_document(uploaded_file)
    
    # Main content area
    if st.session_state.document_processed:
        display_document_analysis()
    else:
        st.info("👆 Please upload a document to get started!")

def process_document(uploaded_file):
    """Process the uploaded document and generate summary"""
    try:
        with st.spinner("Processing document..."):
            # Initialize processors
            doc_processor = DocumentProcessor()
            ai_assistant = AIAssistant()
            
            # Process document
            text_content = doc_processor.extract_text(uploaded_file)
            chunks = doc_processor.chunk_text(text_content)
            
            # Generate summary
            summary = ai_assistant.generate_summary(text_content)
            
            # Store in session state
            st.session_state.document_content = text_content
            st.session_state.document_chunks = chunks
            st.session_state.document_summary = summary
            st.session_state.document_name = uploaded_file.name
            st.session_state.document_processed = True
            st.session_state.conversation_history = []
            
        st.success("Document processed successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")

def display_document_analysis():
    """Display the main document analysis interface"""
    st.header(f"📄 Analysis: {st.session_state.document_name}")
    
    # Display summary
    with st.expander("📋 Document Summary", expanded=True):
        st.write(st.session_state.document_summary)
    
    # Mode selection
    st.subheader("🎯 Choose Interaction Mode")
    mode = st.radio(
        "Select how you'd like to interact with the document:",
        ["Ask Anything", "Challenge Me"],
        horizontal=True
    )
    
    if mode == "Ask Anything":
        display_ask_anything_mode()
    else:
        display_challenge_mode()

def display_ask_anything_mode():
    """Display the Ask Anything mode interface"""
    st.subheader("💬 Ask Anything Mode")
    st.write("Ask any question about the document and get contextual answers with justifications.")
    
    # Display conversation history
    if st.session_state.conversation_history:
        st.subheader("📝 Conversation History")
        for i, (question, answer, justification) in enumerate(st.session_state.conversation_history):
            with st.expander(f"Q{i+1}: {question[:50]}..."):
                st.write(f"**Question:** {question}")
                st.write(f"**Answer:** {answer}")
                st.write(f"**Justification:** {justification}")
    
    # Question input
    question = st.text_input(
        "Enter your question:",
        placeholder="e.g., What are the main findings of this document?"
    )
    
    if st.button("Get Answer") and question:
        try:
            with st.spinner("Analyzing document and generating answer..."):
                ai_assistant = AIAssistant()
                answer, justification = ai_assistant.answer_question(
                    question, 
                    st.session_state.document_content,
                    st.session_state.conversation_history
                )
                
                # Add to conversation history
                st.session_state.conversation_history.append((question, answer, justification))
                
                # Display answer
                st.success("Answer generated!")
                with st.container():
                    st.write(f"**Answer:** {answer}")
                    st.write(f"**Justification:** {justification}")
                    
        except Exception as e:
            st.error(f"Error generating answer: {str(e)}")

def display_challenge_mode():
    """Display the Challenge Me mode interface"""
    st.subheader("🧠 Challenge Me Mode")
    st.write("Test your understanding with AI-generated questions based on the document.")
    
    # Generate questions button
    if not st.session_state.get('challenge_questions'):
        if st.button("Generate Questions", type="primary"):
            try:
                with st.spinner("Generating logic-based questions..."):
                    ai_assistant = AIAssistant()
                    questions = ai_assistant.generate_challenge_questions(
                        st.session_state.document_content
                    )
                    st.session_state.challenge_questions = questions
                    st.session_state.user_answers = [""] * len(questions)
                    st.session_state.evaluations = [None] * len(questions)
                st.rerun()
            except Exception as e:
                st.error(f"Error generating questions: {str(e)}")
    
    # Display questions and collect answers
    if st.session_state.get('challenge_questions'):
        st.write("**Answer the following questions based on the document:**")
        
        for i, question in enumerate(st.session_state.challenge_questions):
            st.write(f"**Question {i+1}:** {question}")
            
            # Answer input
            answer = st.text_area(
                f"Your answer for Question {i+1}:",
                value=st.session_state.user_answers[i],
                key=f"answer_{i}",
                height=100
            )
            st.session_state.user_answers[i] = answer
            
            # Evaluate answer button
            if answer and st.button(f"Evaluate Answer {i+1}", key=f"eval_{i}"):
                try:
                    with st.spinner(f"Evaluating answer {i+1}..."):
                        ai_assistant = AIAssistant()
                        evaluation = ai_assistant.evaluate_answer(
                            question, 
                            answer, 
                            st.session_state.document_content
                        )
                        st.session_state.evaluations[i] = evaluation
                        st.rerun()
                except Exception as e:
                    st.error(f"Error evaluating answer: {str(e)}")
            
            # Display evaluation if available
            if st.session_state.evaluations[i]:
                evaluation = st.session_state.evaluations[i]
                with st.expander(f"Evaluation for Question {i+1}", expanded=True):
                    st.write(f"**Score:** {evaluation['score']}/10")
                    st.write(f"**Feedback:** {evaluation['feedback']}")
                    st.write(f"**Justification:** {evaluation['justification']}")
            
            st.divider()
        
        # Reset button
        if st.button("Generate New Questions"):
            st.session_state.challenge_questions = None
            st.session_state.user_answers = None
            st.session_state.evaluations = None
            st.rerun()

if __name__ == "__main__":
    main()
