import numpy as np
from typing import Dict, Any

def noise_level_detection(audio_chunk: np.ndarray, threshold_db: float = -30) -> Dict[str, Any]:
    """
    Detect noise levels in an audio chunk.
    
    :param audio_chunk: numpy array of audio samples
    :param threshold_db: threshold for considering audio as noise (in dB)
    :return: Dictionary containing noise level detection results
    """
    # Calculate RMS of the audio chunk
    rms = np.sqrt(np.mean(np.square(audio_chunk)))
    
    # Convert RMS to dB
    db = 20 * np.log10(rms)
    
    # Determine if the level is above the threshold
    is_noisy = db > threshold_db
    
    return {
        "noise_level_db": db,
        "is_noisy": is_noisy,
        "threshold_db": threshold_db
    }

def register_plugin():
    return {
        "name": "noise_level_detection",
        "function": noise_level_detection,
        "params": {
            "threshold_db": -30
        }
    }