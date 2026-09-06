// src/services/api.js
//
// Thin API layer for IndicASR. All backend calls live here so the rest of
// the app never talks to fetch() directly.
//
// Expected backend contract (FastAPI, to be implemented separately):
//
//   POST {VITE_API_URL}/transcribe
//   multipart/form-data: { audio: File, language: string }
//
//   200 response:
//   {
//     "transcription": "...",
//     "language": "hi",
//     "processing_time": 1.42,
//     "model": "IndicConformer"
//   }
//
// If VITE_API_URL is unset, unreachable, or the request times out, the
// service layer falls back to a clearly labeled demo mode so the UI stays
// usable for a presentation without a live backend. Mock responses are
// tagged with `isMock: true` and the UI must surface that to the user —
// it must never be presented as a real model result.

const API_BASE_URL = import.meta.env.VITE_API_URL || ''
const REQUEST_TIMEOUT_MS = 15000

const MOCK_SAMPLES = {
  auto: 'यह एक डेमो ट्रांसक्रिप्शन है क्योंकि बैकएंड अभी उपलब्ध नहीं है।',
  hi: 'यह एक डेमो ट्रांसक्रिप्शन है क्योंकि बैकएंड अभी उपलब्ध नहीं है।',
  bn: 'এটি একটি ডেমো ট্রান্সক্রিপশন কারণ ব্যাকএন্ড এখনও উপলব্ধ নেই।',
  te: 'బ్యాకెండ్ ఇంకా అందుబాటులో లేనందున ఇది ఒక డెమో ట్రాన్‌స్క్రిప్షన్.',
  or: 'ବ୍ୟାକଏଣ୍ଡ ଏବେ ଉପଲବ୍ଧ ନଥିବାରୁ ଏହା ଏକ ଡେମୋ ଟ୍ରାନ୍ସକ୍ରିପ୍ସନ।'
}

function timeoutSignal(ms) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), ms)
  return { signal: controller.signal, cancel: () => clearTimeout(timer) }
}

function buildMockResponse(language, audioDurationSeconds) {
  const lang = MOCK_SAMPLES[language] ? language : 'auto'
  return {
    transcription: MOCK_SAMPLES[lang],
    language: lang,
    processing_time: Number((0.6 + Math.random() * 0.8).toFixed(2)),
    model: 'IndicConformer (demo mode)',
    isMock: true,
    audioDurationSeconds: audioDurationSeconds ?? null
  }
}

/**
 * Sends an audio file to the ASR backend for transcription.
 * Falls back to demo mode if the backend is unreachable or not configured.
 *
 * @param {File|Blob} audioFile
 * @param {string} language - one of 'auto' | 'hi' | 'bn' | 'te' | 'or'
 * @param {{ audioDurationSeconds?: number }} [meta]
 * @returns {Promise<{transcription: string, language: string, processing_time: number, model: string, isMock?: boolean}>}
 */
export async function transcribeAudio(audioFile, language, meta = {}) {
  if (!API_BASE_URL) {
    // No backend configured for this deployment — demo mode by design.
    await new Promise((resolve) => setTimeout(resolve, 1200))
    return buildMockResponse(language, meta.audioDurationSeconds)
  }

  const { signal, cancel } = timeoutSignal(REQUEST_TIMEOUT_MS)

  try {
    const formData = new FormData()
    formData.append('audio', audioFile)
    formData.append('language', language)

    const response = await fetch(`${API_BASE_URL}/transcribe`, {
      method: 'POST',
      body: formData,
      signal
    })

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}`)
    }

    const data = await response.json()
    return { ...data, isMock: false }
  } catch (error) {
    // Backend unreachable, timed out, or errored — degrade to demo mode
    // rather than breaking the interview/demo flow.
    console.warn('[IndicASR] Backend unavailable, using demo mode:', error.message)
    return buildMockResponse(language, meta.audioDurationSeconds)
  } finally {
    cancel()
  }
}

/**
 * Fetches live benchmark results from the backend, if configured.
 * Returns null when unavailable so the UI can fall back to the
 * static benchmarks.json checked into the repo.
 */
export async function fetchBenchmarks() {
  if (!API_BASE_URL) return null
  const { signal, cancel } = timeoutSignal(REQUEST_TIMEOUT_MS)
  try {
    const response = await fetch(`${API_BASE_URL}/benchmarks`, { signal })
    if (!response.ok) return null
    return await response.json()
  } catch (error) {
    return null
  } finally {
    cancel()
  }
}

export const isBackendConfigured = Boolean(API_BASE_URL)
