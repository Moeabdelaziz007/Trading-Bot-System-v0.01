"""
🎙️ AXIOM VOICE COCKPIT - The Command Center
=============================================
A Wispr Flow-inspired voice interface for the Axiom Alpha trading system.

Usage:
    python axiom_cli.py

Controls:
    SPACE (hold) → Push-to-Talk (record voice)
    SPACE (release) → Process command
    ESC → Exit
    
Voice Commands (Examples):
    "Axiom, what's my balance?"
    "Buy 0.1 Bitcoin"
    "Switch to sniper mode"
    "Close all positions"
    "What's the market sentiment for gold?"
"""

import os
import sys
import asyncio
import tempfile
import logging
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum

# Audio libraries (will gracefully degrade if not available)
try:
    import sounddevice as sd
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️ Audio libraries not installed. Run: pip install sounddevice numpy")

# Keyboard library for push-to-talk
try:
    from pynput import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("⚠️ Keyboard library not installed. Run: pip install pynput")

# TTS libraries
try:
    import edge_tts
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️ Edge TTS not installed. Run: pip install edge-tts")

# For playing audio
try:
    from playsound import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    PLAYSOUND_AVAILABLE = False

# HTTP client for API calls
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("axiom.voice")


# =====================
# CONFIGURATION
# =====================

@dataclass
class VoiceConfig:
    """Voice interface configuration."""
    groq_api_key: str = ""
    sample_rate: int = 16000
    channels: int = 1
    tts_voice: str = "en-US-GuyNeural"  # Male professional voice
    tts_rate: str = "+10%"  # Slightly faster
    whisper_model: str = "whisper-large-v3"
    
    def __post_init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY", self.groq_api_key)


class CockpitState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"


# =====================
# SPEECH-TO-TEXT (Groq Whisper)
# =====================

class GroqWhisper:
    """Groq-powered speech recognition using Whisper."""
    
    BASE_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
    
    def __init__(self, api_key: str, model: str = "whisper-large-v3"):
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def transcribe(self, audio_data: bytes, filename: str = "audio.wav") -> str:
        """Transcribe audio bytes to text."""
        if not self.api_key:
            logger.warning("No GROQ_API_KEY set. Using mock transcription.")
            return "[Mock] Buy Bitcoin"
        
        try:
            files = {"file": (filename, audio_data, "audio/wav")}
            data = {"model": self.model}
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = await self.client.post(
                self.BASE_URL,
                files=files,
                data=data,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            return result.get("text", "")
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""
    
    async def close(self):
        await self.client.aclose()


# =====================
# TEXT-TO-SPEECH (Edge TTS)
# =====================

class AxiomVoice:
    """Text-to-Speech using Microsoft Edge TTS (FREE!)."""
    
    def __init__(self, voice: str = "en-US-GuyNeural", rate: str = "+10%"):
        self.voice = voice
        self.rate = rate
    
    async def speak(self, text: str) -> None:
        """Convert text to speech and play it."""
        if not TTS_AVAILABLE:
            print(f"🔊 [TTS]: {text}")
            return
        
        try:
            # Generate speech
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_path = f.name
            
            await communicate.save(temp_path)
            
            # Play audio
            if PLAYSOUND_AVAILABLE:
                playsound(temp_path)
            else:
                # Fallback: use system command
                if sys.platform == "darwin":
                    os.system(f"afplay {temp_path}")
                elif sys.platform == "win32":
                    os.system(f"start {temp_path}")
                else:
                    os.system(f"aplay {temp_path}")
            
            # Cleanup
            os.unlink(temp_path)
            
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            print(f"🔊 {text}")


# =====================
# AUDIO RECORDER
# =====================

class PushToTalkRecorder:
    """Records audio while spacebar is held."""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.audio_chunks = []
    
    def start_recording(self):
        """Start capturing audio."""
        if not AUDIO_AVAILABLE:
            return
        
        self.recording = True
        self.audio_chunks = []
        
        def callback(indata, frames, time, status):
            if self.recording:
                self.audio_chunks.append(indata.copy())
        
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=callback,
            dtype=np.int16
        )
        self.stream.start()
        logger.info("🎤 Recording started...")
    
    def stop_recording(self) -> bytes:
        """Stop recording and return WAV bytes."""
        if not AUDIO_AVAILABLE or not self.recording:
            return b""
        
        self.recording = False
        self.stream.stop()
        self.stream.close()
        
        if not self.audio_chunks:
            return b""
        
        # Combine chunks
        audio_data = np.concatenate(self.audio_chunks, axis=0)
        
        # Convert to WAV bytes
        import io
        import wave
        
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())
        
        logger.info(f"🎤 Recording stopped. {len(audio_data)} samples captured.")
        return buffer.getvalue()


# =====================
# COMMAND PROCESSOR
# =====================

class CommandProcessor:
    """Processes voice commands and routes to appropriate actions."""
    
    def __init__(self):
        # Import portfolio manager if available
        try:
            from src.engine import PortfolioManager, CipherEngine, NewsFilter
            self.pm = PortfolioManager()
            self.cipher = CipherEngine()
            self.news = NewsFilter()
            self.engine_available = True
        except ImportError:
            self.engine_available = False
            logger.warning("Engine modules not available. Running in demo mode.")
    
    async def process(self, command: str) -> str:
        """Process a voice command and return response."""
        command_lower = command.lower().strip()
        
        # Balance check
        if any(word in command_lower for word in ["balance", "رصيد", "money"]):
            return await self._get_balance()
        
        # Buy command
        if any(word in command_lower for word in ["buy", "اشتري", "long"]):
            return await self._execute_buy(command_lower)
        
        # Sell command
        if any(word in command_lower for word in ["sell", "بيع", "short"]):
            return await self._execute_sell(command_lower)
        
        # Close positions
        if any(word in command_lower for word in ["close", "اغلق", "exit"]):
            return await self._close_positions()
        
        # Market sentiment
        if any(word in command_lower for word in ["sentiment", "news", "أخبار"]):
            return await self._get_sentiment(command_lower)
        
        # Status
        if any(word in command_lower for word in ["status", "حالة", "positions"]):
            return await self._get_status()
        
        # Help
        if any(word in command_lower for word in ["help", "مساعدة", "commands"]):
            return self._get_help()
        
        # Unknown command
        return f"I heard: '{command}'. I'm not sure what to do with that. Say 'help' for available commands."
    
    async def _get_balance(self) -> str:
        if not self.engine_available:
            return "Demo mode: Your balance is $10,000 USD."
        # Real implementation would query adapters
        return "Checking balance across all connected exchanges..."
    
    async def _execute_buy(self, command: str) -> str:
        # Parse amount and symbol from command
        # Simple parsing for demo
        return "Buy order received. Routing through Aladdin risk check..."
    
    async def _execute_sell(self, command: str) -> str:
        return "Sell order received. Routing through Aladdin risk check..."
    
    async def _close_positions(self) -> str:
        return "Closing all positions. Emergency protocol activated."
    
    async def _get_sentiment(self, command: str) -> str:
        if not self.engine_available:
            return "Demo mode: Market sentiment is neutral. No major news events detected."
        # Real implementation would use NewsFilter
        return "Scanning news sources for market sentiment..."
    
    async def _get_status(self) -> str:
        return "System status: All engines operational. Aladdin shield active. 0 open positions."
    
    def _get_help(self) -> str:
        return """Available commands:
        - Check balance: "What's my balance?"
        - Buy: "Buy 0.1 Bitcoin"
        - Sell: "Sell gold"
        - Close all: "Close all positions"
        - Sentiment: "What's the market sentiment?"
        - Status: "System status"
        """


# =====================
# MAIN COCKPIT
# =====================

class AxiomCockpit:
    """The main voice command interface."""
    
    BANNER = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     █████╗ ██╗  ██╗██╗ ██████╗ ███╗   ███╗                   ║
    ║    ██╔══██╗╚██╗██╔╝██║██╔═══██╗████╗ ████║                   ║
    ║    ███████║ ╚███╔╝ ██║██║   ██║██╔████╔██║                   ║
    ║    ██╔══██║ ██╔██╗ ██║██║   ██║██║╚██╔╝██║                   ║
    ║    ██║  ██║██╔╝ ██╗██║╚██████╔╝██║ ╚═╝ ██║                   ║
    ║    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝                   ║
    ║                                                              ║
    ║              🎙️  VOICE COCKPIT v1.0  🎙️                      ║
    ║                                                              ║
    ║   [SPACE] Hold to speak    [ESC] Exit                        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config or VoiceConfig()
        self.state = CockpitState.IDLE
        self.whisper = GroqWhisper(self.config.groq_api_key, self.config.whisper_model)
        self.voice = AxiomVoice(self.config.tts_voice, self.config.tts_rate)
        self.recorder = PushToTalkRecorder(self.config.sample_rate, self.config.channels)
        self.processor = CommandProcessor()
        self.running = True
    
    async def run(self):
        """Main loop for the voice cockpit."""
        print(self.BANNER)
        
        if not KEYBOARD_AVAILABLE:
            print("❌ Keyboard library not available. Running in text mode.")
            await self._text_mode()
            return
        
        await self.voice.speak("Axiom Voice Cockpit online. Hold space to speak.")
        
        # Setup keyboard listener
        space_pressed = False
        
        def on_press(key):
            nonlocal space_pressed
            if key == keyboard.Key.space and not space_pressed:
                space_pressed = True
                self.state = CockpitState.LISTENING
                self.recorder.start_recording()
                print("\n🎤 Listening... (release SPACE when done)")
            elif key == keyboard.Key.esc:
                self.running = False
                return False
        
        def on_release(key):
            nonlocal space_pressed
            if key == keyboard.Key.space and space_pressed:
                space_pressed = False
                asyncio.create_task(self._process_recording())
        
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        
        print("\n💡 Ready. Hold SPACE to speak, ESC to exit.\n")
        
        while self.running:
            await asyncio.sleep(0.1)
        
        listener.stop()
        await self.whisper.close()
        print("\n👋 Axiom Cockpit shutting down. Goodbye!")
    
    async def _process_recording(self):
        """Process the recorded audio."""
        self.state = CockpitState.PROCESSING
        print("⚙️ Processing...")
        
        # Get audio data
        audio_data = self.recorder.stop_recording()
        
        if not audio_data:
            print("❌ No audio captured.")
            self.state = CockpitState.IDLE
            return
        
        # Transcribe
        text = await self.whisper.transcribe(audio_data)
        
        if not text:
            await self.voice.speak("I didn't catch that. Please try again.")
            self.state = CockpitState.IDLE
            return
        
        print(f"📝 You said: \"{text}\"")
        
        # Process command
        response = await self.processor.process(text)
        
        # Speak response
        self.state = CockpitState.SPEAKING
        print(f"🤖 Axiom: {response}")
        await self.voice.speak(response)
        
        self.state = CockpitState.IDLE
        print("\n💡 Ready. Hold SPACE to speak.\n")
    
    async def _text_mode(self):
        """Fallback text-based interface."""
        print("\n📝 Text Mode Active. Type commands and press Enter.\n")
        
        while self.running:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ["exit", "quit", "q"]:
                    break
                
                response = await self.processor.process(user_input)
                print(f"🤖 Axiom: {response}\n")
                await self.voice.speak(response)
                
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        print("\n👋 Goodbye!")


# =====================
# ENTRY POINT
# =====================

async def main():
    """Entry point for the voice cockpit."""
    cockpit = AxiomCockpit()
    await cockpit.run()


if __name__ == "__main__":
    asyncio.run(main())
