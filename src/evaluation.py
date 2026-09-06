r"""
evaluation.py — IndicASR, Phase 4

Computes WER (Word Error Rate) and CER (Character Error Rate) using jiwer.

Concept notes:
- WER = (substitutions + insertions + deletions) / total words in the
  reference, comparing the model's prediction to the ground-truth
  transcript word by word.
- CER is the same idea but at the character level.
- We normalize text BEFORE scoring so trivial formatting differences
  (punctuation, extra whitespace, casing on any embedded Latin/English)
  aren't counted as recognition errors.

IMPORTANT — Indic-safe normalization:
Python's regex `\w` (used in a naive `[^\w\s]` strip) does NOT reliably
match Indic combining marks — vowel signs (matras) and the virama, which
are Unicode categories Mn (nonspacing mark) and Mc (spacing combining
mark), are NOT counted as "word" characters by Python's `re` module or by
`str.isalnum()`. A regex like `re.sub(r"[^\w\s]", "", text)` would
therefore silently delete matras from Hindi/Bengali/Telugu/Odia text,
corrupting words (e.g. dropping the vowel sign that distinguishes two
different words) — which would make WER/CER numbers meaningless without
any obvious error message.

Instead, normalize_text() below classifies each character by its actual
Unicode category and explicitly keeps:
  - L*  (letters, all scripts)
  - M*  (combining marks — matras, virama, etc. — Mn/Mc/Me)
  - N*  (digits, all scripts)
and drops everything else (P* punctuation, S* symbols, control chars),
collapsing whitespace afterward. This is script-agnostic and doesn't
special-case Devanagari/Bengali/Telugu/Odia individually — it works the
same way for any script by construction.
"""

from dataclasses import dataclass
import re
import unicodedata
from typing import List

import jiwer


def normalize_text(text: str) -> str:
    """
    Lowercases (a no-op for scripts without case, e.g. Devanagari/Bengali/
    Telugu/Odia — only affects embedded Latin/English in code-switched
    text), then keeps only Unicode letters (L*), combining marks (M* —
    this is what preserves matras/virama), and digits (N*). Everything
    else (punctuation, symbols, control characters) is dropped. Whitespace
    is collapsed to single spaces.
    """
    if text is None:
        return ""

    text = text.lower()
    kept_chars = []
    for ch in text:
        if ch.isspace():
            kept_chars.append(" ")
            continue
        category = unicodedata.category(ch)  # e.g. 'Lo', 'Mn', 'Mc', 'Nd', 'Po'
        if category[0] in ("L", "M", "N"):
            kept_chars.append(ch)
        # else: drop (punctuation, symbols, control chars, etc.)

    normalized = "".join(kept_chars)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


@dataclass
class LanguageMetrics:
    language: str
    n_samples: int
    wer: float
    cer: float
    avg_audio_duration: float
    avg_inference_seconds: float
    avg_real_time_factor: float


def compute_metrics_for_language(
    language: str,
    references: List[str],
    hypotheses: List[str],
    durations: List[float],
    inference_times: List[float],
    rtfs: List[float],
) -> LanguageMetrics:
    """
    references/hypotheses must be pre-normalized (call normalize_text on
    each before passing in) so WER/CER reflect recognition errors, not
    formatting differences.
    """
    assert len(references) == len(hypotheses), "references and hypotheses must be same length"

    wer = jiwer.wer(references, hypotheses)
    cer = jiwer.cer(references, hypotheses)

    return LanguageMetrics(
        language=language,
        n_samples=len(references),
        wer=wer,
        cer=cer,
        avg_audio_duration=sum(durations) / len(durations) if durations else float("nan"),
        avg_inference_seconds=sum(inference_times) / len(inference_times) if inference_times else float("nan"),
        avg_real_time_factor=sum(rtfs) / len(rtfs) if rtfs else float("nan"),
    )
