# IndicASR — Frontend

Frontend for IndicASR, a multilingual speech recognition product for Indian
languages. This is a standalone React + Vite + Tailwind app that talks to
the existing ASR backend over a small HTTP contract, and runs in a clearly
labeled demo mode when no backend is configured.

This app does not contain or modify any of the ML pipeline, model, or
evaluation code — it is a UI layer on top of it.

## Getting started

```bash
npm install
npm run dev
```

Runs at `http://localhost:5173` by default, in demo mode until `VITE_API_URL`
is set (see below).

## Connecting the backend

Copy `.env.example` to `.env` and set the backend URL:

```bash
cp .env.example .env
```

```
VITE_API_URL=http://localhost:8000
```

The frontend expects a FastAPI (or equivalent) backend exposing:

```
POST {VITE_API_URL}/transcribe
Content-Type: multipart/form-data
  audio: File
  language: "auto" | "hi" | "bn" | "te" | "or"

200 response:
{
  "transcription": "...",
  "language": "hi",
  "processing_time": 1.42,
  "model": "IndicConformer"
}
```

Optional, for the performance section:

```
GET {VITE_API_URL}/benchmarks
```

returning the same shape as `src/data/benchmarks.json`. If this endpoint is
absent or unreachable, the page falls back to the static JSON file, so you
can also just update that file by hand with real numbers from your eval
scripts.

If `VITE_API_URL` is empty, or the backend is unreachable, `/transcribe`
calls return a response with `isMock: true`, and the UI shows a visible
"Demo mode" badge — a live backend result is never presented as one.

## Project structure

```
src/
  components/     UI components (workspace, sections, icons)
  services/api.js API layer — the only file that calls fetch()
  data/           Static content + benchmarks.json
  hooks/          Audio recording + waveform decoding
```

## Build

```bash
npm run build
npm run preview   # sanity-check the production build locally
```

Output goes to `dist/`.

## Deploy to Netlify

**Option A — Netlify CLI**

```bash
npm install -g netlify-cli
npm run build
netlify deploy --prod --dir=dist
```

**Option B — Git-connected site**

1. Push this repo to GitHub/GitLab/Bitbucket.
2. In Netlify: New site from Git → pick the repo.
3. Build command: `npm run build`, publish directory: `dist` (already set
   in `netlify.toml`, so the defaults just work).
4. In Site settings → Environment variables, add `VITE_API_URL` pointing
   at your deployed backend (or leave it unset to ship in demo mode).
5. Deploy.

No localhost URLs are hardcoded anywhere in the source — the backend URL is
read from `VITE_API_URL` at build time.
