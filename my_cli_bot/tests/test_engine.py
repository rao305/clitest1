import pytest
from unittest.mock import patch, mock_open, MagicMock
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_engine import ChatEngine

class TestChatEngine:
    """Test suite for ChatEngine class"""
    
    @pytest.fixture
    def mock_system_prompt(self):
        """Mock system prompt content"""
        return "You are a test bot. Always respond with 'Bot> ' prefix."
    
    @pytest.fixture
    def mock_Gemini_response(self):
        """Mock Gemini API response"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.text = "Bot> Hello there!"
        return mock_response
    
    @pytest.fixture
    def engine(self, mock_system_prompt, mock_Gemini_response):
        """Create a ChatEngine instance with mocked dependencies"""
        with patch('builtins.open', mock_open(read_data=mock_system_prompt)):
            with patch('llm_engine.Gemini') as mock_Gemini:
                mock_client = MagicMock()
                mock_client.chat.completions.create.return_value = mock_Gemini_response
                mock_Gemini.return_value = mock_client
                
                return ChatEngine(api_key="test-key")
    
    def test_initialization_with_api_key(self, mock_system_prompt):
        """Test ChatEngine initialization with API key"""
        with patch('builtins.open', mock_open(read_data=mock_system_prompt)):
            with patch('llm_engine.Gemini') as mock_Gemini:
                engine = ChatEngine(api_key="test-key")
                assert engine.api_key == "test-key"
                assert engine.system == mock_system_prompt
                mock_Gemini.assert_called_once_with(api_key="test-key")
    
    def test_initialization_with_env_var(self, mock_system_prompt):
        """Test ChatEngine initialization with environment variable"""
        with patch('builtins.open', mock_open(read_data=mock_system_prompt)):
            with patch('llm_engine.Gemini') as mock_Gemini:
                with patch.dict(os.environ, {'GEMINI_API_KEY': 'env-key'}):
                    engine = ChatEngine()
                    assert engine.api_key == "env-key"
                    mock_Gemini.assert_called_once_with(api_key="env-key")
    
    def test_initialization_no_api_key(self, mock_system_prompt):
        """Test ChatEngine initialization without API key raises ValueError"""
        with patch('builtins.open', mock_open(read_data=mock_system_prompt)):
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(ValueError, match="Gemini API key is required"):
                    ChatEngine()
    
    def test_initialization_missing_system_prompt(self):
        """Test ChatEngine initialization with missing system prompt file"""
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            with pytest.raises(FileNotFoundError, match="System prompt file not found"):
                ChatEngine(api_key="test-key")
    
    def test_generate_basic_response(self, engine):
        """Test basic response generation"""
        history = [{"role": "user", "content": "Hi"}]
        response = engine.generate(history)
        assert response == "Bot> Hello there!"
    
    def test_generate_with_system_prompt(self, engine):
        """Test that system prompt is included in API call"""
        history = [{"role": "user", "content": "Hi"}]
        engine.generate(history)
        
        # Check that the API was called with system prompt
        engine.client.chat.completions.create.assert_called_once()
        call_args = engine.client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[1]['role'] == 'user'
        assert messages[1]['content'] == 'Hi'
    
    def test_generate_with_api_error(self, engine):
        """Test error handling when API call fails"""
        engine.client.chat.completions.create.side_effect = Exception("API Error")
        
        history = [{"role": "user", "content": "Hi"}]
        response = engine.generate(history)
        
        assert response.startswith("Bot> I'm sorry, I encountered an error:")
    
    def test_generate_uses_correct_model(self, engine):
        """Test that the correct Gemini model is used"""
        history = [{"role": "user", "content": "Hi"}]
        engine.generate(history)
        
        call_args = engine.client.chat.completions.create.call_args
        assert call_args[1]['model'] == 'Gemini-4o'
    
    def test_generate_parameters(self, engine):
        """Test that correct parameters are passed to Gemini API"""
        history = [{"role": "user", "content": "Hi"}]
        engine.generate(history)
        
        call_args = engine.client.chat.completions.create.call_args
        assert call_args[1]['temperature'] == 0.7
        assert call_args[1]['max_tokens'] == 512
    
    def test_history_summarization(self, engine, mock_system_prompt):
        """Test history summarization when history gets too long"""
        # Create a long history (> 20 messages)
        long_history = []
        for i in range(25):
            long_history.append({"role": "user", "content": f"Message {i}"})
            long_history.append({"role": "assistant", "content": f"Response {i}"})
        
        engine.generate(long_history)
        
        # Verify that summarization was triggered
        call_args = engine.client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        
        # Should have system prompt + summary + recent messages
        assert len(messages) < len(long_history) + 1  # +1 for system prompt
        
        # First message should be system prompt
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == mock_system_prompt
    
    def test_summarize_history_method(self, engine):
        """Test the _summarize_history method directly"""
        # Create history with 15 messages
        history = []
        for i in range(15):
            history.append({"role": "user", "content": f"User message {i}"})
        
        summarized = engine._summarize_history(history)
        
        # Should have 1 summary message + 10 recent messages
        assert len(summarized) == 11
        assert summarized[0]['role'] == 'system'
        assert 'Previous conversation summary' in summarized[0]['content']
        
        # Last 10 messages should be preserved
        for i, msg in enumerate(summarized[1:], 5):
            assert msg['content'] == f"User message {i}"
    
    def test_summarize_history_short_history(self, engine):
        """Test that short history is not summarized"""
        history = [{"role": "user", "content": "Short history"}]
        summarized = engine._summarize_history(history)
        
        # Should return original history unchanged
        assert summarized == history
