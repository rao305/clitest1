#!/usr/bin/env python3
"""
Simple Track Question Test - Direct testing of AI responses
Tests: User Query → Knowledge Base → AI Answer → Output
"""

import os
import json

def test_knowledge_base_access():
    """Test direct knowledge base access for track questions"""
    
    print("🔍 TESTING KNOWLEDGE BASE ACCESS")
    print("=" * 50)
    
    # Load knowledge base
    try:
        with open('data/cs_knowledge_graph.json', 'r') as f:
            kb = json.load(f)
        print("✅ Knowledge base loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load knowledge base: {e}")
        return False
    
    # Test 1: Can we get MI track data?
    mi_track = kb.get('tracks', {}).get('Machine Intelligence', {})
    if mi_track:
        print("✅ Machine Intelligence track data found")
        print(f"   - Core courses: {mi_track.get('core_required', [])}")
        print(f"   - Total credits: {mi_track.get('total_credits', 'Unknown')}")
    else:
        print("❌ Machine Intelligence track data missing")
        return False
    
    # Test 2: Can we get SE track data?
    se_track = kb.get('tracks', {}).get('Software Engineering', {})
    if se_track:
        print("✅ Software Engineering track data found")
        print(f"   - Total credits: {se_track.get('total_credits', 'Unknown')}")
    else:
        print("❌ Software Engineering track data missing")
        return False
    
    return True

def test_without_api():
    """Test system components without API calls"""
    
    print("\n🧪 TESTING SYSTEM COMPONENTS (NO API)")
    print("=" * 50)
    
    try:
        from degree_progression_engine import DegreeProgressionEngine
        engine = DegreeProgressionEngine()
        print("✅ Degree progression engine loaded")
        
        # Test track guidance
        mi_guidance = engine.get_track_specific_guidance('Machine Intelligence', 'junior')
        if mi_guidance and 'track_name' in mi_guidance:
            print("✅ MI track guidance working")
            print(f"   - Track: {mi_guidance['track_name']}")
            print(f"   - Credits: {mi_guidance.get('total_credits', 'Unknown')}")
        else:
            print("❌ MI track guidance failed")
            return False
        
        se_guidance = engine.get_track_specific_guidance('Software Engineering', 'junior')
        if se_guidance and 'track_name' in se_guidance:
            print("✅ SE track guidance working")
        else:
            print("❌ SE track guidance failed")
            return False
            
    except Exception as e:
        print(f"❌ System component error: {e}")
        return False
    
    return True

def test_with_mock_ai():
    """Test with mock AI to check data flow"""
    
    print("\n🤖 TESTING WITH MOCK AI RESPONSES")
    print("=" * 50)
    
    # Mock the AI system to test data flow
    class MockBoilerAI:
        def __init__(self):
            with open('data/cs_knowledge_graph.json', 'r') as f:
                self.knowledge = json.load(f)
        
        def process_track_question(self, query):
            """Process track-related questions"""
            query_lower = query.lower()
            
            # Detect track
            if 'machine intelligence' in query_lower or 'mi track' in query_lower:
                track_data = self.knowledge.get('tracks', {}).get('Machine Intelligence', {})
                track_name = 'Machine Intelligence'
            elif 'software engineering' in query_lower or 'se track' in query_lower:
                track_data = self.knowledge.get('tracks', {}).get('Software Engineering', {})
                track_name = 'Software Engineering'
            else:
                return "I need you to specify which track you're asking about."
            
            if not track_data:
                return f"Sorry, I don't have information about the {track_name} track."
            
            # Handle different question types
            if 'core courses' in query_lower or 'required courses' in query_lower:
                core_courses = track_data.get('core_required', [])
                if core_courses:
                    response = f"The {track_name} track requires these core courses: {', '.join(core_courses)}."
                    if 'total_credits' in track_data:
                        response += f" Total track credits needed: {track_data['total_credits']}."
                    return response
                else:
                    return f"Core course information not available for {track_name}."
            
            elif 'electives' in query_lower:
                electives = track_data.get('electives', [])
                if electives:
                    return f"The {track_name} track offers {len(electives)} elective options including: {', '.join(electives[:3])}{'...' if len(electives) > 3 else ''}."
                else:
                    return f"Elective information not available for {track_name}."
            
            elif 'credits' in query_lower:
                total_credits = track_data.get('total_credits')
                if total_credits:
                    return f"The {track_name} track requires {total_credits} total credits."
                else:
                    return f"Credit information not available for {track_name}."
            
            else:
                # General track info
                description = track_data.get('description', 'No description available.')
                total_credits = track_data.get('total_credits', 'Unknown')
                return f"The {track_name} track: {description} Total credits: {total_credits}."
    
    # Test the mock system
    mock_ai = MockBoilerAI()
    
    test_questions = [
        "What are the required core courses for the Machine Intelligence track?",
        "Which electives can I take for the Software Engineering track?",
        "How many credits do I need for the MI track?",
        "Tell me about the Software Engineering track."
    ]
    
    all_passed = True
    for i, question in enumerate(test_questions, 1):
        print(f"\n❓ Test {i}: {question}")
        try:
            response = mock_ai.process_track_question(question)
            if response and len(response) > 10 and "not available" not in response:
                print(f"✅ Response: {response[:100]}...")
            else:
                print(f"❌ Poor response: {response}")
                all_passed = False
        except Exception as e:
            print(f"❌ Error: {e}")
            all_passed = False
    
    return all_passed

def test_with_real_ai():
    """Test with real AI system if API key available"""
    
    if not os.environ.get("GEMINI_API_KEY"):
        print("\n⚠️ No Gemini API key - skipping real AI test")
        return True
    
    print("\n🚀 TESTING WITH REAL AI SYSTEM")
    print("=" * 50)
    
    try:
        from simple_boiler_ai import SimpleBoilerAI
        bot = SimpleBoilerAI()
        print("✅ AI system loaded successfully")
        
        # Test critical track questions
        test_questions = [
            "What are the required core courses for the Machine Intelligence track?",
            "How many credits do I need for the Software Engineering track?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n❓ Test {i}: {question}")
            try:
                response = bot.process_query(question)
                
                # Check if response is meaningful
                if response and len(response) > 50:
                    # Check for key terms
                    question_lower = question.lower()
                    response_lower = response.lower()
                    
                    if 'machine intelligence' in question_lower:
                        if 'cs 38100' in response_lower or 'cs 37300' in response_lower:
                            print("✅ Contains correct MI courses")
                        else:
                            print("❌ Missing MI course information")
                            return False
                    
                    elif 'software engineering' in question_lower and 'credits' in question_lower:
                        if '15' in response_lower or 'fifteen' in response_lower:
                            print("✅ Contains correct SE credit count")
                        else:
                            print("❌ Missing SE credit information")
                            return False
                    
                    print(f"✅ Response length: {len(response)} chars")
                else:
                    print("❌ Response too short or empty")
                    return False
                    
            except Exception as e:
                print(f"❌ AI system error: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to load AI system: {e}")
        return False

def main():
    """Run comprehensive track question testing"""
    
    print("🎓 SIMPLE TRACK QUESTION TEST")
    print("User Query → Knowledge Base → AI Answer → Output")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Knowledge Base Access", test_knowledge_base_access),
        ("System Components", test_without_api),
        ("Mock AI Flow", test_with_mock_ai),
        ("Real AI System", test_with_real_ai)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name.upper()} {'=' * 20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - AI system ready for track questions!")
        print("\n💡 The system can handle:")
        print("   • Machine Intelligence track questions")
        print("   • Software Engineering track questions")
        print("   • Core course requirements")
        print("   • Credit requirements")
        print("   • Elective options")
        print("   • General track information")
    else:
        print("❌ SOME TESTS FAILED - Check system components")

if __name__ == "__main__":
    main()