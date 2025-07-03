"""
JarvisClone AI Assistant Core Module

This module contains the core functionality for the JarvisClone AI assistant,
including the chat loop, LLM interaction, and memory management.
"""

import json
import os
import requests
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryStore:
    """Simple JSON-based memory store for conversation history and context."""
    
    def __init__(self, memory_file: str = "memory.json"):
        self.memory_file = memory_file
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from JSON file."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load memory: {e}")
                return {"conversations": [], "user_preferences": {}}
        return {"conversations": [], "user_preferences": {}}
    
    def _save_memory(self):
        """Save memory to JSON file."""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Failed to save memory: {e}")
    
    def add_conversation(self, user_input: str, assistant_response: str):
        """Add a conversation turn to memory."""
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": assistant_response
        }
        self.memory["conversations"].append(conversation_entry)
        
        # Keep only last 50 conversations to prevent memory bloat
        if len(self.memory["conversations"]) > 50:
            self.memory["conversations"] = self.memory["conversations"][-50:]
        
        self._save_memory()
    
    def get_recent_conversations(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations for context."""
        return self.memory["conversations"][-count:]
    
    def set_user_preference(self, key: str, value: Any):
        """Set a user preference."""
        self.memory["user_preferences"][key] = value
        self._save_memory()
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        return self.memory["user_preferences"].get(key, default)

class LLMClient:
    """Client for interacting with OpenRouter.ai LLM."""
    
    def __init__(self, api_key: str = None, model: str = "google/gemma-3n-e4b-it:free"):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/jarvisclone",
            "X-Title": "JarvisClone AI Assistant"
        }
    
    def generate_response(self, messages: List[Dict[str, str]], 
                         temperature: float = 0.7, 
                         max_tokens: int = 1000) -> Optional[str]:
        """Generate a response using the LLM."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API request failed: {e}")
            return None
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected LLM API response format: {e}")
            return None

class JarvisCore:
    """Main AI assistant core class."""
    
    def __init__(self, api_key: str = None):
        self.memory = MemoryStore()
        self.llm = LLMClient(api_key)
        self.system_prompt = self._get_system_prompt()
        
        # Import search and voice modules
        try:
            from .search import WebSearcher
            from .voice import TTSClient
            self.searcher = WebSearcher()
            self.tts = TTSClient()
        except ImportError:
            logger.warning("Search or TTS modules not available")
            self.searcher = None
            self.tts = None
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI assistant."""
        return """You are JarvisGPT, a highly capable AI assistant with deep reasoning, project planning, code generation, and multilingual communication skills. You speak and write fluently in Bengali, English, and Hindi, and can switch naturally when required.

Your core capabilities include:
1. Understanding high-level project goals and breaking them down into actionable steps
2. Generating well-structured outputs (Markdown, JSON, code snippets, tables, etc.)
3. Providing thorough explanations with bullet points and numbered lists
4. Maintaining clarity, consistency, and accuracy in all responses
5. Respecting constraints on timeline, budget, and technology stack
6. Suggesting optimizations, trade-offs, and risk mitigations

You have access to web search capabilities for real-time information retrieval and can provide voice responses when requested. Always be helpful, accurate, and maintain context throughout conversations."""
    
    def _build_messages(self, user_input: str) -> List[Dict[str, str]]:
        """Build the message list for LLM including context."""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add recent conversation history for context
        recent_conversations = self.memory.get_recent_conversations(5)
        for conv in recent_conversations:
            messages.append({"role": "user", "content": conv["user"]})
            messages.append({"role": "assistant", "content": conv["assistant"]})
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def process_input(self, user_input: str) -> str:
        """Process user input and generate a response."""
        # Check if user is asking for web search
        if self.searcher and any(keyword in user_input.lower() for keyword in 
                                ["search", "latest", "current", "news", "what's happening"]):
            search_results = self.searcher.search(user_input)
            if search_results:
                enhanced_input = f"{user_input}\n\nWeb search results:\n{search_results}"
            else:
                enhanced_input = user_input
        else:
            enhanced_input = user_input
        
        # Build messages with context
        messages = self._build_messages(enhanced_input)
        
        # Generate response using LLM
        response = self.llm.generate_response(messages)
        
        if response:
            # Store conversation in memory
            self.memory.add_conversation(user_input, response)
            return response
        else:
            fallback_response = "I apologize, but I'm having trouble processing your request right now. Please try again."
            self.memory.add_conversation(user_input, fallback_response)
            return fallback_response
    
    def speak_response(self, text: str) -> bool:
        """Convert text to speech using TTS."""
        if self.tts:
            return self.tts.speak(text)
        return False

def chat_loop():
    """Main chat loop for CLI interface."""
    print("JarvisClone AI Assistant")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("Type 'speak' before your message to get voice response.")
    print("-" * 50)
    
    # Initialize the core
    jarvis = JarvisCore()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Jarvis: Goodbye! Have a great day!")
                break
            
            # Check for voice request
            speak_response = False
            if user_input.lower().startswith('speak '):
                speak_response = True
                user_input = user_input[6:]  # Remove 'speak ' prefix
            
            # Process the input
            response = jarvis.process_input(user_input)
            print(f"Jarvis: {response}")
            
            # Speak response if requested
            if speak_response:
                jarvis.speak_response(response)
                
        except KeyboardInterrupt:
            print("\n\nJarvis: Goodbye! Have a great day!")
            break
        except Exception as e:
            logger.error(f"Error in chat loop: {e}")
            print("Jarvis: I encountered an error. Please try again.")

if __name__ == "__main__":
    chat_loop()

