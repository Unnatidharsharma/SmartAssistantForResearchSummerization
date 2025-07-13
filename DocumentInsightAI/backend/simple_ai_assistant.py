import os
import json
import re
from typing import List, Tuple, Dict, Any
import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings("ignore")

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

class SimpleAIAssistant:
    """Simple AI assistant using rule-based and classical ML approaches"""
    
    def __init__(self):
        print("Initializing simple AI assistant...")
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        print("Simple AI assistant initialized successfully!")
    
    def generate_summary(self, document_content: str) -> str:
        """Generate a concise summary of the document"""
        try:
            # Split document into sentences
            sentences = nltk.sent_tokenize(document_content)
            
            if len(sentences) <= 3:
                return document_content
            
            # Score sentences based on word frequency and position
            word_freq = {}
            words = document_content.lower().split()
            
            # Calculate word frequencies
            for word in words:
                word = re.sub(r'[^\w]', '', word)
                if len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Score sentences
            sentence_scores = []
            for i, sentence in enumerate(sentences):
                score = 0
                words_in_sentence = sentence.lower().split()
                
                # Position bonus (first and last sentences are important)
                if i == 0:
                    score += 2
                elif i == len(sentences) - 1:
                    score += 1
                
                # Word frequency score
                for word in words_in_sentence:
                    word = re.sub(r'[^\w]', '', word)
                    if word in word_freq:
                        score += word_freq[word]
                
                sentence_scores.append((score, sentence))
            
            # Sort by score and take top sentences
            sentence_scores.sort(reverse=True)
            
            # Select sentences to create ~150 word summary
            summary_sentences = []
            word_count = 0
            
            for score, sentence in sentence_scores:
                if word_count + len(sentence.split()) <= 150:
                    summary_sentences.append(sentence)
                    word_count += len(sentence.split())
                else:
                    break
            
            # Sort selected sentences by original order
            original_order = []
            for sentence in summary_sentences:
                idx = sentences.index(sentence)
                original_order.append((idx, sentence))
            
            original_order.sort()
            summary = " ".join([sentence for _, sentence in original_order])
            
            return summary if summary else " ".join(sentences[:3])
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            words = document_content.split()
            return " ".join(words[:150]) + "..." if len(words) > 150 else document_content
    
    def answer_question(self, question: str, document_content: str, conversation_history: List[Tuple]) -> Tuple[str, str]:
        """Answer a question based on document content"""
        try:
            # Find relevant sections
            relevant_sections = self._find_relevant_sections(question, document_content)
            
            # Generate answer
            answer = self._generate_answer(question, relevant_sections, conversation_history)
            
            # Generate justification
            justification = self._generate_justification(question, relevant_sections)
            
            return answer, justification
            
        except Exception as e:
            print(f"Error answering question: {e}")
            return self._fallback_answer(question, document_content)
    
    def _find_relevant_sections(self, question: str, document_content: str) -> List[str]:
        """Find relevant sections using TF-IDF similarity"""
        try:
            # Split into paragraphs
            paragraphs = [p.strip() for p in document_content.split('\n\n') if p.strip()]
            
            if not paragraphs:
                return [document_content[:500]]
            
            # Create TF-IDF matrix
            all_texts = [question] + paragraphs
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
            
            # Calculate similarities
            question_vector = tfidf_matrix[0]
            paragraph_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(question_vector, paragraph_vectors)[0]
            
            # Get top 3 most similar paragraphs
            top_indices = np.argsort(similarities)[-3:][::-1]
            relevant_sections = [paragraphs[i] for i in top_indices if similarities[i] > 0.05]
            
            return relevant_sections if relevant_sections else [document_content[:500]]
            
        except Exception as e:
            print(f"Error finding relevant sections: {e}")
            return [document_content[:500]]
    
    def _generate_answer(self, question: str, relevant_sections: List[str], conversation_history: List[Tuple]) -> str:
        """Generate answer using rule-based approach"""
        try:
            # Combine relevant sections
            context = " ".join(relevant_sections)
            
            # Extract key information based on question type
            question_lower = question.lower()
            
            if any(word in question_lower for word in ['what', 'define', 'definition']):
                answer = self._extract_definition(question, context)
            elif any(word in question_lower for word in ['how', 'process', 'method']):
                answer = self._extract_process(question, context)
            elif any(word in question_lower for word in ['why', 'reason', 'cause']):
                answer = self._extract_reason(question, context)
            elif any(word in question_lower for word in ['when', 'time', 'date']):
                answer = self._extract_time(question, context)
            elif any(word in question_lower for word in ['where', 'location', 'place']):
                answer = self._extract_location(question, context)
            else:
                answer = self._extract_general_info(question, context)
            
            return answer
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            return "Based on the document, I found relevant information but had difficulty generating a comprehensive answer."
    
    def _extract_definition(self, question: str, context: str) -> str:
        """Extract definition-type information"""
        sentences = nltk.sent_tokenize(context)
        
        # Look for sentences that contain definition patterns
        definition_sentences = []
        for sentence in sentences:
            if any(pattern in sentence.lower() for pattern in ['is', 'are', 'refers to', 'means', 'defined as']):
                definition_sentences.append(sentence)
        
        if definition_sentences:
            return f"According to the document, {definition_sentences[0]}"
        else:
            return f"The document provides information about this topic: {sentences[0] if sentences else 'No specific definition found.'}"
    
    def _extract_process(self, question: str, context: str) -> str:
        """Extract process or method information"""
        sentences = nltk.sent_tokenize(context)
        
        # Look for sentences with process indicators
        process_sentences = []
        for sentence in sentences:
            if any(pattern in sentence.lower() for pattern in ['first', 'then', 'next', 'finally', 'step', 'process', 'method']):
                process_sentences.append(sentence)
        
        if process_sentences:
            return f"The document explains the process: {' '.join(process_sentences[:2])}"
        else:
            return f"The document provides information about this method: {sentences[0] if sentences else 'No specific process found.'}"
    
    def _extract_reason(self, question: str, context: str) -> str:
        """Extract reason or cause information"""
        sentences = nltk.sent_tokenize(context)
        
        # Look for sentences with causal indicators
        reason_sentences = []
        for sentence in sentences:
            if any(pattern in sentence.lower() for pattern in ['because', 'due to', 'caused by', 'result of', 'reason']):
                reason_sentences.append(sentence)
        
        if reason_sentences:
            return f"The document explains: {reason_sentences[0]}"
        else:
            return f"Based on the document: {sentences[0] if sentences else 'No specific reason found.'}"
    
    def _extract_time(self, question: str, context: str) -> str:
        """Extract time-related information"""
        sentences = nltk.sent_tokenize(context)
        
        # Look for sentences with time indicators
        time_sentences = []
        for sentence in sentences:
            if any(pattern in sentence.lower() for pattern in ['when', 'during', 'time', 'year', 'month', 'day', 'period']):
                time_sentences.append(sentence)
        
        if time_sentences:
            return f"The document indicates: {time_sentences[0]}"
        else:
            return f"The document mentions: {sentences[0] if sentences else 'No specific time information found.'}"
    
    def _extract_location(self, question: str, context: str) -> str:
        """Extract location-related information"""
        sentences = nltk.sent_tokenize(context)
        
        # Look for sentences with location indicators
        location_sentences = []
        for sentence in sentences:
            if any(pattern in sentence.lower() for pattern in ['where', 'location', 'place', 'at', 'in']):
                location_sentences.append(sentence)
        
        if location_sentences:
            return f"The document states: {location_sentences[0]}"
        else:
            return f"The document provides: {sentences[0] if sentences else 'No specific location found.'}"
    
    def _extract_general_info(self, question: str, context: str) -> str:
        """Extract general information"""
        sentences = nltk.sent_tokenize(context)
        
        # Return the most relevant sentences
        if sentences:
            return f"Based on the document: {sentences[0]}"
        else:
            return "I found relevant information in the document."
    
    def _generate_justification(self, question: str, relevant_sections: List[str]) -> str:
        """Generate justification for the answer"""
        if len(relevant_sections) == 1:
            return "This answer is based on the most relevant section of the document that matches your question."
        else:
            return f"This answer is supported by {len(relevant_sections)} relevant sections of the document that contain information related to your question."
    
    def _fallback_answer(self, question: str, document_content: str) -> Tuple[str, str]:
        """Fallback answer when processing fails"""
        answer = "I found information in the document that relates to your question, but I'm having difficulty providing a detailed response."
        justification = "This response is based on a general analysis of the document content."
        return answer, justification
    
    def generate_challenge_questions(self, document_content: str) -> List[str]:
        """Generate challenge questions based on document content"""
        try:
            # Extract key concepts
            key_concepts = self._extract_key_concepts(document_content)
            
            # Generate questions
            questions = []
            
            if key_concepts:
                questions.append(f"What are the main points discussed about {key_concepts[0]} in the document?")
                
                if len(key_concepts) > 1:
                    questions.append(f"How do {key_concepts[0]} and {key_concepts[1]} relate to each other according to the document?")
                else:
                    questions.append("What specific examples or evidence does the document provide to support its main points?")
            else:
                questions.append("What are the main themes or topics covered in this document?")
                questions.append("What specific examples or evidence does the document provide?")
            
            # Add a critical thinking question
            questions.append("What conclusions can be drawn from the information presented in the document?")
            
            return questions[:3]
            
        except Exception as e:
            print(f"Error generating challenge questions: {e}")
            return [
                "What are the main themes or topics covered in this document?",
                "What specific examples or evidence does the document provide?",
                "What conclusions can be drawn from the information presented?"
            ]
    
    def _extract_key_concepts(self, document_content: str) -> List[str]:
        """Extract key concepts from document content"""
        try:
            # Use TF-IDF to find important terms
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([document_content])
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Get top scoring terms
            top_indices = np.argsort(tfidf_scores)[-10:][::-1]
            key_concepts = [feature_names[i] for i in top_indices if tfidf_scores[i] > 0]
            
            # Filter out common words and short terms
            filtered_concepts = []
            for concept in key_concepts:
                if len(concept) > 3 and concept.lower() not in ['document', 'information', 'content', 'text']:
                    filtered_concepts.append(concept)
            
            return filtered_concepts[:5]
            
        except Exception as e:
            print(f"Error extracting key concepts: {e}")
            return ["topic", "content", "information"]
    
    def evaluate_answer(self, question: str, user_answer: str, document_content: str) -> Dict[str, Any]:
        """Evaluate user's answer to a challenge question"""
        try:
            # Find relevant sections
            relevant_sections = self._find_relevant_sections(question, document_content)
            
            # Calculate score
            score = self._calculate_answer_score(question, user_answer, relevant_sections)
            
            # Generate feedback
            feedback = self._generate_feedback(score, user_answer)
            
            # Generate justification
            justification = "This evaluation is based on how well your answer addresses the question using information from the document, considering relevance, completeness, and specificity."
            
            return {
                "score": score,
                "feedback": feedback,
                "justification": justification
            }
            
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return {
                "score": 5,
                "feedback": "I was able to review your answer, but had difficulty providing a detailed evaluation.",
                "justification": "Evaluation based on general assessment of the response."
            }
    
    def _calculate_answer_score(self, question: str, user_answer: str, relevant_sections: List[str]) -> int:
        """Calculate a score for the user's answer"""
        try:
            score = 0
            
            # Basic length check
            answer_length = len(user_answer.split())
            if answer_length > 10:
                score += 2
            elif answer_length > 5:
                score += 1
            
            # Keyword matching with document
            document_text = " ".join(relevant_sections).lower()
            answer_text = user_answer.lower()
            
            document_words = set(document_text.split())
            answer_words = set(answer_text.split())
            
            # Remove common words
            common_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'a', 'an']
            document_words = document_words - set(common_words)
            answer_words = answer_words - set(common_words)
            
            # Calculate overlap
            overlap = len(answer_words.intersection(document_words))
            
            if overlap > 5:
                score += 3
            elif overlap > 2:
                score += 2
            elif overlap > 0:
                score += 1
            
            # Bonus for specific terms
            if any(word in answer_text for word in ['because', 'therefore', 'however', 'additionally', 'furthermore']):
                score += 1
            
            # Bonus for structure
            if any(word in answer_text for word in ['first', 'second', 'finally', 'in conclusion']):
                score += 1
            
            return min(score, 10)
            
        except Exception as e:
            print(f"Error calculating score: {e}")
            return 5
    
    def _generate_feedback(self, score: int, user_answer: str) -> str:
        """Generate feedback based on score"""
        if score >= 8:
            return "Excellent answer! You demonstrated strong understanding and provided comprehensive details from the document."
        elif score >= 6:
            return "Good answer! You showed understanding of the key concepts. Consider adding more specific details or examples."
        elif score >= 4:
            return "Fair answer. You touched on relevant points but could provide more comprehensive information from the document."
        else:
            return "Your answer could be improved. Try to include more specific information from the document and elaborate on key points."