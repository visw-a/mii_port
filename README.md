# McIntire Investment Institute Portfolio Dashboard

A lightweight, maintenance-friendly dashboard that displays portfolio positions, performance, sector allocation, and risk metrics from a single JSON data source.

## Why this starter is easy to maintain

- **Single data file** (`portfolio-data.json`) drives the dashboard.
- **No build tooling required** (plain HTML/CSS/JS).
- **Clear metric functions** in `app.js` for simple future extensions.
- **Auto refresh** every 30 seconds with manual refresh support.

## Run locally

Because browsers block local `fetch()` calls from `file://`, run a local server:

```bash
python3 -m http.server 8080
```

Then open: <http://localhost:8080>

## Data model

Update `portfolio-data.json` with:

- `holdings[]` records containing `ticker`, `name`, `sector`, `shares`, `price`, `costBasis`, `dayChangePct`, and `beta`.
- `updates[]` records to show operational updates in the feed.

## Going from demo to true live data

1. Replace `CONFIG.dataUrl` in `app.js` with your API endpoint.
2. Feed real-time/near-real-time prices from your broker, data vendor, or OMS/PMS.
3. Keep the same response shape to avoid frontend rewrites.

## Suggested next features

- Authentication + role-based access (analyst vs. PM vs. executive view).
- Alert rules (drawdown, sector concentration, beta caps).
- Performance attribution and benchmark-relative tracking.
- Export snapshots for investment committee materials.
