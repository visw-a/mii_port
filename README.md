# McIntire Investment Institute Portfolio Dashboard + FastAPI Backend

This repo now runs as a **single local web app**:
- FastAPI serves live portfolio JSON at `/api/portfolio/live`.
- The same FastAPI process serves the frontend dashboard at `/`.

Baseline holdings are from your screenshot values and now marked as **2026-01-01** in the payload.

## 1) Open your terminal in this repo

```bash
cd /workspace/mii_port
```

Yes — these commands are run in your terminal.

## 2) Create and activate a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

After activation, your prompt should show `(.venv)`.

## 3) Install backend dependencies

```bash
pip install -r requirements.txt
```

## 4) Start the FastAPI server

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Keep this terminal running.

## 5) Verify backend endpoints (open a second terminal)

```bash
cd /workspace/mii_port
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/portfolio/baseline | python3 -m json.tool | head -n 20
curl http://127.0.0.1:8000/api/portfolio/live | python3 -m json.tool | head -n 30
```

Expected:
- `/api/health` returns `{"status":"ok"}`
- portfolio endpoints return JSON with `meta`, `holdings`, `updates`

## 6) Open the dashboard in browser

Go to:

- <http://127.0.0.1:8000>

The dashboard should auto-refresh every 30 seconds and can be manually refreshed with **Refresh now**.

## 7) How to check it is truly live

Run this twice, a minute apart:

```bash
curl http://127.0.0.1:8000/api/portfolio/live | python3 -m json.tool | rg '"asOfUtc"|"symbol"|"price"|"dayChangePct"' -n
```

You should see `asOfUtc` update and simulated prices/dayChangePct values move for non-cash positions.

## API routes

- `GET /api/health`
- `GET /api/portfolio/baseline` (fixed baseline snapshot)
- `GET /api/portfolio/live` (live-simulated prices)

## Next prompt to give me

If you want real market data (instead of simulation), prompt:

> Replace simulated FastAPI prices with Polygon/IEX/Alpaca live quotes and persist intraday history for charts.
