# backend/app/rag_system/generator.py
"""
Response generation for RAG.

By default:
- If OPENAI_API_KEY set and `openai` package installed -> use ChatCompletions (gpt-3.5/4 family)
- Otherwise: a safe local fallback that composes a structured summary from retrieved docs.

Functions:
  generate_answer(query, retrieved_docs, use_openai=True, openai_model="gpt-3.5-turbo")
"""

import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)
_OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

# Try import openai if available
try:
    import openai
    _OPENAI_AVAILABLE = True
except Exception:
    _OPENAI_AVAILABLE = False

def _compose_context(retrieved_docs: List[Dict[str, Any]], max_chars: int = 3000) -> str:
    """
    Compose a single context string from retrieved documents.
    Truncate intelligently to max_chars.
    """
    pieces = []
    total = 0
    for d in retrieved_docs:
        txt = d.get("text", "")
        snippet = txt.strip().replace("\n", " ")
        # prefer shorter excerpt
        if len(snippet) > 1000:
            snippet = snippet[:1000] + "..."
        if total + len(snippet) > max_chars:
            break
        pieces.append(f"Source: {d.get('source')}\n{snippet}")
        total += len(snippet)
    return "\n\n---\n\n".join(pieces)


def _build_system_prompt() -> str:
    return (
        "You are an expert agronomist assistant. Use the provided documents to answer the user's question. "
        "Be concise, practical, and include actionable steps where relevant. If the documents do not contain enough information, "
        "explain what additional info is needed."
    )


def _openai_generate(query: str, retrieved_docs: List[Dict[str, Any]], model: str = "gpt-3.5-turbo", max_tokens: int = 256) -> str:
    if not _OPENAI_AVAILABLE or not _OPENAI_KEY:
        raise RuntimeError("OpenAI not available")

    openai.api_key = _OPENAI_KEY
    context = _compose_context(retrieved_docs)
    system_prompt = _build_system_prompt()
    user_prompt = f"User question: {query}\n\nContext:\n{context}\n\nAnswer the question using the context."
    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.2,
            n=1,
        )
        out = resp["choices"][0]["message"]["content"].strip()
        return out
    except Exception as e:
        logger.exception("OpenAI generation failed: %s", e)
        raise


def _local_fallback_generate(query: str, retrieved_docs: List[Dict[str, Any]]) -> str:
    """
    Local fallback: produces a structured answer by:
      - listing top sources and their short snippets
      - giving a synthesized bullet-point answer by extracting key sentences heuristically.
    This avoids calling any external LLM.
    """
    if not retrieved_docs:
        return "I could not find any relevant documents in the knowledge base."

    context = _compose_context(retrieved_docs, max_chars=2000)
    # Very simple heuristic "synthesis": pick first sentence from each doc snippet, then join
    bullets = []
    for d in retrieved_docs[:5]:
        txt = d.get("text", "").strip().replace("\n", " ")
        if not txt:
            continue
        # take first 2 sentences
        sentences = txt.split(".")
        s = ". ".join([s.strip() for s in sentences[:2] if s.strip()])
        if s:
            bullets.append(f"- {s.strip()}. (source: {d.get('source')})")

    header = f"Found {len(retrieved_docs)} documents. Here are key points from top sources:\n\n"
    synth = "\n".join(bullets) if bullets else "No concise points could be extracted."
    footer = ("\n\nNote: This is an extractive summary (no external LLM used). "
              "For a more fluent, integrated answer, set OPENAI_API_KEY and use the OpenAI option.")
    return header + synth + footer


def generate_answer(
    query: str,
    retrieved_docs: List[Dict[str, Any]],
    prefer_openai: bool = True,
    openai_model: str = "gpt-3.5-turbo",
    max_tokens: int = 256,
) -> Dict[str, Any]:
    """
    Generate a final answer to present to the user.

    returns: {
      "answer": str,
      "used_model": "openai" | "fallback",
      "sources": [ {id, source, score} ],
    }
    """
    sources = [{"id": d.get("id"), "source": d.get("source"), "score": d.get("score")} for d in retrieved_docs]

    # Prefer OpenAI if requested and available
    if prefer_openai and _OPENAI_AVAILABLE and _OPENAI_KEY:
        try:
            ans = _openai_generate(query, retrieved_docs, model=openai_model, max_tokens=max_tokens)
            return {"answer": ans, "used_model": "openai", "sources": sources}
        except Exception:
            logger.exception("OpenAI generation failed, falling back to local summarizer.")

    # fallback
    ans = _local_fallback_generate(query, retrieved_docs)
    return {"answer": ans, "used_model": "fallback", "sources": sources}
