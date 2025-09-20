#!/usr/bin/env python3
"""
Normalize and chunk text data for vector embeddings
"""

import json
import os
import re
from pathlib import Path
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def chunk_text(text, ):
    """Chunk text into smaller pieces for embeddings"""
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""
    current_tokens = 0
    
    for sentence in sentences:
        sentence_tokens = len(word_tokenize(sentence))
        
        if current_tokens + sentence_tokens > max_tokens and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
            current_tokens = sentence_tokens
        else:
            current_chunk += " " + sentence
            current_tokens += sentence_tokens
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def normalize_html_data():
    """Normalize HTML scraped course data"""
    chunks = []
    
    if os.path.exists("data/courses_html.csv"):
        df = pd.read_csv("data/courses_html.csv")
        
        for _, row in df.iterrows():
            content = f"Course: {row['code']} - {row['title']}"
            if row['credits']:
                content += f" ({row['credits']} credits)"
            
            chunks.append({
                "content": content,
                "source": row['source'],
                "type": "course_info",
                "course_code": row['code']
            })
    
    return chunks

def normalize_pdf_data():
    """Normalize PDF text data"""
    chunks = []
    pdf_dir = Path("data/pdf")
    
    for txt_file in pdf_dir.glob("*.txt"):
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Clean up text
            text = re.sub(r'\n+', '\n', text)
            text = re.sub(r'\s+', ' ', text)
            
            # Chunk the text
            text_chunks = chunk_text(text)
            
            for i, chunk in enumerate(text_chunks):
                chunks.append({
                    "content": chunk,
                    "source": f"pdf/{txt_file.name}",
                    "type": "degree_guide",
                    "chunk_id": f"{txt_file.stem}_chunk_{i}"
                })
        
        except Exception as e:
            print(f"Error processing {txt_file}: {e}")
    
    return chunks

def main():
    """Main normalization function"""
    print("Normalizing HTML data...")
    html_chunks = normalize_html_data()
    
    print("Normalizing PDF data...")
    pdf_chunks = normalize_pdf_data()
    
    # Combine all chunks
    all_chunks = html_chunks + pdf_chunks
    
    # Save to JSON
    os.makedirs("data", exist_ok=True)
    with open("data/normalized_chunks.json", "w") as f:
        json.dump(all_chunks, f, indent=2)
    
    print(f"Created {len(all_chunks)} normalized chunks")
    print(f"  - HTML chunks: {len(html_chunks)}")
    print(f"  - PDF chunks: {len(pdf_chunks)}")
    
    return all_chunks

if __name__ == "__main__":
    main()