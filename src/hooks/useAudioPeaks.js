import { useEffect, useState } from 'react'

const BAR_COUNT = 72

/**
 * Decodes an audio file into `BAR_COUNT` normalized peak values (0–1)
 * so the workspace can render a real waveform for the loaded clip
 * instead of a generic placeholder.
 */
export function useAudioPeaks(file) {
  const [peaks, setPeaks] = useState(null)
  const [duration, setDuration] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!file) {
      setPeaks(null)
      setDuration(null)
      return
    }

    let cancelled = false
    setError(null)

    async function decode() {
      try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext
        const ctx = new AudioCtx()
        const arrayBuffer = await file.arrayBuffer()
        const audioBuffer = await ctx.decodeAudioData(arrayBuffer.slice(0))
        const channel = audioBuffer.getChannelData(0)
        const blockSize = Math.floor(channel.length / BAR_COUNT) || 1
        const result = new Array(BAR_COUNT).fill(0).map((_, i) => {
          const start = i * blockSize
          let sum = 0
          for (let j = 0; j < blockSize; j++) {
            sum += Math.abs(channel[start + j] || 0)
          }
          return sum / blockSize
        })
        const max = Math.max(...result, 0.0001)
        const normalized = result.map((v) => Math.max(0.06, v / max))

        if (!cancelled) {
          setPeaks(normalized)
          setDuration(audioBuffer.duration)
        }
        ctx.close().catch(() => {})
      } catch (err) {
        if (!cancelled) {
          setError('Could not decode this audio file for preview.')
          setPeaks(null)
        }
      }
    }

    decode()
    return () => {
      cancelled = true
    }
  }, [file])

  return { peaks, duration, error }
}
