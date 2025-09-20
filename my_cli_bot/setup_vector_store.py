#!/usr/bin/env python3
"""
Setup vector store for Enhanced Boiler AI
Creates FAISS index with Gemini embeddings for course information
"""

import os
import json
import faiss
import numpy as np
from google.generativeai import google.generativeai as genai

def create_vector_store():
    """Create vector store from knowledge graph data"""
    
    # Initialize Gemini client
    client = Gemini(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # Load knowledge graph data
    with open('data/cs_knowledge_graph.json', 'r') as f:
        data = json.load(f)
    
    # Prepare text chunks for embedding
    chunks = []
    
    # Add course information
    for course_id, course_data in data['courses'].items():
        chunk = {
            'content': f"{course_id} - {course_data['title']} ({course_data['credits']} credits): {course_data['description']}",
            'source': 'course_catalog',
            'course_id': course_id
        }
        chunks.append(chunk)
    
    # Add track information
    for track_name, track_data in data['tracks'].items():
        required_courses = track_data.get('required_courses', [])
        elective_req = track_data.get('elective_requirements', {})
        elective_count = elective_req.get('count', 0)
        
        chunk = {
            'content': f"{track_name} track requires courses: {required_courses} and {elective_count} electives",
            'source': 'track_requirements',
            'track': track_name
        }
        chunks.append(chunk)
    
    # Add prerequisite information
    for course_id, prereqs in data['prerequisites'].items():
        if prereqs:
            chunk = {
                'content': f"{course_id} has prerequisites: {', '.join(prereqs)}",
                'source': 'prerequisites',
                'course_id': course_id
            }
            chunks.append(chunk)
    
    print(f"Creating embeddings for {len(chunks)} text chunks...")
    
    # Create embeddings
    embeddings = []
    for i, chunk in enumerate(chunks):
        try:
            response = client.embeddings.create(
                input=chunk['content'],
                model="text-embedding-3-small"
            )
            embedding = response.data[0].embedding
            embeddings.append(embedding)
            
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(chunks)} chunks")
                
        except Exception as e:
            print(f"Error processing chunk {i}: {e}")
            # Use zero vector as fallback
            embeddings.append([0.0] * 1536)
    
    # Create FAISS index
    embeddings_array = np.array(embeddings, dtype=np.float32)
    dimension = embeddings_array.shape[1]
    
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)
    
    # Save vector store
    os.makedirs('data', exist_ok=True)
    faiss.write_index(index, 'data/vector_store.faiss')
    
    with open('data/chunks.json', 'w') as f:
        json.dump(chunks, f, indent=2)
    
    print(f"✓ Vector store created with {len(chunks)} chunks")
    print(f"✓ Saved to data/vector_store.faiss and data/chunks.json")
    
    return index, chunks

if __name__ == "__main__":
    create_vector_store()