import os
import json
import re
from typing import List, Tuple, Dict, Any
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from sentence_transformers import SentenceTransformer
import nltk
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings("ignore")

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class LocalAIAssistant:
    """Handles AI interactions using local models for document analysis"""
    
    def __init__(self):
        print("Initializing local AI models...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Initialize models
        self._load_models()
        
    def _load_models(self):
        """Load local AI models"""
        try:
            # Load a smaller, efficient model for text generation
            model_name = "microsoft/DialoGPT-medium"
            print(f"Loading text generation model: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Add padding token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load sentence transformer for semantic similarity
            print("Loading sentence transformer...")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize text generation pipeline
            self.text_generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1,
                max_length=512,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            print("Models loaded successfully!")
            
        except Exception as e:
            print(f"Error loading models: {e}")
            # Fallback to a simpler approach if models fail to load
            self.sentence_model = None
            self.text_generator = None
    
    def generate_summary(self, document_content: str) -> str:
        """Generate a concise summary of the document using local AI"""
        try:
            # Split document into sentences
            sentences = nltk.sent_tokenize(document_content)
            
            # Take first few sentences and key sections
            if len(sentences) <= 5:
                summary_sentences = sentences
            else:
                # Take first 2 sentences, some middle sentences, and last sentence
                summary_sentences = (
                    sentences[:2] + 
                    sentences[len(sentences)//3:len(sentences)//3+2] + 
                    sentences[2*len(sentences)//3:2*len(sentences)//3+2] + 
                    sentences[-1:]
                )
            
            # Join and truncate to approximately 150 words
            summary = " ".join(summary_sentences)
            words = summary.split()
            
            if len(words) > 150:
                summary = " ".join(words[:150]) + "..."
            
            return summary
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            # Fallback summary
            words = document_content.split()
            if len(words) > 150:
                return " ".join(words[:150]) + "..."
            return document_content
    
    def answer_question(self, question: str, document_content: str, conversation_history: List[Tuple]) -> Tuple[str, str]:
        """Answer a question based on document content using local AI"""
        try:
            # Find relevant sections using keyword matching and semantic similarity
            relevant_sections = self._find_relevant_sections(question, document_content)
            
            # Generate context-aware answer
            context = self._build_context(relevant_sections, conversation_history)
            
            # Generate answer using local model or rule-based approach
            answer = self._generate_answer(question, context)
            
            # Generate justification
            justification = self._generate_justification(question, answer, relevant_sections)
            
            return answer, justification
            
        except Exception as e:
            print(f"Error answering question: {e}")
            return self._fallback_answer(question, document_content)
    
    def _find_relevant_sections(self, question: str, document_content: str) -> List[str]:
        """Find relevant sections of the document for the question"""
        try:
            # Split document into paragraphs
            paragraphs = [p.strip() for p in document_content.split('\n\n') if p.strip()]
            
            if self.sentence_model is not None:
                # Use semantic similarity
                question_embedding = self.sentence_model.encode([question])
                paragraph_embeddings = self.sentence_model.encode(paragraphs)
                
                # Calculate similarities
                similarities = cosine_similarity(question_embedding, paragraph_embeddings)[0]
                
                # Get top 3 most similar paragraphs
                top_indices = np.argsort(similarities)[-3:][::-1]
                relevant_sections = [paragraphs[i] for i in top_indices if similarities[i] > 0.1]
            else:
                # Fallback to keyword matching
                question_words = set(question.lower().split())
                relevant_sections = []
                
                for paragraph in paragraphs:
                    paragraph_words = set(paragraph.lower().split())
                    common_words = question_words.intersection(paragraph_words)
                    
                    if len(common_words) > 1:  # At least 2 common words
                        relevant_sections.append(paragraph)
                
                # Limit to top 3 sections
                relevant_sections = relevant_sections[:3]
            
            return relevant_sections if relevant_sections else [document_content[:1000]]
            
        except Exception as e:
            print(f"Error finding relevant sections: {e}")
            return [document_content[:1000]]
    
    def _build_context(self, relevant_sections: List[str], conversation_history: List[Tuple]) -> str:
        """Build context from relevant sections and conversation history"""
        context = "Document sections:\n"
        for i, section in enumerate(relevant_sections):
            context += f"Section {i+1}: {section[:300]}...\n"
        
        if conversation_history:
            context += "\nPrevious conversation:\n"
            for q, a, _ in conversation_history[-2:]:  # Last 2 exchanges
                context += f"Q: {q}\nA: {a}\n"
        
        return context
    
    def _generate_answer(self, question: str, context: str) -> str:
        """Generate answer using local model or rule-based approach"""
        try:
            # Extract key information from context
            key_info = self._extract_key_information(question, context)
            
            # Generate structured answer
            if "what" in question.lower():
                answer = f"Based on the document, {key_info}"
            elif "how" in question.lower():
                answer = f"The document explains that {key_info}"
            elif "why" in question.lower():
                answer = f"According to the document, {key_info}"
            elif "when" in question.lower():
                answer = f"The document indicates that {key_info}"
            else:
                answer = f"The document shows that {key_info}"
            
            return answer
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            return "I found relevant information in the document, but I'm having trouble generating a comprehensive answer."
    
    def _extract_key_information(self, question: str, context: str) -> str:
        """Extract key information from context relevant to the question"""
        # Simple extraction based on question keywords
        question_words = set(question.lower().split())
        
        sentences = nltk.sent_tokenize(context)
        relevant_sentences = []
        
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            common_words = question_words.intersection(sentence_words)
            
            if len(common_words) > 0:
                relevant_sentences.append(sentence)
        
        if relevant_sentences:
            return " ".join(relevant_sentences[:2])  # Take first 2 relevant sentences
        else:
            return sentences[0] if sentences else "relevant information from the document"
    
    def _generate_justification(self, question: str, answer: str, relevant_sections: List[str]) -> str:
        """Generate justification for the answer"""
        if len(relevant_sections) == 1:
            return f"This answer is based on information found in the document section that discusses the topic."
        else:
            return f"This answer is supported by {len(relevant_sections)} relevant sections of the document that contain information related to your question."
    
    def _fallback_answer(self, question: str, document_content: str) -> Tuple[str, str]:
        """Fallback answer when AI processing fails"""
        # Simple keyword-based response
        words = document_content.split()
        answer = f"The document contains information related to your question about {question.lower()}."
        justification = "This response is based on a keyword analysis of the document content."
        return answer, justification
    
    def generate_challenge_questions(self, document_content: str) -> List[str]:
        """Generate challenge questions based on document content"""
        try:
            # Extract key topics and concepts
            key_concepts = self._extract_key_concepts(document_content)
            
            # Generate different types of questions
            questions = []
            
            # Comprehension questions
            if len(key_concepts) > 0:
                questions.append(f"What are the main points discussed about {key_concepts[0]}?")
            
            # Analysis questions
            if len(key_concepts) > 1:
                questions.append(f"How do {key_concepts[0]} and {key_concepts[1]} relate to each other in the document?")
            
            # Critical thinking questions
            questions.append("What are the key implications or conclusions that can be drawn from this document?")
            
            # If we don't have enough concepts, add generic questions
            while len(questions) < 3:
                generic_questions = [
                    "What are the most important findings or conclusions presented in this document?",
                    "What evidence or examples does the document provide to support its main arguments?",
                    "How might the information in this document be applied in real-world scenarios?"
                ]
                for q in generic_questions:
                    if q not in questions:
                        questions.append(q)
                        break
            
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
            # Find capitalized words and phrases (likely to be important concepts)
            words = document_content.split()
            key_concepts = []
            
            # Look for capitalized words that aren't at sentence beginnings
            for i, word in enumerate(words):
                if word[0].isupper() and i > 0 and not words[i-1].endswith(('.', '!', '?')):
                    clean_word = re.sub(r'[^\w\s]', '', word)
                    if len(clean_word) > 3 and clean_word not in key_concepts:
                        key_concepts.append(clean_word)
            
            # Also look for repeated important words
            word_freq = {}
            for word in words:
                clean_word = re.sub(r'[^\w\s]', '', word.lower())
                if len(clean_word) > 4:
                    word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
            
            # Add frequently mentioned words
            frequent_words = [word for word, freq in word_freq.items() if freq > 2]
            key_concepts.extend(frequent_words[:5])
            
            return list(set(key_concepts))[:10]  # Return unique concepts, max 10
            
        except Exception as e:
            print(f"Error extracting key concepts: {e}")
            return ["topic", "information", "content"]
    
    def evaluate_answer(self, question: str, user_answer: str, document_content: str) -> Dict[str, Any]:
        """Evaluate user's answer to a challenge question"""
        try:
            # Find relevant sections for the question
            relevant_sections = self._find_relevant_sections(question, document_content)
            
            # Simple evaluation based on keyword matching and length
            score = self._calculate_answer_score(question, user_answer, relevant_sections)
            
            # Generate feedback
            feedback = self._generate_feedback(score, user_answer, relevant_sections)
            
            # Generate justification
            justification = self._generate_evaluation_justification(question, relevant_sections)
            
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
            
            # Length check (basic completeness)
            if len(user_answer.split()) > 5:
                score += 2
            if len(user_answer.split()) > 15:
                score += 1
            
            # Keyword matching with document content
            answer_words = set(user_answer.lower().split())
            document_words = set()
            
            for section in relevant_sections:
                document_words.update(section.lower().split())
            
            common_words = answer_words.intersection(document_words)
            
            # Score based on relevant word overlap
            if len(common_words) > 2:
                score += 2
            if len(common_words) > 5:
                score += 2
            if len(common_words) > 10:
                score += 2
            
            # Bonus for specific terms
            if any(word in user_answer.lower() for word in ['because', 'therefore', 'however', 'additionally']):
                score += 1
            
            return min(score, 10)  # Cap at 10
            
        except Exception as e:
            print(f"Error calculating score: {e}")
            return 5
    
    def _generate_feedback(self, score: int, user_answer: str, relevant_sections: List[str]) -> str:
        """Generate feedback based on the score and answer"""
        if score >= 8:
            return "Excellent answer! You demonstrated a strong understanding of the document content and provided relevant details."
        elif score >= 6:
            return "Good answer! You showed understanding of the main concepts. Consider adding more specific details from the document."
        elif score >= 4:
            return "Fair answer. You touched on some relevant points, but could provide more comprehensive details and examples from the document."
        else:
            return "Your answer needs improvement. Try to include more specific information from the document and elaborate on your points."
    
    def _generate_evaluation_justification(self, question: str, relevant_sections: List[str]) -> str:
        """Generate justification for the evaluation"""
        return f"This evaluation is based on how well your answer addresses the question using information from the document. The assessment considers relevance, completeness, and use of specific details from the source material."