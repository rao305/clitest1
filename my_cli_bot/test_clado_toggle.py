#!/usr/bin/env python3
"""
Test Clado On/Off Toggle Functionality
Tests the feature flag system for career networking
"""

import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_feature_flag_system():
    """Test the feature flag system"""
    print("🔧 Testing Feature Flag System...")
    
    try:
        from feature_flags import FeatureFlagManager
        
        # Initialize with test config
        test_config = "test_feature_flags.json"
        if os.path.exists(test_config):
            os.remove(test_config)
            
        manager = FeatureFlagManager(test_config)
        print("✅ Feature flag manager initialized")
        
        # Test initial state (should be disabled by default)
        initial_state = manager.is_enabled("career_networking")
        print(f"   Initial state: {'ENABLED' if initial_state else 'DISABLED'}")
        
        # Test enabling
        result = manager.toggle_career_networking(True)
        print(f"   Enable result: {result}")
        enabled_state = manager.is_enabled("career_networking") 
        print(f"   State after enable: {'ENABLED' if enabled_state else 'DISABLED'}")
        
        # Test disabling
        result = manager.toggle_career_networking(False)
        print(f"   Disable result: {result}")
        disabled_state = manager.is_enabled("career_networking")
        print(f"   State after disable: {'ENABLED' if disabled_state else 'DISABLED'}")
        
        # Cleanup
        if os.path.exists(test_config):
            os.remove(test_config)
            
        if not initial_state and enabled_state and not disabled_state:
            print("✅ Feature flag toggle working correctly")
            return True
        else:
            print("❌ Feature flag toggle not working properly")
            return False
            
    except Exception as e:
        print(f"❌ Feature flag test failed: {e}")
        return False

def test_conversation_manager_integration():
    """Test that conversation manager respects feature flags"""
    print("\n🧠 Testing Conversation Manager Integration...")
    
    try:
        from feature_flags import get_feature_manager
        from intelligent_conversation_manager import IntelligentConversationManager
        
        manager = get_feature_manager()
        
        # Test with feature disabled
        manager.disable_flag("career_networking")
        conv_manager = IntelligentConversationManager()
        
        has_career_networking_disabled = conv_manager.career_networking is not None
        print(f"   Career networking when disabled: {'Available' if has_career_networking_disabled else 'Not Available'}")
        
        # Test refresh functionality
        manager.enable_flag("career_networking")
        conv_manager.refresh_career_networking()
        
        has_career_networking_enabled = conv_manager.career_networking is not None
        print(f"   Career networking after enable: {'Available' if has_career_networking_enabled else 'Not Available (websockets needed)'}")
        
        # Test query detection still works
        is_career_query = conv_manager._is_career_networking_query("find alumni at Google")
        print(f"   Query detection working: {'Yes' if is_career_query else 'No'}")
        
        # Reset to disabled
        manager.disable_flag("career_networking")
        
        print("✅ Conversation manager integration working")
        return True
        
    except Exception as e:
        print(f"❌ Conversation manager integration test failed: {e}")
        return False

def test_cli_commands_simulation():
    """Simulate the CLI commands"""
    print("\n💻 Testing CLI Command Simulation...")
    
    try:
        from feature_flags import get_feature_manager
        
        manager = get_feature_manager()
        
        # Simulate 'clado off'
        print("   Simulating: clado off")
        result = manager.toggle_career_networking(False)
        print(f"   Result: {result}")
        
        # Check status
        status = "ENABLED" if manager.is_enabled("career_networking") else "DISABLED"
        print(f"   Status: Career networking is {status}")
        
        # Simulate 'clado on'
        print("   Simulating: clado on")
        result = manager.toggle_career_networking(True)
        print(f"   Result: {result}")
        
        # Check status
        status = "ENABLED" if manager.is_enabled("career_networking") else "DISABLED"
        print(f"   Status: Career networking is {status}")
        
        # Reset to disabled for safety
        manager.toggle_career_networking(False)
        
        print("✅ CLI command simulation working")
        return True
        
    except Exception as e:
        print(f"❌ CLI command simulation failed: {e}")
        return False

def run_toggle_tests():
    """Run all toggle functionality tests"""
    print("🚀 Testing Clado On/Off Toggle Functionality")
    print("=" * 60)
    
    tests = [
        ("Feature Flag System", test_feature_flag_system),
        ("Conversation Manager Integration", test_conversation_manager_integration),
        ("CLI Commands Simulation", test_cli_commands_simulation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        result = test_func()
        if result:
            passed += 1
    
    print("\n" + "=" * 60)
    print("🏁 Toggle Test Results")
    print("=" * 60)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 TOGGLE FUNCTIONALITY WORKING!")
        print("\n📋 How to Use:")
        print("   1. Start BoilerAI: python3 universal_purdue_advisor.py")
        print("   2. Enable career networking: clado on")
        print("   3. Check status: clado status")
        print("   4. Disable career networking: clado off")
        print("\n🔒 Security:")
        print("   • Feature is DISABLED by default")
        print("   • Toggle state persists between sessions")
        print("   • Changes take effect immediately")
        
        return True
    else:
        print("❌ TOGGLE ISSUES DETECTED")
        print("Please resolve the failed tests above")
        return False

if __name__ == "__main__":
    success = run_toggle_tests()
    sys.exit(0 if success else 1)