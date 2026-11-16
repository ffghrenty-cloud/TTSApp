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
    """Loads the multilingual Silero model on first use and synthesizes audio."""

    def __init__(self) -> None:
        self._model: Any | None = None
        self._symbols: Any | None = None
        self._apply_tts: Any | None = None
        self._device = torch.device(DEVICE)

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def load(self) -> None:
        if self.is_loaded:
            return

        # The first launch downloads the model; subsequent launches use the
        # PyTorch Hub cache. Synthesis itself runs locally on the CPU.
        loaded = torch.hub.load(
            repo_or_dir=MODEL_REPOSITORY,
            model=MODEL_NAME,
            language=MODEL_LANGUAGE,
            speaker=MODEL_CHECKPOINT,
            trust_repo=True,
        )

        if not isinstance(loaded, (tuple, list)) or len(loaded) < 5:
            raise RuntimeError(
                "Неожиданный формат модели Silero. "
                "Проверьте версию модели и подключение при первой загрузке."
            )

        self._model, self._symbols, _, _, self._apply_tts = loaded
        self._model = self._model.to(self._device)
        self._model.eval()

    def synthesize(self, text: str, speaker: str) -> tuple[np.ndarray, int]:
        text = text.strip()
        if not text:
            raise ValueError("Введите текст для озвучивания.")

        self.load()

        with torch.inference_mode():
            # The multilingual checkpoint exposes apply_tts on the model.
            if hasattr(self._model, "apply_tts"):
                audio = self._model.apply_tts(
                    text=text,
                    speaker=speaker,
                    sample_rate=SAMPLE_RATE,
                )
            else:
                # Compatibility with the classic PyTorch Hub interface.
                try:
                    audio = self._apply_tts(
                        texts=[text],
                        model=self._model,
                        sample_rate=SAMPLE_RATE,
                        symbols=self._symbols,
                        device=self._device,
                        speaker=speaker,
                    )
                except TypeError as exc:
                    raise RuntimeError(
                        "Установленная версия Silero не поддерживает "
                        "выбор голоса для многоязычной модели."
                    ) from exc

        if isinstance(audio, (tuple, list)):
            audio = audio[0]

        if isinstance(audio, torch.Tensor):
            audio = audio.detach().cpu().numpy()

        result = np.asarray(audio, dtype=np.float32).squeeze()
        if result.size == 0:
            raise RuntimeError("Silero вернул пустую аудиозапись.")

        return result, SAMPLE_RATE
