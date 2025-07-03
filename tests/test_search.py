"""
Unit tests for JarvisClone search functionality.
"""

import pytest
import json
from unittest.mock import Mock, patch
from assistant.search import WebSearcher


class TestWebSearcher:
    """Test cases for WebSearcher class."""
    
    def test_web_searcher_initialization(self):
        """Test WebSearcher initialization."""
        searcher = WebSearcher()
        assert searcher.base_url == "https://api.duckduckgo.com/"
        assert searcher.session is not None
        assert "User-Agent" in searcher.session.headers
    
    @patch('requests.Session.get')
    def test_search_with_instant_answer(self, mock_get):
        """Test search with instant answer response."""
        # Mock DuckDuckGo API response with instant answer
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Answer": "Python is a programming language",
            "AnswerType": "definition",
            "Abstract": "Python is a high-level programming language",
            "AbstractURL": "https://python.org"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        searcher = WebSearcher()
        result = searcher.search("Python programming")
        
        assert result is not None
        assert "Python is a programming language" in result
        assert "https://python.org" in result
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_search_with_related_topics(self, mock_get):
        """Test search with related topics response."""
        # Mock DuckDuckGo API response with related topics
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "RelatedTopics": [
                {
                    "Text": "Python is a programming language",
                    "FirstURL": "https://python.org"
                },
                {
                    "Text": "Python syntax is easy to learn",
                    "FirstURL": "https://docs.python.org"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        searcher = WebSearcher()
        result = searcher.search("Python programming", max_results=2)
        
        assert result is not None
        assert "Related Information:" in result
        assert "Python is a programming language" in result
        assert "Python syntax is easy to learn" in result
    
    @patch('requests.Session.get')
    def test_search_with_definition(self, mock_get):
        """Test search with definition response."""
        # Mock DuckDuckGo API response with definition
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Definition": "Artificial Intelligence (AI) is intelligence demonstrated by machines",
            "DefinitionURL": "https://en.wikipedia.org/wiki/Artificial_intelligence"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        searcher = WebSearcher()
        result = searcher.search("define artificial intelligence")
        
        assert result is not None
        assert "Definition:" in result
        assert "intelligence demonstrated by machines" in result
        assert "wikipedia.org" in result
    
    @patch('requests.Session.get')
    def test_search_with_infobox(self, mock_get):
        """Test search with infobox response."""
        # Mock DuckDuckGo API response with infobox
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Infobox": {
                "content": [
                    {"label": "Founded", "value": "1991"},
                    {"label": "Creator", "value": "Guido van Rossum"},
                    {"label": "Type", "value": "Programming Language"}
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        searcher = WebSearcher()
        result = searcher.search("Python programming language")
        
        assert result is not None
        assert "Additional Information:" in result
        assert "Founded: 1991" in result
        assert "Creator: Guido van Rossum" in result
    
    @patch('requests.Session.get')
    def test_search_empty_response(self, mock_get):
        """Test search with empty response."""
        # Mock DuckDuckGo API response with no useful data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        searcher = WebSearcher()
        result = searcher.search("nonexistent query")
        
        # Should fall back to web search
        assert result is not None
        assert "Web search performed" in result
    
    @patch('requests.Session.get')
    def test_search_network_error(self, mock_get):
        """Test search with network error."""
        # Mock network error
        mock_get.side_effect = Exception("Network error")
        
        searcher = WebSearcher()
        result = searcher.search("test query")
        
        assert result is None
    
    @patch('requests.Session.get')
    def test_search_json_decode_error(self, mock_get):
        """Test search with JSON decode error."""
        # Mock invalid JSON response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        searcher = WebSearcher()
        result = searcher.search("test query")
        
        assert result is None
    
    @patch('requests.Session.get')
    def test_get_news(self, mock_get):
        """Test news retrieval functionality."""
        # Mock news response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "RelatedTopics": [
                {
                    "Text": "Latest technology news: AI breakthrough",
                    "FirstURL": "https://news.example.com/ai-breakthrough"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        searcher = WebSearcher()
        result = searcher.get_news("technology")
        
        assert result is not None
        assert "AI breakthrough" in result
        
        # Check that the correct query was made
        call_args = mock_get.call_args
        assert "technology news latest" in str(call_args)
    
    @patch('requests.Session.get')
    def test_get_weather(self, mock_get):
        """Test weather retrieval functionality."""
        # Mock weather response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Answer": "Weather in New York: 72°F, Sunny"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        searcher = WebSearcher()
        result = searcher.get_weather("New York")
        
        assert result is not None
        assert "72°F" in result
        assert "Sunny" in result
        
        # Check that the correct query was made
        call_args = mock_get.call_args
        assert "weather New York" in str(call_args)
    
    @patch('requests.Session.get')
    def test_get_definition(self, mock_get):
        """Test definition retrieval functionality."""
        # Mock definition response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Definition": "Machine Learning is a subset of artificial intelligence",
            "DefinitionURL": "https://en.wikipedia.org/wiki/Machine_learning"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        searcher = WebSearcher()
        result = searcher.get_definition("machine learning")
        
        assert result is not None
        assert "subset of artificial intelligence" in result
        assert "wikipedia.org" in result
        
        # Check that the correct query was made
        call_args = mock_get.call_args
        assert "define machine learning" in str(call_args)
    
    def test_format_results_comprehensive(self):
        """Test comprehensive result formatting."""
        searcher = WebSearcher()
        
        # Test data with all possible fields
        test_data = {
            "Answer": "Test answer",
            "Abstract": "Test abstract",
            "AbstractURL": "https://test.com/abstract",
            "Definition": "Test definition",
            "DefinitionURL": "https://test.com/definition",
            "RelatedTopics": [
                {
                    "Text": "Related topic 1",
                    "FirstURL": "https://test.com/topic1"
                },
                {
                    "Text": "Related topic 2",
                    "FirstURL": "https://test.com/topic2"
                }
            ],
            "Infobox": {
                "content": [
                    {"label": "Label 1", "value": "Value 1"},
                    {"label": "Label 2", "value": "Value 2"}
                ]
            }
        }
        
        result = searcher._format_results(test_data, 5)
        
        assert result is not None
        assert "Answer: Test answer" in result
        assert "Summary: Test abstract" in result
        assert "Definition: Test definition" in result
        assert "Related Information:" in result
        assert "Related topic 1" in result
        assert "Additional Information:" in result
        assert "Label 1: Value 1" in result
    
    def test_format_results_empty(self):
        """Test formatting with empty data."""
        searcher = WebSearcher()
        result = searcher._format_results({}, 5)
        assert result is None
    
    def test_format_results_partial(self):
        """Test formatting with partial data."""
        searcher = WebSearcher()
        
        test_data = {
            "Answer": "Partial answer only"
        }
        
        result = searcher._format_results(test_data, 5)
        assert result == "Answer: Partial answer only"


class TestSearchIntegration:
    """Integration tests for search functionality."""
    
    @patch('requests.Session.get')
    def test_search_integration_with_core(self, mock_get):
        """Test search integration with JarvisCore."""
        from assistant.core import JarvisCore
        
        # Mock search response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Answer": "Python is a programming language"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock LLM response
        with patch('assistant.core.LLMClient') as mock_llm:
            mock_llm_instance = Mock()
            mock_llm_instance.generate_response.return_value = "Based on the search results, Python is indeed a programming language."
            mock_llm.return_value = mock_llm_instance
            
            jarvis = JarvisCore(api_key="test_key")
            
            # Test search-triggering query
            response = jarvis.process_input("search for Python programming")
            
            assert response == "Based on the search results, Python is indeed a programming language."
            mock_get.assert_called_once()


# Performance tests
class TestSearchPerformance:
    """Performance tests for search functionality."""
    
    @patch('requests.Session.get')
    def test_search_timeout_handling(self, mock_get):
        """Test search timeout handling."""
        import requests
        
        # Mock timeout
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        searcher = WebSearcher()
        result = searcher.search("test query")
        
        assert result is None
    
    @patch('requests.Session.get')
    def test_multiple_searches_performance(self, mock_get):
        """Test performance with multiple searches."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Answer": "Test answer"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        searcher = WebSearcher()
        
        import time
        start_time = time.time()
        
        # Perform multiple searches
        for i in range(10):
            result = searcher.search(f"test query {i}")
            assert result is not None
        
        end_time = time.time()
        
        # Should complete within reasonable time
        assert end_time - start_time < 2.0  # Adjust as needed
        assert mock_get.call_count == 10


# Fixtures for testing
@pytest.fixture
def sample_duckduckgo_response():
    """Sample DuckDuckGo API response for testing."""
    return {
        "Answer": "Sample answer",
        "AnswerType": "definition",
        "Abstract": "Sample abstract text",
        "AbstractURL": "https://example.com/abstract",
        "Definition": "Sample definition",
        "DefinitionURL": "https://example.com/definition",
        "RelatedTopics": [
            {
                "Text": "Related topic 1",
                "FirstURL": "https://example.com/topic1"
            },
            {
                "Text": "Related topic 2", 
                "FirstURL": "https://example.com/topic2"
            }
        ],
        "Infobox": {
            "content": [
                {"label": "Type", "value": "Example"},
                {"label": "Category", "value": "Test"}
            ]
        }
    }


@pytest.fixture
def web_searcher():
    """WebSearcher instance for testing."""
    return WebSearcher()

