"""
verify_audio.py — IndicASR, Phase 3 pre-check

Confirms that Kathbath's audio_filepath column decodes to REAL, usable
audio arrays (not just metadata or a null path) before we trust it inside
the inference pipeline. This has NOT been run in this environment (no
network access here) — run it yourself and paste the output back.

What it checks, per sample, and why each check matters:

1. audio_array is not None and is a numpy ndarray
   -> catches the case where HF's Audio feature failed to decode and just
      returned a path/None (this is the exact failure mode a path-only
      assumption would hide until inference silently crashes or trains on
      garbage).
2. audio_array.dtype is floating point and array is non-empty
   -> catches empty/corrupt decodes.
3. audio_array is not silence
   -> np.abs(audio_array).max() > a small epsilon; an all-zero array
      would "load" successfully but contain nothing to transcribe.
4. sampling_rate is a sane positive integer (typically 16000 or 48000)
   -> if it's something unexpected, resampling logic in preprocessing.py
      needs to know before, not after, inference.
5. actual audio duration (len(array)/sampling_rate) is compared against
   the dataset's own reported `duration` field
   -> a large mismatch would mean either the decode is wrong or the
      metadata is wrong; either is worth knowing before trusting WER
      numbers computed on top of it.

Usage:
    python src/verify_audio.py --config configs/baseline.yaml --n 5
"""

import argparse

import numpy as np

from data_loader import load_config, _iter_kathbath


def verify_language(language: str, split: str, n: int, duration_tolerance: float = 0.5):
    print(f"\n=== Verifying Kathbath / {language} / {split} (n={n}) ===")
    checked = 0
    failures = 0

    for sample in _iter_kathbath(language, split, n):
        checked += 1
        issues = []

        arr = sample.audio_array
        if arr is None or not isinstance(arr, np.ndarray):
            issues.append(f"audio_array is not a numpy array (got {type(arr)})")
        else:
            if arr.size == 0:
                issues.append("audio_array is empty")
            elif not np.issubdtype(arr.dtype, np.floating):
                issues.append(f"unexpected dtype {arr.dtype} (expected float)")
            elif np.abs(arr).max() < 1e-6:
                issues.append("audio_array appears to be silence (max amplitude ~0)")

        if sample.sampling_rate is None or sample.sampling_rate <= 0:
            issues.append(f"invalid sampling_rate: {sample.sampling_rate}")

        if arr is not None and isinstance(arr, np.ndarray) and arr.size > 0 and sample.sampling_rate:
            computed_duration = len(arr) / sample.sampling_rate
            if sample.duration is not None:
                diff = abs(computed_duration - sample.duration)
                if diff > duration_tolerance:
                    issues.append(
                        f"duration mismatch: computed={computed_duration:.2f}s "
                        f"vs metadata={sample.duration:.2f}s (diff={diff:.2f}s)"
                    )

        if issues:
            failures += 1
            print(f"  [FAIL] {sample.sample_id}: {'; '.join(issues)}")
        else:
            dur = len(arr) / sample.sampling_rate
            print(
                f"  [OK]   {sample.sample_id}: shape={arr.shape}, "
                f"sr={sample.sampling_rate}, duration={dur:.2f}s, "
                f"transcript_preview='{sample.transcript[:40]}...'"
            )

    print(f"--- {language}: {checked - failures}/{checked} samples passed ---")
    return checked, failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/baseline.yaml")
    parser.add_argument("--n", type=int, default=5, help="samples to check per language")
    args = parser.parse_args()

    config = load_config(args.config)
    languages = config["data"]["languages"]
    kathbath_cfg = next(d for d in config["data"]["datasets"] if d["name"] == "kathbath")
    split = kathbath_cfg["eval_split"]

    total_checked, total_failed = 0, 0
    for lang in languages:
        checked, failed = verify_language(lang, split, args.n)
        total_checked += checked
        total_failed += failed

    print(f"\n=== SUMMARY: {total_checked - total_failed}/{total_checked} samples passed across "
          f"{len(languages)} languages ===")
    if total_failed > 0:
        print("FIX BEFORE PROCEEDING: some samples failed verification — do not trust "
              "downstream WER/CER numbers until these are resolved.")
    else:
        print("All checked samples produced real, non-silent audio arrays with sane "
              "sampling rates and durations consistent with metadata.")


if __name__ == "__main__":
    main()
