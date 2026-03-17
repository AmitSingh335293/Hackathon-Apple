"""
Embedding Service
Handles text embedding generation using AWS Bedrock
"""

import json
from typing import List
import boto3
from botocore.exceptions import ClientError
import numpy as np

from app.config import get_settings
from app.utils import get_logger

logger = get_logger(__name__)
settings = get_settings()


class EmbeddingService:
    """
    Service for generating embeddings using AWS Bedrock
    Used for semantic search of query templates
    """
    
    def __init__(self):
        """Initialize Bedrock client for embeddings"""
        self.settings = settings
        
        if not self.settings.MOCK_MODE:
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=self.settings.AWS_REGION,
                aws_access_key_id=self.settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self.settings.AWS_SECRET_ACCESS_KEY
            )
        else:
            self.client = None
            logger.info("Embedding Service running in MOCK mode")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for the given text
        
        Args:
            text: Input text to embed
        
        Returns:
            Embedding vector as list of floats
        """
        if self.settings.MOCK_MODE:
            return self._mock_generate_embedding(text)
        
        try:
            # Titan Embeddings format
            body = json.dumps({
                "inputText": text
            })
            
            response = self.client.invoke_model(
                modelId=self.settings.BEDROCK_EMBEDDING_MODEL_ID,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            embedding = response_body['embedding']
            
            logger.info("Embedding generated", dimension=len(embedding))
            return embedding
        
        except ClientError as e:
            logger.error("Failed to generate embedding", error=str(e))
            raise
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)
        
        logger.info("Batch embeddings generated", count=len(embeddings))
        return embeddings
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
        
        Returns:
            Similarity score between 0 and 1
        """
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        
        return float(dot_product / (norm_v1 * norm_v2))
    
    def _mock_generate_embedding(self, text: str) -> List[float]:
        """
        Generate mock embedding for testing
        Uses a simple hash-based approach to create consistent vectors
        """
        # Create a deterministic "embedding" based on text hash
        # In reality, this would be a 1536-dimensional vector from Titan
        np.random.seed(hash(text) % (2**32))
        
        # Titan embeddings are 1536 dimensions
        embedding = np.random.randn(1536).tolist()
        
        # Normalize to unit vector
        norm = np.linalg.norm(embedding)
        embedding = (np.array(embedding) / norm).tolist()
        
        return embedding
