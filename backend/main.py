from __future__ import annotations

import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.parse import quote_plus
from urllib.request import urlopen

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "portfolio-data.json"
YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbols}"

app = FastAPI(title="MII Portfolio API", version="1.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_baseline() -> dict:
    with BASELINE_PATH.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def fetch_live_quotes(symbols: list[str]) -> dict[str, dict]:
    if not symbols:
        return {}

    symbols_query = quote_plus(",".join(symbols))
    url = YAHOO_QUOTE_URL.format(symbols=symbols_query)

    with urlopen(url, timeout=8) as response:
        data = json.loads(response.read().decode("utf-8"))

    rows = data.get("quoteResponse", {}).get("result", [])
    return {row.get("symbol"): row for row in rows if row.get("symbol")}


def build_live_payload() -> dict:
    payload = load_baseline()
    live_payload = deepcopy(payload)

    now = datetime.now(timezone.utc)
    tradable_symbols = [
        row["symbol"] for row in live_payload["holdings"] if row["symbol"] != "Cash_USD"
    ]

    live_quotes: dict[str, dict] = {}
    quote_error = None
    try:
        live_quotes = fetch_live_quotes(tradable_symbols)
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        quote_error = str(exc)

    for row in live_payload["holdings"]:
        if row["symbol"] == "Cash_USD":
            row["dayChangePct"] = 0.0
            row["marketValue"] = round(row["shares"] * row["price"], 2)
            continue

        quote = live_quotes.get(row["symbol"], {})
        live_price = quote.get("regularMarketPrice")
        live_change_pct = quote.get("regularMarketChangePercent")

        if isinstance(live_price, (int, float)) and live_price > 0:
            row["price"] = round(float(live_price), 2)
            row["marketValue"] = round(row["shares"] * row["price"], 2)
        else:
            row["marketValue"] = round(row["shares"] * row["price"], 2)

        if isinstance(live_change_pct, (int, float)):
            row["dayChangePct"] = round(float(live_change_pct) / 100, 4)
        else:
            row["dayChangePct"] = row.get("dayChangePct", 0)

    live_payload["meta"]["snapshotDate"] = "2026-01-01"
    live_payload["meta"]["asOfUtc"] = now.isoformat()
    live_payload["meta"]["pricingSource"] = "Yahoo Finance quote API"

    if quote_error:
        live_payload["updates"] = [
            {
                "date": now.strftime("%Y-%m-%d"),
                "note": f"Live quote fetch failed; using last-known values. Error: {quote_error}",
            },
            *live_payload["updates"],
        ]
    else:
        live_payload["updates"] = [
            {
                "date": now.strftime("%Y-%m-%d"),
                "note": "Live prices refreshed from Yahoo Finance quote API.",
            },
            *live_payload["updates"],
        ]

    return live_payload


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "pricing_mode": os.getenv("PRICING_MODE", "live")}


@app.get("/api/portfolio/baseline")
def get_baseline_portfolio() -> dict:
    payload = load_baseline()
    payload["meta"]["snapshotDate"] = "2026-01-01"
    payload["meta"]["pricingSource"] = "Baseline snapshot"
    return payload


@app.get("/api/portfolio/live")
def get_live_portfolio() -> dict:
    return build_live_payload()


app.mount("/", StaticFiles(directory=ROOT, html=True), name="static")
