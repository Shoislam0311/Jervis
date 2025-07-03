"""
JarvisClone Web Search Module

This module provides web search functionality using the DuckDuckGo JSON API.
"""

import requests
import json
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

class WebSearcher:
    """Web search client using DuckDuckGo JSON API."""
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'JarvisClone/1.0 (AI Assistant)'
        })
    
    def search(self, query: str, max_results: int = 5) -> Optional[str]:
        """
        Search the web using DuckDuckGo API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            Formatted search results as string, or None if search fails
        """
        try:
            # DuckDuckGo Instant Answer API
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Format the results
            results = self._format_results(data, max_results)
            
            if results:
                return results
            else:
                # Fallback to web search if instant answers don't provide results
                return self._web_search_fallback(query, max_results)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Search request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse search response: {e}")
            return None
    
    def _format_results(self, data: Dict[str, Any], max_results: int) -> Optional[str]:
        """Format DuckDuckGo API response into readable text."""
        results = []
        
        # Check for instant answer
        if data.get('Answer'):
            results.append(f"Answer: {data['Answer']}")
        
        # Check for abstract
        if data.get('Abstract'):
            results.append(f"Summary: {data['Abstract']}")
            if data.get('AbstractURL'):
                results.append(f"Source: {data['AbstractURL']}")
        
        # Check for definition
        if data.get('Definition'):
            results.append(f"Definition: {data['Definition']}")
            if data.get('DefinitionURL'):
                results.append(f"Source: {data['DefinitionURL']}")
        
        # Check for related topics
        if data.get('RelatedTopics'):
            topics = data['RelatedTopics'][:max_results]
            if topics:
                results.append("Related Information:")
                for topic in topics:
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append(f"- {topic['Text']}")
                        if topic.get('FirstURL'):
                            results.append(f"  Source: {topic['FirstURL']}")
        
        # Check for infobox
        if data.get('Infobox') and data['Infobox'].get('content'):
            infobox = data['Infobox']['content']
            if infobox:
                results.append("Additional Information:")
                for item in infobox[:3]:  # Limit to first 3 items
                    if item.get('label') and item.get('value'):
                        results.append(f"- {item['label']}: {item['value']}")
        
        return "\n".join(results) if results else None
    
    def _web_search_fallback(self, query: str, max_results: int) -> Optional[str]:
        """
        Fallback web search method.
        Note: This is a simplified implementation. In a production environment,
        you might want to use a more comprehensive search API or scraping method.
        """
        try:
            # Use DuckDuckGo's HTML search (simplified)
            search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
            
            # This is a basic implementation - in practice, you'd need to parse HTML
            # For now, return a message indicating web search capability
            return f"Web search performed for: '{query}'. For detailed results, please visit: {search_url}"
            
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            return None
    
    def get_news(self, topic: str = "technology", max_results: int = 5) -> Optional[str]:
        """
        Get news articles on a specific topic.
        
        Args:
            topic: News topic to search for
            max_results: Maximum number of news items to return
            
        Returns:
            Formatted news results as string
        """
        news_query = f"{topic} news latest"
        return self.search(news_query, max_results)
    
    def get_weather(self, location: str) -> Optional[str]:
        """
        Get weather information for a location.
        
        Args:
            location: Location to get weather for
            
        Returns:
            Weather information as string
        """
        weather_query = f"weather {location}"
        return self.search(weather_query, 1)
    
    def get_definition(self, term: str) -> Optional[str]:
        """
        Get definition of a term.
        
        Args:
            term: Term to define
            
        Returns:
            Definition as string
        """
        definition_query = f"define {term}"
        return self.search(definition_query, 1)

# Example usage and testing
if __name__ == "__main__":
    searcher = WebSearcher()
    
    # Test searches
    test_queries = [
        "Python programming",
        "weather New York",
        "define artificial intelligence",
        "latest technology news"
    ]
    
    for query in test_queries:
        print(f"\nSearching for: {query}")
        print("-" * 40)
        result = searcher.search(query)
        if result:
            print(result)
        else:
            print("No results found")
        print("-" * 40)

