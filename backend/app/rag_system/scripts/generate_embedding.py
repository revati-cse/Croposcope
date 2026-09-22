# rag-system/scripts/generate_embeddings.py

import os
import faiss
import pickle
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings


# 1. Load documents from the knowledge base
def load_documents(knowledge_dir: str):
    loader = DirectoryLoader(
        knowledge_dir,
        glob="**/*.txt",  # supports .txt files; adjust for .md/.pdf if needed
        loader_cls=TextLoader,
        show_progress=True,
    )
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from {knowledge_dir}")
    return documents


# 2. Split documents into smaller chunks
def split_documents(documents, chunk_size=1000, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    return chunks


# 3. Generate embeddings and create FAISS index
def build_faiss_index(chunks, index_path="rag-system/faiss_index", store_path="rag-system/chunks.pkl"):
    embeddings = OpenAIEmbeddings()  # Uses OPENAI_API_KEY from environment
    texts = [chunk.page_content for chunk in chunks]

    print("Generating embeddings...")
    vectors = embeddings.embed_documents(texts)

    # Build FAISS index
    dimension = len(vectors[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(vectors).astype("float32"))

    # Save FAISS index
    os.makedirs(index_path, exist_ok=True)
    faiss.write_index(index, os.path.join(index_path, "docs.index"))
    print(f"FAISS index saved to {index_path}/docs.index")

    # Save text chunks for retrieval
    with open(store_path, "wb") as f:
        pickle.dump(chunks, f)
    print(f"Document chunks saved to {store_path}")


if __name__ == "__main__":
    import numpy as np

    KNOWLEDGE_DIR = "rag-system/knowledge"  # adjust path to your docs

    docs = load_documents(KNOWLEDGE_DIR)
    chunks = split_documents(docs)
    build_faiss_index(chunks)
