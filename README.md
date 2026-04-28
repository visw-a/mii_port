# MII Portfolio Dashboard (Frontend + FastAPI)

You are correct: on your Mac, `/workspace/mii_port` does **not** exist unless you created it.
That path only existed in my container.

Use the steps below on your own machine.

## Step-by-step on macOS Terminal

### 1) Clone the repo from GitHub

In Terminal:

```bash
git clone <YOUR_GITHUB_REPO_URL> mii_port
cd mii_port
```

If you already cloned it before, then instead do:

```bash
cd /path/to/your/existing/mii_port
git pull
```

### 2) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should now see `(.venv)` at the start of your prompt.

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Run the backend + frontend server

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Leave this running.

### 5) Open in your browser

Go to:
- <http://127.0.0.1:8000>

### 6) Verify API is live (new terminal tab)

```bash
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/portfolio/live | python3 -m json.tool | head -n 40
```

Run the second command twice a few seconds apart. `asOfUtc`, `price`, and `dayChangePct` should refresh as live quotes update.

## Cursor clone error fix (dyld / `_curl_global_trace`)

If you see this in Cursor while cloning:

- `Symbol not found: _curl_global_trace`
- `git-remote-https died`

it means the Homebrew git binary is linked against a libcurl symbol mismatch.

### Fastest workaround (recommended)

1. In macOS Terminal, clone using Apple system git:

```bash
/usr/bin/git clone https://github.com/visw-a/mii_port.git ~/mii_port
```

2. In Cursor, open that folder directly:
   - **File → Open Folder... → `/Users/<your-user>/mii_port`**

3. Optional: make Cursor use system git instead of Homebrew git.
   - Cursor Settings → search `git.path`
   - Set to `/usr/bin/git`

### Permanent fix for Homebrew git

Run:

```bash
brew update
brew reinstall curl git
brew doctor
```

Then restart Cursor and verify:

```bash
/opt/homebrew/bin/git --version
/opt/homebrew/bin/git clone https://github.com/visw-a/mii_port.git ~/mii_port_test
```

If the clone still fails, keep using `/usr/bin/git` in Cursor.

## Is the stock data always live?

`/api/portfolio/live` now fetches quote data directly from Yahoo Finance on each request.
So prices/day-change are live (or market-delayed depending on exchange availability), not simulated.

If quote fetching fails temporarily (network/API issue), the API falls back to last-known baseline values and adds a warning note in `updates`.

## Endpoints

- `GET /api/health`
- `GET /api/portfolio/baseline`
- `GET /api/portfolio/live`

## Next step prompt for me

If you want institutional-grade live data + robustness, prompt:

> Switch the quote source from Yahoo to Polygon (or Alpaca), add API key env vars, and add Redis caching + retry/backoff.
