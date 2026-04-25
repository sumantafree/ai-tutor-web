"""
Voice Engine - Text-to-Speech and Speech-to-Text
Uses pyttsx3 for TTS and SpeechRecognition for STT
Runs in separate thread to avoid blocking UI
"""

import threading
import queue
import time

# ─────────────────────────────────────────────────────────
# SAFE IMPORTS
# ─────────────────────────────────────────────────────────

def _try_import_pyttsx3():
    try:
        import pyttsx3
        return pyttsx3
    except ImportError:
        return None

def _try_import_speech_recognition():
    try:
        import speech_recognition as sr
        return sr
    except ImportError:
        return None

# ─────────────────────────────────────────────────────────
# TEXT-TO-SPEECH
# ─────────────────────────────────────────────────────────

_tts_queue = queue.Queue()
_tts_thread = None
_tts_running = False

def _tts_worker():
    """Background thread for TTS to prevent blocking."""
    global _tts_running
    pyttsx3 = _try_import_pyttsx3()
    if not pyttsx3:
        return

    try:
        engine = pyttsx3.init()
        # Set a friendly voice rate and volume
        engine.setProperty('rate', 150)    # Speed (150 = comfortable)
        engine.setProperty('volume', 0.9)  # Volume

        # Try to use a female voice if available (more friendly for children)
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break

        while _tts_running:
            try:
                text = _tts_queue.get(timeout=0.5)
                if text == "__STOP__":
                    break
                if text:
                    engine.say(text)
                    engine.runAndWait()
                _tts_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                continue
    except Exception:
        pass


def speak(text, enabled=True):
    """
    Speak text aloud using TTS.
    Non-blocking - runs in background thread.
    """
    global _tts_thread, _tts_running

    if not enabled:
        return False

    pyttsx3 = _try_import_pyttsx3()
    if not pyttsx3:
        return False

    # Clean text for speech
    clean_text = _clean_for_speech(text)
    if not clean_text:
        return False

    # Start TTS thread if not running
    if _tts_thread is None or not _tts_thread.is_alive():
        _tts_running = True
        _tts_thread = threading.Thread(target=_tts_worker, daemon=True)
        _tts_thread.start()

    _tts_queue.put(clean_text)
    return True


def stop_speech():
    """Stop any ongoing speech."""
    global _tts_running
    _tts_running = False
    _tts_queue.put("__STOP__")


def _clean_for_speech(text):
    """Remove markdown and special chars for clean TTS output."""
    import re
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'`[^`]+`', '', text)
    # Remove emojis (basic removal)
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Limit length
    if len(text) > 500:
        text = text[:500] + "."
    return text.strip()


def is_tts_available():
    """Check if TTS is available."""
    return _try_import_pyttsx3() is not None


# ─────────────────────────────────────────────────────────
# SPEECH-TO-TEXT
# ─────────────────────────────────────────────────────────

def listen_for_speech(timeout=5, phrase_time_limit=10):
    """
    Listen for speech input and return recognized text.
    Returns (text, success, error_message)
    """
    sr = _try_import_speech_recognition()
    if not sr:
        return "", False, "SpeechRecognition library not installed. Run: pip install SpeechRecognition"

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    try:
        with sr.Microphone() as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            # Listen
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

        # Recognize using Google (free, no API key)
        text = recognizer.recognize_google(audio, language="en-IN")
        return text, True, ""

    except sr.WaitTimeoutError:
        return "", False, "No speech detected. Please try again."
    except sr.UnknownValueError:
        return "", False, "Could not understand. Please speak clearly."
    except sr.RequestError as e:
        return "", False, f"Speech service error. Check internet connection."
    except OSError:
        return "", False, "Microphone not found. Please connect a microphone."
    except Exception as e:
        return "", False, f"Error: {str(e)}"


def is_stt_available():
    """Check if speech recognition is available."""
    sr = _try_import_speech_recognition()
    if not sr:
        return False
    try:
        sr.Microphone()
        return True
    except Exception:
        return False


def get_voice_status():
    """Return status of voice features."""
    return {
        "tts_available": is_tts_available(),
        "stt_available": _try_import_speech_recognition() is not None,
        "microphone": is_stt_available()
    }
