"""
Vector Knowledge Base for AlphaAxiom Learning Loop v2.0

This module implements enhanced knowledge storage and retrieval using vector 
embeddings for the AlphaAxiom trading system. It applies concepts from 
DeepMind's Alpha series frameworks to organize and retrieve trading knowledge.
"""

import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class KnowledgeEntry:
    """Represents a knowledge entry in the vector knowledge base"""
    entry_id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    timestamp: datetime
    relevance_score: float = 0.0


@dataclass
class SearchResult:
    """Represents a search result from the vector knowledge base"""
    entry_id: str
    content: str
    similarity: float
    metadata: Dict[str, Any]
    timestamp: datetime


class VectorKnowledgeBase:
    """
    Enhanced knowledge storage and retrieval using vector embeddings.
    
    This knowledge base applies concepts from DeepMind's Alpha series 
    frameworks to organize and retrieve trading knowledge using vector 
    embeddings. It enables semantic search and knowledge transfer similar 
    to how AlphaZero uses neural networks to encode and retrieve game 
    knowledge.
    """
    
    def __init__(self, d1_db, kv_store, vectorize_client=None):
        """
        Initialize the Vector Knowledge Base.
        
        Args:
            d1_db: D1 database connection for persistent storage
            kv_store: KV store for fast access to knowledge data
            vectorize_client: Vectorize client for vector operations (optional)
        """
        self.d1 = d1_db
        self.kv = kv_store
        self.vectorize = vectorize_client
        self.knowledge_cache = {}
        self.embedding_dimension = 768  # Standard for many embedding models
        
        # Default knowledge base parameters
        self.kb_params = {
            'similarity_threshold': 0.7,
            'max_results': 10,
            'cache_ttl': 3600,  # 1 hour
            'embedding_model': 'text-embedding-ada-002'
        }
    
    async def add_knowledge_entry(
            self, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a knowledge entry to the vector knowledge base.
        
        Args:
            content: Content of the knowledge entry
            metadata: Metadata associated with the entry
            
        Returns:
            String representing the entry ID
        """
        # 1. Generate embedding for the content
        embedding = await self._generate_embedding(content)
        
        # 2. Create entry ID
        timestamp = int(datetime.now().timestamp())
        hash_val = hash(content) % 10000
        entry_id = f"kb_{timestamp}_{hash_val}"
        
        # 3. Create knowledge entry
        entry = KnowledgeEntry(
            entry_id=entry_id,
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            timestamp=datetime.now()
        )
        
        # 4. Store in database
        await self._store_knowledge_entry(entry)
        
        # 5. Update cache
        self.knowledge_cache[entry_id] = entry
        
        # 6. Index in vector database if available
        if self.vectorize:
            await self._index_in_vector_db(entry)
        
        return entry_id
    
    async def search_knowledge(
            self, query: str, top_k: int = 5
    ) -> List[SearchResult]:
        """
        Search for relevant knowledge entries using vector similarity.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of SearchResult objects
        """
        # 1. Generate embedding for the query
        query_embedding = await self._generate_embedding(query)
        
        # 2. Search in vector database if available
        if self.vectorize:
            return await self._search_vector_db(query_embedding, top_k)
        
        # 3. Fallback to database search
        return await self._search_database(query_embedding, top_k)
    
    async def get_related_knowledge(
            self, entry_id: str, top_k: int = 5
    ) -> List[SearchResult]:
        """
        Get knowledge entries related to a specific entry.
        
        Args:
            entry_id: ID of the reference entry
            top_k: Number of related entries to return
            
        Returns:
            List of SearchResult objects
        """
        # 1. Retrieve the reference entry
        entry = await self._get_knowledge_entry(entry_id)
        if not entry:
            return []
        
        # 2. Search for similar entries
        return await self.search_knowledge(entry.content, top_k)
    
    async def update_knowledge_entry(
            self, entry_id: str, content: Optional[str] = None, 
            metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing knowledge entry.
        
        Args:
            entry_id: ID of the entry to update
            content: New content (optional)
            metadata: New metadata (optional)
            
        Returns:
            Boolean indicating success
        """
        # 1. Retrieve existing entry
        entry = await self._get_knowledge_entry(entry_id)
        if not entry:
            return False
        
        # 2. Update content if provided
        if content is not None:
            entry.content = content
            # Regenerate embedding for new content
            entry.embedding = await self._generate_embedding(content)
        
        # 3. Update metadata if provided
        if metadata is not None:
            entry.metadata.update(metadata)
        
        # 4. Update timestamp
        entry.timestamp = datetime.now()
        
        # 5. Store updated entry
        await self._store_knowledge_entry(entry)
        
        # 6. Update cache
        self.knowledge_cache[entry_id] = entry
        
        # 7. Update vector database if available
        if self.vectorize:
            await self._update_vector_db_entry(entry)
        
        return True
    
    async def delete_knowledge_entry(self, entry_id: str) -> bool:
        """
        Delete a knowledge entry.
        
        Args:
            entry_id: ID of the entry to delete
            
        Returns:
            Boolean indicating success
        """
        # 1. Remove from database
        result = await self.d1.execute(
            "DELETE FROM knowledge_entries WHERE entry_id = ?",
            entry_id
        )
        
        # 2. Remove from cache
        if entry_id in self.knowledge_cache:
            del self.knowledge_cache[entry_id]
        
        # 3. Remove from vector database if available
        if self.vectorize:
            await self._delete_vector_db_entry(entry_id)
        
        return result is not None
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text content.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        # Check cache first
        cache_key = f"embedding_{hash(text)}"
        cached = await self.kv.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # In a production implementation, this would call an actual 
        # embedding service. In practice, you might use OpenAI embeddings, 
        # Sentence Transformers, etc.
        
        # Simple mock embedding - in reality, this would be a proper vector
        np.random.seed(hash(text) % (2**32))  # For reproducible "embeddings"
        embedding = np.random.randn(self.embedding_dimension).tolist()
        
        # Normalize the embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        # Cache the embedding
        await self.kv.put(cache_key, json.dumps(embedding))
        
        return embedding
    
    async def _store_knowledge_entry(self, entry: KnowledgeEntry) -> None:
        """
        Store a knowledge entry in the database.
        
        Args:
            entry: KnowledgeEntry to store
        """
        query = """
            INSERT OR REPLACE INTO knowledge_entries 
            (entry_id, content, embedding, metadata, timestamp, relevance_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        await self.d1.execute(
            query,
            entry.entry_id, 
            entry.content, 
            json.dumps(entry.embedding),
            json.dumps(entry.metadata), 
            entry.timestamp.isoformat(),
            entry.relevance_score
        )
    
    async def _get_knowledge_entry(
            self, entry_id: str
    ) -> Optional[KnowledgeEntry]:
        """
        Retrieve a knowledge entry by ID.
        
        Args:
            entry_id: ID of the entry to retrieve
            
        Returns:
            KnowledgeEntry object or None
        """
        # Check cache first
        if entry_id in self.knowledge_cache:
            entry = self.knowledge_cache[entry_id]
            # Check if still fresh
            cache_ttl = self.kb_params['cache_ttl']
            if (datetime.now() - entry.timestamp).seconds < cache_ttl:
                return entry
        
        # Check database
        result = await self.d1.execute(
            "SELECT * FROM knowledge_entries WHERE entry_id = ?",
            entry_id
        )
        
        if not result:
            return None
        
        row = result[0]
        entry = KnowledgeEntry(
            entry_id=row['entry_id'],
            content=row['content'],
            embedding=json.loads(row['embedding']),
            metadata=json.loads(row['metadata']),
            timestamp=datetime.fromisoformat(row['timestamp']),
            relevance_score=row['relevance_score']
        )
        
        # Cache the entry
        self.knowledge_cache[entry_id] = entry
        
        return entry
    
    async def _search_database(
            self, query_embedding: List[float], top_k: int
    ) -> List[SearchResult]:
        """
        Search for knowledge entries in the database using cosine similarity.
        
        Args:
            query_embedding: Embedding of the query
            top_k: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        # Retrieve all entries (in practice, you'd use a more efficient method)
        results = await self.d1.execute(
            "SELECT * FROM knowledge_entries ORDER BY timestamp DESC LIMIT 100"
        )
        
        if not results:
            return []
        
        # Calculate similarities
        similarities = []
        for row in results:
            entry_embedding = json.loads(row['embedding'])
            similarity = self._cosine_similarity(query_embedding, entry_embedding)
            
            threshold = self.kb_params['similarity_threshold']
            if similarity >= threshold:
                search_result = SearchResult(
                    entry_id=row['entry_id'],
                    content=row['content'],
                    similarity=similarity,
                    metadata=json.loads(row['metadata']),
                    timestamp=datetime.fromisoformat(row['timestamp'])
                )
                similarities.append((similarity, search_result))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [result for _, result in similarities[:top_k]]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            Float representing cosine similarity
        """
        # Convert to numpy arrays
        a_arr = np.array(a)
        b_arr = np.array(b)
        
        # Calculate dot product
        dot_product = np.dot(a_arr, b_arr)
        
        # Calculate magnitudes
        magnitude_a = np.linalg.norm(a_arr)
        magnitude_b = np.linalg.norm(b_arr)
        
        # Calculate cosine similarity
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        return float(dot_product / (magnitude_a * magnitude_b))
    
    async def _index_in_vector_db(self, entry: KnowledgeEntry) -> None:
        """
        Index a knowledge entry in the vector database.
        
        Args:
            entry: KnowledgeEntry to index
        """
        # This would interface with Cloudflare Vectorize or similar service
        # Implementation depends on the specific vector database being used
        pass
    
    async def _search_vector_db(
            self, query_embedding: List[float], top_k: int
    ) -> List[SearchResult]:
        """
        Search for knowledge entries in the vector database.
        
        Args:
            query_embedding: Embedding of the query
            top_k: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        # This would interface with Cloudflare Vectorize or similar service
        # Implementation depends on the specific vector database being used
        
        # Fallback to database search
        return await self._search_database(query_embedding, top_k)
    
    async def _update_vector_db_entry(self, entry: KnowledgeEntry) -> None:
        """
        Update a knowledge entry in the vector database.
        
        Args:
            entry: KnowledgeEntry to update
        """
        # This would interface with Cloudflare Vectorize or similar service
        pass
    
    async def _delete_vector_db_entry(self, entry_id: str) -> None:
        """
        Delete a knowledge entry from the vector database.
        
        Args:
            entry_id: ID of the entry to delete
        """
        # This would interface with Cloudflare Vectorize or similar service
        pass
    
    async def get_knowledge_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.
        
        Returns:
            Dictionary with knowledge base statistics
        """
        result = await self.d1.execute(
            "SELECT COUNT(*) as total_entries, "
            "MAX(timestamp) as last_updated "
            "FROM knowledge_entries"
        )
        
        if result:
            row = result[0]
            return {
                'total_entries': row['total_entries'],
                'last_updated': row['last_updated'],
                'cache_size': len(self.knowledge_cache),
                'dimension': self.embedding_dimension
            }
        
        return {
            'total_entries': 0,
            'last_updated': None,
            'cache_size': len(self.knowledge_cache),
            'dimension': self.embedding_dimension
        }