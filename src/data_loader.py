"""
data_loader.py — IndicASR

Loads evaluation/training subsets from the datasets documented in
DATASETS.md (Kathbath, FLEURS, Common Voice) and returns them in a common
format: a list of dicts with keys {audio_path_or_array, sampling_rate,
transcript, language, dataset_name, sample_id}.

This module does the actual network calls (via the `datasets` library) — it
has NOT been run in this environment (no network access here), so treat it
as ready-to-run code for your Colab/Kaggle session, not as something whose
output has already been verified. Run `python src/data_loader.py --smoke_test`
first on a tiny sample to confirm access/auth works before scaling up.

Concept notes (since you're new to some of this):
- "streaming=True" in HF `datasets` lets you pull examples one at a time
  instead of downloading the whole dataset up front — important for Kathbath,
  which is large in total even though we only want a few thousand clips.
- Kathbath and Common Voice are "gated": you must accept the dataset's terms
  on the Hugging Face website once, then run `huggingface-cli login` locally
  so your script is authenticated.
"""

import argparse
import os
import random
from dataclasses import dataclass, asdict
from typing import Iterator

import yaml


@dataclass
class Sample:
    sample_id: str
    dataset_name: str
    language: str
    transcript: str
    audio_array: object = None
    audio_path: str = None
    sampling_rate: int = 16000


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _iter_kathbath(language: str, split: str, max_samples: int) -> Iterator[Sample]:
    """
    Streams Kathbath for one language/split.
    Requires: `huggingface-cli login` done once, and dataset terms accepted
    at https://huggingface.co/datasets/ai4bharat/Kathbath
    """
    from datasets import load_dataset

    # Kathbath's HF config naming follows the language name, e.g. "hindi",
    # "bengali", "telugu", "odia" — map ISO codes to that here.
    lang_name_map = {"hi": "hindi", "bn": "bengali", "te": "telugu", "or": "odia"}
    hf_lang = lang_name_map[language]

    ds = load_dataset(
        "ai4bharat/Kathbath",
        hf_lang,
        split=split,
        streaming=True,
    )

    for i, row in enumerate(ds):
        if i >= max_samples:
            break
        yield Sample(
            sample_id=f"kathbath_{hf_lang}_{i}",
            dataset_name="kathbath",
            language=language,
            transcript=row.get("text") or row.get("transcript") or row.get("sentence"),
            audio_path=row["audio"]["path"] if "audio" in row else None,
            sampling_rate=row["audio"].get("sampling_rate", 16000) if "audio" in row else 16000,
        )


def _iter_fleurs(language: str, lang_config: str, split: str, max_samples: int) -> Iterator[Sample]:
    """Streams FLEURS for one language config (e.g. 'hi_in')."""
    from datasets import load_dataset

    ds = load_dataset(
        "google/fleurs",
        lang_config,
        split=split,
        streaming=True,
    )

    for i, row in enumerate(ds):
        if i >= max_samples:
            break

        audio = row["audio"]

        # Current Hugging Face datasets may expose audio through
        # torchcodec AudioDecoder rather than the old dictionary format.
        try:
            audio_data = audio.get_all_samples()
            sampling_rate = audio_data.sample_rate
            audio_array = audio_data.data
        except AttributeError:
            # Fallback for older dictionary-style audio objects.
            audio_array = audio["array"]
            sampling_rate = audio.get("sampling_rate", 16000)

        yield Sample(
            sample_id=f"fleurs_{lang_config}_{i}",
            dataset_name="fleurs",
            language=language,
            transcript=row["transcription"],
            audio_array=audio_array,
            audio_path=None,
            sampling_rate=int(sampling_rate),
        )


def _iter_common_voice(language: str, split: str, max_samples: int, cv_version: str = "17_0") -> Iterator[Sample]:
    """
    Streams a Common Voice release for one language.
    Requires: `huggingface-cli login` + accepting CV terms once.
    """
    from datasets import load_dataset

    ds = load_dataset(
        f"mozilla-foundation/common_voice_{cv_version}",
        language,
        split=split,
        streaming=True,
    )

    for i, row in enumerate(ds):
        if i >= max_samples:
            break
        yield Sample(
            sample_id=f"cv{cv_version}_{language}_{i}",
            dataset_name="common_voice",
            language=language,
            transcript=row["sentence"],
            audio_path=row["audio"]["path"] if "audio" in row else None,
            sampling_rate=row["audio"].get("sampling_rate", 16000) if "audio" in row else 16000,
        )


def load_eval_samples(config: dict) -> list:
    """
    Reads configs/baseline.yaml-style config and returns a flat list of
    Sample objects across all configured languages and datasets, capped at
    config['data']['max_eval_samples'] per (dataset, language) pair.
    """
    random.seed(config.get("reproducibility", {}).get("seed", 42))

    languages = config["data"]["languages"]
    max_n = config["data"]["max_eval_samples"]
    all_samples = []

    for dset in config["data"]["datasets"]:
        name = dset["name"]
        split = dset["split"]

        for lang in languages:
            if name == "kathbath":
                samples = list(_iter_kathbath(lang, split, max_n))
            elif name == "fleurs":
                lang_cfg = dset["lang_config_map"][lang]
                samples = list(_iter_fleurs(lang, lang_cfg, split, max_n))
            elif name == "common_voice":
                samples = list(_iter_common_voice(lang, split, max_n))
            else:
                raise ValueError(f"Unknown dataset name in config: {name}")

            print(f"[data_loader] {name}/{lang}: loaded {len(samples)} samples")
            all_samples.extend(samples)

    return all_samples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/baseline.yaml")
    parser.add_argument(
        "--smoke_test",
        action="store_true",
        help="Override max_eval_samples to 5 for a fast auth/connectivity check.",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    if args.smoke_test:
        config["data"]["max_eval_samples"] = 5
        print("[data_loader] Running smoke test with 5 samples per (dataset, language).")

    samples = load_eval_samples(config)
    print(f"[data_loader] Total samples loaded: {len(samples)}")
    for s in samples[:3]:
        print(asdict(s))


if __name__ == "__main__":
    main()
