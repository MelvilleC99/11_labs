"""
OpenAI client setup and configuration
"""
import os
import openai
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("Missing OPENAI_API_KEY in environment variables")
        
        openai.api_key = self.api_key
    
    def get_client(self):
        """Get the OpenAI client (returns openai module)"""
        return openai

# Global instance
openai_client = OpenAIClient()
