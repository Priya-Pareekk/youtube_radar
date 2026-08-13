# TubeRadar

YouTube comment sentiment scanner — now a proper FastAPI backend + React
frontend instead of a single Streamlit script.

## What changed from the original

- **Backend** (`/backend`): the YouTube-fetching and sentiment-scoring logic
  from the old `youtube_radar.py`, exposed as a JSON API (`FastAPI`).
  Sentiment scoring moved from **TextBlob → VADER**, which reads
  slang/emphasis/emoji-adjacent text (the kind YouTube comments are full of)
  more accurately.
- **Frontend** (`/frontend`): a React app with its own custom design —
  no Streamlit widgets. Adds a per-video sentiment breakdown, a session
  scan log, and CSV export, on top of the original Solo / Competitor Battle
  modes.

The `wake_app.py` / GitHub Action from the original repo were there only to
keep a free-tier Streamlit app awake — not needed anymore, so they've been
dropped. Wire up your own host's keep-alive if the platform you deploy to
needs one.

## Running it locally

### 1. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # optional but recommended
pip install -r requirements.txt
cp .env.example .env   # then paste in your YouTube Data API v3 key
uvicorn main:app --reload --port 8000
```

Check it's alive: `http://localhost:8000/api/health`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies `/api/*` calls to
`http://localhost:8000`, so both need to be running.

### 3. Production build

```bash
cd frontend
npm run build
```

Serve the resulting `dist/` folder with any static host, and point it at a
deployed instance of the backend (update the API base URL / proxy target,
or put both behind the same reverse proxy).

## API

- `POST /api/analyze` — `{ topic, limit }` → sentiment breakdown for one topic
- `POST /api/compare` — `{ topic_a, topic_b, limit }` → head-to-head result
- `GET /api/health` — liveness + whether the API key is configured

## Notes

- The scan log is session-only (kept in React state) — nothing is persisted
  server-side. Refreshing the page clears it.
- YouTube Data API v3 has a daily quota; each scan costs roughly
  `1 search call + 1 call per video`, so keep "videos to scan" modest while
  testing.
