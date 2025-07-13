import os
import json
from typing import List, Tuple, Dict, Any
from openai import OpenAI

class AIAssistant:
    """Handles AI interactions for document analysis and question generation"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
    
    def generate_summary(self, document_content: str) -> str:
        """Generate a concise summary of the document (≤150 words)"""
        try:
            prompt = f"""
            Please provide a concise summary of the following document in no more than 150 words.
            Focus on the main points, key findings, and core themes.
            
            Document:
            {document_content[:4000]}  # Limit input to avoid token limits
            
            Summary (≤150 words):
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")
    
    def answer_question(self, question: str, document_content: str, conversation_history: List[Tuple]) -> Tuple[str, str]:
        """Answer a question based on the document content with justification"""
        try:
            # Build context from conversation history
            context = self._build_conversation_context(conversation_history)
            
            prompt = f"""
            You are an expert document analyst. Answer the following question based ONLY on the provided document content.
            
            IMPORTANT RULES:
            1. Base your answer ONLY on the document content provided
            2. Do not use external knowledge or make assumptions
            3. If the document doesn't contain enough information, say so explicitly
            4. Provide a clear justification referencing specific parts of the document
            
            Document Content:
            {document_content}
            
            Previous Conversation Context:
            {context}
            
            Question: {question}
            
            Please provide:
            1. A clear, comprehensive answer
            2. A justification explaining which parts of the document support your answer
            
            Format your response as:
            ANSWER: [your answer here]
            JUSTIFICATION: [explanation of which parts of the document support this answer]
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.2
            )
            
            content = response.choices[0].message.content.strip()
            return self._parse_answer_response(content)
        except Exception as e:
            raise Exception(f"Failed to answer question: {str(e)}")
    
    def generate_challenge_questions(self, document_content: str) -> List[str]:
        """Generate 3 logic-based questions for the Challenge Me mode"""
        try:
            prompt = f"""
            Based on the following document, generate exactly 3 challenging questions that test:
            1. Comprehension and inference
            2. Logical reasoning
            3. Critical thinking about the content
            
            The questions should:
            - Require deep understanding of the document
            - Test ability to make connections between different parts
            - Challenge analytical thinking
            - Have clear answers that can be found in or inferred from the document
            
            Document Content:
            {document_content}
            
            Generate exactly 3 questions in JSON format:
            {{"questions": ["question1", "question2", "question3"]}}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=400,
                temperature=0.4
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("questions", [])
        except Exception as e:
            raise Exception(f"Failed to generate challenge questions: {str(e)}")
    
    def evaluate_answer(self, question: str, user_answer: str, document_content: str) -> Dict[str, Any]:
        """Evaluate user's answer to a challenge question"""
        try:
            prompt = f"""
            You are an expert evaluator. Evaluate the user's answer to a question based on the provided document.
            
            Document Content:
            {document_content}
            
            Question: {question}
            User's Answer: {user_answer}
            
            Please evaluate the answer based on:
            1. Accuracy (how correct the answer is)
            2. Completeness (how well it addresses the question)
            3. Use of document evidence (how well it references the source)
            
            Provide your evaluation in JSON format:
            {{
                "score": [score out of 10],
                "feedback": "[detailed feedback on the answer]",
                "justification": "[reference to specific parts of the document that support the correct answer]"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=600,
                temperature=0.2
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Failed to evaluate answer: {str(e)}")
    
    def _build_conversation_context(self, conversation_history: List[Tuple]) -> str:
        """Build context string from conversation history"""
        if not conversation_history:
            return "No previous conversation."
        
        context = "Previous Q&A:\n"
        for i, (q, a, j) in enumerate(conversation_history[-3:]):  # Last 3 for context
            context += f"Q{i+1}: {q}\nA{i+1}: {a}\n\n"
        
        return context
    
    def _parse_answer_response(self, response: str) -> Tuple[str, str]:
        """Parse the AI response to extract answer and justification"""
        try:
            # Look for ANSWER: and JUSTIFICATION: markers
            answer_match = response.split("ANSWER:")
            if len(answer_match) > 1:
                answer_part = answer_match[1].split("JUSTIFICATION:")[0].strip()
                justification_part = response.split("JUSTIFICATION:")[-1].strip()
                return answer_part, justification_part
            else:
                # Fallback: split response in half
                parts = response.split("\n\n")
                if len(parts) >= 2:
                    return parts[0].strip(), parts[1].strip()
                else:
                    return response.strip(), "Based on the document content provided."
        except Exception:
            return response.strip(), "Based on the document content provided."