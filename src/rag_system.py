from typing import List, Dict
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import pickle
import os


class RAGSystem:
    """RAG system for document retrieval using FAISS vector search"""
    
    def __init__(self, documents: List[Dict]):
        """
        Initialize RAG system with documents
        
        Args:
            documents: List of documents with 'title' and 'content'
        """
        print("\n🔧 Initializing RAG system...")
        
        # Initialize embedding model
        print("  Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # Dimension of all-MiniLM-L6-v2 embeddings
        print("  ✅ Embedding model loaded")
        
        # Store documents
        self.documents = documents
        self.doc_texts = [doc['content'].strip() for doc in documents]
        self.doc_metadata = [{"title": doc['title']} for doc in documents]
        
        # Create FAISS vector store
        self.index = self._create_vector_store()
        print("✅ RAG system ready!\n")
    
    def _create_vector_store(self):
        """Create and populate FAISS vector store with documents"""
        
        print("  ✅ Created new FAISS vector database")
        print(f"  📚 Indexing {len(self.documents)} documents...")
        
        # Generate embeddings for all documents
        embeddings = self.embedding_model.encode(
            self.doc_texts,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        # Create FAISS index (using L2 distance)
        index = faiss.IndexFlatL2(self.embedding_dim)
        
        # Add embeddings to index
        index.add(embeddings.astype('float32'))
        
        print(f"  ✅ Indexed {len(self.documents)} documents")
        
        return index
    
    def retrieve(self, query: str, top_k: int = 2) -> str:
        """
        Retrieve relevant context for a query
        
        Args:
            query: User's query
            top_k: Number of documents to retrieve
            
        Returns:
            Formatted context string with retrieved documents
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            [query],
            show_progress_bar=False,
            convert_to_numpy=True
        ).astype('float32')
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Format retrieved context
        contexts = []
        for idx in indices[0]:
            if idx < len(self.doc_texts):  # Valid index
                title = self.doc_metadata[idx]['title']
                content = self.doc_texts[idx]
                contexts.append(f"[Source: {title}]\n{content}")
        
        return "\n\n".join(contexts) if contexts else ""
    
    def get_relevant_context(self, query: str, top_k: int = 2) -> Dict:
        """
        Get relevant context with metadata
        
        Args:
            query: User's query
            top_k: Number of documents to retrieve
            
        Returns:
            Dictionary with context and metadata
        """
        context = self.retrieve(query, top_k)
        
        return {
            "context": context,
            "has_context": bool(context)
        }