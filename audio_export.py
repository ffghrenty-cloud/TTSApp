"""Export synthesized audio to common audio formats."""

from pathlib import Path

import numpy as np
import soundfile as sf


def save_wav(path: str | Path, audio: np.ndarray, sample_rate: int) -> None:
    sf.write(str(path), np.asarray(audio, dtype=np.float32), sample_rate)


def save_mp3(path: str | Path, audio: np.ndarray, sample_rate: int) -> None:
    try:
        from pydub import AudioSegment
    except ImportError as exc:
        raise RuntimeError(
            "Для сохранения MP3 установите pydub: pip install pydub. "
            "Также потребуется FFmpeg в PATH. Пока можно сохранить WAV."
        ) from exc

    import io

    buffer = io.BytesIO()
    sf.write(buffer, np.asarray(audio, dtype=np.float32), sample_rate, format="WAV")
    buffer.seek(0)
    AudioSegment.from_wav(buffer).export(str(path), format="mp3", bitrate="192k")
