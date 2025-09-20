#!/usr/bin/env python3
"""
Test script for the Purdue CS AI Assistant chatbot
"""

import os
import sys
from complete_replit_deployment import ReplitDeploymentManager

def test_chatbot():
    """Test the chatbot functionality"""
    print("🚀 Testing Purdue CS AI Assistant...")
    print("=" * 50)
    
    try:
        # Create deployment manager
        deployment = ReplitDeploymentManager()
        print("✅ Deployment manager created")
        
        # Initialize system
        if deployment.initialize_system():
            print("✅ System initialized successfully")
            
            # Test query processing
            test_queries = [
                "What are the required courses for MI track?",
                "Tell me about SE track electives",
                "What's the difference between MI and SE tracks?"
            ]
            
            print("\n📝 Testing sample queries:")
            print("-" * 30)
            
            for query in test_queries:
                print(f"\nQ: {query}")
                response = deployment.rg.generate_response(query)
                print(f"A: {response['response'][:200]}...")
                print(f"Confidence: {response['confidence']:.2f}")
                print(f"Track: {response.get('track', 'N/A')}")
                
            print("\n✅ Chatbot test completed successfully!")
            return True
            
        else:
            print("❌ System initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chatbot()
    sys.exit(0 if success else 1)