import time
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from core.data import get_spot, get_expirations, get_options_chain
from core.calc import compute_exposure, smooth_profile
from core.nodes import extract_nodes

# Rebranded API title
app = FastAPI(title="GammaMaps API", version="2.0.0")

CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 30


def build_nodes(symbol: str, expiration: str = None) -> dict:
    """
    Build GEX nodes for a given symbol and expiration.
    If expiration is None, uses the nearest expiration.
    """
    spot = get_spot(symbol)
    expirations = get_expirations(symbol)

    # Use provided expiration or default to first (nearest)
    if expiration and expiration in expirations:
        selected_exp = expiration
    else:
        selected_exp = expirations[0]

    options = get_options_chain(symbol, selected_exp)
    raw_profile = compute_exposure(options, spot)
    profile = smooth_profile(raw_profile, window=1)

    nodes = extract_nodes(profile, spot, symbol=symbol)

    result = {
        "symbol": symbol,
        "spot": round(spot, 2),
        "expiration": selected_exp,
        "timestamp": int(time.time()),
        **nodes,
    }

    return result


def get_cached_or_build(symbol: str, expiration: str = None) -> Dict[str, Any]:
    """
    Returns cached data if fresh, otherwise builds new data.
    Cache key includes expiration to cache multiple expirations separately.
    """
    cache_key = f"{symbol.upper()}_{expiration or 'default'}"
    now = time.time()
    entry = CACHE.get(cache_key)

    if entry and now - entry["timestamp"] < CACHE_TTL_SECONDS:
        return entry["data"]

    data = build_nodes(symbol.upper(), expiration)
    CACHE[cache_key] = {"data": data, "timestamp": now}
    return data


@app.get("/nodes")
def get_nodes(symbol: str = "SPX", expiration: Optional[str] = None):
    """
    Get GEX nodes for a symbol and expiration.

    Args:
        symbol: Ticker symbol (SPX, SPY, QQQ, etc.)
        expiration: Optional expiration date in YYYY-MM-DD format
    """
    try:
        data = get_cached_or_build(symbol, expiration)
        return JSONResponse(content=data)
    except Exception as e:
        print(f"GammaMaps Error [{symbol}]: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/expirations")
def get_expirations_list(symbol: str = "SPX"):
    """
    Returns list of available expirations for a symbol.

    Args:
        symbol: Ticker symbol

    Returns:
        {"symbol": "SPX", "expirations": ["2025-11-25", "2025-11-26", ...]}
    """
    try:
        exps = get_expirations(symbol)
        return {"symbol": symbol.upper(), "expirations": exps}
    except Exception as e:
        print(f"GammaMaps Error [Expirations/{symbol}]: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
