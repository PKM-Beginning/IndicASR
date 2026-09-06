import { useState } from 'react'
import { IconCopy, IconDownload, IconReset, IconCheck } from './icons.jsx'
import { LANGUAGES } from '../data/content.js'

function languageLabel(code) {
  return LANGUAGES.find((l) => l.code === code)?.label || code
}

export default function TranscriptionPanel({ result, onReset }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    if (!result) return
    await navigator.clipboard.writeText(result.transcription)
    setCopied(true)
    setTimeout(() => setCopied(false), 1600)
  }

  const handleDownload = () => {
    if (!result) return
    const blob = new Blob([result.transcription], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'indicasr-transcription.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  if (!result) {
    return (
      <div className="flex h-full min-h-[220px] flex-col items-center justify-center rounded-xl border border-hairline/70 bg-raised/40 px-6 text-center">
        <p className="text-[13.5px] text-mute">
          Your transcription will appear here once you run a clip through the model.
        </p>
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col rounded-xl border border-hairline/70 bg-raised/40 p-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="rounded-full border border-hairline px-2.5 py-1 text-[11.5px] text-mute">
            {languageLabel(result.language)}
          </span>
          {result.isMock && (
            <span className="rounded-full border border-signal-dim bg-signal/10 px-2.5 py-1 text-[11.5px] text-signal-soft">
              Demo mode
            </span>
          )}
        </div>
        <span className="text-[11.5px] text-mute">{result.model}</span>
      </div>

      <p className="mt-4 flex-1 whitespace-pre-wrap text-[15.5px] leading-relaxed text-ivory">
        {result.transcription}
      </p>

      <div className="mt-5 flex items-center justify-between border-t border-hairline/70 pt-4">
        <span className="text-[12px] text-mute">
          Processed in {result.processing_time?.toFixed ? result.processing_time.toFixed(2) : result.processing_time}s
        </span>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleCopy}
            className="flex items-center gap-1.5 rounded-lg border border-hairline px-3 py-1.5 text-[12.5px] text-ivory transition-colors hover:border-signal-dim"
          >
            {copied ? <IconCheck className="h-3.5 w-3.5 text-wave" /> : <IconCopy className="h-3.5 w-3.5" />}
            {copied ? 'Copied' : 'Copy'}
          </button>
          <button
            type="button"
            onClick={handleDownload}
            className="flex items-center gap-1.5 rounded-lg border border-hairline px-3 py-1.5 text-[12.5px] text-ivory transition-colors hover:border-signal-dim"
          >
            <IconDownload className="h-3.5 w-3.5" /> Download
          </button>
          <button
            type="button"
            onClick={onReset}
            className="flex items-center gap-1.5 rounded-lg border border-hairline px-3 py-1.5 text-[12.5px] text-mute transition-colors hover:border-red-400/60 hover:text-red-300"
          >
            <IconReset className="h-3.5 w-3.5" /> Clear
          </button>
        </div>
      </div>
    </div>
  )
}
