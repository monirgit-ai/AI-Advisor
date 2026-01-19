"""LLM chat service using Ollama."""
import requests
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class OllamaChatClient:
    """Service for generating chat responses using Ollama."""
    
    def __init__(self, base_url: str = None, model: str = None):
        """
        Initialize Ollama chat client.
        
        Args:
            base_url: Ollama API base URL (defaults to settings)
            model: Chat model name (defaults to settings)
        """
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_CHAT_MODEL
        self.api_url = f"{self.base_url}/api/generate"
    
    def generate(self, prompt: str) -> Optional[str]:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The full prompt (system + context + user question)
            
        Returns:
            Generated response text, or None if failed
        """
        if not prompt or not prompt.strip():
            return None
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120  # 120 second timeout for LLM generation
            )
            response.raise_for_status()
            
            data = response.json()
            answer = data.get("response")
            
            if not answer:
                logger.error(f"Invalid response from Ollama: {data}")
                return None
            
            return answer.strip()
        
        except requests.exceptions.Timeout:
            logger.error("Ollama API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating response: {e}")
            return None


# Global instance
llm_client = OllamaChatClient()
