#!/usr/bin/env python3
"""
Setup script for Roo CS Advisor - scrapes data and builds vector store
"""

import os
import sys
from pathlib import Path

def setup_roo():
    """Complete setup process for Roo CS Advisor"""
    
    print("🤖 Setting up Roo - Purdue CS Academic Advisor")
    print("=" * 50)
    
    # Check if Gemini API key is available
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key before running setup")
        sys.exit(1)
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Step 1: Scrape HTML data
    print("\n1. Scraping HTML course data...")
    try:
        from scrape_html import scrape_course_data
        scrape_course_data()
        print("✓ HTML data scraped successfully")
    except Exception as e:
        print(f"✗ Error scraping HTML: {e}")
        print("  Continuing with setup...")
    
    # Step 2: Scrape PDF data  
    print("\n2. Downloading and extracting PDF data...")
    try:
        from scrape_pdfs import download_and_extract_pdfs
        download_and_extract_pdfs()
        print("✓ PDF data extracted successfully")
    except Exception as e:
        print(f"✗ Error processing PDFs: {e}")
        print("  Continuing with setup...")
    
    # Step 3: Normalize data
    print("\n3. Normalizing and chunking data...")
    try:
        from normalize import main as normalize_main
        normalize_main()
        print("✓ Data normalized successfully")
    except Exception as e:
        print(f"✗ Error normalizing data: {e}")
        print("  Continuing with setup...")
    
    # Step 4: Build vector store
    print("\n4. Building vector embeddings...")
    try:
        from build_vector import main as build_vector_main
        build_vector_main()
        print("✓ Vector store built successfully")
    except Exception as e:
        print(f"✗ Error building vector store: {e}")
        print("  Roo will run in basic mode without RAG capabilities")
    
    print("\n" + "=" * 50)
    print("🎉 Roo setup complete!")
    print()
    print("You can now run Roo using:")
    print("  python roo_chat.py")
    print()
    print("Or use the basic version:")
    print("  python chat.py")
    print()

if __name__ == "__main__":
    setup_roo()