"""
JarvisClone Text-to-Speech Module

This module provides text-to-speech functionality using the puter.ai service.
"""

import requests
import json
import logging
import tempfile
import os
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)

class TTSClient:
    """Text-to-Speech client using puter.ai service."""
    
    def __init__(self):
        self.base_url = "https://api.puter.ai/v1/ai/txt2speech"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'JarvisClone/1.0 (AI Assistant)'
        })
    
    def speak(self, text: str, voice: str = "en-US-Standard-A", speed: float = 1.0) -> bool:
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use for synthesis
            speed: Speech speed (0.5 to 2.0)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate speech audio
            audio_data = self._generate_speech(text, voice, speed)
            
            if audio_data:
                # Play the audio
                return self._play_audio(audio_data)
            else:
                logger.error("Failed to generate speech audio")
                return False
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False
    
    def _generate_speech(self, text: str, voice: str, speed: float) -> Optional[bytes]:
        """
        Generate speech audio from text using puter.ai API.
        
        Args:
            text: Text to convert
            voice: Voice identifier
            speed: Speech speed
            
        Returns:
            Audio data as bytes, or None if failed
        """
        try:
            payload = {
                "text": text,
                "voice": voice,
                "speed": speed,
                "format": "mp3"
            }
            
            response = self.session.post(
                self.base_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                # Check if response is JSON (error) or binary (audio)
                content_type = response.headers.get('content-type', '')
                
                if 'application/json' in content_type:
                    # Handle JSON response (might be an error or URL)
                    try:
                        json_response = response.json()
                        if 'audio_url' in json_response:
                            # Download audio from URL
                            audio_response = self.session.get(json_response['audio_url'])
                            if audio_response.status_code == 200:
                                return audio_response.content
                        else:
                            logger.error(f"TTS API error: {json_response}")
                            return None
                    except json.JSONDecodeError:
                        logger.error("Invalid JSON response from TTS API")
                        return None
                else:
                    # Direct binary audio response
                    return response.content
            else:
                logger.error(f"TTS API request failed with status {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"TTS API request failed: {e}")
            return None
    
    def _play_audio(self, audio_data: bytes) -> bool:
        """
        Play audio data using system audio player.
        
        Args:
            audio_data: Audio data as bytes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Try different audio players based on the system
            audio_players = [
                ['mpg123', temp_file_path],  # Linux
                ['afplay', temp_file_path],  # macOS
                ['start', temp_file_path],   # Windows
                ['vlc', '--intf', 'dummy', '--play-and-exit', temp_file_path],  # VLC
                ['ffplay', '-nodisp', '-autoexit', temp_file_path]  # FFmpeg
            ]
            
            played = False
            for player_cmd in audio_players:
                try:
                    # Try to play with current player
                    result = subprocess.run(
                        player_cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        played = True
                        break
                        
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
            
            if not played:
                logger.warning("No suitable audio player found. Audio file was generated but not played.")
                # Fallback: save audio to a known location
                fallback_path = "jarvis_speech.mp3"
                with open(fallback_path, 'wb') as f:
                    f.write(audio_data)
                logger.info(f"Audio saved to {fallback_path}")
            
            return played
            
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
            return False
    
    def save_speech(self, text: str, filename: str, voice: str = "en-US-Standard-A", speed: float = 1.0) -> bool:
        """
        Generate speech and save to file.
        
        Args:
            text: Text to convert to speech
            filename: Output filename
            voice: Voice to use for synthesis
            speed: Speech speed
            
        Returns:
            True if successful, False otherwise
        """
        try:
            audio_data = self._generate_speech(text, voice, speed)
            
            if audio_data:
                with open(filename, 'wb') as f:
                    f.write(audio_data)
                logger.info(f"Speech saved to {filename}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Save speech error: {e}")
            return False
    
    def get_available_voices(self) -> list:
        """
        Get list of available voices.
        Note: This is a placeholder implementation.
        In practice, you'd query the API for available voices.
        
        Returns:
            List of available voice identifiers
        """
        # Common voice options (this would ideally come from the API)
        return [
            "en-US-Standard-A",  # Female
            "en-US-Standard-B",  # Male
            "en-US-Standard-C",  # Female
            "en-US-Standard-D",  # Male
            "en-GB-Standard-A",  # British Female
            "en-GB-Standard-B",  # British Male
        ]

# Example usage and testing
if __name__ == "__main__":
    tts = TTSClient()
    
    # Test text-to-speech
    test_text = "Hello! I am JarvisClone, your AI assistant. How can I help you today?"
    
    print("Testing text-to-speech...")
    success = tts.speak(test_text)
    
    if success:
        print("Speech synthesis successful!")
    else:
        print("Speech synthesis failed. Trying to save to file...")
        if tts.save_speech(test_text, "test_speech.mp3"):
            print("Speech saved to test_speech.mp3")
        else:
            print("Failed to save speech")
    
    # List available voices
    print("\nAvailable voices:")
    for voice in tts.get_available_voices():
        print(f"- {voice}")

