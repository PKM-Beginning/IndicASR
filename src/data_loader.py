"""
data_loader.py — IndicASR

Loads evaluation/training subsets from Kathbath and FLEURS (see
DATASETS.md) and returns them in a common format: a list of Sample objects
carrying the decoded audio array + sampling rate + transcript directly —
not just a file path, since streamed HF datasets don't guarantee a real
path on disk.

This module has NOT been run in this environment (no network access here)
— treat it as ready-to-run code for your Colab/Kaggle session, not as
already-verified output. Run `python src/data_loader.py --smoke_test`
first on a tiny sample to confirm access/schema assumptions hold before
scaling up. If the actual schema differs from what's documented here
(schemas do change), the smoke test will surface a KeyError immediately —
report that back rather than silently patching around it.

Concept notes (since you're new to some of this):
- "streaming=True" in HF `datasets` lets you pull examples one at a time
  instead of downloading the whole dataset up front — important for
  Kathbath, which is large in total even though we only want a few
  thousand clips.
- Kathbath's `audio_filepath` column is an HF `Audio` feature: when you
  iterate over a streamed row, HF decodes it on the fly into a dict of
  `{"array": np.ndarray, "sampling_rate": int, "path": str|None}` — the
  `path` key is often None in streaming mode, which is why this loader
  keeps the decoded array itself rather than assuming a file path.
"""

import argparse
from dataclasses import dataclass, asdict
from typing import Iterator, Optional

import numpy as np
import yaml


@dataclass
class Sample:
    sample_id: str
    dataset_name: str
    language: str
    transcript: str
    audio_array: Optional[np.ndarray] = None
    sampling_rate: int = 16000
    duration: Optional[float] = None


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _iter_kathbath(language: str, split: str, max_samples: int) -> Iterator[Sample]:
    """
    Streams the CURRENT ai4bharat/Kathbath (capital K, parquet) repo for one
    language config and split.

    Verified current schema (per the dataset card's dataset_info block):
        fname: string
        text: string            <- transcript
        audio_filepath: Audio   <- decodes to {"array", "sampling_rate", "path"}
        lang: string
        duration: float64
        gender: string
        speaker_id: int64

    Verified current splits: "train", "valid" ONLY. There is no
    test_known/test_unknown in this repo (that split naming belongs to the
    older, unmaintained lowercase "ai4bharat/kathbath" tar-file repo, which
    this project deliberately does not use).
    """
    from datasets import load_dataset

    if split not in ("train", "valid"):
        raise ValueError(
            f"Kathbath (ai4bharat/Kathbath) only has 'train' and 'valid' splits "
            f"in the current schema — got '{split}'."
        )

    ds = load_dataset(
        "ai4bharat/Kathbath",
        language,   # e.g. "hindi", "bengali", "telugu", "odia"
        split=split,
        streaming=True,
    )

    for i, row in enumerate(ds):
        if i >= max_samples:
            break
        audio = row["audio_filepath"]   # NOTE: field is audio_filepath, not audio
        yield Sample(
            sample_id=f"kathbath_{language}_{split}_{i}",
            dataset_name="kathbath",
            language=language,
            transcript=row["text"],
            audio_array=audio["array"],
            sampling_rate=audio["sampling_rate"],
            duration=row.get("duration"),
        )


def _iter_fleurs(language: str, lang_config: str, split: str, max_samples: int) -> Iterator[Sample]:
    """Streams FLEURS for one language config (e.g. 'hi_in')."""
    from datasets import load_dataset

    ds = load_dataset("google/fleurs", lang_config, split=split, streaming=True)

    for i, row in enumerate(ds):
        if i >= max_samples:
            break
        audio = row["audio"]
        yield Sample(
            sample_id=f"fleurs_{lang_config}_{i}",
            dataset_name="fleurs",
            language=language,
            transcript=row["transcription"],
            audio_array=audio["array"],
            sampling_rate=audio["sampling_rate"],
        )


def load_eval_samples(config: dict) -> list:
    """
    Reads a baseline.yaml-style config and returns a flat list of Sample
    objects across all configured languages and datasets, capped at
    config['data']['max_eval_samples'] per (dataset, language) pair.

    Uses Kathbath's 'valid' split and FLEURS's configured eval split for
    evaluation. Kathbath's 'train' split is intentionally NOT touched here
    — that's loaded separately in Phase 8 for fine-tuning only.
    """
    languages = config["data"]["languages"]
    max_n = config["data"]["max_eval_samples"]
    all_samples = []

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
                raise ValueError(f"Unknown or removed dataset name in config: {name}")

            print(f"[data_loader] {name}/{lang}: loaded {len(samples)} samples")
            all_samples.extend(samples)

    return all_samples


def load_kathbath_train_subset(config: dict, language: str, max_samples: int) -> list:
    """Separate helper for Phase 8 fine-tuning — pulls from Kathbath 'train' only."""
    return list(_iter_kathbath(language, "train", max_samples))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/baseline.yaml")
    parser.add_argument(
        "--smoke_test",
        action="store_true",
        help="Override max_eval_samples to 5 for a fast auth/schema check.",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    if args.smoke_test:
        config["data"]["max_eval_samples"] = 5
        print("[data_loader] Running smoke test with 5 samples per (dataset, language).")

    samples = load_eval_samples(config)
    print(f"[data_loader] Total samples loaded: {len(samples)}")
    for s in samples[:3]:
        d = asdict(s)
        d["audio_array"] = f"<array shape={s.audio_array.shape if s.audio_array is not None else None}>"
        print(d)


if __name__ == "__main__":
    main()
