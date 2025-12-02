# core/data.py
import os
import requests

TRADIER_BASE = "https://api.tradier.com/v1"
TRADIER_TOKEN = os.environ.get("TRADIER_TOKEN")

def tradier_headers():
    if not TRADIER_TOKEN:
        raise RuntimeError("TRADIER_TOKEN environment variable is not set.")
    return {
        "Authorization": f"Bearer {TRADIER_TOKEN}",
        "Accept": "application/json",
    }

def get_spot(symbol: str):
    url = f"{TRADIER_BASE}/markets/quotes"
    params = {"symbols": symbol}
    resp = requests.get(url, headers=tradier_headers(), params=params, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"Tradier API Error: {resp.text}")
    data = resp.json()
    quote = data.get("quotes", {}).get("quote")
    if isinstance(quote, list):
        quote = quote[0]
    return float(quote.get("last") or quote.get("close"))

def get_expirations(symbol: str):
    url = f"{TRADIER_BASE}/markets/options/expirations"
    params = {"symbol": symbol, "includeAllRoots": "true", "strikes": "false"}
    resp = requests.get(url, headers=tradier_headers(), params=params, timeout=10)
    data = resp.json()
    return data.get("expirations", {}).get("date", [])

def get_options_chain(symbol: str, expiration: str):
    url = f"{TRADIER_BASE}/markets/options/chains"
    params = {"symbol": symbol, "expiration": expiration, "greeks": "true"}
    resp = requests.get(url, headers=tradier_headers(), params=params, timeout=15)
    data = resp.json()
    options = data.get("options", {}).get("option", [])
    return options if isinstance(options, list) else [options]
