"""
preprocessing.py — IndicASR

Prepares a raw decoded audio array (as returned by data_loader.Sample) for
Whisper: resample to 16kHz mono float32, since that's what
`WhisperFeatureExtractor` expects.

Concept note: Whisper's feature extractor internally converts raw audio
into a log-mel spectrogram — a frequency-over-time representation — since
the model was trained on that, not on raw waveforms. We only need to get
the waveform into 16kHz mono float32 first; the feature extractor (used in
inference.py) does the rest.
"""

import numpy as np

# Real audio essentially never has more channels than this; sample counts
# (thousands to millions) are always far larger. Used to identify the
# channel axis explicitly rather than assuming "the smaller dimension is
# always channels" — see to_mono() docstring for why that assumption is
# unsafe.
MAX_REASONABLE_CHANNELS = 8


def to_mono(audio_array: np.ndarray, max_reasonable_channels: int = MAX_REASONABLE_CHANNELS) -> np.ndarray:
    """
    Reduces an audio array to 1-D mono by averaging across the channel
    axis. Handles all three shapes that different audio libraries produce:

      - (samples,)             -> already mono; returned unchanged
      - (channels, samples)    -> librosa-style multi-channel
      - (samples, channels)    -> soundfile-style multi-channel

    The channel axis is identified by checking which axis has a size
    <= max_reasonable_channels, NOT by assuming "the smaller axis is
    always channels" — that assumption breaks for pathologically short
    clips (e.g. a genuinely mono (3,)-shaped edge case, or any case where
    sample count happens to be small). If neither axis looks like a
    plausible channel count, or both do (genuinely ambiguous), this raises
    instead of silently guessing wrong — a wrong silent guess here would
    corrupt every downstream WER/CER number without any visible error.
    """
    if audio_array.ndim == 1:
        return audio_array

    if audio_array.ndim != 2:
        raise ValueError(
            f"Unexpected audio array shape {audio_array.shape} (ndim={audio_array.ndim}); "
            f"expected 1-D mono or 2-D multi-channel audio."
        )

    dim0, dim1 = audio_array.shape
    dim0_is_channel = dim0 <= max_reasonable_channels
    dim1_is_channel = dim1 <= max_reasonable_channels

    if dim0_is_channel and not dim1_is_channel:
        # (channels, samples)
        return np.mean(audio_array, axis=0)
    elif dim1_is_channel and not dim0_is_channel:
        # (samples, channels)
        return np.mean(audio_array, axis=1)
    elif dim0_is_channel and dim1_is_channel:
        raise ValueError(
            f"Ambiguous audio shape {audio_array.shape}: both dimensions are "
            f"<= {max_reasonable_channels} so the channel axis can't be "
            f"identified safely. Inspect this sample manually rather than guessing."
        )
    else:
        raise ValueError(
            f"Could not identify a channel axis in shape {audio_array.shape} "
            f"(neither dimension is <= {max_reasonable_channels} channels)."
        )


def resample(audio_array: np.ndarray, orig_sr: int, target_sr: int = 16000) -> np.ndarray:
    """
    Resamples using librosa if the rates differ. No-ops when
    orig_sr == target_sr — most Kathbath/FLEURS audio is expected to
    already be 16kHz, but this is checked per-sample at runtime via
    sample.sampling_rate, never assumed.
    """
    if orig_sr == target_sr:
        return audio_array

    import librosa

    return librosa.resample(audio_array.astype(np.float32), orig_sr=orig_sr, target_sr=target_sr)


def prepare_for_whisper(audio_array: np.ndarray, sampling_rate: int, target_sr: int = 16000) -> np.ndarray:
    """Full prep: mono -> resample -> float32, ready for WhisperFeatureExtractor."""
    mono = to_mono(audio_array)
    resampled = resample(mono, sampling_rate, target_sr)
    return resampled.astype(np.float32)
