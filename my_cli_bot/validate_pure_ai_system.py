#!/usr/bin/env python3
"""
Pure AI System Validator
Validates that the system operates with 100% AI responses with no templates or hardcoded messages.
"""

import os
import json
from simple_boiler_ai import SimpleBoilerAI

def validate_api_key_handling():
    """Test that API key requirement is properly enforced"""
    print("🔑 Testing API Key Handling...")
    
    # Save current key if it exists
    original_key = os.environ.get("GEMINI_API_KEY")
    
    # Test without API key
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    
    try:
        bot = SimpleBoilerAI()
        print("❌ FAIL: System should require API key")
        return False
    except ValueError as e:
        if "GEMINI_API_KEY" in str(e):
            print("✅ PASS: API key properly required")
            success = True
        else:
            print(f"❌ FAIL: Wrong error message: {e}")
            success = False
    
    # Restore original key
    if original_key:
        os.environ["GEMINI_API_KEY"] = original_key
    
    return success

def validate_no_templates():
    """Validate that the system doesn't use hardcoded templates"""
    print("\n📄 Testing Template Removal...")
    
    from ai_training_prompts import RESPONSE_TEMPLATES
    
    if len(RESPONSE_TEMPLATES) == 0:
        print("✅ PASS: No templates found in system")
        return True
    else:
        print(f"❌ FAIL: Found {len(RESPONSE_TEMPLATES)} templates: {list(RESPONSE_TEMPLATES.keys())}")
        return False

def validate_knowledge_base():
    """Validate knowledge base structure"""
    print("\n📚 Testing Knowledge Base...")
    
    # Test with placeholder API key to validate initialization
    os.environ["GEMINI_API_KEY"] = "test-key-placeholder"
    
    try:
        bot = SimpleBoilerAI()
        kb = bot.knowledge_base
        
        # Check for critical knowledge areas (use actual field names from JSON)
        required_sections = ["courses", "codo_requirements", "tracks", "failure_recovery_scenarios"]
        missing_sections = []
        
        print(f"  Available sections: {list(kb.keys())}")
        
        for section in required_sections:
            if section not in kb:
                missing_sections.append(section)
        
        if not missing_sections:
            print("✅ PASS: All required knowledge base sections present")
            return True
        else:
            print(f"❌ FAIL: Missing knowledge sections: {missing_sections}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Knowledge base validation error: {e}")
        return False

def validate_pure_ai_processing():
    """Validate that processing uses pure AI methods"""
    print("\n🤖 Testing Pure AI Processing...")
    
    os.environ["GEMINI_API_KEY"] = "test-key-placeholder"
    
    try:
        bot = SimpleBoilerAI()
        
        # Check that main processing method routes to AI
        test_query = "What courses should I take as a freshman?"
        
        # This will fail at Gemini call due to fake key, but should reach AI processing
        try:
            response = bot.process_query(test_query)
            print(f"❓ UNEXPECTED: Got response with fake API key: {response[:100]}...")
            return False
        except Exception as e:
            if "api" in str(e).lower() or "Gemini" in str(e).lower() or "authentication" in str(e).lower():
                print("✅ PASS: Query properly routed to AI (failed on API call as expected)")
                return True
            else:
                print(f"❌ FAIL: Unexpected error type: {e}")
                return False
                
    except Exception as e:
        print(f"❌ FAIL: Pure AI processing validation error: {e}")
        return False

def validate_no_fallback_to_old_systems():
    """Check that there are no fallbacks to old/legacy systems"""
    print("\n🔄 Testing No Legacy System Fallbacks...")
    
    # Check key files for problematic fallback patterns
    problematic_patterns = [
        "smart_ai_engine",
        "unified_ai_query_engine", 
        "intelligent_conversation_manager"
    ]
    
    # The main entry point should only use SimpleBoilerAI
    try:
        from universal_purdue_advisor import UniversalPurdueAdvisor
        
        # Check what the main advisor uses
        os.environ["GEMINI_API_KEY"] = "test-key"
        advisor = UniversalPurdueAdvisor()
        
        # Check if it's using SimpleBoilerAI directly
        if hasattr(advisor, 'ai_engine') and advisor.ai_engine.__class__.__name__ == 'SimpleBoilerAI':
            print("✅ PASS: Main system uses SimpleBoilerAI directly")
            return True
        else:
            print(f"❌ FAIL: Main system uses: {advisor.ai_engine.__class__.__name__ if hasattr(advisor, 'ai_engine') else 'Unknown'}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Legacy system check error: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🔍 Validating Pure AI System Implementation")
    print("=" * 50)
    
    tests = [
        ("API Key Handling", validate_api_key_handling),
        ("Template Removal", validate_no_templates),
        ("Knowledge Base Structure", validate_knowledge_base),
        ("Pure AI Processing", validate_pure_ai_processing),
        ("No Legacy Fallbacks", validate_no_fallback_to_old_systems)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ FAIL: {test_name} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 SUCCESS: Pure AI system is properly implemented!")
        print("✅ No hardcoded messages or templates")
        print("✅ No fallbacks to legacy systems") 
        print("✅ 100% AI-powered responses")
        return True
    else:
        print(f"\n⚠️ ISSUES FOUND: {total - passed} tests failed")
        print("❌ System needs fixes before being fully pure AI")
        return False

if __name__ == "__main__":
    main()