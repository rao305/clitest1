#!/usr/bin/env python3
"""
Build vector embeddings using Gemini's text-embedding-3-small model
"""

import json
import os
import numpy as np
import faiss
from google.generativeai import google.generativeai as genai
import pickle
from pathlib import Path

class VectorStore:
    def __init__(self, api_key=None):
        self.client = Gemini(api_key=api_key or os.getenv("GEMINI_API_KEY"))
        self.index = None
        self.chunks = []
        self.embeddings = None
        
    def embed_text(self, text):
        """Create embedding for a single text"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error embedding text: {e}")
            return None
    
    def embed_chunks(self, chunks):
        """Create embeddings for all chunks"""
        print(f"Creating embeddings for {len(chunks)} chunks...")
        embeddings = []
        
        for i, chunk in enumerate(chunks):
            if i % 10 == 0:
                print(f"  Processing chunk {i+1}/{len(chunks)}")
            
            embedding = self.embed_text(chunk["content"])
            if embedding:
                embeddings.append(embedding)
            else:
                # Skip failed embeddings
                print(f"  Skipping chunk {i} due to embedding failure")
                continue
        
        return np.array(embeddings, dtype=np.float32)
    
    def build_index(self, chunks):
        """Build FAISS index from chunks"""
        self.chunks = chunks
        
        # Create embeddings
        self.embeddings = self.embed_chunks(chunks)
        
        if len(self.embeddings) == 0:
            raise ValueError("No embeddings created")
        
        # Build FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings)
        
        print(f"Built FAISS index with {self.index.ntotal} vectors")
        
    def save_index(self, path="data/vector_store"):
        """Save the index and metadata"""
        os.makedirs(path, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, f"{path}/faiss_index.idx")
        
        # Save metadata
        metadata = {
            "chunks": self.chunks,
            "embeddings_shape": self.embeddings.shape,
            "total_vectors": self.index.ntotal
        }
        
        with open(f"{path}/metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Save embeddings
        np.save(f"{path}/embeddings.npy", self.embeddings)
        
        print(f"Saved vector store to {path}")
    
    def load_index(self, path="data/vector_store"):
        """Load the index and metadata"""
        if not os.path.exists(f"{path}/faiss_index.idx"):
            raise FileNotFoundError(f"No index found at {path}")
        
        # Load FAISS index
        self.index = faiss.read_index(f"{path}/faiss_index.idx")
        
        # Load metadata
        with open(f"{path}/metadata.json", "r") as f:
            metadata = json.load(f)
        
        self.chunks = metadata["chunks"]
        self.embeddings = np.load(f"{path}/embeddings.npy")
        
        print(f"Loaded vector store from {path}")
        
    def search(self, query, k=5):
        """Search for similar chunks"""
        if not self.index:
            raise ValueError("No index loaded")
        
        # Embed query
        query_embedding = self.embed_text(query)
        if not query_embedding:
            return []
        
        # Search
        query_vector = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_vector, k)
        
        # Return results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.chunks):
                result = self.chunks[idx].copy()
                result["distance"] = float(dist)
                result["rank"] = i + 1
                results.append(result)
        
        return results

def main():
    """Build vector store from normalized chunks"""
    
    # Load chunks
    if not os.path.exists("data/normalized_chunks.json"):
        print("Error: No normalized chunks found. Run normalize.py first.")
        return
    
    with open("data/normalized_chunks.json", "r") as f:
        chunks = json.load(f)
    
    if not chunks:
        print("Error: No chunks to process")
        return
    
    # Build vector store
    vector_store = VectorStore()
    vector_store.build_index(chunks)
    vector_store.save_index()
    
    print("Vector store built successfully!")
    
    # Test search
    print("\nTesting search...")
    results = vector_store.search("CS core courses", k=3)
    for result in results:
        print(f"  {result['rank']}: {result['content'][:100]}...")

if __name__ == "__main__":
    main()