# Datasets — IndicASR

All datasets below are real, publicly documented sources. Nothing here is
fabricated; sample counts and durations marked "TBD (Phase 2 run)" will be
filled in with actual numbers once the download/exploration notebook is run,
not estimated in advance.

---

## 1. AI4Bharat Kathbath (primary evaluation + fine-tuning source)

- **Source (current, actively maintained)**:
  https://huggingface.co/datasets/ai4bharat/Kathbath
  — parquet format, last updated within days at time of writing. This
  supersedes the older lowercase `ai4bharat/kathbath` repo (tar-file
  distribution with `test_known`/`test_unknown` splits) — that repo has not
  been updated in ~2 years and its splits are not what the current
  dataset card documents, so it is **not** the version this project uses.
- **Paper**: Javed et al., "IndicSUPERB: A Speech Processing Universal
  Performance Benchmark for Indian Languages" (arXiv:2208.11761)
- **Description**: Human-labeled ASR dataset, 1,684 hours of labelled speech
  across 12 Indian languages, collected from 1,218 contributors across 203
  districts in India.
- **Current schema** (verified from the dataset card's `dataset_info`,
  per language config, e.g. `bengali`):
  - `fname` (string)
  - `text` (string) — transcript
  - `audio_filepath` (Audio feature — **not** `audio`)
  - `lang` (string)
  - `duration` (float64)
  - `gender` (string)
  - `speaker_id` (int64)
- **Current splits**: only `train` and `valid`. There is **no** `test_known`
  or `test_unknown` split in this repo — that split naming belongs to the
  old lowercase repo. This project uses `valid` for evaluation and `train`
  for the Phase 8 fine-tuning subset.
- **Languages used in this project**: `hindi`, `bengali`, `telugu`, `odia`
  (config names, lowercase, matching AI4Bharat's 12 supported languages)
- **License**: **CC BY 4.0**, as stated directly in the current dataset
  card's YAML metadata (`license: cc-by-4.0`). This corrects the earlier
  version of this file, which cited CC0/CC BY-SA based on the older repo
  and a government mirror — neither applies to the repo actually used here.
- **Access note**: still appears gated on Hugging Face for some
  configs — run `huggingface-cli login` and accept any dataset terms shown
  on the page before downloading; confirm at run time in Phase 2 execution
  whether a given language config actually requires gating (this can
  change independent of the schema).
- **Samples/duration used**: TBD (Phase 2 run) — target up to 500–2,000
  clips per language from `valid` for evaluation; a small subset of
  `train` for Phase 8 LoRA fine-tuning.
- **Why suitable**: still the only human-labeled, multi-district
  Indian-language ASR benchmark of this scale that is freely downloadable
  and includes Odia natively.

## 2. Google FLEURS (secondary/independent evaluation set)

- **Source**: https://huggingface.co/datasets/google/fleurs
- **Paper**: Conneau et al., "FLEURS: Few-shot Learning Evaluation of
  Universal Representations of Speech" (arXiv:2205.12446)
- **Description**: Speech version of the FLoRes MT benchmark; ~2,009
  n-way parallel sentences per language read aloud, train/dev/test splits.
  Training sets have roughly 10 hours of supervision per language; distinct
  speakers between train and dev/test.
- **Languages used**: Hindi (`hi_in`), Bengali (`bn_in`), Telugu (`te_in`),
  Odia (`or_in`, listed as "Oriya" in the FLEURS language table)
- **License**: CC-BY
- **Samples/duration used**: TBD (Phase 2 run) — full FLEURS test split per
  language (small enough to use in full; will report exact counts after
  download).
- **Why suitable**: independently constructed from Kathbath (different
  speakers, different source text), so it lets us check whether the
  baseline's WER is dataset-specific or a general language-level pattern —
  directly answers "why does performance differ between languages."

## 3. Noise source for SNR experiments (Phase 6) — TBD

Not yet selected. Candidates to verify before Phase 6: MUSAN (freely
licensed noise/music/speech corpus) or ESC-50 (environmental sound
classification, CC-BY). Clean speech for this experiment will come from
Kathbath `valid` (the same evaluation set used for the baseline), with
synthetic noise mixed in at controlled SNR — not from Common Voice (see
below). Will confirm actual noise-dataset availability/license before use
rather than assume.

## Explicitly not used (with reason)

- **Mozilla Common Voice**: removed from the pipeline. Mozilla moved
  Common Voice distribution to the Mozilla Data Collective in October
  2025, and the `mozilla-foundation/common_voice_17_0` Hugging Face
  repository referenced in an earlier version of this plan is no longer a
  usable/current data source. If a Common-Voice-equivalent is needed later
  (e.g. for extra acoustic variety), it will be re-sourced from whatever
  Mozilla's current official distribution channel is at that time, verified
  first — not assumed to still be on that old HF repo.
- **MUCS**: requires separate per-dataset registration; not pulled in
  unless the code-switching experiment specifically needs it and Kathbath
  proves insufficient.
- **GramVaani**: call-center audio, more licensing friction; same
  treatment as MUCS.
- **IndicWhisper / Vistaar benchmark numbers**: used only as external
  published reference points in the README discussion, never reported as
  results of this project's own experiments.
