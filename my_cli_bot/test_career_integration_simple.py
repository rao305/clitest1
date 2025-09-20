#!/usr/bin/env python3
"""
Simple Career Networking Integration Test
Tests integration without requiring websockets dependency
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_conversation_manager_integration():
    """Test that career networking is integrated into conversation manager"""
    print("🔍 Testing Career Networking Integration...")
    
    try:
        from intelligent_conversation_manager import IntelligentConversationManager
        
        # Initialize conversation manager
        manager = IntelligentConversationManager()
        print("✅ Conversation manager initialized")
        
        # Test intent pattern detection
        career_queries = [
            "alumni working at Microsoft",
            "find professionals in my field", 
            "networking opportunities",
            "mentorship in software engineering",
            "purdue graduates in AI",
            "connect with professionals",
            "people working at Google"
        ]
        
        detected_count = 0
        for query in career_queries:
            is_career_query = manager._is_career_networking_query(query)
            status = "✅" if is_career_query else "❌"
            print(f"   {status} '{query}' -> Career query: {is_career_query}")
            if is_career_query:
                detected_count += 1
        
        if detected_count >= 5:
            print(f"✅ Career query detection working ({detected_count}/7 detected)")
            return True
        else:
            print(f"❌ Career query detection needs improvement ({detected_count}/7 detected)")
            return False
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_ai_prompts():
    """Test AI training prompts include career networking"""
    print("\n🔍 Testing AI Training Prompts...")
    
    try:
        from ai_training_prompts import get_comprehensive_system_prompt
        
        system_prompt = get_comprehensive_system_prompt()
        
        # Check for career networking content
        career_content_checks = [
            ("Career Networking", "7. **Career Networking & Professional Connections**" in system_prompt),
            ("Alumni Discovery", "alumni" in system_prompt.lower()),
            ("Professional Search", "professionals" in system_prompt.lower()),
            ("Mentorship", "mentorship" in system_prompt.lower()),
            ("Query Patterns", "CAREER NETWORKING QUERY PATTERNS:" in system_prompt)
        ]
        
        passed_checks = 0
        for check_name, result in career_content_checks:
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}: {'Found' if result else 'Missing'}")
            if result:
                passed_checks += 1
        
        if passed_checks >= 4:
            print(f"✅ AI prompts properly configured ({passed_checks}/5 checks passed)")
            return True
        else:
            print(f"❌ AI prompts missing career content ({passed_checks}/5 checks passed)")
            return False
        
    except Exception as e:
        print(f"❌ AI prompts test failed: {e}")
        return False

def test_intent_patterns():
    """Test intent patterns are properly configured"""
    print("\n🔍 Testing Intent Pattern Configuration...")
    
    try:
        from intelligent_conversation_manager import IntelligentConversationManager
        
        manager = IntelligentConversationManager()
        
        # Check if career_networking patterns exist
        if "career_networking" in manager.intent_patterns:
            patterns = manager.intent_patterns["career_networking"]
            print(f"✅ Career networking patterns found: {len(patterns)} patterns")
            
            expected_patterns = ["alumni", "professionals", "mentor", "networking", "connect"]
            found_patterns = 0
            
            for expected in expected_patterns:
                # Check if any pattern contains the expected keyword
                found = any(expected in pattern for pattern in patterns)
                status = "✅" if found else "❌"
                print(f"   {status} Pattern contains '{expected}': {found}")
                if found:
                    found_patterns += 1
            
            if found_patterns >= 4:
                print(f"✅ Intent patterns properly configured ({found_patterns}/5 found)")
                return True
            else:
                print(f"❌ Intent patterns incomplete ({found_patterns}/5 found)")
                return False
        else:
            print("❌ Career networking intent patterns not found")
            return False
        
    except Exception as e:
        print(f"❌ Intent patterns test failed: {e}")
        return False

def test_career_module_structure():
    """Test career networking module structure"""
    print("\n🔍 Testing Career Module Structure...")
    
    try:
        # Test that module can be imported (even if websockets not available)
        module_file = "career_networking.py"
        if os.path.exists(module_file):
            print("✅ Career networking module file exists")
            
            # Read and check module structure
            with open(module_file, 'r') as f:
                content = f.read()
            
            structure_checks = [
                ("CareerNetworkingInterface", "class CareerNetworkingInterface" in content),
                ("CladoAPIClient", "class CladoAPIClient" in content),
                ("WebSocket Support", "websockets" in content),
                ("Student Context", "student_context" in content),
                ("Query Processing", "process_career_query" in content)
            ]
            
            passed_checks = 0
            for check_name, result in structure_checks:
                status = "✅" if result else "❌"
                print(f"   {status} {check_name}: {'Found' if result else 'Missing'}")
                if result:
                    passed_checks += 1
            
            if passed_checks >= 4:
                print(f"✅ Module structure complete ({passed_checks}/5 components)")
                return True
            else:
                print(f"❌ Module structure incomplete ({passed_checks}/5 components)") 
                return False
        else:
            print("❌ Career networking module file not found")
            return False
        
    except Exception as e:
        print(f"❌ Module structure test failed: {e}")
        return False

def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Career Networking Integration Validation")
    print("=" * 50)
    print("Testing core integration without external dependencies")
    print()
    
    tests = [
        ("Conversation Manager Integration", test_conversation_manager_integration),
        ("AI Training Prompts", test_ai_prompts),
        ("Intent Pattern Configuration", test_intent_patterns), 
        ("Career Module Structure", test_career_module_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        result = test_func()
        if result:
            passed += 1
    
    print("\n" + "=" * 50)
    print("🏁 Integration Test Results")
    print("=" * 50)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 INTEGRATION SUCCESSFUL!")
        print("\n✨ Career Networking Features:")
        print("   ✅ Query detection and routing")
        print("   ✅ AI training and prompts")
        print("   ✅ Intent pattern matching")
        print("   ✅ Module structure complete")
        print("\n📋 Next Steps:")
        print("   1. Install websockets: pip install websockets")
        print("   2. Test with live API calls")
        print("   3. Deploy to production")
        print("\n💬 Example Queries:")
        print("   • 'Find Purdue CS alumni at Google'")
        print("   • 'Connect me with ML professionals'")
        print("   • 'I need mentors in software engineering'")
        
        return True
    else:
        print("❌ INTEGRATION ISSUES DETECTED")
        print("Please resolve the failed tests above")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)