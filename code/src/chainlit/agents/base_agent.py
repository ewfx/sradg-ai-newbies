import os
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from typing import List, Dict, Any, Optional
from pydantic import SecretStr



class BaseAgent:
    """Base agent class for different chat profiles"""
    
    def __init__(
        self,
        persona: str,
        model_name: str = "gemini-2.0-flash", 
        temperature: float = 0.2,
    ):
        self.persona = persona
        self.model_name = model_name
        self.temperature = temperature
        self.memory = ConversationBufferMemory(return_messages=True)
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            api_key=SecretStr(os.getenv('GEMINI_API_KEY'))
        )
    
    async def get_response(self, message: str) -> str:
        """Process a message and return a response"""
        # To be implemented by subclasses
        raise NotImplementedError
    
    def reset_memory(self):
        """Reset the agent's memory"""
        self.memory = ConversationBufferMemory(return_messages=True)
        
    def update_persona(self, persona: str):
        """Update the agent's persona"""
        self.persona = persona