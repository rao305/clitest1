#!/usr/bin/env python3
"""
Debug script for CLADO integration
"""

import os
import sys

# Test 1: Check feature flags
print("=== Testing Feature Flags ===")
try:
    from feature_flags import is_career_networking_enabled, is_feature_enabled
    print(f"Career networking enabled (method 1): {is_career_networking_enabled()}")
    print(f"Career networking enabled (method 2): {is_feature_enabled('career_networking')}")
except Exception as e:
    print(f"Feature flags error: {e}")

# Test 2: Check career networking import
print("\n=== Testing Career Networking Import ===")
try:
    from career_networking import CareerNetworkingInterface
    print("✅ CareerNetworkingInterface imported successfully")
except Exception as e:
    print(f"❌ CareerNetworkingInterface import failed: {e}")

# Test 3: Check intelligent conversation manager
print("\n=== Testing Intelligent Conversation Manager ===")
try:
    from intelligent_conversation_manager import IntelligentConversationManager
    conv_manager = IntelligentConversationManager()
    print(f"✅ IntelligentConversationManager created")
    print(f"Career networking object: {conv_manager.career_networking}")
    print(f"Career networking type: {type(conv_manager.career_networking)}")
except Exception as e:
    print(f"❌ IntelligentConversationManager error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test actual query processing
print("\n=== Testing Query Processing ===")
try:
    from intelligent_conversation_manager import IntelligentConversationManager
    conv_manager = IntelligentConversationManager()
    
    test_query = "can you find me a recent purdue grad who majored in computer science who landed a role at NVIDIA"
    
    print(f"Testing query: {test_query}")
    print(f"Career networking available: {conv_manager.career_networking is not None}")
    
    if hasattr(conv_manager, '_is_career_networking_query'):
        is_career_query = conv_manager._is_career_networking_query(test_query)
        print(f"Is career networking query: {is_career_query}")
    
    # Try processing the query
    session_id = "debug_session"
    result = conv_manager.process_query(session_id, test_query)
    print(f"✅ Query processed successfully")
    print(f"Result length: {len(result)} characters")
    print(f"Result preview: {result[:200]}...")
    
except Exception as e:
    print(f"❌ Query processing error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Debug Complete ===")