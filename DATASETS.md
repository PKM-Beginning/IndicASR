# Datasets — IndicASR

All datasets below are real, publicly documented sources. Nothing here is
fabricated; sample counts and durations marked "TBD (Phase 2 run)" will be
filled in with actual numbers once the download/exploration notebook is run,
not estimated in advance.

---

## 1. AI4Bharat Kathbath (primary evaluation + fine-tuning source)

- **Source**: https://huggingface.co/datasets/ai4bharat/Kathbath
- **Paper**: Javed et al., "IndicSUPERB: A Speech Processing Universal
  Performance Benchmark for Indian Languages" (arXiv:2208.11761)
- **Description**: Human-labeled ASR dataset, 1,684 hours of labelled speech
  across 12 Indian languages, collected from 1,218 contributors across 203
  districts in India. Split into "known" and "hard" test sets per language.
- **Languages used in this project**: Hindi, Bengali, Telugu, Odia
- **License**: Packaging released as CC0 by AI4Bharat (HF page); the
  government AIKosh/Bhashini mirror lists CC BY-SA 4.0 for individual
  language subsets — confirm the specific license tag shown on the HF
  dataset card for the config you download before redistributing anything.
- **Access note**: gated on Hugging Face — requires agreeing to share
  contact info before download (`huggingface-cli login` + accept dataset
  terms on the dataset page).
- **Samples/duration used**: TBD (Phase 2 run) — target 500–2,000 clips per
  language from the "test known" split for evaluation, small train subset
  from "train" split for Phase 8 LoRA fine-tuning.
- **Why suitable**: only human-labeled, multi-district Indian-language ASR
  benchmark of this scale that is freely downloadable and includes Odia
  natively, with a documented "hard" split that's useful for error analysis.

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

## 3. Mozilla Common Voice (noise-robustness experiment source)

- **Source**: https://commonvoice.mozilla.org/en/datasets ,
  mirrored at https://huggingface.co/datasets/mozilla-foundation/common_voice_17_0
- **Description**: Crowdsourced, CC0-licensed multilingual speech corpus.
  Hindi, Bengali, Telugu and Odia are all present as configs in current
  releases.
- **License**: CC0
- **Samples/duration used**: TBD (Phase 2 run) — small clean subset per
  language, used as the source audio for the controlled-noise experiment
  (Phase 6), since its crowdsourced recording conditions are closer to
  "clean but not studio-perfect" than Kathbath/FLEURS.
- **Why suitable**: gives a second, differently-collected data source and
  is the most permissively licensed of the three (CC0), useful for any
  audio we may want to lightly transform/redistribute in demo form.

## 4. Noise source for SNR experiments (Phase 6) — TBD

Not yet selected. Candidates to verify in Phase 2: MUSAN (freely licensed
noise/music/speech corpus) or ESC-50 (environmental sound classification,
CC-BY). Will confirm actual availability/license before use rather than
assume — no noise audio will be used without a verified real source and
license.

## Explicitly not used (with reason)

- **MUCS**: requires separate per-dataset registration; not pulled in
  unless the code-switching experiment specifically needs it and the above
  three sources prove insufficient.
- **GramVaani**: call-center audio, more licensing friction; same
  treatment as MUCS.
- **IndicWhisper / Vistaar benchmark numbers**: used only as external
  published reference points in the README discussion, never reported as
  results of this project's own experiments.
