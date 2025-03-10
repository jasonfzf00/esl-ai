import json
from typing import Dict, Any, List
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from app.core.config import settings

class OllamaService:
    """Service for interacting with Ollama LLM."""
    
    def __init__(self):
        """Initialize the Ollama service."""
        self.llm = Ollama(
            model=settings.OLLAMA_MODEL,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
        )
        
    def pick_words(self, text: str, grade: int) -> List[str]:
        """
        Pick 10 words from the text.
        """
        
        print("Using model", settings.OLLAMA_MODEL)
        prompt = f"""
            Given the following text from grade {grade}, please:
            1. Select exactly 10 words that would be appropriately challenging for a grade {grade} student
            2. Choose words that are important for vocabulary building and academic success
            3. Return only the selected words as a comma-separated list, with no other text
            4. Format example: word1, word2, word3, word4, word5, word6, word7, word8, word9, word10
            
            Text: {text}
        """
        try:
            response = self.llm.invoke(prompt)
            # Clean and process the response
            words = [word.strip() for word in response.strip('[]"\' ').split(',')]
            # Ensure we have exactly 10 words
            words = words[:10] if len(words) > 10 else words
            return words
        except Exception as e:
            print(f"Error picking words: {str(e)}")
            return []
    
    def generate_conversation_from_words(self, words: List[str], grade: int) -> Dict[str, Any]:
        """
        Generate conversation for practice using Ollama.
        """
        
        prompt = f"""
            You are helping create educational content for grade {grade} students.
            Given these vocabulary words: {', '.join(words)}
            
            Create a natural conversation between two students that:
            1. Uses all the vocabulary words naturally and appropriately 
            2. Has at least 5 sentences for each student
            3. Focuses on topics relevant to grade {grade} students
            4. Includes subtle context clues for the vocabulary words
            
            Return ONLY a JSON object with this exact format:
            {{
                "conversation": [
                    {{"speaker": "Student1", "text": "First line of dialogue"}},
                    {{"speaker": "Student2", "text": "Response dialogue"}},
                    {{"speaker": "Student1", "text": "Next line"}},
                    {{"speaker": "Student2", "text": "Response"}}
                ]
            }}
            
            The conversation should flow naturally while incorporating the vocabulary words. Do not include any other text or explanation.
        """
        
        try:
            # Get response from Ollama
            response = self.llm.invoke(prompt)
            
            # Extract JSON from the response
            # Find the first occurrence of '{' and the last occurrence of '}'
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
                return result
            else:
                # If JSON parsing fails, create a structured response
                return {
                    "conversation": {
                        "system": "Failed to generate a proper conversation. Please try again."
                    },
                    "raw_response": response
                }
                
        except Exception as e:
            # Handle any exceptions
            return {
                "conversation": {
                    "system": f"An error occurred: {str(e)}"
                }
            } 