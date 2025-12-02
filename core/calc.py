# core/calc.py

def compute_exposure(options, spot):
    by_strike = {}
    for opt in options:
        try:
            strike = float(opt["strike"])
            opt_type = opt["option_type"]
            oi = float(opt.get("open_interest") or 0.0)
            gamma = float(opt.get("greeks", {}).get("gamma") or 0.0)
        except Exception:
            continue
            
        if oi <= 0 or gamma == 0.0:
            continue

        # GEX Formula: Gamma * OI * 100 * Spot^2 * 0.01
        # Note: Some simplified versions just use Gamma * OI * 100. 
        # Scaling by Spot^2 makes it dollar-gamma-exposure which is standard for dealers.
        gex_line = gamma * oi * 100.0 * (spot ** 2) * 0.01
        
        if opt_type == "put":
            gex_line *= -1.0
            
        by_strike[strike] = by_strike.get(strike, 0.0) + gex_line

    return by_strike

def smooth_profile(by_strike, window=1):
    # Simple moving average smoothing to reduce noise
    strikes = sorted(by_strike.keys())
    smoothed = {}
    for i, k in enumerate(strikes):
        total = 0.0
        count = 0
        # look back/forward 'window' steps
        for j in range(max(0, i - window), min(len(strikes), i + window + 1)):
            total += by_strike[strikes[j]]
            count += 1
        smoothed[k] = total / count if count > 0 else by_strike[k]
    return smoothed
