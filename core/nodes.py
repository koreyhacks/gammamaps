# core/nodes.py
from typing import Dict, List, Optional

# Simple in-memory cache to track previous GEX for "Rate of Change"
# Format: { "SPX": { strike: gex_value, ... } }
PREVIOUS_STATE = {}

def extract_nodes(profile: Dict[float, float], spot: float, symbol: str = "UNKNOWN") -> Dict:
    """
    Extracts nodes with advanced logic:
    - Gatekeeper detection (nodes blocking path to King Node)
    - Rate of Change (RoC) vs previous fetch
    - Absolute strength normalization
    """
    if not profile:
        return None

    # --- 1. Basic Calculations ---
    net_exposure = sum(profile.values())
    abs_values = [abs(v) for v in profile.values()]
    max_abs = max(abs_values) if abs_values else 1.0

    # --- 2. Identify King Node ---
    # The strike with the single highest absolute GEX
    king_strike = max(profile.items(), key=lambda kv: abs(kv[1]))[0]

    # --- 3. Prepare "All Nodes" with Logic ---
    relevant_strikes = [k for k in profile.keys() if 0.90 * spot < k < 1.10 * spot]
    relevant_strikes.sort(reverse=True)

    # Retrieve previous state for this symbol to calc RoC
    prev_gex_map = PREVIOUS_STATE.get(symbol, {})
    new_gex_map = {}

    all_nodes = []
    
    for strike in relevant_strikes:
        val = profile[strike]
        new_gex_map[strike] = val
        
        # Absolute Strength (0.0 to 1.0)
        strength = abs(val) / max_abs

        # --- Bias / Color Logic ---
        # Yellow (Magnet) if very strong (>65% of max)
        if strength > 0.65:
            bias = "magnet"
        elif val > 0:
            bias = "resistance"
        else:
            bias = "support"

        # --- Rate of Change (RoC) ---
        # Calculate change from last fetch
        prev_val = prev_gex_map.get(strike, val) # Default to current if no history
        gex_change = val - prev_val 
        
        # Determine RoC Label
        # Threshold: e.g., change > 5% of max_abs is significant
        roc_label = "neutral"
        if gex_change > (0.05 * max_abs):
            roc_label = "accumulation" # gaining positive exposure (or shrinking negative)
        elif gex_change < -(0.05 * max_abs):
            roc_label = "unwinding"    # losing positive exposure (or growing negative)

        # --- Gatekeeper Logic ---
        # A Gatekeeper is a strong node (e.g. >40% strength) that sits BETWEEN Spot and King
        is_gatekeeper = False
        if strength > 0.40 and strike != king_strike:
            if spot < strike < king_strike:  # Price is below, King is above, node is in middle
                is_gatekeeper = True
            elif king_strike < strike < spot: # Price is above, King is below, node is in middle
                is_gatekeeper = True

        all_nodes.append({
            "strike": strike,
            "strength": round(strength, 4),
            "gex": int(val),
            "gex_change": int(gex_change),
            "bias": bias,
            "is_king": (strike == king_strike),
            "is_gatekeeper": is_gatekeeper,
            "roc": roc_label
        })

    # Update cache for next time
    PREVIOUS_STATE[symbol] = new_gex_map

    # --- 4. Summary Stats ---
    strong_nodes = sorted(all_nodes, key=lambda x: x['strength'], reverse=True)[:5]
    
    # Nearest Levels logic remains same
    below = [n for n in all_nodes if n["strike"] <= spot and n["bias"] != "resistance" and n["strength"] > 0.15]
    above = [n for n in all_nodes if n["strike"] >= spot and n["bias"] != "support" and n["strength"] > 0.15]
    
    nearest_support = max(below, key=lambda n: n["strike"])["strike"] if below else None
    nearest_resistance = min(above, key=lambda n: n["strike"])["strike"] if above else None

    # Environment Logic
    if abs(net_exposure) < 0.2 * max_abs:
        environment = "mixed"
    elif net_exposure > 0:
        environment = "low_vol_pin"
    else:
        environment = "high_vol_trend"

    return dict(
        net_exposure=net_exposure,
        environment=environment,
        king_node=king_strike,
        all_nodes=all_nodes,
        strong_nodes=strong_nodes,
        nearest_levels={"support": nearest_support, "resistance": nearest_resistance}
    )
