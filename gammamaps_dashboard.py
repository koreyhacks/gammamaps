import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# --- CONFIG ---
API_URL = "http://127.0.0.1:8051/nodes"
EXPIRATIONS_URL = "http://127.0.0.1:8051/expirations"
AVAILABLE_SYMBOLS = ["SPX", "SPY", "QQQ", "IWM", "GLD"]
REFRESH_INTERVAL = 15 * 1000  # ms

st.set_page_config(
    page_title="GammaMaps",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st_autorefresh(interval=REFRESH_INTERVAL, key="gammamaps_refresh")

# --- ENHANCED CSS WITH ANIMATIONS ---
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #000000 0%, #0a0a0a 50%, #000000 100%);
            color: #e0e0e0;
        }

        .gammamaps-logo {
            font-size: 48px; font-weight: 900; letter-spacing: 4px;
            background: linear-gradient(90deg, #fff 0%, #888 50%, #fff 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 3s linear infinite;
        }

        @keyframes shimmer {
            0% { background-position: 0% center; }
            100% { background-position: 200% center; }
        }

        /* Glassmorphism Widget */
        .core-widget {
            background: rgba(10, 10, 10, 0.4);
            backdrop-filter: blur(20px) saturate(180%);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 30px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
            transition: all 0.3s ease;
        }

        .core-widget:hover {
            border-color: rgba(0, 255, 0, 0.3);
            box-shadow: 0 8px 32px rgba(0, 255, 0, 0.2);
        }

        /* Animated Status Glow */
        @keyframes pulse-green {
            0%, 100% { box-shadow: 0 0 20px rgba(0, 255, 0, 0.3); }
            50% { box-shadow: 0 0 40px rgba(0, 255, 0, 0.6); }
        }

        @keyframes pulse-purple {
            0%, 100% { box-shadow: 0 0 20px rgba(180, 0, 255, 0.3); }
            50% { box-shadow: 0 0 40px rgba(180, 0, 255, 0.6); }
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }

        .live-dot {
            height: 10px; width: 10px;
            background: radial-gradient(circle, #0f0 0%, #0a0 100%);
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
            animation: blink 2s ease-in-out infinite;
            box-shadow: 0 0 10px #0f0;
        }

        .symbol-text {
            font-family: 'SF Pro Display', 'Roboto Mono', monospace;
            font-size: 20px;
            font-weight: 700;
            color: #fff;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
        }

        .price-text {
            font-family: 'SF Pro Display', 'Roboto Mono', monospace;
            font-size: 32px;
            font-weight: 800;
            background: linear-gradient(90deg, #fff 0%, #aaa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .timestamp-badge {
            font-family: 'Roboto Mono', monospace;
            font-size: 11px;
            color: #888;
            background: rgba(255,255,255,0.05);
            padding: 6px 12px;
            border-radius: 20px;
            display: inline-block;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }

        .timestamp-badge:hover {
            background: rgba(255,255,255,0.1);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .js-plotly-plot {
            margin-bottom: 0 !important;
            transition: opacity 0.3s ease;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        div.block-container { padding-top: 2rem; }

        div[data-baseweb="select"] {
            margin-bottom: 20px;
            border-radius: 8px;
            transition: all 0.3s ease;
        }

        div[data-baseweb="select"]:hover {
            box-shadow: 0 4px 12px rgba(0, 255, 0, 0.1);
        }

        @keyframes skeleton-loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }

        .skeleton {
            background: linear-gradient(
                90deg,
                rgba(255, 255, 255, 0.05) 25%,
                rgba(255, 255, 255, 0.1) 50%,
                rgba(255, 255, 255, 0.05) 75%
            );
            background-size: 200% 100%;
            animation: skeleton-loading 1.5s infinite;
        }

        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #0a0a0a;
        }

        ::-webkit-scrollbar-thumb {
            background: #333;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- HEADER ---
col_logo, col_selector, col_status = st.columns([2, 2, 1])

with col_logo:
    st.markdown('<h1 class="gammamaps-logo">GammaMaps</h1>', unsafe_allow_html=True)
    st.caption("QUANTITATIVE MARKET FORCE TERMINAL")

with col_selector:
    selected_symbol = st.selectbox("Select Ticker", AVAILABLE_SYMBOLS, index=0, key="ticker_select")

with col_status:
    current_time = datetime.now().strftime("%I:%M %p EST")
    st.markdown(
        f'<div class="timestamp-badge">UPDATED: {current_time}</div>',
        unsafe_allow_html=True,
    )

# --- FETCH EXPIRATIONS FOR SELECTED TICKER ---
try:
    exp_response = requests.get(EXPIRATIONS_URL, params={"symbol": selected_symbol}, timeout=2)
    if exp_response.status_code == 200:
        expirations = exp_response.json().get("expirations", [])[:3]
    else:
        expirations = []
except Exception:
    expirations = []

if not expirations:
    st.error(f"Could not fetch expirations for {selected_symbol}. Check backend.")
    st.stop()

# --- FETCH DATA FOR EACH EXPIRATION ---
expiry_data = {}
for exp in expirations:
    try:
        r = requests.get(API_URL, params={"symbol": selected_symbol, "expiration": exp}, timeout=3)
        if r.status_code == 200:
            expiry_data[exp] = r.json()
        else:
            expiry_data[exp] = {}
    except Exception:
        expiry_data[exp] = {}

# --- CONFLUENCE WIDGET ---
first_exp_data = expiry_data.get(expirations[0], {})
net_gex = first_exp_data.get("net_exposure", 0) or 0

glow_style = "border: 1px solid rgba(255, 255, 255, 0.1);"
status_msg = f"{selected_symbol} MARKET STATE: NEUTRAL"
status_color = "#888"

if net_gex > 0:
    glow_style = "border: 1px solid rgba(0, 255, 0, 0.3); animation: pulse-green 2s infinite;"
    status_msg = f"{selected_symbol} MARKET STATE: POSITIVE GEX (LOW VOL)"
    status_color = "#0f0"
elif net_gex < 0:
    glow_style = "border: 1px solid rgba(180, 0, 255, 0.3); animation: pulse-purple 2s infinite;"
    status_msg = f"{selected_symbol} MARKET STATE: NEGATIVE GEX (HIGH VOL)"
    status_color = "#d0f"

st.markdown(
    f"""
    <div class="core-widget" style="{glow_style}">
        <h3 style="margin:0; color: {status_color}; letter-spacing: 2px; font-family: 'Roboto Mono';">
            {status_msg}
        </h3>
        <div style="display: flex; justify-content: center; gap: 30px; margin-top: 10px;
                    font-family: 'Roboto Mono'; font-size: 14px; color: #aaa;">
            <span>NET GEX (0DTE): {net_gex/1e9:+.2f}B</span>
            <span>SPOT: ${first_exp_data.get("spot", 0):,.2f}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- BUILD COMBINED TABLE DATA ---
all_strikes = set()
for exp in expirations:
    data = expiry_data.get(exp, {})
    nodes = data.get("all_nodes", [])
    if nodes:
        df_tmp = pd.DataFrame(nodes)
        all_strikes.update(df_tmp["strike"].tolist())

sorted_strikes = sorted(list(all_strikes), reverse=True)
strike_col = [f"{s:.1f}" for s in sorted_strikes]

exp_columns = []
exp_colors = []

for exp in expirations:
    data = expiry_data.get(exp, {})
    spot = data.get("spot", 0)
    nodes = data.get("all_nodes", [])

    if not nodes:
        exp_columns.append(["N/A"] * len(sorted_strikes))
        exp_colors.append(["#121212"] * len(sorted_strikes))
        continue

    df = pd.DataFrame(nodes)
    if "gex" not in df.columns:
        # fallback if backend only provides strength
        df["gex"] = df["strength"] * 1e6

    gex_values = df["gex"].abs()
    max_gex = gex_values.max()
    min_gex = gex_values.min()

    strike_map = {row["strike"]: row for _, row in df.iterrows()}

    col_values = []
    col_colors = []

    for strike in sorted_strikes:
        if strike in strike_map:
            row = strike_map[strike]
            val = row["gex"]

            txt = f"${val/1e3:,.1f}K"
            if abs(strike - spot) < 2.5:
                txt += " ▶"
            if row.get("is_king"):
                txt += " ⭐"

            col_values.append(txt)

            bias = row.get("bias", "")
            abs_val = abs(val)

            if max_gex > min_gex:
                strength_pct = (abs_val - min_gex) / (max_gex - min_gex)
            else:
                strength_pct = 1.0

            if row.get("is_king"):
                col_colors.append("#8B008B")

            elif bias == "magnet":
                if strength_pct > 0.8:
                    col_colors.append("#FFD700")
                elif strength_pct > 0.6:
                    col_colors.append("#FFEB3B")
                elif strength_pct > 0.4:
                    col_colors.append("#FFF176")
                elif strength_pct > 0.2:
                    col_colors.append("#FFF59D")
                else:
                    col_colors.append("#FFFDE7")

            elif bias == "resistance":
                if strength_pct > 0.9:
                    col_colors.append("#1B5E20")
                elif strength_pct > 0.75:
                    col_colors.append("#2E7D32")
                elif strength_pct > 0.6:
                    col_colors.append("#388E3C")
                elif strength_pct > 0.45:
                    col_colors.append("#4CAF50")
                elif strength_pct > 0.3:
                    col_colors.append("#66BB6A")
                elif strength_pct > 0.15:
                    col_colors.append("#81C784")
                elif strength_pct > 0.05:
                    col_colors.append("#A5D6A7")
                else:
                    col_colors.append("#C8E6C9")

            elif bias == "support":
                if strength_pct > 0.9:
                    col_colors.append("#0D47A1")
                elif strength_pct > 0.75:
                    col_colors.append("#1565C0")
                elif strength_pct > 0.6:
                    col_colors.append("#1976D2")
                elif strength_pct > 0.45:
                    col_colors.append("#1E88E5")
                elif strength_pct > 0.3:
                    col_colors.append("#42A5F5")
                elif strength_pct > 0.15:
                    col_colors.append("#64B5F6")
                elif strength_pct > 0.05:
                    col_colors.append("#90CAF9")
                else:
                    col_colors.append("#BBDEFB")

            else:
                col_colors.append("#121212")
        else:
            col_values.append("$0.0K")
            col_colors.append("#121212")

    exp_columns.append(col_values)
    exp_colors.append(col_colors)

# --- LABELS FOR EXPIRATIONS ---
exp_labels = []
for exp in expirations:
    try:
        exp_date = datetime.strptime(exp, "%Y-%m-%d")
        exp_labels.append(exp_date.strftime("%m/%d"))
    except Exception:
        exp_labels.append(exp)

all_values = [strike_col] + exp_columns
all_colors = [["#000000"] * len(sorted_strikes)] + exp_colors

fig = go.Figure(
    data=[
        go.Table(
            header=dict(
                values=["Strike"] + exp_labels,
                fill_color="#1a1a1a",
                align="center",
                font=dict(color="white", size=14, family="Roboto Mono"),
                height=30,
            ),
            cells=dict(
                values=all_values,
                align=["right"] + ["right"] * len(expirations),
                font=dict(
                    color=["#FFFFFF"] + ["#000000"] * len(expirations),
                    size=16,
                    family="Roboto Mono, monospace",
                ),
                fill=dict(color=all_colors),
                height=35,
                line=dict(width=0.5, color="#333"),
            ),
        )
    ]
)

fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    height=800,
    paper_bgcolor="#000000",
    plot_bgcolor="#000000",
    hoverlabel=dict(
        bgcolor="rgba(255, 255, 255, 0.1)",
        font_size=14,
        font_family="Roboto Mono",
    ),
)

st.plotly_chart(fig, use_container_width=True)

# --- FADE-IN ANIMATION ---
st.markdown(
    """
    <script>
        setTimeout(() => {
            document.querySelectorAll('.js-plotly-plot').forEach(el => {
                el.style.opacity = '0';
                el.style.transition = 'opacity 0.5s ease-in';
                setTimeout(() => { el.style.opacity = '1'; }, 100);
            });
        }, 100);
    </script>
    """,
    unsafe_allow_html=True,
)
