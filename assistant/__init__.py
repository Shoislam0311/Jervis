"""
JarvisClone AI Assistant Package

This package contains the core functionality for the JarvisClone AI assistant.
"""

from .core import JarvisCore, chat_loop
from .search import WebSearcher
from .voice import TTSClient

__version__ = "1.0.0"
__author__ = "JarvisClone Team"

__all__ = [
    "JarvisCore",
    "chat_loop", 
    "WebSearcher",
    "TTSClient"
]

