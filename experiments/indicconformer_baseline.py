"""
indicconformer_baseline.py — IndicASR, Phase 4

Runs IndicConformer-600M-Multilingual on the configured
(dataset, language) pairs.

Features:
- Uses the existing IndicASR data loader.
- Uses official IndicConformer CTC inference API.
- Calculates WER, CER and RTF.
- Saves every prediction immediately.
- Supports safe resume after interruption/disconnection.
- Rebuilds the final summary from ALL saved predictions.
- Keeps Whisper baseline completely separate.

IMPORTANT:
The model is gated on Hugging Face and requires accepted access.
"""

import argparse
import csv
import os
import sys
import time
from collections import defaultdict

import torch
from jiwer import wer, cer


# -------------------------------------------------------------------
# Allow imports from src/
# -------------------------------------------------------------------

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src")
)

from data_loader import load_config, _iter_kathbath, _iter_fleurs
from evaluation import normalize_text


# -------------------------------------------------------------------
# Language mapping
# -------------------------------------------------------------------

LANGUAGE_CODES = {
    "hindi": "hi",
    "bengali": "bn",
    "telugu": "te",
    "odia": "or",
}


# -------------------------------------------------------------------
# IndicConformer wrapper
# -------------------------------------------------------------------

class IndicConformerASR:

    def __init__(
        self,
        model_name="ai4bharat/indic-conformer-600m-multilingual",
        device="cuda",
    ):

        from transformers import AutoModel

        # Report requested/available device.
        if device == "cuda" and torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"

        print(
            f"[indicconformer] PyTorch CUDA available: "
            f"{torch.cuda.is_available()}"
        )

        if torch.cuda.is_available():
            print(
                f"[indicconformer] GPU: "
                f"{torch.cuda.get_device_name(0)}"
            )

        print(
            f"[indicconformer] Requested device: {device}"
        )

        print(
            f"[indicconformer] Loading model: "
            f"{model_name}"
        )

        self.model_name = model_name

        # IMPORTANT:
        # IndicConformer uses custom remote code and its own
        # ONNX execution provider/device handling.
        self.model = AutoModel.from_pretrained(
            model_name,
            trust_remote_code=True,
        )

        print(
            "[indicconformer] Model loaded successfully."
        )


    def transcribe(
        self,
        audio_array,
        sampling_rate,
        language,
    ):

        if language not in LANGUAGE_CODES:
            raise ValueError(
                f"Unsupported language: {language}"
            )

        if sampling_rate != 16000:
            raise ValueError(
                "IndicConformer expects 16kHz audio, "
                f"got {sampling_rate}Hz"
            )

        lang_code = LANGUAGE_CODES[language]

        # NumPy → PyTorch tensor
        wav = torch.tensor(
            audio_array,
            dtype=torch.float32,
        ).unsqueeze(0)

        audio_duration = (
            len(audio_array) / sampling_rate
        )

        start = time.perf_counter()

        with torch.no_grad():

            prediction = self.model(
                wav,
                lang_code,
                "ctc",
            )

        elapsed = (
            time.perf_counter() - start
        )

        # Official model normally returns decoded text.
        if isinstance(prediction, str):
            text = prediction
        else:
            text = str(prediction)

        rtf = (
            elapsed / audio_duration
            if audio_duration > 0
            else float("nan")
        )

        return {
            "prediction": text,
            "inference_seconds": elapsed,
            "audio_duration_seconds": audio_duration,
            "rtf": rtf,
        }


# -------------------------------------------------------------------
# Dataset iterator
# -------------------------------------------------------------------

def get_samples(
    dataset_name,
    language,
    dataset_config,
    max_samples,
):

    if dataset_name == "kathbath":

        split = dataset_config["eval_split"]

        return _iter_kathbath(
            language,
            split,
            max_samples,
        )

    elif dataset_name == "fleurs":

        lang_cfg = dataset_config[
            "lang_config_map"
        ][language]

        split = dataset_config["split"]

        return _iter_fleurs(
            language,
            lang_cfg,
            split,
            max_samples,
        )

    else:

        raise ValueError(
            f"Unknown dataset: {dataset_name}"
        )


# -------------------------------------------------------------------
# Resume support
# -------------------------------------------------------------------

def load_completed_ids(path):

    completed = set()

    if not os.path.exists(path):
        return completed

    with open(
        path,
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            sample_id = row.get("sample_id")

            if sample_id:
                completed.add(sample_id)

    return completed


# -------------------------------------------------------------------
# Rebuild summary from cumulative predictions CSV
# -------------------------------------------------------------------

def rebuild_summary(
    predictions_path,
    summary_path,
):

    if not os.path.exists(predictions_path):
        print(
            "[indicconformer] "
            "No predictions file found. "
            "Summary not generated."
        )
        return

    groups = defaultdict(
        lambda: {
            "references": [],
            "predictions": [],
            "durations": [],
            "inference_times": [],
            "rtfs": [],
        }
    )

    with open(
        predictions_path,
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            dataset = row["dataset"]
            language = row["language"]

            key = (
                dataset,
                language,
            )

            groups[key]["references"].append(
                row["reference_normalized"]
            )

            groups[key]["predictions"].append(
                row["prediction_normalized"]
            )

            groups[key]["durations"].append(
                float(row["audio_duration_s"])
            )

            groups[key]["inference_times"].append(
                float(row["inference_s"])
            )

            groups[key]["rtfs"].append(
                float(row["real_time_factor"])
            )

    fieldnames = [
        "dataset",
        "language",
        "n_samples",
        "wer",
        "cer",
        "avg_audio_duration_s",
        "avg_inference_s",
        "avg_rtf",
    ]

    with open(
        summary_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for (
            dataset,
            language,
        ), data in sorted(groups.items()):

            references = data["references"]
            predictions = data["predictions"]

            if not references:
                continue

            group_wer = wer(
                references,
                predictions,
            )

            group_cer = cer(
                references,
                predictions,
            )

            durations = data["durations"]
            inference_times = data[
                "inference_times"
            ]
            rtfs = data["rtfs"]

            avg_duration = (
                sum(durations)
                / len(durations)
            )

            avg_inference = (
                sum(inference_times)
                / len(inference_times)
            )

            avg_rtf = (
                sum(rtfs)
                / len(rtfs)
            )

            writer.writerow({

                "dataset":
                    dataset,

                "language":
                    language,

                "n_samples":
                    len(references),

                "wer":
                    f"{group_wer:.4f}",

                "cer":
                    f"{group_cer:.4f}",

                "avg_audio_duration_s":
                    f"{avg_duration:.3f}",

                "avg_inference_s":
                    f"{avg_inference:.3f}",

                "avg_rtf":
                    f"{avg_rtf:.3f}",
            })

            print(
                f"[summary] "
                f"{dataset}/{language}: "
                f"n={len(references)} | "
                f"WER={group_wer:.4f} | "
                f"CER={group_cer:.4f} | "
                f"RTF={avg_rtf:.3f}"
            )

    print()
    print(
        "[indicconformer] "
        "Cumulative summary rebuilt successfully."
    )


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        default="configs/baseline.yaml",
    )

    parser.add_argument(
        "--smoke_test",
        action="store_true",
        help="Run 5 samples per dataset/language.",
    )

    parser.add_argument(
        "--model",
        default=(
            "ai4bharat/"
            "indic-conformer-600m-multilingual"
        ),
    )

    args = parser.parse_args()

    # ----------------------------------------------------------------
    # Load configuration
    # ----------------------------------------------------------------

    config = load_config(args.config)

    if args.smoke_test:

        config["data"]["max_eval_samples"] = 5

        print(
            "[indicconformer] "
            "SMOKE TEST MODE: "
            "5 samples per dataset/language."
        )

    max_samples = (
        config["data"]["max_eval_samples"]
    )

    languages = config["data"]["languages"]

    # ----------------------------------------------------------------
    # Output paths
    # ----------------------------------------------------------------

    output_dir = (
        "results/indicconformer"
    )

    os.makedirs(
        output_dir,
        exist_ok=True,
    )

    predictions_path = os.path.join(
        output_dir,
        "indicconformer_predictions.csv",
    )

    summary_path = os.path.join(
        output_dir,
        "indicconformer_summary.csv",
    )

    # ----------------------------------------------------------------
    # Resume support
    # ----------------------------------------------------------------

    completed_ids = load_completed_ids(
        predictions_path
    )

    if completed_ids:

        print(
            f"[indicconformer] "
            f"Found {len(completed_ids)} "
            f"completed samples."
        )

        print(
            "[indicconformer] "
            "Completed samples will be skipped."
        )

    # ----------------------------------------------------------------
    # Load model
    # ----------------------------------------------------------------

    asr = IndicConformerASR(
        model_name=args.model,
        device=config["model"]["device"],
    )

    # ----------------------------------------------------------------
    # CSV setup
    # ----------------------------------------------------------------

    file_exists = os.path.exists(
        predictions_path
    )

    fieldnames = [
        "sample_id",
        "dataset",
        "language",
        "reference_raw",
        "prediction_raw",
        "reference_normalized",
        "prediction_normalized",
        "audio_duration_s",
        "inference_s",
        "real_time_factor",
        "wer",
        "cer",
    ]

    # ----------------------------------------------------------------
    # Open predictions file in append mode
    # ----------------------------------------------------------------

    with open(
        predictions_path,
        "a",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )

        if not file_exists:

            writer.writeheader()
            f.flush()

        # ------------------------------------------------------------
        # Dataset loop
        # ------------------------------------------------------------

        for dataset_config in (
            config["data"]["datasets"]
        ):

            dataset_name = (
                dataset_config["name"]
            )

            for language in languages:

                print()
                print("=" * 60)
                print(
                    f"[indicconformer] "
                    f"{dataset_name}/{language}"
                )
                print("=" * 60)

                samples = get_samples(
                    dataset_name,
                    language,
                    dataset_config,
                    max_samples,
                )

                processed = 0

                # ----------------------------------------------------
                # Process samples
                # ----------------------------------------------------

                for sample in samples:

                    sample_id = sample.sample_id

                    if sample_id in completed_ids:

                        print(
                            f"[indicconformer] "
                            f"Skipping completed: "
                            f"{sample_id}"
                        )

                        continue

                    # ------------------------------------------------
                    # Inference
                    # ------------------------------------------------

                    result = asr.transcribe(
                        audio_array=(
                            sample.audio_array
                        ),
                        sampling_rate=(
                            sample.sampling_rate
                        ),
                        language=language,
                    )

                    reference_raw = (
                        sample.transcript
                    )

                    prediction_raw = (
                        result["prediction"]
                    )

                    # ------------------------------------------------
                    # Normalization
                    # ------------------------------------------------

                    reference_normalized = (
                        normalize_text(
                            reference_raw
                        )
                    )

                    prediction_normalized = (
                        normalize_text(
                            prediction_raw
                        )
                    )

                    # ------------------------------------------------
                    # Metrics
                    # ------------------------------------------------

                    sample_wer = wer(
                        reference_normalized,
                        prediction_normalized,
                    )

                    sample_cer = cer(
                        reference_normalized,
                        prediction_normalized,
                    )

                    # ------------------------------------------------
                    # Save immediately
                    # ------------------------------------------------

                    writer.writerow({

                        "sample_id":
                            sample_id,

                        "dataset":
                            dataset_name,

                        "language":
                            language,

                        "reference_raw":
                            reference_raw,

                        "prediction_raw":
                            prediction_raw,

                        "reference_normalized":
                            reference_normalized,

                        "prediction_normalized":
                            prediction_normalized,

                        "audio_duration_s":
                            (
                                f"{result['audio_duration_seconds']:.3f}"
                            ),

                        "inference_s":
                            (
                                f"{result['inference_seconds']:.3f}"
                            ),

                        "real_time_factor":
                            (
                                f"{result['rtf']:.3f}"
                            ),

                        "wer":
                            f"{sample_wer:.4f}",

                        "cer":
                            f"{sample_cer:.4f}",
                    })

                    # Force data to disk immediately.
                    f.flush()

                    # Mark as completed only AFTER successful save.
                    completed_ids.add(sample_id)

                    processed += 1

                    print(
                        f"{language:8s} | "
                        f"WER={sample_wer:.3f} | "
                        f"CER={sample_cer:.3f} | "
                        f"RTF={result['rtf']:.3f}"
                    )

                print(
                    f"[indicconformer] "
                    f"New samples processed: "
                    f"{processed}"
                )

    # ----------------------------------------------------------------
    # IMPORTANT:
    # Rebuild summary from ALL cumulative predictions.
    # ----------------------------------------------------------------

    rebuild_summary(
        predictions_path,
        summary_path,
    )

    print()
    print(
        "[indicconformer] "
        "Benchmark run finished."
    )

    print(
        f"[indicconformer] "
        f"Predictions: {predictions_path}"
    )

    print(
        f"[indicconformer] "
        f"Summary: {summary_path}"
    )


if __name__ == "__main__":
    main()