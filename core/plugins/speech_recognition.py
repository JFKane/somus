import numpy as np
import speech_recognition as sr
from typing import Dict, Any

def speech_recognition(audio_chunk: np.ndarray, sample_rate: int = 44100, language: str = "en-US") -> Dict[str, Any]:
    """
    Transcribe speech in an audio chunk using Google Speech Recognition.
    
    :param audio_chunk: numpy array of audio samples
    :param sample_rate: sample rate of the audio
    :param language: language code for recognition (default: en-US)
    :return: Dictionary containing transcription results
    """
    recognizer = sr.Recognizer()
    
    # Convert numpy array to audio data
    audio_data = sr.AudioData(audio_chunk.tobytes(), sample_rate, 2)  # Assuming 16-bit audio
    
    try:
        text = recognizer.recognize_google(audio_data, language=language)
        return {
            "transcription": text,
            "success": True
        }
    except sr.UnknownValueError:
        return {
            "transcription": "",
            "success": False,
            "error": "Speech unintelligible"
        }
    except sr.RequestError as e:
        return {
            "transcription": "",
            "success": False,
            "error": f"Could not request results from Google Speech Recognition service; {e}"
        }

def register_plugin():
    return {
        "name": "speech_recognition",
        "function": speech_recognition,
        "params": {
            "sample_rate": 44100,
            "language": "en-US"
        }
    }