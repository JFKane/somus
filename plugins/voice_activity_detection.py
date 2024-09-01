import numpy as np

def voice_activity_detection(audio_chunk: np.ndarray, energy_threshold: float = 0.1) -> Dict[str, Any]:
    """
    Detect voice activity in an audio chunk using a simple energy-based method.
    
    :param audio_chunk: numpy array of audio samples
    :param energy_threshold: threshold for considering a frame as containing voice
    :return: Dictionary containing detection results
    """
    energy = np.sum(audio_chunk**2) / len(audio_chunk)
    is_voice = energy > energy_threshold
    
    return {
        "is_voice": is_voice,
        "energy": energy,
        "threshold": energy_threshold
    }

def register_plugin():
    return {
        "name": "voice_activity_detection",
        "function": voice_activity_detection,
        "params": {
            "energy_threshold": 0.1
        }
    }