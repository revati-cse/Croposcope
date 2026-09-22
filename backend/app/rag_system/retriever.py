# backend/app/rag_system/retriever.py
import os
from typing import List, Tuple
import numpy as np

# requires: sentence-transformers, faiss-cpu
from sentence_transformers import SentenceTransformer
import faiss
import json
import threading

KB_DIR = os.environ.get("RAG_KB_DIR", "/app/rag-system/knowledge_base")
EMB_MODEL = os.environ.get("RAG_EMB_MODEL", "all-MiniLM-L6-v2")
_INDEX_FILE = os.path.join(KB_DIR, "faiss.index")
_META_FILE = os.path.join(KB_DIR, "meta.json")

_lock = threading.Lock()
_index = None
_meta = None
_encoder = None

def _load_index():
    global _index, _meta, _encoder
    if _index is not None:
        return
    with _lock:
        if _index is not None:
            return
        if not os.path.exists(_META_FILE) or not os.path.exists(_INDEX_FILE):
            raise FileNotFoundError("RAG index or meta not found. Run build_knowledge_base.py first.")
        _encoder = SentenceTransformer(EMB_MODEL)
        _index = faiss.read_index(_INDEX_FILE)
        with open(_META_FILE, "r", encoding="utf-8") as f:
            _meta = json.load(f)

def retrieve(query: str, k: int = 5) -> List[dict]:
    _load_index()
    vec = _encoder.encode([query], convert_to_numpy=True)
    D, I = _index.search(vec, k)
    results = []
    for dist, idx in zip(D[0], I[0]):
        if idx < 0 or idx >= len(_meta):
            continue
        meta_item = _meta[idx]
        results.append({
            "score": float(dist),
            "id": meta_item.get("id"),
            "source": meta_item.get("source"),
            "text": meta_item.get("text"),
            "metadata": meta_item.get("metadata", {})
        })
    return results
