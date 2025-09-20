#!/usr/bin/env python3
"""
Interactive real-world testing - ask actual questions to the hybrid system
"""

import os
import sys
from universal_purdue_advisor import UniversalPurdueAdvisor

def interactive_session():
    """Interactive session with real Gemini API"""
    
    # Check for real API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ Please set your real Gemini API key:")
        print("export GEMINI_API_KEY='sk-your-real-key-here'")
        return
    
    if not api_key.startswith('sk-') or len(api_key) < 40:
        print("⚠️ API key doesn't look like a real Gemini key")
        print("Format should be: sk-...")
        return
    
    print("🤖 Boiler AI - Real Gemini Integration")
    print("=" * 50)
    print(f"✅ API Key: {api_key[:10]}...{api_key[-10:]}")
    
    try:
        advisor = UniversalPurdueAdvisor()
        print("✅ Hybrid AI System initialized with real Gemini")
        print("\n💬 Ask any Purdue CS question (type 'quit' to exit):")
        print("-" * 50)
        
        while True:
            query = input("\n🎓 Your question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not query:
                continue
            
            print(f"\n🔄 Processing: {query}")
            print("-" * 40)
            
            try:
                response = advisor.ask_question(query)
                print(f"\n💬 Response:\n{response}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                print("Please try another question.")
            
            print("\n" + "=" * 50)
    
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        print("Make sure your Gemini API key is valid and has credits.")

if __name__ == "__main__":
    interactive_session()