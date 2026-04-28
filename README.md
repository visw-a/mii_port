# McIntire Investment Institute Portfolio Dashboard

A lightweight, maintenance-friendly dashboard that now uses your **January 19, 2026 portfolio snapshot** as the baseline dataset.

## What changed

- The seed data now matches your screenshot portfolio (16 holdings + cash, owner metadata, benchmark, and market values).
- The dashboard renders profile metadata, holdings, sector mix, and risk/performance statistics from one JSON file.
- The app is ready for a live API by swapping one config value.

## Run locally (right now)

```bash
python3 -m http.server 8080
```

Open <http://localhost:8080>.

## What to do next to make this truly live

1. Keep `portfolio-data.json` as your fallback snapshot.
2. Build or expose an endpoint that returns this same JSON shape (positions + metadata + updates).
3. In `app.js`, change:

```js
const CONFIG = {
  dataUrl: "https://your-api.example.com/mii/portfolio/live",
  refreshMs: 30_000,
};
```

4. Add a server-side job that refreshes holdings/prices periodically (e.g., every 1–5 minutes).

## Prompts you can give me next

Use one of these exactly (or similar):

- "Connect this dashboard to a FastAPI backend that serves live holdings and price updates."
- "Create a Node/Express API that reads a CSV export from our OMS and returns the dashboard JSON format."
- "Add authentication (Google SSO) and role-based access for analyst vs PM."
- "Add historical performance charts and benchmark-relative return metrics."
- "Add alerting rules for max position weight, sector concentration, and beta limits."

## Data model expected by frontend

- `meta`: portfolio name, owner, dates, benchmark, currency.
- `holdings[]`: `symbol`, `name`, `sector`, `shares`, `price`, optional `marketValue`, optional `costBasis`, optional `dayChangePct`, optional `beta`.
- `updates[]`: date-stamped operational notes.
