"""
Vector Store for Document Retrieval
向量存储 - 用于文档检索
"""

import json
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class VectorStore:
    """
    Store and retrieve document chunks using vector embeddings.
    使用向量嵌入存储和检索文档块。
    """
    
    def __init__(self, storage_path: str = "data/vector_store"):
        """
        Initialize vector store.
        
        Args:
            storage_path: Path to store vector data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.documents = []
        self.embeddings = []
        self.metadata = []
        
    def add_documents(self, documents: List[Dict[str, any]], embeddings: List[List[float]]):
        """
        Add documents and their embeddings to the store.
        将文档及其嵌入添加到存储中。
        
        Args:
            documents: List of document chunks
            embeddings: List of embedding vectors
        """
        self.documents.extend(documents)
        self.embeddings.extend(embeddings)
        
    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, any]]:
        """
        Find most similar documents to the query.
        查找与查询最相似的文档。
        
        Args:
            query_embedding: Query vector embedding
            top_k: Number of top results to return
            
        Returns:
            List of most similar documents with scores
        """
        if not self.embeddings:
            return []
        
        # Calculate cosine similarity
        query_vec = np.array(query_embedding)
        embeddings_array = np.array(self.embeddings)
        
        # Normalize vectors
        query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-8)
        embeddings_norm = embeddings_array / (np.linalg.norm(embeddings_array, axis=1, keepdims=True) + 1e-8)
        
        # Compute similarities
        similarities = np.dot(embeddings_norm, query_norm)
        
        # Get top k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                "document": self.documents[idx],
                "similarity": float(similarities[idx])
            })
            
        return results
    
    def save(self, filename: str = "vector_store.json"):
        """
        Save vector store to disk.
        将向量存储保存到磁盘。
        
        Args:
            filename: Name of the file to save
        """
        store_data = {
            "documents": self.documents,
            "embeddings": [emb if isinstance(emb, list) else emb.tolist() for emb in self.embeddings],
            "metadata": self.metadata
        }
        
        save_path = self.storage_path / filename
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(store_data, f, ensure_ascii=False, indent=2)
            
        print(f"Vector store saved to {save_path}")
    
    def load(self, filename: str = "vector_store.json"):
        """
        Load vector store from disk.
        从磁盘加载向量存储。
        
        Args:
            filename: Name of the file to load
        """
        load_path = self.storage_path / filename
        
        if not load_path.exists():
            print(f"No saved vector store found at {load_path}")
            return
        
        with open(load_path, 'r', encoding='utf-8') as f:
            store_data = json.load(f)
            
        self.documents = store_data.get("documents", [])
        self.embeddings = store_data.get("embeddings", [])
        self.metadata = store_data.get("metadata", [])
        
        print(f"Vector store loaded from {load_path}")
        print(f"Loaded {len(self.documents)} documents")
