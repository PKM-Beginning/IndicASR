"""
inference.py — IndicASR, Phase 3

Loads openai/whisper-small once and exposes a transcribe() function that:
  - forces the correct language decoding token for languages Whisper
    officially supports (Hindi, Bengali, Telugu)
  - falls back to unconstrained/auto-detect decoding for Odia, since
    Odia has no token in Whisper's official language list (verified
    against transformers' WhisperTokenizer LANGUAGES dict — see the
    note in DATASETS.md / README limitations)
  - records wall-clock inference time per sample, so latency/RTF numbers
    in Phase 4 come from real measurements, not estimates

Concept notes:
- "forced_decoder_ids" tells Whisper's decoder which language and task
  (transcribe vs translate) to assume, instead of letting it guess from
  the audio itself. Guessing (auto-detect) is less reliable, especially
  on short or noisy clips, which is exactly why we force it whenever we
  can.
- Real-time factor (RTF) = inference_time / audio_duration. RTF < 1 means
  the model transcribes faster than real time.
"""

from dataclasses import dataclass
from typing import Optional
import time

import numpy as np


# Kathbath config name -> Whisper's official language code.
# Odia intentionally maps to None: Whisper has no "odia"/"or" token, so we
# do not force a language for it (see DATASETS.md / README limitations).
KATHBATH_TO_WHISPER_LANG = {
    "hindi": "hindi",
    "bengali": "bengali",
    "telugu": "telugu",
    "odia": None,
}


@dataclass
class TranscriptionResult:
    sample_id: str
    prediction: str
    inference_seconds: float
    audio_duration_seconds: float
    real_time_factor: float
    language_forced: Optional[str]  # None if we could not force a language (e.g. Odia)


class WhisperASR:
    def __init__(self, model_name: str = "openai/whisper-small", device: str = "cuda"):
        import torch
        from transformers import WhisperForConditionalGeneration, WhisperProcessor

        self.device = device if torch.cuda.is_available() else "cpu"
        if device == "cuda" and self.device == "cpu":
            print("[inference] CUDA requested but not available — falling back to CPU. "
                  "This will be slow; confirm you're on a GPU runtime in Colab if unexpected.")

        self.processor = WhisperProcessor.from_pretrained(model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def transcribe(self, sample_id: str, audio_array: np.ndarray, sampling_rate: int,
                    kathbath_language: str) -> TranscriptionResult:
        import torch

        assert sampling_rate == 16000, (
            f"Expected 16kHz audio going into Whisper, got {sampling_rate}Hz — "
            f"run preprocessing.prepare_for_whisper() first."
        )

        whisper_lang = KATHBATH_TO_WHISPER_LANG.get(kathbath_language, None)

        inputs = self.processor(
            audio_array, sampling_rate=sampling_rate, return_tensors="pt"
        ).input_features.to(self.device)

        forced_decoder_ids = None
        if whisper_lang is not None:
            forced_decoder_ids = self.processor.get_decoder_prompt_ids(
                language=whisper_lang, task="transcribe"
            )

        start = time.perf_counter()
        with torch.no_grad():
            generated_ids = self.model.generate(
                inputs, forced_decoder_ids=forced_decoder_ids
            )
        elapsed = time.perf_counter() - start

        prediction = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        audio_duration = len(audio_array) / sampling_rate
        rtf = elapsed / audio_duration if audio_duration > 0 else float("nan")

        return TranscriptionResult(
            sample_id=sample_id,
            prediction=prediction,
            inference_seconds=elapsed,
            audio_duration_seconds=audio_duration,
            real_time_factor=rtf,
            language_forced=whisper_lang,
        )
