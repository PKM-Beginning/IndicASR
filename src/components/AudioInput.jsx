import { useCallback, useRef, useState } from 'react'
import { IconUpload, IconMic, IconStop } from './icons.jsx'
import { useAudioRecorder } from '../hooks/useAudioRecorder.js'

export default function AudioInput({ onFileReady, disabled }) {
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef(null)
  const recorder = useAudioRecorder()

  const handleFiles = useCallback(
    (fileList) => {
      const file = fileList?.[0]
      if (file && file.type.startsWith('audio/')) {
        onFileReady(file)
      }
    },
    [onFileReady]
  )

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault()
      setIsDragging(false)
      handleFiles(e.dataTransfer.files)
    },
    [handleFiles]
  )

  const handleRecordToggle = useCallback(async () => {
    if (recorder.isRecording) {
      const blob = await recorder.stop()
      if (blob) {
        const file = new File([blob], `recording-${Date.now()}.webm`, { type: blob.type })
        onFileReady(file)
      }
    } else {
      recorder.start()
    }
  }, [recorder, onFileReady])

  return (
    <div>
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => !disabled && inputRef.current?.click()}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed px-6 py-8 text-center transition-colors ${
          isDragging ? 'border-signal bg-signal/5' : 'border-hairline hover:border-signal-dim'
        } ${disabled ? 'pointer-events-none opacity-50' : ''}`}
      >
        <IconUpload className="h-5 w-5 text-mute" />
        <p className="mt-3 text-[13.5px] text-ivory">
          Drop an audio file, or <span className="text-signal-soft">browse</span>
        </p>
        <p className="mt-1 text-[12px] text-mute">WAV, MP3, or M4A</p>
        <input
          ref={inputRef}
          type="file"
          accept="audio/*"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      <div className="mt-3 flex items-center gap-3">
        <div className="h-px flex-1 bg-hairline" />
        <span className="text-[11.5px] uppercase tracking-wide text-mute/70">or</span>
        <div className="h-px flex-1 bg-hairline" />
      </div>

      <button
        type="button"
        onClick={handleRecordToggle}
        disabled={disabled || !recorder.isSupported}
        className={`mt-3 flex w-full items-center justify-center gap-2 rounded-xl border px-4 py-3 text-[13.5px] transition-colors ${
          recorder.isRecording
            ? 'border-wave bg-wave/10 text-wave'
            : 'border-hairline text-ivory hover:border-signal-dim'
        } ${disabled || !recorder.isSupported ? 'pointer-events-none opacity-50' : ''}`}
      >
        {recorder.isRecording ? (
          <>
            <IconStop className="h-4 w-4" /> Stop recording
          </>
        ) : (
          <>
            <IconMic className="h-4 w-4" /> Record from microphone
          </>
        )}
      </button>

      {recorder.error && <p className="mt-2 text-[12px] text-red-400">{recorder.error}</p>}
      {!recorder.isSupported && (
        <p className="mt-2 text-[12px] text-mute">
          Microphone recording isn't supported in this browser — file upload still works.
        </p>
      )}

      {recorder.isRecording && (
        <RecordingMeter level={recorder.level} />
      )}
    </div>
  )
}

function RecordingMeter({ level }) {
  return (
    <div className="mt-3 flex h-10 items-center justify-center gap-[3px] rounded-lg border border-hairline bg-raised/60 px-3">
      {Array.from({ length: 28 }).map((_, i) => {
        const distance = Math.abs(i - 14) / 14
        const bar = Math.max(0.08, level * (1 - distance * 0.6))
        return (
          <span
            key={i}
            className="w-[3px] flex-1 rounded-full bg-wave transition-[height] duration-75"
            style={{ height: `${10 + bar * 90}%` }}
          />
        )
      })}
    </div>
  )
}
