import { useCallback, useEffect, useRef, useState } from 'react'

const isRecordingSupported =
  typeof navigator !== 'undefined' &&
  Boolean(navigator.mediaDevices) &&
  typeof window !== 'undefined' &&
  Boolean(window.MediaRecorder)

/**
 * Records microphone audio and exposes a live amplitude level (0–1)
 * for driving a waveform animation while recording.
 */
export function useAudioRecorder() {
  const [isRecording, setIsRecording] = useState(false)
  const [level, setLevel] = useState(0)
  const [error, setError] = useState(null)

  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const audioContextRef = useRef(null)
  const analyserRef = useRef(null)
  const rafRef = useRef(null)
  const streamRef = useRef(null)

  const stopMetering = useCallback(() => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current)
    rafRef.current = null
    if (audioContextRef.current) {
      audioContextRef.current.close().catch(() => {})
      audioContextRef.current = null
    }
    setLevel(0)
  }, [])

  const startMetering = useCallback((stream) => {
    const AudioCtx = window.AudioContext || window.webkitAudioContext
    const ctx = new AudioCtx()
    const source = ctx.createMediaStreamSource(stream)
    const analyser = ctx.createAnalyser()
    analyser.fftSize = 256
    source.connect(analyser)
    audioContextRef.current = ctx
    analyserRef.current = analyser

    const data = new Uint8Array(analyser.frequencyBinCount)
    const tick = () => {
      analyser.getByteFrequencyData(data)
      const avg = data.reduce((sum, v) => sum + v, 0) / data.length
      setLevel(Math.min(1, avg / 130))
      rafRef.current = requestAnimationFrame(tick)
    }
    tick()
  }, [])

  const start = useCallback(async () => {
    setError(null)
    if (!isRecordingSupported) {
      setError('Microphone recording is not supported in this browser.')
      return
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      const recorder = new MediaRecorder(stream)
      chunksRef.current = []
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }
      mediaRecorderRef.current = recorder
      recorder.start()
      startMetering(stream)
      setIsRecording(true)
    } catch (err) {
      setError('Microphone access was denied or is unavailable.')
    }
  }, [startMetering])

  const stop = useCallback(() => {
    return new Promise((resolve) => {
      const recorder = mediaRecorderRef.current
      if (!recorder) {
        resolve(null)
        return
      }
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        streamRef.current?.getTracks().forEach((track) => track.stop())
        stopMetering()
        setIsRecording(false)
        resolve(blob)
      }
      recorder.stop()
    })
  }, [stopMetering])

  useEffect(() => stopMetering, [stopMetering])

  return { isRecording, level, error, start, stop, isSupported: isRecordingSupported }
}
