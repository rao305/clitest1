#!/usr/bin/env python3
"""
PDF scraping script for Purdue CS degree progression guides
"""

import requests
import pathlib
import subprocess
import json
import os
from pdfminer.high_level import extract_text

# Purdue CS PDF sources
PDFS = {
    "2024_dpg": "https://www.purdue.edu/science/Current_Students/docs/majors/fall2024/computer-science-f24-dpg.pdf",
    "2025_dpg": "https://www.purdue.edu/science/Current_Students/docs/majors/fall2025/computer-science-f25-dpg.pdf",
    "2025_honors_dpg": "https://www.purdue.edu/science/Current_Students/docs/majors/fall2025/computer-science-honors-f25-dpg.pdf",
    "2023_dpg": "https://www.purdue.edu/science/Current_Students/docs/majors/fall2023/Computer%20Science%20F23%20DPG.pdf",
}

def download_and_extract_pdfs():
    """Download PDFs and extract text content"""
    
    # Create directories
    pdf_dir = pathlib.Path("data/pdf")
    pdf_dir.mkdir(parents=True, exist_ok=True)
    
    extracted_texts = {}
    
    for name, url in PDFS.items():
        try:
            print(f"Downloading: {name}")
            pdf_path = pdf_dir / f"{name}.pdf"
            
            # Download PDF
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            pdf_path.write_bytes(response.content)
            
            print(f"Extracting text from: {name}")
            # Extract text using pdfminer
            text = extract_text(str(pdf_path))
            
            # Save extracted text
            txt_path = pdf_dir / f"{name}.txt"
            txt_path.write_text(text, encoding='utf-8')
            
            extracted_texts[name] = text
            
        except Exception as e:
            print(f"Error processing {name}: {e}")
    
    # Save metadata
    metadata = {
        "sources": PDFS,
        "extracted_count": len(extracted_texts),
        "files": list(extracted_texts.keys())
    }
    
    with open("data/pdf_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Extracted text from {len(extracted_texts)} PDFs")
    return extracted_texts

if __name__ == "__main__":
    download_and_extract_pdfs()