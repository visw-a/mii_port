from __future__ import annotations

import json
import random
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "portfolio-data.json"

app = FastAPI(title="MII Portfolio API", version="1.0.0")
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


def simulated_price(base_price: float, symbol: str, now: datetime) -> float:
    minute_bucket = now.strftime("%Y%m%d%H%M")
    seed = f"{symbol}:{minute_bucket}"
    rng = random.Random(seed)
    drift = 0.0002
    shock = rng.uniform(-0.01, 0.01)
    return round(base_price * (1 + drift + shock), 2)


def build_live_payload() -> dict:
    payload = load_baseline()
    live_payload = deepcopy(payload)

    now = datetime.now(timezone.utc)
    holdings = []
    for row in live_payload["holdings"]:
        updated = dict(row)

        if updated["symbol"] != "Cash_USD":
            new_price = simulated_price(updated["price"], updated["symbol"], now)
            updated["price"] = new_price
            updated["marketValue"] = round(updated["shares"] * new_price, 2)
            updated["dayChangePct"] = round((new_price / row["price"]) - 1, 4)
        else:
            updated["dayChangePct"] = 0.0
            updated["marketValue"] = round(updated["shares"] * updated["price"], 2)

        holdings.append(updated)

    live_payload["holdings"] = holdings
    live_payload["meta"]["snapshotDate"] = "2026-01-01"
    live_payload["meta"]["asOfUtc"] = now.isoformat()
    live_payload["updates"] = [
        {
            "date": now.strftime("%Y-%m-%d"),
            "note": "Live pricing simulation refreshed from FastAPI service.",
        },
        *live_payload["updates"],
    ]

    return live_payload


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/portfolio/baseline")
def get_baseline_portfolio() -> dict:
    payload = load_baseline()
    payload["meta"]["snapshotDate"] = "2026-01-01"
    return payload


@app.get("/api/portfolio/live")
def get_live_portfolio() -> dict:
    return build_live_payload()


app.mount("/", StaticFiles(directory=ROOT, html=True), name="static")
