export const LANGUAGES = [
  { code: 'auto', label: 'Auto Detect' },
  { code: 'hi', label: 'Hindi' },
  { code: 'bn', label: 'Bengali' },
  { code: 'te', label: 'Telugu' },
  { code: 'or', label: 'Odia' }
]

export const PIPELINE_STAGES = [
  { title: 'Audio', detail: 'Uploaded file, drag-and-drop, or a live microphone capture.' },
  { title: 'Preprocessing', detail: 'Resampling and normalization to a common 16 kHz input.' },
  { title: 'Speech Recognition', detail: 'IndicConformer or Whisper-small decodes the audio.' },
  { title: 'Transcription', detail: 'Decoded text is assembled and script-normalized.' },
  { title: 'Evaluation', detail: 'Output is scored against reference transcripts (WER / CER).' }
]

export const ARCHITECTURE_STAGES = [
  'Audio input',
  '16 kHz preprocessing',
  'IndicConformer / Whisper',
  'Text normalization',
  'WER / CER evaluation',
  'Result'
]

export const ERROR_CATEGORIES = [
  {
    id: 'substitution',
    label: 'Substitutions',
    detail: 'A reference word is recognized as a different word.'
  },
  {
    id: 'deletion',
    label: 'Deletions',
    detail: 'A word present in the reference is missing from the hypothesis.'
  },
  {
    id: 'insertion',
    label: 'Insertions',
    detail: 'An extra word appears in the hypothesis with no counterpart in the reference.'
  },
  {
    id: 'script',
    label: 'Language / script errors',
    detail: 'Output is produced in the wrong script or language for a multilingual input.'
  },
  {
    id: 'noise',
    label: 'Noisy speech',
    detail: 'Background noise, overlapping speech, or low signal quality degrades recognition.'
  }
]

export const MODEL_FACTS = [
  { label: 'Model', value: 'IndicConformer' },
  { label: 'Architecture', value: 'Hybrid CTC + RNNT' },
  { label: 'Languages supported (base model)', value: '22 Indian languages' },
  { label: 'Demo languages in this build', value: 'Hindi, Bengali, Telugu, Odia' }
]
