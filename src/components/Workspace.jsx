import { useMemo, useState } from 'react'
import LanguageSelector from './LanguageSelector.jsx'
import AudioInput from './AudioInput.jsx'
import WaveformDisplay from './WaveformDisplay.jsx'
import TranscriptionPanel from './TranscriptionPanel.jsx'
import { useAudioPeaks } from '../hooks/useAudioPeaks.js'
import { transcribeAudio, isBackendConfigured } from '../services/api.js'

export default function Workspace() {
  const [language, setLanguage] = useState('auto')
  const [file, setFile] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState(null)

  const { peaks, duration } = useAudioPeaks(file)
  const audioUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file])

  const handleFileReady = (nextFile) => {
    setFile(nextFile)
    setResult(null)
  }

  const handleTranscribe = async () => {
    if (!file) return
    setIsProcessing(true)
    try {
      const response = await transcribeAudio(file, language, { audioDurationSeconds: duration })
      setResult(response)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleReset = () => {
    setFile(null)
    setResult(null)
  }

  return (
    <section id="workspace" className="section">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="section-heading">Transcription workspace</h2>
          <p className="section-sub">
            Upload a clip, drag one in, or record from your microphone. The model runs against
            the live backend when one is configured, and falls back to a demo response otherwise.
          </p>
        </div>
        {!isBackendConfigured && (
          <span className="mt-1 inline-block w-fit rounded-full border border-signal-dim bg-signal/10 px-3 py-1 text-[12px] text-signal-soft">
            Running in demo mode — no backend connected
          </span>
        )}
      </div>

      <div className="mt-8 grid gap-5 lg:grid-cols-[1.05fr_0.95fr]">
        <div className="panel p-5 sm:p-6">
          <p className="mb-3 text-[12.5px] font-medium text-mute">Language</p>
          <LanguageSelector value={language} onChange={setLanguage} />

          <p className="mb-3 mt-6 text-[12.5px] font-medium text-mute">Audio</p>
          <AudioInput onFileReady={handleFileReady} disabled={isProcessing} />

          {file && (
            <div className="mt-5">
              <div className="flex items-center justify-between text-[12px] text-mute">
                <span className="truncate">{file.name}</span>
                {duration && <span>{duration.toFixed(1)}s</span>}
              </div>
              <div className="mt-2 rounded-lg border border-hairline/70 bg-raised/40 px-3 py-2">
                <WaveformDisplay peaks={peaks} isProcessing={isProcessing} />
              </div>
              {audioUrl && !isProcessing && (
                <audio controls src={audioUrl} className="mt-3 w-full" style={{ height: 32 }} />
              )}
            </div>
          )}

          <button
            type="button"
            onClick={handleTranscribe}
            disabled={!file || isProcessing}
            className="btn-primary mt-6 w-full disabled:pointer-events-none disabled:opacity-40"
          >
            {isProcessing ? 'Transcribing…' : 'Transcribe Audio'}
          </button>
        </div>

        <TranscriptionPanel result={result} onReset={handleReset} />
      </div>
    </section>
  )
}
