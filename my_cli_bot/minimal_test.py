#!/usr/bin/env python3
"""
Minimal test for the knowledge graph system
"""

import sys
import traceback

def minimal_test():
    """Minimal test to identify issues"""
    try:
        print("Step 1: Testing knowledge graph initialization...")
        from knowledge_graph_system import KnowledgeGraph
        kg = KnowledgeGraph()
        print("✅ Knowledge graph created")
        
        print("Step 2: Testing response generator...")
        from knowledge_graph_system import DynamicResponseGenerator
        rg = DynamicResponseGenerator(kg)
        print("✅ Response generator created")
        
        print("Step 3: Testing a simple query...")
        response = rg.generate_response("Hello")
        print(f"✅ Query processed: {response['response'][:100]}...")
        
        print("Step 4: Testing MI scraper...")
        from mi_track_scraper import PurdueMITrackScraper
        mi_scraper = PurdueMITrackScraper()
        print("✅ MI scraper created")
        
        print("Step 5: Testing SE scraper...")  
        from se_track_scraper import PurdueSETrackScraper
        se_scraper = PurdueSETrackScraper()
        print("✅ SE scraper created")
        
        print("\n🎉 All components working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = minimal_test()
    sys.exit(0 if success else 1)