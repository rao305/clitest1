#!/usr/bin/env python3
"""
Test script for Roo CS Advisor
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from roo_engine import RooCSAdvisor

def test_roo_initialization():
    """Test that Roo initializes correctly with mocked dependencies"""
    with patch('roo_engine.Gemini') as mock_Gemini:
        with patch('builtins.open', mock_open(read_data="Test system prompt")):
            with patch('roo_engine.os.path.exists', return_value=False):
                roo = RooCSAdvisor(api_key="test-key")
                assert roo.api_key == "test-key"
                assert roo.vector_store == False

def test_basic_query_responses():
    """Test basic query responses without vector store"""
    system_prompt = """You are Roo_CS_Advisor, a Purdue-specific academic-planning assistant.
    
    SCOPE
    • Answer ONLY questions about the Purdue University Computer Science bachelor's curriculum
    
    STYLE
    • Use a friendly yet concise tone
    • Always prepend "Bot> " before your reply text
    """
    
    with patch('roo_engine.Gemini') as mock_Gemini:
        with patch('builtins.open', mock_open(read_data=system_prompt)):
            with patch('roo_engine.os.path.exists', return_value=False):
                # Mock Gemini response
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.text = "Bot> CS 18000, 18200, 24000, 25000, 25100, 25200 are the six core courses."
                
                mock_client = MagicMock()
                mock_client.chat.completions.create.return_value = mock_response
                mock_Gemini.return_value = mock_client
                
                roo = RooCSAdvisor(api_key="test-key")
                response = roo.generate_response("What are the six core CS courses?", [])
                
                assert "Bot>" in response
                assert "CS 18000" in response or "six core" in response

def test_out_of_scope_queries():
    """Test that out-of-scope queries are handled appropriately"""
    system_prompt = """You are Roo_CS_Advisor, a Purdue-specific academic-planning assistant.
    
    POLICIES
    1. If a user asks outside-scope (e.g., ME degree rules), reply:
       "Bot> I specialize in Purdue CS requirements. Try Purdue's general advisor for that topic."
    """
    
    with patch('roo_engine.Gemini') as mock_Gemini:
        with patch('builtins.open', mock_open(read_data=system_prompt)):
            with patch('roo_engine.os.path.exists', return_value=False):
                # Mock Gemini response for out-of-scope query
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.text = "Bot> I specialize in Purdue CS requirements. Try Purdue's general advisor for that topic."
                
                mock_client = MagicMock()
                mock_client.chat.completions.create.return_value = mock_response
                mock_Gemini.return_value = mock_client
                
                roo = RooCSAdvisor(api_key="test-key")
                response = roo.generate_response("What are the ME degree requirements?", [])
                
                assert "specialize in Purdue CS" in response

def mock_open(read_data):
    """Helper function to create mock file open"""
    from unittest.mock import mock_open as _mock_open
    return _mock_open(read_data=read_data)

if __name__ == "__main__":
    # Run basic tests
    print("Running Roo CS Advisor tests...")
    
    try:
        test_roo_initialization()
        print("✓ Initialization test passed")
    except Exception as e:
        print(f"✗ Initialization test failed: {e}")
    
    try:
        test_basic_query_responses()
        print("✓ Basic query test passed")
    except Exception as e:
        print(f"✗ Basic query test failed: {e}")
    
    try:
        test_out_of_scope_queries()
        print("✓ Out-of-scope query test passed")
    except Exception as e:
        print(f"✗ Out-of-scope query test failed: {e}")
    
    print("\nTest summary complete!")