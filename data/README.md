# data/

Raw and processed audio/transcripts are NOT committed to git (see
`.gitignore`) — they're pulled at runtime by `src/data_loader.py` from the
sources documented in `../DATASETS.md`.

Expected layout once populated (created automatically by the pipeline):

```
data/
├── raw/            # cached audio pulled from HF datasets
├── processed/       # resampled/normalized 16kHz mono wavs
└── manifests/        # csv manifests: sample_id, dataset, language, transcript, path
```

To populate this directory for the first time:

```bash
huggingface-cli login          # once, needed for Kathbath + Common Voice (gated)
# then accept dataset terms in a browser at:
#   https://huggingface.co/datasets/ai4bharat/Kathbath
#   https://huggingface.co/datasets/mozilla-foundation/common_voice_17_0

python src/data_loader.py --smoke_test          # 5 samples/lang, verifies auth + connectivity
python src/data_loader.py --config configs/baseline.yaml   # full configured pull
```
