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

# --- AUTO REFRESH ---
st_autorefresh(interval=REFRESH_INTERVAL, key="data_refresh")

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
            animation: shine 4s linear infinite;
        }

        @keyframes shine {
            0% { background-position: 0% 50%; }
            100% { background-position: 200% 50%; }
        }

        .subtitle-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            border-radius: 999px;
            background: rgba(0, 255, 0, 0.06);
            border: 1px solid rgba(0, 255, 0, 0.4);
            font-size: 13px;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #b2ff59;
        }

        .subtitle-badge span.dot {
            width: 7px; height: 7px;
            border-radius: 999px;
            background: #00e676;
            box-shadow: 0 0 12px rgba(0, 230, 118, 0.9);
        }

        .core-widget {
            background: radial-gradient(circle at top left, rgba(0, 255, 0, 0.08), transparent 55%),
                        radial-gradient(circle at bottom right, rgba(0, 230, 118, 0.06), transparent 55%),
                        #050505;
            border-radius: 20px;
            padding: 18px 22px 14px 22px;
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
            border-radius: 999px;
            background: #00e676;
            box-shadow: 0 0 14px rgba(0, 230, 118, 0.9);
            animation: blink 1.2s infinite;
        }

        .ticker-pill {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 6px 16px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.12);
            font-size: 13px;
        }

        .ticker-pill .change-up {
            color: #00e676;
        }

        .ticker-pill .label {
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.09em;
            color: #b0bec5;
        }

        .status-chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 12px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #cfd8dc;
        }

        .status-dot {
            width: 8px; height: 8px;
            border-radius: 999px;
        }

        .status-dot.green {
            background: #00e676;
            box-shadow: 0 0 12px rgba(0, 230, 118, 0.8);
        }

        .status-dot.purple {
            background: #d500f9;
            box-shadow: 0 0 12px rgba(213, 0, 249, 0.8);
        }

        .timestamp-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 11px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #90a4ae;
        }

        .timestamp-badge svg {
            margin-right: 2px;
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

        .skeleton-bar {
            height: 22px;
            border-radius: 999px;
            background: linear-gradient(90deg, #222 0%, #333 50%, #222 100%);
            background-size: 200% 100%;
            animation: skeleton-loading 1.5s infinite;
            margin-bottom: 10px;
        }

        .bottom-bar {
            position: sticky;
            bottom: 0;
            background: #000000;
            padding: 10px 16px 6px 16px;
            border-top: 1px solid #222;
            box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.8);
        }

        .bottom-label {
            font-size: 13px;
            color: #aaa;
        }

        .bottom-value {
            font-size: 16px;
            font-weight: 700;
            color: #fff;
        }

        .bottom-change {
            font-size: 13px;
            font-weight: 600;
            color: #4CAF50;
        }

    </style>
    """,
    unsafe_allow_html=True,
)

# --- PAGE HEADER ---
header_col1, header_col2 = st.columns([2, 1])

with header_col1:
    st.markdown(
        """
        <div style="margin-bottom: 8px;">
            <span class="subtitle-badge">
                <span class="dot"></span>
                <span>Quantitative Market Force Terminal</span>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="gammamaps-logo">GAMMAMAPS</div>', unsafe_allow_html=True)

with header_col2:
    st.markdown(
        """
        <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:4px;">
            <div class="status-chip">
                <span class="status-dot green"></span>
                Live GEX Feeds
            </div>
            <div class="status-chip">
                <span class="status-dot purple"></span>
                0DTE Focus
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")  # small spacing

# --- SIDEBAR CONTROLS AREA ---
control_col1, control_col2, control_col3 = st.columns([1.4, 1.2, 1.2])

with control_col1:
    selected_symbol = st.selectbox("Select Ticker", AVAILABLE_SYMBOLS, index=0)

with control_col2:
    refresh_display = f"{REFRESH_INTERVAL // 1000}s"
    st.text_input("Auto-refresh", refresh_display, disabled=True)

with control_col3:
    st.text_input("View Mode", "Net GEX Heatmap", disabled=True)

st.write("")

# --- FETCH EXPIRATIONS ---
try:
    resp = requests.get(EXPIRATIONS_URL, params={"symbol": selected_symbol}, timeout=5)
    resp.raise_for_status()
    expirations = resp.json().get("expirations", [])
except Exception:
    expirations = []

if not expirations:
    st.error("No expirations available from backend.")
    st.stop()

# --- FETCH NODES FOR EACH EXPIRY ---
expiry_data = {}
for exp in expirations:
    try:
        r = requests.get(API_URL, params={"symbol": selected_symbol, "expiration": exp}, timeout=8)
        if r.status_code == 200:
            expiry_data[exp] = r.json()
        else:
            expiry_data[exp] = {}
    except Exception:
        expiry_data[exp] = {}

# --- CONFLUENCE WIDGET ---
first_exp_data = expiry_data.get(expirations[0], {})
net_gex = first_exp_data.get("net_exposure", 0) or 0

# Determine a highlight strike for styling (front-expiry king level if available)
highlight_strike = None
first_nodes = first_exp_data.get("all_nodes", [])
if isinstance(first_nodes, list) and first_nodes:
    try:
        df_first = pd.DataFrame(first_nodes)
        if "strike" in df_first.columns and "is_king" in df_first.columns:
            kings = df_first[df_first["is_king"] == True]
            if not kings.empty:
                highlight_strike = float(kings.iloc[0]["strike"])
    except Exception:
        highlight_strike = None

glow_style = "border: 1px solid rgba(255, 255, 255, 0.1);"
status_msg = f"{selected_symbol} MARKET STATE: NEUTRAL"
status_color = "#888"

if net_gex > 0:
    glow_style = "border: 1px solid rgba(0, 255, 0, 0.4); animation: pulse-green 2.8s infinite;"
    status_msg = f"{selected_symbol} MARKET STATE: POSITIVE GEX (LOW VOL)"
    status_color = "#00e676"
elif net_gex < 0:
    glow_style = "border: 1px solid rgba(213, 0, 249, 0.4); animation: pulse-purple 2.8s infinite;"
    status_msg = f"{selected_symbol} MARKET STATE: NEGATIVE GEX (HIGH VOL)"
    status_color = "#d500f9"

last_updated = first_exp_data.get("last_updated", "")

st.markdown(
    f"""
    <div class="core-widget" style="{glow_style}">
        <div style="font-size: 15px; color: #90a4ae; letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 6px;">
            <span style="opacity:0.8;">Dealer Positioning Atlas</span>
        </div>
        <div style="font-size: 22px; font-weight: 600; color: {status_color}; margin-bottom: 10px;">
            {status_msg}
        </div>

        <div style="display:flex; justify-content:center; gap:24px; align-items:center;">
            <div class="ticker-pill">
                <span class="label">Ticker</span>
                <span style="font-weight: 700; color:#fff;">{selected_symbol}</span>
            </div>
            <div class="ticker-pill">
                <span class="label">Net GEX (0DTE)</span>
                <span class="change-up">{net_gex/1e9:+.2f}B</span>
            </div>
            <div class="ticker-pill">
                <span class="label">Spot</span>
                <span style="font-weight: 700;">${first_exp_data.get("spot", 0):,.2f}</span>
            </div>
            <div class="ticker-pill">
                <span class="label">Live</span>
                <span class="live-dot"></span>
            </div>
        </div>

        <div style="margin-top: 12px; display:flex; justify-content:center;">
            <div class="timestamp-badge">
                <span style="display:inline-flex; align-items:center; margin-right:6px;">
                    🕒
                </span>
                <span>Last Update: {last_updated or "N/A"}</span>
            </div>
        </div>

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

            abs_val = abs(val)

            # Normalize absolute GEX value into [0, 1] so stronger levels -> darker colors
            if max_gex > min_gex:
                strength_pct = (abs_val - min_gex) / (max_gex - min_gex)
            else:
                strength_pct = 0.0

            # Special styling for "king" levels – deep purple bar
            if row.get("is_king"):
                col_colors.append("#4B007F")
            else:
                # Single green color scale: stronger level => darker green
                if strength_pct > 0.90:
                    base_color = "#1B5E20"
                elif strength_pct > 0.75:
                    base_color = "#2E7D32"
                elif strength_pct > 0.60:
                    base_color = "#388E3C"
                elif strength_pct > 0.45:
                    base_color = "#4CAF50"
                elif strength_pct > 0.30:
                    base_color = "#66BB6A"
                elif strength_pct > 0.15:
                    base_color = "#A5D6A7"
                elif strength_pct > 0.05:
                    base_color = "#C8E6C9"
                else:
                    base_color = "#E8F5E9"

                col_colors.append(base_color)
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

strike_colors = []
for s in sorted_strikes:
    if highlight_strike is not None and abs(s - highlight_strike) < 1e-6:
        strike_colors.append("#FFFFFF")
    else:
        strike_colors.append("#000000")

all_colors = [strike_colors] + exp_colors

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
                line_color="#111111",
            ),
        )
    ]
)

fig.update_layout(
    margin=dict(l=0, r=0, t=4, b=4),
    height=640,
)

st.plotly_chart(fig, use_container_width=True)

# --- BOTTOM TICKER BAR ---
spot = first_exp_data.get("spot", 0)
st.markdown(
    f"""
    <div class="bottom-bar">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div class="bottom-label">All Tickers</div>
                <div class="bottom-value">{selected_symbol}</div>
            </div>
            <div>
                <div class="bottom-label">Last</div>
                <div class="bottom-value">${spot:,.2f}</div>
            </div>
            <div>
                <div class="bottom-label">Change</div>
                <div class="bottom-change">+0.00 (+0.00%)</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Small JS hook to fade-in plotly table
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
