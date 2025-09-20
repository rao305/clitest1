#!/usr/bin/env python3
"""
Interactive test for the Purdue CS AI Assistant chatbot
"""

import sys
from knowledge_graph_system import initialize_system, PurdueDataLoader

def interactive_test():
    """Interactive test of the chatbot"""
    print("🎓 Purdue CS AI Assistant - Interactive Test")
    print("=" * 50)
    
    try:
        # Initialize system
        print("Initializing system...")
        kg, rg, n8n = initialize_system()
        print("✅ System initialized")
        
        # Load track data
        print("Loading track data...")
        loader = PurdueDataLoader(kg)
        
        print("Loading MI track...")
        mi_loaded = loader.load_machine_intelligence_track()
        print(f"MI track loaded: {mi_loaded}")
        
        print("Loading SE track...")
        se_loaded = loader.load_software_engineering_track() 
        print(f"SE track loaded: {se_loaded}")
        
        print("\n📊 System ready for queries!")
        print("-" * 30)
        
        # Interactive query loop
        while True:
            query = input("\n🤖 Ask me about Purdue CS tracks (or 'quit' to exit): ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
                
            if not query:
                continue
                
            print(f"\n💭 Processing: {query}")
            response = rg.generate_response(query)
            
            print(f"\n📝 Response:")
            print(f"{response['response']}")
            print(f"\n📊 Confidence: {response['confidence']:.2f}")
            print(f"🎯 Track Context: {response.get('track', 'General')}")
            print(f"🔍 Source: {response.get('source', 'Unknown')}")
            
        print("\n👋 Thanks for testing the Purdue CS AI Assistant!")
        return True
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = interactive_test()
    sys.exit(0 if success else 1)