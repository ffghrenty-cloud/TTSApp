"""Local text-to-speech engine powered by Silero."""

from __future__ import annotations

from typing import Any

import numpy as np
import torch

from config import (
    DEVICE,
    MODEL_CHECKPOINT,
    MODEL_LANGUAGE,
    MODEL_NAME,
    MODEL_REPOSITORY,
    SAMPLE_RATE,
)


class SileroTTSEngine:
    """Loads Silero's multilingual checkpoint once and synthesizes speech."""

    def __init__(self) -> None:
        self._model: Any | None = None
        self._available_speakers: Any | None = None
        self._device = torch.device(DEVICE)

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def load(self) -> None:
        if self.is_loaded:
            return

        # multi_v2 returns (model, speaker_metadata), unlike older single-
        # language PyTorch Hub checkpoints that return five values.
        loaded = torch.hub.load(
            repo_or_dir=MODEL_REPOSITORY,
            model=MODEL_NAME,
            language=MODEL_LANGUAGE,
            speaker=MODEL_CHECKPOINT,
            trust_repo=True,
        )

        if not isinstance(loaded, (tuple, list)) or len(loaded) != 2:
            raise RuntimeError(
                "Silero вернул неожиданный формат многоязычной модели. "
                "Проверьте установленную версию PyTorch и доступ к модели."
            )

        self._model, self._available_speakers = loaded
        self._model = self._model.to(self._device)
        self._model.eval()

    def synthesize(self, text: str, speaker: str) -> tuple[np.ndarray, int]:
        text = text.strip()
        if not text:
            raise ValueError("Введите текст для озвучивания.")

        self.load()

        if hasattr(self._available_speakers, "keys"):
            known_speakers = self._available_speakers.keys()
            if speaker not in known_speakers:
                raise ValueError(f"Голос «{speaker}» отсутствует в модели Silero.")

        with torch.inference_mode():
            audio = self._model.apply_tts(
                text=text,
                speaker=speaker,
                sample_rate=SAMPLE_RATE,
            )

        if isinstance(audio, torch.Tensor):
            audio = audio.detach().cpu().numpy()

        result = np.asarray(audio, dtype=np.float32).squeeze()
        if result.size == 0:
            raise RuntimeError("Silero вернул пустую аудиозапись.")

        return result, SAMPLE_RATE
