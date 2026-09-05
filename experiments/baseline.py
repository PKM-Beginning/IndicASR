"""
baseline.py — IndicASR, Phase 3/4 orchestration

Runs: data_loader -> preprocessing -> WhisperASR -> evaluation, for every
(dataset, language) pair configured in configs/baseline.yaml.

This has NOT been executed in this environment (no network/GPU access
here). Run it yourself on Colab/Kaggle and paste back the console output
and the generated results/metrics/*.csv files — nothing here should be
treated as a real result until that happens.

Usage:
    python experiments/baseline.py --config configs/baseline.yaml
    python experiments/baseline.py --config configs/baseline.yaml --smoke_test   # 5 samples/lang
"""

import argparse
import csv
import os
import sys

# allow running from repo root: `python experiments/baseline.py`
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from data_loader import load_config, _iter_kathbath, _iter_fleurs  # noqa: E402
from preprocessing import prepare_for_whisper  # noqa: E402
from inference import WhisperASR  # noqa: E402
from evaluation import normalize_text, compute_metrics_for_language  # noqa: E402


def run_dataset_language(asr, dataset_name, language, samples, predictions_writer):
    references, hypotheses = [], []
    durations, inference_times, rtfs = [], [], []

    for sample in samples:
        prepped = prepare_for_whisper(sample.audio_array, sample.sampling_rate)
        result = asr.transcribe(
            sample_id=sample.sample_id,
            audio_array=prepped,
            sampling_rate=16000,
            kathbath_language=language,
        )

        ref_norm = normalize_text(sample.transcript)
        hyp_norm = normalize_text(result.prediction)

        references.append(ref_norm)
        hypotheses.append(hyp_norm)
        durations.append(result.audio_duration_seconds)
        inference_times.append(result.inference_seconds)
        rtfs.append(result.real_time_factor)

        predictions_writer.writerow({
            "sample_id": sample.sample_id,
            "dataset": dataset_name,
            "language": language,
            "reference_raw": sample.transcript,
            "prediction_raw": result.prediction,
            "reference_normalized": ref_norm,
            "prediction_normalized": hyp_norm,
            "audio_duration_s": f"{result.audio_duration_seconds:.3f}",
            "inference_s": f"{result.inference_seconds:.3f}",
            "real_time_factor": f"{result.real_time_factor:.3f}",
            "language_forced": result.language_forced or "NONE_AUTODETECT",
        })

    return compute_metrics_for_language(
        language=language,
        references=references,
        hypotheses=hypotheses,
        durations=durations,
        inference_times=inference_times,
        rtfs=rtfs,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/baseline.yaml")
    parser.add_argument("--smoke_test", action="store_true",
                         help="Override max_eval_samples to 5 for a fast pipeline check.")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.smoke_test:
        config["data"]["max_eval_samples"] = 5
        print("[baseline] SMOKE TEST MODE: 5 samples per (dataset, language).")

    os.makedirs("results/metrics", exist_ok=True)

    asr = WhisperASR(
        model_name=config["model"]["name"],
        device=config["model"]["device"],
    )

    languages = config["data"]["languages"]
    max_n = config["data"]["max_eval_samples"]

    predictions_path = config["evaluation"]["predictions_path"]
    fieldnames = [
        "sample_id", "dataset", "language", "reference_raw", "prediction_raw",
        "reference_normalized", "prediction_normalized", "audio_duration_s",
        "inference_s", "real_time_factor", "language_forced",
    ]

    all_metrics = []

    with open(predictions_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for dset in config["data"]["datasets"]:
            name = dset["name"]
            for lang in languages:
                if name == "kathbath":
                    split = dset["eval_split"]
                    samples = list(_iter_kathbath(lang, split, max_n))
                elif name == "fleurs":
                    lang_cfg = dset["lang_config_map"][lang]
                    split = dset["split"]
                    samples = list(_iter_fleurs(lang, lang_cfg, split, max_n))
                else:
                    raise ValueError(f"Unknown dataset: {name}")

                if not samples:
                    print(f"[baseline] WARNING: 0 samples loaded for {name}/{lang} — skipping.")
                    continue

                print(f"[baseline] Running {name}/{lang} ({len(samples)} samples)...")
                metrics = run_dataset_language(asr, name, lang, samples, writer)
                all_metrics.append((name, metrics))
                print(
                    f"[baseline]   {name}/{lang}: WER={metrics.wer:.4f} CER={metrics.cer:.4f} "
                    f"(n={metrics.n_samples}, avg_rtf={metrics.avg_real_time_factor:.3f})"
                )

    summary_path = "results/metrics/baseline_summary.csv"
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["dataset", "language", "n_samples", "wer", "cer",
                          "avg_audio_duration_s", "avg_inference_s", "avg_rtf"])
        for dataset_name, m in all_metrics:
            writer.writerow([dataset_name, m.language, m.n_samples,
                              f"{m.wer:.4f}", f"{m.cer:.4f}",
                              f"{m.avg_audio_duration:.3f}", f"{m.avg_inference_seconds:.3f}",
                              f"{m.avg_real_time_factor:.3f}"])

    print(f"\n[baseline] Done. Per-sample predictions: {predictions_path}")
    print(f"[baseline] Per-language summary: {summary_path}")
    print("[baseline] These numbers are only real once you've actually run this script — "
          "report the console output and CSVs back before we treat any WER/CER as final.")


if __name__ == "__main__":
    main()
