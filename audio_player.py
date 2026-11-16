"""Audio playback helpers."""

import sounddevice as sd
import numpy as np


def play_audio(audio: np.ndarray, sample_rate: int) -> None:
    sd.stop()
    sd.play(np.asarray(audio, dtype=np.float32), sample_rate)


def stop_audio() -> None:
    sd.stop()
