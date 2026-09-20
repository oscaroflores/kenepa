from __future__ import annotations

from typing import Any

import requests


class MarketClient:
    def __init__(self, timeout: int = 15) -> None:
        self.timeout = timeout
        self.headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json,text/plain,*/*"}

    def fetch_quote(self, ticker: str) -> dict[str, Any] | None:
        symbol = ticker.upper()
        yahoo_url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"
        try:
            response = requests.get(yahoo_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            result = (response.json().get("chart", {}).get("result") or [None])[0]
            meta = (result or {}).get("meta", {})
            price = meta.get("regularMarketPrice") or meta.get("fulldayPrice")
            if price:
                return {"price": float(price), "source": "yahoo_chart", "url": yahoo_url, "metadata": meta}
        except Exception:
            pass

        nasdaq_url = f"https://api.nasdaq.com/api/quote/{symbol}/info?assetclass=stocks"
        try:
            response = requests.get(nasdaq_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json().get("data", {})
            raw_price = data.get("primaryData", {}).get("lastSalePrice")
            if raw_price:
                price = float(str(raw_price).replace("$", "").replace(",", ""))
                return {"price": price, "source": "nasdaq_quote", "url": nasdaq_url, "metadata": data}
        except Exception:
            pass

        return None
