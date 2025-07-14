import os
import json
import logging
from typing import List, Tuple, Dict, Any
from google import genai
from google.genai import types
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiAIAssistant:
    """Handles AI interactions using Google's Gemini API"""
    
    def __init__(self):
        # Initialize Gemini client
        api_key ="Place Api Key here"  # Replace with your real key
        self.client = genai.Client(api_key=api_key)
        logger.info("✅ Gemini AI Assistant initialized with hardcoded API key!")

        
        # self.client = genai.Client(api_key=api_key)
        # logger.info("Gemini AI Assistant initialized successfully!")
    
    def generate_summary(self, document_content: str) -> str:
        """Generate a concise summary of the document (≤150 words)"""
        try:
            prompt = f"""Please provide a concise summary of the following document in exactly 150 words or less. 
Focus on the main points, key findings, and important conclusions:

{document_content}

Summary:"""

            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )

            # Try to get the text from the response
            if hasattr(response, "text"):
                return response.text or "Unable to generate summary"
            elif hasattr(response, "result") and hasattr(response.result, "text"):
                return response.result.text or "Unable to generate summary"
            elif isinstance(response, dict) and "text" in response:
                return response["text"] or "Unable to generate summary"
            else:
                return str(response)
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Fallback to first 150 words
            words = document_content.split()
            return " ".join(words[:150]) + "..." if len(words) > 150 else document_content
    
    def answer_question(self, question: str, document_content: str, conversation_history: List[Tuple]) -> Tuple[str, str]:
        """Answer a question based on the document content with justification"""
        try:
            # Build conversation context
            context = self._build_conversation_context(conversation_history)
            
            prompt = f"""Based on the following document, please answer the question. Provide a clear, accurate answer followed by a brief justification.

Document:
{document_content}

{context}

Question: {question}

Please provide your response in the following format:
Answer: [Your detailed answer here]
Justification: [Brief explanation of how you found this answer in the document]"""

            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )

            if response.text:
                return self._parse_answer_response(response.text)
            else:
                return "I found relevant information but couldn't generate a complete answer.", "Based on document analysis."
                
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return "I encountered an error while processing your question.", "Error in AI processing."
    
    def generate_challenge_questions(self, document_content: str) -> List[str]:
        """Generate 3 logic-based questions for the Challenge Me mode"""
        try:
            prompt = f"""Based on the following document, generate exactly 3 challenging questions that test comprehension, analysis, and critical thinking. 
The questions should require understanding of the document content and logical reasoning.

Document:
{document_content}

Please generate 3 questions that:
1. Test understanding of key concepts
2. Require analysis and synthesis of information
3. Encourage critical thinking about the content

Format your response as a numbered list:
1. [Question 1]
2. [Question 2]
3. [Question 3]"""

            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )

            if response.text:
                # Parse the numbered list
                questions = []
                lines = response.text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                        # Remove the number prefix
                        question = line[2:].strip()
                        if question:
                            questions.append(question)
                
                # Ensure we have exactly 3 questions
                if len(questions) >= 3:
                    return questions[:3]
                else:
                    # Add fallback questions if needed
                    while len(questions) < 3:
                        questions.append("What are the key insights or conclusions from this document?")
                    return questions
            else:
                return self._fallback_questions()
                
        except Exception as e:
            logger.error(f"Error generating challenge questions: {e}")
            return self._fallback_questions()
    
    def evaluate_answer(self, question: str, user_answer: str, document_content: str) -> Dict[str, Any]:
        """Evaluate user's answer to a challenge question"""
        try:
            prompt = f"""Evaluate the following answer to a question based on the provided document. 
Provide a score from 1-10, constructive feedback, and justification.

Document:
{document_content}

Question: {question}

User's Answer: {user_answer}

Please evaluate the answer and provide your response in the following JSON format:
{{
    "score": [number from 1-10],
    "feedback": "[Constructive feedback on the answer]",
    "justification": "[Explanation of how you evaluated the answer]"
}}"""

            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            if response.text:
                try:
                    result = json.loads(response.text)
                    return {
                        "score": max(1, min(10, int(result.get("score", 5)))),
                        "feedback": result.get("feedback", "Good effort on your answer."),
                        "justification": result.get("justification", "Evaluation based on document content analysis.")
                    }
                except json.JSONDecodeError:
                    return self._fallback_evaluation(user_answer)
            else:
                return self._fallback_evaluation(user_answer)
                
        except Exception as e:
            logger.error(f"Error evaluating answer: {e}")
            return self._fallback_evaluation(user_answer)
    
    def _build_conversation_context(self, conversation_history: List[Tuple]) -> str:
        """Build context string from conversation history"""
        if not conversation_history:
            return ""
        
        context = "Previous conversation:\n"
        for i, (question, answer, justification) in enumerate(conversation_history[-3:]):  # Last 3 exchanges
            context += f"Q{i+1}: {question}\nA{i+1}: {answer}\n"
        
        return context
    
    def _parse_answer_response(self, response: str) -> Tuple[str, str]:
        """Parse the AI response to extract answer and justification"""
        try:
            lines = response.strip().split('\n')
            answer = ""
            justification = ""
            
            current_section = None
            for line in lines:
                line = line.strip()
                if line.startswith("Answer:"):
                    current_section = "answer"
                    answer = line[7:].strip()
                elif line.startswith("Justification:"):
                    current_section = "justification"
                    justification = line[13:].strip()
                elif current_section == "answer" and line:
                    answer += " " + line
                elif current_section == "justification" and line:
                    justification += " " + line
            
            if not answer:
                answer = response.strip()
            if not justification:
                justification = "Based on document analysis."
            
            return answer, justification
            
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return response.strip(), "Based on document analysis."
    
    def _fallback_questions(self) -> List[str]:
        """Fallback questions if generation fails"""
        return [
            "What are the main themes or concepts discussed in this document?",
            "What evidence or examples does the document provide to support its key points?",
            "What conclusions or implications can be drawn from the information presented?"
        ]
    
    def _fallback_evaluation(self, user_answer: str) -> Dict[str, Any]:
        """Fallback evaluation if AI evaluation fails"""
        score = 5
        if len(user_answer.split()) > 20:
            score = 6
        if len(user_answer.split()) > 50:
            score = 7
        
        return {
            "score": score,
            "feedback": "Your answer shows understanding of the topic. Consider providing more specific details from the document.",
            "justification": "Evaluation based on answer length and general assessment."
        }
