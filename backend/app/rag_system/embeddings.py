# backend/app/rag_system/embeddings.py
"""
Embedding client wrapper.

Supports:
- OpenAI embeddings (if OPENAI_API_KEY set and openai package installed)
- sentence-transformers local model fallback

Usage:
  client = EmbeddingClient(model_name="all-MiniLM-L6-v2")
  vec = client.embed_text("hello")
  vectors = client.embed_documents([...])
"""

import os
import logging
from typing import List
import numpy as np

logger = logging.getLogger(__name__)

_OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

# try OpenAI client if available and key present
_OPENAI_AVAILABLE = False
try:
    import openai
    _OPENAI_AVAILABLE = True
except Exception:
    _OPENAI_AVAILABLE = False

# try sentence-transformers fallback
try:
    from sentence_transformers import SentenceTransformer
    _SENTENCE_TRANSFORMERS_AVAILABLE = True
except Exception:
    _SENTENCE_TRANSFORMERS_AVAILABLE = False


class EmbeddingClient:
    def __init__(self, model_name: str = None):
        """
        If OPENAI_API_KEY is set and openai is installed, default to OpenAI embeddings (text-embedding-3-small or text-embedding-3-large).
        Otherwise falls back to sentence-transformers `model_name` (default: all-MiniLM-L6-v2).
        """
        self.model_name = model_name
        self.use_openai = False
        if _OPENAI_KEY and _OPENAI_AVAILABLE:
            self.use_openai = True
            openai.api_key = _OPENAI_KEY
            # choose a sensible default if not provided
            self.openai_model = model_name or os.environ.get("OPENAI_EMB_MODEL", "text-embedding-3-small")
            logger.info("EmbeddingClient using OpenAI model %s", self.openai_model)
        elif _SENTENCE_TRANSFORMERS_AVAILABLE:
            self.local_model_name = model_name or os.environ.get("HF_EMB_MODEL", "all-MiniLM-L6-v2")
            self.encoder = SentenceTransformer(self.local_model_name)
            logger.info("EmbeddingClient using SentenceTransformer %s", self.local_model_name)
        else:
            raise RuntimeError("No embedding backend available. Install `openai` or `sentence-transformers`.")

    def embed_text(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.use_openai:
            # batch call OpenAI embeddings
            # note: OpenAI has rate limits; consider batching smaller lists
            resp = openai.Embedding.create(input=texts, model=self.openai_model)
            return [r["embedding"] for r in resp["data"]]
        else:
            # sentence-transformers -> numpy list
            arr = self.encoder.encode(texts, show_progress_bar=False, convert_to_numpy=True)
            return [list(v.astype(float)) for v in arr]
