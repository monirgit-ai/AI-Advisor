"""Embedding generation service using Ollama."""
import requests
from typing import List, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class OllamaEmbedder:
    """Service for generating embeddings using Ollama."""
    
    def __init__(self, base_url: str = None, model: str = None):
        """
        Initialize Ollama embedder.
        
        Args:
            base_url: Ollama API base URL (defaults to settings)
            model: Embedding model name (defaults to settings)
        """
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_EMBED_MODEL
        self.api_url = f"{self.base_url}/api/embed"
    
    def embed(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding, or None if failed
        """
        if not text or not text.strip():
            return None
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "input": text
                },
                timeout=60  # 60 second timeout for embedding generation
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Ollama returns "embeddings" (plural) as a list of lists
            # For single input, it's: {"embeddings": [[...768 floats...]]}
            embeddings_list = data.get("embeddings")
            
            if not embeddings_list or not isinstance(embeddings_list, list) or len(embeddings_list) == 0:
                logger.error(f"Invalid embedding response: {data}")
                return None
            
            # Get the first embedding (for single text input)
            embedding = embeddings_list[0]
            
            if not embedding or not isinstance(embedding, list):
                logger.error(f"Invalid embedding format: {embedding}")
                return None
            
            if len(embedding) != 768:
                logger.warning(f"Expected 768 dimensions, got {len(embedding)}")
            
            return embedding
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating embedding: {e}")
            return None
    
    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings (None for failed ones)
        """
        return [self.embed(text) for text in texts]


# Global instance
embedder = OllamaEmbedder()
