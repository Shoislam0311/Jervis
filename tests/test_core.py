"""
Unit tests for JarvisClone core functionality.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from assistant.core import JarvisCore, MemoryStore, LLMClient


class TestMemoryStore:
    """Test cases for MemoryStore class."""
    
    def test_memory_store_initialization(self):
        """Test MemoryStore initialization."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            memory_file = f.name
        
        try:
            memory = MemoryStore(memory_file)
            assert memory.memory_file == memory_file
            assert "conversations" in memory.memory
            assert "user_preferences" in memory.memory
        finally:
            if os.path.exists(memory_file):
                os.unlink(memory_file)
    
    def test_add_conversation(self):
        """Test adding conversations to memory."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            memory_file = f.name
        
        try:
            memory = MemoryStore(memory_file)
            memory.add_conversation("Hello", "Hi there!")
            
            assert len(memory.memory["conversations"]) == 1
            conv = memory.memory["conversations"][0]
            assert conv["user"] == "Hello"
            assert conv["assistant"] == "Hi there!"
            assert "timestamp" in conv
        finally:
            if os.path.exists(memory_file):
                os.unlink(memory_file)
    
    def test_get_recent_conversations(self):
        """Test retrieving recent conversations."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            memory_file = f.name
        
        try:
            memory = MemoryStore(memory_file)
            
            # Add multiple conversations
            for i in range(15):
                memory.add_conversation(f"Message {i}", f"Response {i}")
            
            recent = memory.get_recent_conversations(5)
            assert len(recent) == 5
            assert recent[-1]["user"] == "Message 14"  # Most recent
        finally:
            if os.path.exists(memory_file):
                os.unlink(memory_file)
    
    def test_user_preferences(self):
        """Test user preference management."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            memory_file = f.name
        
        try:
            memory = MemoryStore(memory_file)
            
            # Set preferences
            memory.set_user_preference("language", "en")
            memory.set_user_preference("voice_enabled", True)
            
            # Get preferences
            assert memory.get_user_preference("language") == "en"
            assert memory.get_user_preference("voice_enabled") is True
            assert memory.get_user_preference("nonexistent", "default") == "default"
        finally:
            if os.path.exists(memory_file):
                os.unlink(memory_file)


class TestLLMClient:
    """Test cases for LLMClient class."""
    
    def test_llm_client_initialization(self):
        """Test LLMClient initialization."""
        client = LLMClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.model == "google/gemma-3n-e4b-it:free"
        assert "Authorization" in client.headers
    
    @patch('requests.post')
    def test_generate_response_success(self, mock_post):
        """Test successful response generation."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Hello! How can I help you?"
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        client = LLMClient(api_key="test_key")
        messages = [{"role": "user", "content": "Hello"}]
        
        response = client.generate_response(messages)
        assert response == "Hello! How can I help you?"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_generate_response_failure(self, mock_post):
        """Test response generation failure."""
        # Mock failed API response
        mock_post.side_effect = Exception("API Error")
        
        client = LLMClient(api_key="test_key")
        messages = [{"role": "user", "content": "Hello"}]
        
        response = client.generate_response(messages)
        assert response is None


class TestJarvisCore:
    """Test cases for JarvisCore class."""
    
    @patch('assistant.core.MemoryStore')
    @patch('assistant.core.LLMClient')
    def test_jarvis_core_initialization(self, mock_llm, mock_memory):
        """Test JarvisCore initialization."""
        jarvis = JarvisCore(api_key="test_key")
        
        mock_memory.assert_called_once()
        mock_llm.assert_called_once_with("test_key")
        assert jarvis.system_prompt is not None
    
    @patch('assistant.core.MemoryStore')
    @patch('assistant.core.LLMClient')
    def test_build_messages(self, mock_llm, mock_memory):
        """Test message building with context."""
        # Mock memory to return some conversations
        mock_memory_instance = Mock()
        mock_memory_instance.get_recent_conversations.return_value = [
            {"user": "Hi", "assistant": "Hello!"}
        ]
        mock_memory.return_value = mock_memory_instance
        
        jarvis = JarvisCore(api_key="test_key")
        messages = jarvis._build_messages("How are you?")
        
        assert len(messages) >= 3  # system + history + current
        assert messages[0]["role"] == "system"
        assert messages[-1]["content"] == "How are you?"
    
    @patch('assistant.core.MemoryStore')
    @patch('assistant.core.LLMClient')
    def test_process_input_success(self, mock_llm, mock_memory):
        """Test successful input processing."""
        # Mock LLM response
        mock_llm_instance = Mock()
        mock_llm_instance.generate_response.return_value = "I'm doing well, thank you!"
        mock_llm.return_value = mock_llm_instance
        
        # Mock memory
        mock_memory_instance = Mock()
        mock_memory_instance.get_recent_conversations.return_value = []
        mock_memory.return_value = mock_memory_instance
        
        jarvis = JarvisCore(api_key="test_key")
        response = jarvis.process_input("How are you?")
        
        assert response == "I'm doing well, thank you!"
        mock_memory_instance.add_conversation.assert_called_once()
    
    @patch('assistant.core.MemoryStore')
    @patch('assistant.core.LLMClient')
    def test_process_input_failure(self, mock_llm, mock_memory):
        """Test input processing failure."""
        # Mock LLM failure
        mock_llm_instance = Mock()
        mock_llm_instance.generate_response.return_value = None
        mock_llm.return_value = mock_llm_instance
        
        # Mock memory
        mock_memory_instance = Mock()
        mock_memory_instance.get_recent_conversations.return_value = []
        mock_memory.return_value = mock_memory_instance
        
        jarvis = JarvisCore(api_key="test_key")
        response = jarvis.process_input("How are you?")
        
        assert "trouble processing" in response.lower()
        mock_memory_instance.add_conversation.assert_called_once()


class TestIntegration:
    """Integration tests for the complete system."""
    
    @patch('assistant.core.LLMClient')
    def test_end_to_end_conversation(self, mock_llm):
        """Test end-to-end conversation flow."""
        # Mock LLM responses
        mock_llm_instance = Mock()
        mock_llm_instance.generate_response.side_effect = [
            "Hello! How can I help you?",
            "The weather is sunny today.",
            "You're welcome!"
        ]
        mock_llm.return_value = mock_llm_instance
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            memory_file = f.name
        
        try:
            # Create JarvisCore with temporary memory
            jarvis = JarvisCore(api_key="test_key")
            jarvis.memory = MemoryStore(memory_file)
            
            # Simulate conversation
            response1 = jarvis.process_input("Hello")
            assert response1 == "Hello! How can I help you?"
            
            response2 = jarvis.process_input("What's the weather?")
            assert response2 == "The weather is sunny today."
            
            response3 = jarvis.process_input("Thank you")
            assert response3 == "You're welcome!"
            
            # Check memory
            conversations = jarvis.memory.get_recent_conversations(10)
            assert len(conversations) == 3
            
        finally:
            if os.path.exists(memory_file):
                os.unlink(memory_file)


# Fixtures for testing
@pytest.fixture
def temp_memory_file():
    """Create a temporary memory file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        yield f.name
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def mock_api_response():
    """Mock API response for testing."""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a test response from the AI."
                }
            }
        ]
    }


# Performance tests
class TestPerformance:
    """Performance tests for JarvisCore."""
    
    def test_memory_performance_with_large_history(self):
        """Test memory performance with large conversation history."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            memory_file = f.name
        
        try:
            memory = MemoryStore(memory_file)
            
            # Add many conversations
            import time
            start_time = time.time()
            
            for i in range(1000):
                memory.add_conversation(f"Message {i}", f"Response {i}")
            
            end_time = time.time()
            
            # Should complete within reasonable time (adjust as needed)
            assert end_time - start_time < 5.0
            
            # Memory should be limited to 50 conversations
            assert len(memory.memory["conversations"]) == 50
            
        finally:
            if os.path.exists(memory_file):
                os.unlink(memory_file)

