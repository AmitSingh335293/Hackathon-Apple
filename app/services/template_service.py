"""
Template Service
Manages query templates and performs semantic search
"""

import json
from typing import List, Dict, Any, Optional
from opensearchpy import OpenSearch, AsyncOpenSearch
from opensearchpy.exceptions import NotFoundError

from app.config import get_settings
from app.utils import get_logger
from app.services.embedding_service import EmbeddingService

logger = get_logger(__name__)
settings = get_settings()


class TemplateService:
    """
    Service for managing SQL query templates
    Provides storage, retrieval, and semantic search capabilities
    """
    
    def __init__(self):
        """Initialize OpenSearch client and embedding service"""
        self.settings = settings
        self.embedding_service = EmbeddingService()
        
        # Load templates from file (fallback for mock mode)
        self.local_templates: List[Dict[str, Any]] = []
        
        if not self.settings.MOCK_MODE:
            self.client = AsyncOpenSearch(
                hosts=[{
                    'host': self.settings.OPENSEARCH_HOST,
                    'port': self.settings.OPENSEARCH_PORT
                }],
                http_auth=(
                    self.settings.OPENSEARCH_USERNAME,
                    self.settings.OPENSEARCH_PASSWORD
                ) if self.settings.OPENSEARCH_USERNAME else None,
                use_ssl=self.settings.OPENSEARCH_USE_SSL,
                verify_certs=False,
                ssl_show_warn=False
            )
        else:
            self.client = None
            logger.info("Template Service running in MOCK mode")
            self._load_local_templates()
    
    def _load_local_templates(self):
        """Load templates from local JSON file for mock mode"""
        try:
            with open('data/templates/query_templates.json', 'r') as f:
                data = json.load(f)
                self.local_templates = data.get('templates', [])
                logger.info("Loaded local templates", count=len(self.local_templates))
        except FileNotFoundError:
            logger.warning("Template file not found, using empty template list")
            self.local_templates = []
    
    async def search_similar_templates(
        self,
        user_query: str,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar query templates using semantic search
        
        Args:
            user_query: Natural language query
            top_k: Number of top results to return
        
        Returns:
            List of matching templates with similarity scores
        """
        top_k = top_k or self.settings.MAX_TEMPLATE_RESULTS
        
        # Generate embedding for user query
        query_embedding = await self.embedding_service.generate_embedding(user_query)
        
        if self.settings.MOCK_MODE:
            return await self._search_local_templates(query_embedding, top_k)
        
        try:
            # OpenSearch k-NN search
            search_body = {
                "size": top_k,
                "query": {
                    "knn": {
                        "embedding": {
                            "vector": query_embedding,
                            "k": top_k
                        }
                    }
                },
                "_source": ["name", "description", "sql_template", "parameters", "tags"]
            }
            
            response = await self.client.search(
                index=self.settings.OPENSEARCH_INDEX_NAME,
                body=search_body
            )
            
            results = []
            for hit in response['hits']['hits']:
                template = hit['_source']
                template['template_id'] = hit['_id']
                template['similarity_score'] = float(hit['_score'])
                results.append(template)
            
            logger.info("Template search completed", results_found=len(results))
            return results
        
        except NotFoundError:
            logger.warning("Template index not found")
            return []
        except Exception as e:
            logger.error("Template search failed", error=str(e))
            return []
    
    async def _search_local_templates(
        self,
        query_embedding: List[float],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Search templates locally using cosine similarity
        Used in mock mode
        """
        if not self.local_templates:
            return []
        
        # Calculate similarity scores
        scored_templates = []
        for template in self.local_templates:
            # Generate embedding for template description
            template_text = f"{template['name']} {template['description']}"
            template_embedding = await self.embedding_service.generate_embedding(template_text)
            
            similarity = self.embedding_service.cosine_similarity(
                query_embedding,
                template_embedding
            )
            
            if similarity >= self.settings.SIMILARITY_THRESHOLD:
                template_copy = template.copy()
                template_copy['similarity_score'] = similarity
                scored_templates.append(template_copy)
        
        # Sort by similarity and return top k
        scored_templates.sort(key=lambda x: x['similarity_score'], reverse=True)
        results = scored_templates[:top_k]
        
        logger.info("Local template search completed", results_found=len(results))
        return results
    
    async def get_template_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific template by ID
        
        Args:
            template_id: Template identifier
        
        Returns:
            Template dictionary or None if not found
        """
        if self.settings.MOCK_MODE:
            for template in self.local_templates:
                if template.get('template_id') == template_id:
                    return template
            return None
        
        try:
            response = await self.client.get(
                index=self.settings.OPENSEARCH_INDEX_NAME,
                id=template_id
            )
            template = response['_source']
            template['template_id'] = template_id
            return template
        except NotFoundError:
            return None
    
    async def create_template(self, template: Dict[str, Any]) -> str:
        """
        Create a new query template
        
        Args:
            template: Template data
        
        Returns:
            Created template ID
        """
        # Generate embedding for the template
        template_text = f"{template['name']} {template['description']}"
        embedding = await self.embedding_service.generate_embedding(template_text)
        
        template_with_embedding = {
            **template,
            "embedding": embedding
        }
        
        if self.settings.MOCK_MODE:
            template_id = f"tpl_{len(self.local_templates) + 1}"
            template_with_embedding['template_id'] = template_id
            self.local_templates.append(template_with_embedding)
            logger.info("Template created locally", template_id=template_id)
            return template_id
        
        try:
            response = await self.client.index(
                index=self.settings.OPENSEARCH_INDEX_NAME,
                body=template_with_embedding
            )
            template_id = response['_id']
            logger.info("Template created in OpenSearch", template_id=template_id)
            return template_id
        except Exception as e:
            logger.error("Failed to create template", error=str(e))
            raise
    
    async def update_template_usage(self, template_id: str):
        """
        Update template usage statistics
        
        Args:
            template_id: Template identifier
        """
        if self.settings.MOCK_MODE:
            return
        
        try:
            await self.client.update(
                index=self.settings.OPENSEARCH_INDEX_NAME,
                id=template_id,
                body={
                    "script": {
                        "source": "ctx._source.usage_count = (ctx._source.usage_count ?: 0) + 1",
                        "lang": "painless"
                    }
                }
            )
            logger.info("Template usage updated", template_id=template_id)
        except Exception as e:
            logger.warning("Failed to update template usage", error=str(e))
