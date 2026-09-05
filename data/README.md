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
hf auth login       # once, needed if Kathbath requires accepting dataset terms
# then, if prompted, accept dataset terms in a browser at:
#   https://huggingface.co/datasets/ai4bharat/Kathbath
#   https://huggingface.co/datasets/ai4bharat/Kathbath

python src/data_loader.py --smoke_test          # 5 samples/lang, verifies auth + connectivity
python src/data_loader.py --config configs/baseline.yaml   # full configured pull
```

This project uses only Kathbath and Google FLEURS (see `../DATASETS.md`).
FLEURS is ungated and needs no login step.
