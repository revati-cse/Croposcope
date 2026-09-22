# backend/app/rag_system/__init__.py
"""
RAG system package.

Provides:
- high-level helpers to build the knowledge base
- generate embeddings and faiss index
- retrieve relevant docs
- generate responses from retrieved docs
"""

from .knowledge_base import (build_knowledge_base, load_chunks, save_chunks,
                             DEFAULT_KB_DIR, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP)
from .embeddings import EmbeddingClient
from .retriever import FaissRetriever
from .generator import generate_answer

__all__ = [
    "build_knowledge_base",
    "load_chunks",
    "save_chunks",
    "EmbeddingClient",
    "FaissRetriever",
    "generate_answer",
    "DEFAULT_KB_DIR",
    "DEFAULT_CHUNK_SIZE",
    "DEFAULT_CHUNK_OVERLAP",
]
