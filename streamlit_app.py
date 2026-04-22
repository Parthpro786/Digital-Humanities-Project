import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import altair as alt
import plotly.graph_objects as go
from scipy import stats
from sklearn.neighbors import KernelDensity
from itertools import combinations
import feedparser

# =============================================================================
# 1. PAGE CONFIG
# =============================================================================
st.set_page_config(layout="wide", page_title="Strategic Topography GIS", page_icon="◆")

# =============================================================================
# 2. CINEMATIC BLACK + GOLD THEME
# =============================================================================
st.markdown("""
    <style>
    /* ---------- FONT IMPORTS ---------- */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700;900&family=Inter:wght@300;400;500;600;700;800&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@300;400;500&display=swap');

    /* ---------- COLOR TOKENS ---------- */
    :root {
        --bg-0:        #05060a;
        --bg-1:        #0a0b10;
        --bg-2:        #10111a;
        --bg-3:        #161826;
        --line:        rgba(212, 175, 55, 0.18);
        --line-soft:   rgba(212, 175, 55, 0.08);
        --gold:        #D4AF37;
        --gold-soft:   #C9A961;
        --gold-deep:   #8B6F1F;
        --champagne:   #E8C872;
        --ivory:       #F5ECD7;
        --text-hi:     #F5ECD7;
        --text-md:     #C9C2B2;
        --text-lo:     #8A8470;
        --danger:      #E04B4B;
        --warn:        #E8A23A;
        --ok:          #8BBF6B;
    }

    /* ---------- GLOBAL BASE ---------- */
    .stApp {
        background:
            radial-gradient(1200px 700px at 85% -10%, rgba(212, 175, 55, 0.07), transparent 60%),
            radial-gradient(900px 500px at -5% 110%, rgba(212, 175, 55, 0.05), transparent 60%),
            linear-gradient(180deg, #05060a 0%, #07080d 50%, #05060a 100%);
        color: var(--text-hi);
    }

    /* Subtle grain texture */
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0.82 0 0 0 0 0.69 0 0 0 0 0.22 0 0 0 0.06 0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");
        opacity: 0.55;
        mix-blend-mode: overlay;
        z-index: 0;
    }
    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 3rem;
        max-width: 98%;
        position: relative;
        z-index: 1;
    }
    #MainMenu, footer, header [data-testid="stToolbar"] { visibility: hidden; }

    /* ---------- TYPOGRAPHY ---------- */
    html, body, [class*="css"], p, span, div, label, li, td, th {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        color: var(--text-md);
        letter-spacing: 0.005em;
    }
    h1, h2, h3, h4 {
        font-family: 'Playfair Display', serif !important;
        color: var(--ivory) !important;
        letter-spacing: 0.01em;
        font-weight: 600;
    }
    h3 { font-size: 1.6rem !important; }
    strong, b { color: var(--ivory); font-weight: 600; }

    /* ---------- SIDEBAR ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #08090e 0%, #0c0d14 100%);
        border-right: 1px solid var(--line);
    }

    /* ---------- SCROLLBAR ---------- */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: #07080d; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--gold-deep), var(--gold));
        border-radius: 10px;
        border: 2px solid #07080d;
    }

    ::selection { background: rgba(212, 175, 55, 0.35); color: var(--ivory); }

    /* ---------- HERO BANNER ---------- */
    .hero-wrap {
        position: relative;
        padding: 38px 44px;
        border-radius: 18px;
        margin-bottom: 34px;
        background:
            radial-gradient(800px 300px at 100% 0%, rgba(212, 175, 55, 0.14), transparent 60%),
            linear-gradient(135deg, #0b0c12 0%, #131424 60%, #0b0c12 100%);
        border: 1px solid var(--line);
        box-shadow:
            0 40px 80px -40px rgba(0, 0, 0, 0.8),
            inset 0 1px 0 rgba(212, 175, 55, 0.12);
        overflow: hidden;
    }
    .hero-wrap::before {
        content: "";
        position: absolute;
        inset: 0;
        background: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='40' height='40'><path d='M0 39 L40 39 M39 0 L39 40' stroke='%23D4AF37' stroke-width='0.3' opacity='0.18'/></svg>");
        opacity: 0.35;
        pointer-events: none;
    }
    .hero-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 24px;
        position: relative;
        z-index: 2;
    }
    .hero-title {
        font-family: 'Playfair Display', serif !important;
        font-size: 46px !important;
        font-weight: 700 !important;
        letter-spacing: 0.015em !important;
        margin: 0 !important;
        line-height: 1.05;
        background: linear-gradient(92deg,
            #F5ECD7 0%, #E8C872 28%, #D4AF37 50%, #E8C872 72%, #F5ECD7 100%);
        background-size: 220% auto;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        color: transparent;
        animation: gold-shimmer 7s linear infinite;
    }
    .hero-eyebrow {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10.5px;
        letter-spacing: 0.32em;
        text-transform: uppercase;
        color: var(--gold);
        opacity: 0.85;
        margin-bottom: 10px;
    }
    .hero-sub {
        font-family: 'Cormorant Garamond', serif;
        color: var(--text-md);
        font-size: 17px;
        font-style: italic;
        letter-spacing: 0.01em;
        margin: 14px 0 0 0;
        max-width: 780px;
        line-height: 1.55;
    }
    .uplink-pill {
        font-family: 'JetBrains Mono', monospace;
        padding: 8px 14px;
        border-radius: 999px;
        font-size: 10.5px;
        letter-spacing: 0.24em;
        color: var(--gold);
        border: 1px solid var(--line);
        background: rgba(212, 175, 55, 0.05);
        display: inline-flex;
        align-items: center;
        gap: 8px;
        backdrop-filter: blur(8px);
    }
    @keyframes gold-shimmer { to { background-position: 220% center; } }
    @keyframes pulse-gold {
        0%   { box-shadow: 0 0 0 0   rgba(212, 175, 55, 0.75); }
        70%  { box-shadow: 0 0 0 10px rgba(212, 175, 55, 0); }
        100% { box-shadow: 0 0 0 0   rgba(212, 175, 55, 0); }
    }
    .pulse-dot-gold {
        width: 8px; height: 8px; border-radius: 50%;
        background: var(--gold);
        animation: pulse-gold 2s infinite;
    }

    /* ---------- GLASS HUD CARDS ---------- */
    .hud-card {
        background: linear-gradient(180deg, rgba(22, 24, 38, 0.55) 0%, rgba(10, 11, 16, 0.55) 100%);
        backdrop-filter: blur(18px) saturate(140%);
        -webkit-backdrop-filter: blur(18px) saturate(140%);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 22px 24px;
        position: relative;
        overflow: hidden;
        transition: transform 0.4s cubic-bezier(.2,.8,.2,1), border-color 0.3s, box-shadow 0.4s;
    }
    .hud-card::before {
        content: "";
        position: absolute;
        left: 0; top: 0;
        width: 2px; height: 100%;
        background: linear-gradient(180deg, transparent, var(--gold), transparent);
        opacity: 0.7;
    }
    .hud-card:hover {
        transform: translateY(-4px);
        border-color: rgba(212, 175, 55, 0.42);
        box-shadow: 0 24px 50px -24px rgba(212, 175, 55, 0.22);
    }
    .hud-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10.5px;
        letter-spacing: 0.26em;
        text-transform: uppercase;
        color: var(--gold);
        opacity: 0.82;
        margin-bottom: 10px;
    }
    .hud-value {
        font-family: 'Playfair Display', serif;
        font-size: 40px;
        font-weight: 700;
        line-height: 1.05;
        color: var(--ivory);
        letter-spacing: 0.01em;
    }

    /* ---------- GLASS METRIC BOX ---------- */
    .metric-box {
        background: linear-gradient(180deg, rgba(22, 24, 38, 0.5), rgba(10, 11, 16, 0.5));
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        padding: 18px 20px;
        border-radius: 12px;
        border: 1px solid var(--line);
        border-left: 3px solid var(--gold);
        margin-bottom: 14px;
    }
    .metric-title {
        color: var(--gold);
        font-family: 'JetBrains Mono', monospace;
        font-size: 10.5px;
        text-transform: uppercase;
        letter-spacing: 0.26em;
        margin-bottom: 8px;
        font-weight: 500;
    }
    .metric-text {
        color: var(--text-hi);
        font-size: 15px;
        line-height: 1.65;
        font-family: 'Inter', sans-serif;
    }
    .metric-text b { color: var(--champagne); }

    /* ---------- CAP TAGS ---------- */
    .tag-large, .tag-mid, .tag-small {
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.2em;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 4px;
        border: 1px solid;
    }
    .tag-large { color: #F1B0B0; border-color: rgba(224, 75, 75, 0.45); background: rgba(224, 75, 75, 0.08); }
    .tag-mid   { color: #F4CE8F; border-color: rgba(232, 162, 58, 0.45); background: rgba(232, 162, 58, 0.08); }
    .tag-small { color: #C4E0A8; border-color: rgba(139, 191, 107, 0.45); background: rgba(139, 191, 107, 0.08); }

    /* ---------- BUTTONS ---------- */
    .stButton > button {
        background: linear-gradient(135deg, #1a1b26 0%, #0e0f17 100%);
        color: var(--gold) !important;
        border: 1px solid var(--gold) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 500 !important;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        font-size: 11px !important;
        padding: 12px 22px !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--gold) 0%, var(--champagne) 100%) !important;
        color: #0a0b10 !important;
        box-shadow: 0 12px 28px -10px rgba(212, 175, 55, 0.55) !important;
        transform: translateY(-1px);
    }
    .stButton > button:focus { box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.35) !important; }

    /* ---------- TABS ---------- */
    [data-baseweb="tab-list"] { gap: 6px !important; border-bottom: 1px solid var(--line) !important; }
    button[data-baseweb="tab"] {
        background: transparent !important;
        border: 1px solid transparent !important;
        border-bottom: none !important;
        border-radius: 10px 10px 0 0 !important;
        padding: 14px 26px !important;
        transition: all 0.3s ease !important;
    }
    button[data-baseweb="tab"] p {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11.5px !important;
        letter-spacing: 0.22em !important;
        color: var(--text-lo) !important;
        text-transform: uppercase;
        font-weight: 500 !important;
    }
    button[data-baseweb="tab"]:hover p { color: var(--champagne) !important; }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(180deg, rgba(212, 175, 55, 0.10), rgba(212, 175, 55, 0.02)) !important;
        border-color: var(--line) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] p { color: var(--gold) !important; font-weight: 600 !important; }
    [data-baseweb="tab-highlight"] {
        background: linear-gradient(90deg, transparent, var(--gold), transparent) !important;
        height: 2px !important;
    }

    /* ---------- SLIDER ---------- */
    .stSlider label { font-family: 'JetBrains Mono', monospace !important; font-size: 10.5px !important; letter-spacing: 0.26em !important; color: var(--gold) !important; text-transform: uppercase; }
    .stSlider [data-baseweb="slider"] div[data-testid="stTickBar"] { height: 4px !important; border-radius: 3px !important; background: rgba(212, 175, 55, 0.15) !important; }
    .stSlider [data-baseweb="slider"] [role="slider"] {
        width: 20px !important; height: 20px !important;
        background: radial-gradient(circle, var(--gold) 0%, var(--gold-deep) 100%) !important;
        border: 2px solid #0a0b10 !important;
        box-shadow: 0 0 0 2px var(--gold), 0 0 20px rgba(212, 175, 55, 0.55) !important;
    }
    .stSlider [data-baseweb="slider"] [role="slider"] ~ div { color: var(--gold) !important; font-family: 'JetBrains Mono', monospace !important; }

    /* ---------- ALERTS ---------- */
    [data-testid="stAlert"] {
        background: linear-gradient(180deg, rgba(22, 24, 38, 0.6), rgba(10, 11, 16, 0.6)) !important;
        backdrop-filter: blur(12px);
        border: 1px solid var(--line) !important;
        border-left: 3px solid var(--gold) !important;
        border-radius: 10px !important;
        color: var(--text-hi) !important;
    }
    [data-testid="stAlert"] * { color: var(--text-hi) !important; }

    /* ---------- DATAFRAME ---------- */
    [data-testid="stDataFrame"] {
        background: rgba(10, 11, 16, 0.5) !important;
        border: 1px solid var(--line) !important;
        border-radius: 10px !important;
        overflow: hidden;
    }

    /* ---------- IMAGES ---------- */
    [data-testid="stImage"] img {
        border-radius: 12px;
        border: 1px solid var(--line);
        box-shadow: 0 20px 40px -20px rgba(0, 0, 0, 0.8);
    }

    /* ---------- MAP LEGEND ---------- */
    .map-legend {
        background: linear-gradient(180deg, rgba(22, 24, 38, 0.7), rgba(10, 11, 16, 0.7));
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 12px 18px;
        margin-top: 10px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.08em;
        color: var(--text-md);
    }
    .map-legend b { color: var(--gold); letter-spacing: 0.22em; text-transform: uppercase; font-size: 10.5px; }
    .map-legend .sep { color: var(--text-lo); margin: 0 10px; }

    /* ---------- SECTION EYEBROW ---------- */
    .section-eyebrow {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10.5px;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        color: var(--gold);
        margin: 30px 0 6px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-eyebrow::before { content: ""; width: 22px; height: 1px; background: var(--gold); }
    .section-heading {
        font-family: 'Playfair Display', serif !important;
        color: var(--ivory) !important;
        font-size: 28px;
        font-weight: 600;
        margin: 0 0 8px 0;
        letter-spacing: 0.005em;
    }
    .section-kicker {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        color: var(--text-md);
        font-size: 15px;
        margin-bottom: 18px;
    }

    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, var(--line), transparent) !important;
        margin: 28px 0 !important;
    }

    @media (max-width: 900px) {
        .hero-title { font-size: 32px !important; }
        .hud-value { font-size: 30px; }
        .block-container { padding-top: 1rem; }
        .hero-wrap { padding: 24px 22px; }
    }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# 3. STATE
# =============================================================================
if "selected_node" not in st.session_state:
    st.session_state.selected_node = None

def clear_selection():
    st.session_state.selected_node = None

# =============================================================================
# 4. CURVE + RSS HELPERS
# =============================================================================
def generate_curve(start, end, bend=0.2):
    p0, p2 = np.array(start), np.array(end)
    mid = (p0 + p2) / 2
    perp = np.array([-(p2[1]-p0[1]), p2[0]-p0[0]])
    p1 = mid + perp * bend
    t = np.linspace(0, 1, 30)
    curve = np.outer((1-t)**2, p0) + np.outer(2*(1-t)*t, p1) + np.outer(t**2, p2)
    return curve.tolist(), curve[15].tolist()

@st.cache_data(ttl=3600)
def fetch_live_intelligence():
    url = "https://news.google.com/rss/search?q=India+semiconductor+manufacturing&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    return feed.entries[:7]

# =============================================================================
# 5. DATASET — PRESERVED EXACTLY
# =============================================================================
data = [
    {"name": "TSMC Fab 18 (Taiwan)", "region": "Global", "cap": "Large", "lat": 23.10, "lon": 120.28},
    {"name": "TSMC Kumamoto (Japan)", "region": "Global", "cap": "Large", "lat": 32.88, "lon": 130.84},
    {"name": "Intel Ocotillo (USA)", "region": "Global", "cap": "Large", "lat": 33.27, "lon": -111.88},
    {"name": "Intel Magdeburg (Germany)", "region": "Global", "cap": "Large", "lat": 52.12, "lon": 11.62},
    {"name": "Samsung Taylor (USA)", "region": "Global", "cap": "Large", "lat": 30.56, "lon": -97.40},
    {"name": "Samsung Pyeongtaek (Korea)", "region": "Global", "cap": "Large", "lat": 37.02, "lon": 127.04},
    {"name": "Micron Boise (USA)", "region": "Global", "cap": "Large", "lat": 43.52, "lon": -116.15},
    {"name": "Rapidus Hokkaido (Japan)", "region": "Global", "cap": "Large", "lat": 42.76, "lon": 141.67},
    {"name": "GlobalFoundries Dresden (Ger)", "region": "Global", "cap": "Mid", "lat": 51.12, "lon": 13.71},
    {"name": "SMIC Shanghai (China)", "region": "Global", "cap": "Large", "lat": 31.20, "lon": 121.59},
    {"name": "Tata-PSMC Dholera", "region": "India", "year": 2026, "cap": "Large", "lat": 22.25, "lon": 72.11, "elev": 15, "terrain": "Coastal Plateau", "w_name": "Sabarmati Desalination", "w_lat": 22.50, "w_lon": 72.30, "w_dist": 32, "m_name": "Gulf of Khambhat Port", "m_lat": 21.75, "m_lon": 72.25, "m_dist": 55, "l_name": "Ahmedabad Urban Center", "l_lat": 23.02, "l_lon": 72.57, "l_dist": 85, "bt": "India's First Commercial 28nm Mega-Fab. Sovereign logic node production.", "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRqIQdQsnEGk-qsjXopCw4ZG3o-HgKqlO5aDg&s", "profile": [0, 8, 3, 14, 15, 15, 15, 15, 11, 4, 5], "sti": 99.5, "lcp": 0.97, "rad": [99, 95, 98, 90, 85], "rationale": "Engineered for 0.02% seismic vibration friction. The absolute flatness prevents multi-billion dollar EUV wafer spoilage. Proximity to deep-water port yields high logistical cost-efficiency."},
    {"name": "Tata-TSAT Assam", "region": "India", "year": 2026, "cap": "Large", "lat": 26.24, "lon": 92.33, "elev": 55, "terrain": "River Valley", "w_name": "Brahmaputra Basin", "w_lat": 26.50, "w_lon": 92.60, "w_dist": 40, "m_name": "Haldia Port Transit", "m_lat": 25.50, "m_lon": 91.00, "m_dist": 180, "l_name": "Guwahati Metropolis", "l_lat": 26.14, "l_lon": 91.73, "l_dist": 65, "bt": "Sovereign Advanced Packaging Hub. Eastern frontier geopolitical hedge.", "img": "https://scontent.ftrv2-1.fna.fbcdn.net/v/t39.30808-6/535992862_1186350260197029_12401593196388291_n.jpg?stp=dst-jpg_s640x640_tt6&_nc_cat=104&ccb=1-7&_nc_sid=13d280&_nc_ohc=uCGe0x5dj7IQ7kNvwHTQgRh&_nc_oc=Adq6zKwzlR2PEBXHhilqH0ybFDm2k1OPVn86DKpb-J71nSTjjZg6rRqRNBjtcoly4QU&_nc_zt=23&_nc_ht=scontent.ftrv2-1.fna&_nc_gid=8jhxxgLQ08IWL_0Y-iLOqw&_nc_ss=7a389&oh=00_AfwQOBe7hb8uQei8t2dpJOMUz9Oz_MkAaaYJQhb18tjNUg&oe=69D1291B", "profile": [120, 140, 85, 40, 55, 55, 55, 80, 130, 95, 110], "sti": 84.4, "lcp": 0.70, "rad": [75, 99, 65, 95, 80], "rationale": "High topographical friction (34% higher logistics cost) is offset by strategic geographic defense and inexhaustible fresh water supply for Chemical Mechanical Polishing (CMP)."},
    {"name": "Micron Sanand", "region": "India", "year": 2024, "cap": "Large", "lat": 22.98, "lon": 72.37, "elev": 45, "terrain": "Industrial Plains", "w_name": "Narmada Canal System", "w_lat": 23.10, "w_lon": 72.50, "w_dist": 20, "m_name": "Mundra Port Transit", "m_lat": 22.80, "m_lon": 72.00, "m_dist": 250, "l_name": "Sanand Industrial GIDC", "l_lat": 22.95, "l_lon": 72.38, "l_dist": 5, "bt": "High Bandwidth Memory (HBM) ATMP validation.", "img": "https://scontent.ftrv2-1.fna.fbcdn.net/v/t39.30808-6/539589177_1185658950266160_3534972847653672713_n.jpg?stp=dst-jpg_s640x640_tt6&_nc_cat=106&ccb=1-7&_nc_sid=13d280&_nc_ohc=tDQVQ4vl_YIQ7kNvwE48ola&_nc_oc=AdqGo0sl9fFkN5yCSlit_MTSAPDNAuZBxl2WI1DpfV1CZQYvSvD5bqppSoVRPxZsd2U&_nc_zt=23&_nc_ht=scontent.ftrv2-1.fna&_nc_gid=MVD5QTrX8ZKup4kRM4qx1w&_nc_ss=7a389&oh=00_AfyKzVMKFRajrsAvhnLhJn2a3qcg7NzLBAHi-yScuNspMg&oe=69D13CE2", "profile": [10, 18, 12, 35, 45, 45, 45, 42, 48, 44, 48], "sti": 92.0, "lcp": 0.90, "rad": [90, 85, 88, 85, 98], "rationale": "Chosen for pre-existing grid stability and rapid scalability. Flat plains allow for rapid construction modularity without deep-pile foundation engineering."},
    {"name": "CG Power-Renesas Sanand", "region": "India", "year": 2025, "cap": "Mid", "lat": 23.00, "lon": 72.35, "elev": 43, "terrain": "Industrial Plains", "w_name": "Narmada Canal System", "w_lat": 23.10, "w_lon": 72.50, "w_dist": 22, "m_name": "Regional Rail Freight", "m_lat": 22.80, "m_lon": 72.20, "m_dist": 28, "l_name": "Ahmedabad Urban Grid", "l_lat": 23.02, "l_lon": 72.57, "l_dist": 25, "bt": "Specialized OSAT for consumer and industrial power management ICs.", "img": "https://scontent.ftrv2-1.fna.fbcdn.net/v/t39.30808-6/536276519_1089638920018545_3749532980793753876_n.jpg?stp=dst-jpg_s640x640_tt6&_nc_cat=105&ccb=1-7&_nc_sid=13d280&_nc_ohc=Y5plPb5MCwgQ7kNvwEvXhxY&_nc_oc=AdpUyQYZysaFWNGXWTGDJ06tHVseSYdZqEV6Z-Ja5d3FuvUoz0cCk_MSOqc5lAnSYXQ&_nc_zt=23&_nc_ht=scontent.ftrv2-1.fna&_nc_gid=u0kpeP0xHHjhvfEkygxlFw&_nc_ss=7a389&oh=00_AfxJIGoSkrrBSYkniuOf2uw4HniVB9d1rM9ntB3B8mS4fw&oe=69D1333C", "profile": [20, 28, 22, 38, 43, 43, 43, 40, 48, 42, 46], "sti": 89.0, "lcp": 0.88, "rad": [90, 85, 92, 85, 95], "rationale": "Leverages the same topographical stability as the Micron facility, creating a localized high-density packaging cluster with shared logistics."},
    {"name": "Texas Instruments Bangalore", "region": "India", "year": 1985, "cap": "Large", "lat": 12.97, "lon": 77.59, "elev": 920, "terrain": "Deccan Plateau", "w_name": "Cauvery Basin Municipal", "w_lat": 12.40, "w_lon": 77.30, "w_dist": 85, "m_name": "HAL Airport Data Transit", "m_lat": 12.95, "m_lon": 77.66, "m_dist": 12, "l_name": "Bangalore Urban Grid", "l_lat": 12.97, "l_lon": 77.59, "l_dist": 2, "bt": "First Global R&D Center in India. Pioneered satellite data export.", "img": "https://www.ti.com/content/dam/ticom/images/themes/facilities/india-bangalore-corporate-building.jpg", "profile": [850, 890, 860, 910, 920, 920, 920, 890, 915, 870, 880], "sti": 88.0, "lcp": 0.85, "rad": [95, 75, 80, 90, 99], "rationale": "Human-Centric Topography. Elevation provided moderate climate reducing 1980s mainframe cooling loads by 14%. Immediate access to elite engineering institutions."},
    {"name": "SCL Mohali", "region": "India", "year": 1983, "cap": "Small", "lat": 30.70, "lon": 76.69, "elev": 310, "terrain": "Shivalik Foothills", "w_name": "Sutlej River Tributaries", "w_lat": 30.90, "w_lon": 76.50, "w_dist": 28, "m_name": "Northern Rail Depot", "m_lat": 30.50, "m_lon": 76.80, "m_dist": 24, "l_name": "Chandigarh Sector 17", "l_lat": 30.73, "l_lon": 76.77, "l_dist": 10, "bt": "ISRO space-grade and military radiation-hardened 180nm CMOS nodes.", "img": "https://pbs.twimg.com/media/G66Lu77bkAIWVpP.jpg", "profile": [280, 270, 295, 285, 310, 310, 310, 340, 320, 370, 380], "sti": 75.0, "lcp": 0.65, "rad": [60, 85, 65, 99, 88], "rationale": "Defense-in-Depth location. Sacrificed maritime logistics to push sensitive military infrastructure deep inland. Foundation anchored in local bedrock shelf."},
    {"name": "Hind Rectifiers Mumbai", "region": "India", "year": 1980, "cap": "Small", "lat": 19.117, "lon": 72.848, "elev": 10, "terrain": "Western Coastal Plain", "w_name": "Ulhas River Catchment", "w_lat": 19.00, "w_lon": 72.80, "w_dist": 15, "m_name": "JNPT Port Transit", "m_lat": 18.95, "m_lon": 72.90, "m_dist": 60, "l_name": "Mumbai Metropolis", "l_lat": 19.07, "l_lon": 72.87, "l_dist": 5, "bt": "Pioneer in power semiconductor devices for Indian Railways traction rectifiers.", "img": "https://investdesk.in/wp-content/uploads/2024/09/1717276048229.jpg", "profile": [2, 12, 5, 10, 10, 10, 10, 12, 9, 7, 8], "sti": 91.5, "lcp": 0.92, "rad": [65, 80, 98, 90, 99], "rationale": "Classic coastal export config. Sacrifices absolute seismic neutrality (Western Ghats proximity) for hyper-frictionless logistics."},
    {"name": "Qualcomm Hyderabad", "region": "India", "year": 2010, "cap": "Large", "lat": 17.443, "lon": 78.375, "elev": 550, "terrain": "Deccan Plateau", "w_name": "Municipal Mains", "w_lat": 17.40, "w_lon": 78.35, "w_dist": 10, "m_name": "Hyderabad Airport Cargo", "m_lat": 17.25, "m_lon": 78.43, "m_dist": 35, "l_name": "HITEC City Hub", "l_lat": 17.44, "l_lon": 78.38, "l_dist": 5, "bt": "Snapdragon design and validation mega-center. Pure play VLSI node.", "img": "https://content3.jdmagicbox.com/v2/comp/hyderabad/p8/040pxx40.xx40.230926140348.p9p8/catalogue/qualcomm-commerzone-building-silpa-gram-craft-village-hyderabad-corporate-companies-LdctlKINeF.jpg", "profile": [500, 520, 530, 550, 550, 550, 550, 530, 510, 500, 490], "sti": 94.0, "lcp": 0.94, "rad": [92, 85, 90, 88, 99], "rationale": "Chosen for pre-existing grid stability (500kV primary substation) and rapid construction modularity. Human-Centric Topography."},
    {"name": "Tessolve Bangalore", "region": "India", "year": 2005, "cap": "Mid", "lat": 12.923, "lon": 77.682, "elev": 910, "terrain": "Deccan Plateau", "w_name": "Cauvery Basins pipelines", "w_lat": 12.45, "w_lon": 77.40, "w_dist": 75, "m_name": "HAL Airport Data Transit", "m_lat": 12.95, "m_lon": 77.66, "m_dist": 12, "l_name": "Electronics City Grid", "l_lat": 12.93, "l_lon": 77.69, "l_dist": 5, "bt": "Global validation and testing engineering hub. Critical for wafer sort.", "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRCgAYNBA-p238CAGyLa0plRWE4ahnz_MAqKg&s", "profile": [860, 880, 890, 910, 910, 910, 910, 890, 880, 870, 860], "sti": 89.0, "lcp": 0.88, "rad": [95, 80, 85, 92, 98], "rationale": "Standard high-plateau configuration. Leveraging the same topographical stability as the TI campus, maximizing labor corridor access."},
    {"name": "Continental Device India Limited", "region": "India", "year": 1964, "cap": "Small", "lat": 28.667, "lon": 77.217, "elev": 210, "terrain": "Indo-Gangetic Plains", "w_name": "Yamuna River Pipelines", "w_lat": 28.60, "w_lon": 77.20, "w_dist": 15, "m_name": "NCR Rail Corridor", "m_lat": 28.70, "m_lon": 77.25, "m_dist": 10, "l_name": "Delhi Urban Grid", "l_lat": 28.67, "l_lon": 77.22, "l_dist": 5, "bt": "India's first fabless design and discrete transistor manufacturing.", "img": "https://pbs.twimg.com/media/GyJiMM4XQAAIBrY?format=jpg&name=small", "profile": [190, 195, 200, 210, 210, 210, 210, 200, 198, 195, 190], "sti": 78.0, "lcp": 0.65, "rad": [65, 70, 88, 85, 99], "rationale": "Built for proximity to the National Capital. Topographical variance is high due to the Yamuna river plain's inherent instability."}
]

df = pd.DataFrame(data)

# =============================================================================
# 6. MAP ENCODING + PULSING HALOS
# =============================================================================
ICON_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-atlas.png"
icon_data = {"url": ICON_URL, "width": 128, "height": 128, "y": 128, "anchorY": 128}
df['icon_data'] = [icon_data for _ in range(len(df))]

def get_color(cap):
    if cap == "Large": return [224, 75, 75]
    if cap == "Mid":   return [232, 162, 58]
    return [139, 191, 107]

def get_glow_color(cap):
    if cap == "Large": return [224, 75, 75, 90]
    if cap == "Mid":   return [232, 162, 58, 90]
    return [139, 191, 107, 90]

df['color'] = df['cap'].apply(get_color)
df['glow_color'] = df['cap'].apply(get_glow_color)

if "pulse_tick" not in st.session_state:
    st.session_state.pulse_tick = 0
st.session_state.pulse_tick = (st.session_state.pulse_tick + 1) % 6

_halo_outer = 28000 + (st.session_state.pulse_tick * 2400)
_halo_mid   = 16000 + (st.session_state.pulse_tick * 1400)
_halo_inner = 7000

df['halo_outer'] = _halo_outer
df['halo_mid']   = _halo_mid
df['halo_inner'] = _halo_inner

# =============================================================================
# 7. HERO
# =============================================================================
st.markdown("""
    <div class='hero-wrap'>
        <div class='hero-top'>
            <div>
                <div class='hero-eyebrow'>◆ Sovereign Intelligence &nbsp;·&nbsp; Vol. I</div>
                <div class='hero-title'>Strategic Topography GIS</div>
            </div>
            <div class='uplink-pill'><span class='pulse-dot-gold'></span> Secure Uplink</div>
        </div>
        <p class='hero-sub'>A cinematic macro-analysis of semiconductor infrastructure, topographical friction, and sovereign routing — rendered as cartographic cinema.</p>
    </div>
""", unsafe_allow_html=True)

# =============================================================================
# 8. TABS
# =============================================================================
tab1, tab2, tab3 = st.tabs(["India Timeline Ecosystem", "Global Macro Ecosystem", "S.T.I. Statistical Distribution"])

# ---- TAB 1 ----
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    selected_year = st.select_slider("◆ Historical Timeline", options=[1980, 1990, 2000, 2010, 2020, 2026], value=2026)
    active_df = df[(df['region'] == 'India') & (df['year'] <= selected_year)].copy()

    avg_sti = f"{active_df['sti'].mean():.1f}%" if not active_df.empty else "N/A"
    avg_lcp = f"{active_df['lcp'].mean():.2f}" if not active_df.empty else "N/A"

    st.markdown(f"""
    <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 22px; margin-top: 18px; margin-bottom: 34px;'>
        <div class='hud-card'><div class='hud-label'>◆ Active Sovereign Nodes</div><div class='hud-value'>{len(active_df)}</div></div>
        <div class='hud-card'><div class='hud-label'>◆ Mean Topographical Index</div><div class='hud-value'>{avg_sti}</div></div>
        <div class='hud-card'><div class='hud-label'>◆ Logistics Efficiency · LCP</div><div class='hud-value'>{avg_lcp}</div></div>
    </div>
    """, unsafe_allow_html=True)

    col_map, col_dossier = st.columns([6, 4], gap="large")

    with col_map:
        layers = [
            pdk.Layer("ScatterplotLayer", active_df, get_position=["lon","lat"], get_fill_color="glow_color", get_radius="halo_outer", opacity=0.20, stroked=False, pickable=False, id="halo_outer"),
            pdk.Layer("ScatterplotLayer", active_df, get_position=["lon","lat"], get_fill_color="glow_color", get_radius="halo_mid",   opacity=0.35, stroked=False, pickable=False, id="halo_mid"),
            pdk.Layer("ScatterplotLayer", active_df, get_position=["lon","lat"], get_fill_color="color",      get_radius="halo_inner", opacity=0.9,  stroked=True,  get_line_color=[245,236,215], line_width_min_pixels=1, pickable=False, id="halo_inner"),
            pdk.Layer("IconLayer", active_df, get_icon="icon_data", get_size=4, size_scale=12, get_position=["lon","lat"], get_color="color", pickable=True, id="facility_pins")
        ]
        init_view = pdk.ViewState(latitude=22.0, longitude=79.0, zoom=4.2, pitch=0)

        if st.session_state.selected_node:
            n = st.session_state.selected_node
            f_coord = [n['lon'], n['lat']]
            w_curve, w_mid = generate_curve([n['w_lon'], n['w_lat']], f_coord, 0.15)
            m_curve, m_mid = generate_curve([n['m_lon'], n['m_lat']], f_coord, -0.2)
            l_curve, l_mid = generate_curve([n['l_lon'], n['l_lat']], f_coord, -0.1)

            route_data = [
                {"path": w_curve, "color": [212, 175, 55]},
                {"path": m_curve, "color": [245, 236, 215]},
                {"path": l_curve, "color": [232, 200, 114]},
            ]
            layers.append(pdk.Layer("PathLayer", pd.DataFrame(route_data), get_path="path", get_color="color", width_scale=20, width_min_pixels=3, get_dash_array=[8, 8], dash_justified=True))

            res_data = [
                {"lon": n['w_lon'], "lat": n['w_lat'], "color": [212, 175, 55]},
                {"lon": n['m_lon'], "lat": n['m_lat'], "color": [245, 236, 215]},
                {"lon": n['l_lon'], "lat": n['l_lat'], "color": [232, 200, 114]}
            ]
            layers.append(pdk.Layer("ScatterplotLayer", pd.DataFrame(res_data), get_position=["lon","lat"], get_fill_color="color", get_radius=3500, stroked=True, get_line_color=[10,11,16]))

            label_data = [
                {"lon": n['lon'], "lat": n['lat'], "text": f"Target: {n['lat']} N, {n['lon']} E", "color": [245,236,215], "offset": [0,-40]},
                {"lon": w_mid[0], "lat": w_mid[1], "text": f"{n['w_dist']}km (Water Corridor)", "color": [212,175,55], "offset": [0,25]},
                {"lon": m_mid[0], "lat": m_mid[1], "text": f"{n['m_dist']}km (Raw Material Transit)", "color": [245,236,215], "offset": [0,-25]},
                {"lon": l_mid[0], "lat": l_mid[1], "text": f"{n['l_dist']}km (Urban Labor Corridor)", "color": [232,200,114], "offset": [40,0]}
            ]
            layers.append(pdk.Layer("TextLayer", pd.DataFrame(label_data), get_position=["lon","lat"], get_text="text", get_color="color", get_size=13, get_alignment_baseline="'center'", get_pixel_offset="offset"))

            init_view = pdk.ViewState(latitude=n['lat'], longitude=n['lon'], zoom=6.8, pitch=0)

        map_event = st.pydeck_chart(
            pdk.Deck(
                layers=layers, initial_view_state=init_view,
                map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
                tooltip={"text": "{name}\nCap: {cap}", "style": {"backgroundColor": "rgba(10,11,16,0.92)", "border": "1px solid rgba(212,175,55,0.4)", "color": "#F5ECD7", "fontFamily": "JetBrains Mono, monospace", "fontSize": "11px", "padding": "8px 12px", "borderRadius": "6px"}}
            ),
            on_select="rerun", selection_mode="single-object"
        )

        st.markdown("""
            <div class='map-legend'>
                <b>Cap Classification</b> &nbsp; · &nbsp;
                <span style="color:#E04B4B">● Large</span><span class='sep'>|</span>
                <span style="color:#E8A23A">● Mid</span><span class='sep'>|</span>
                <span style="color:#8BBF6B">● Small</span>
                &nbsp;&nbsp;&nbsp;&nbsp;
                <b>Logistics Routes</b> &nbsp; · &nbsp;
                <span style="color:#D4AF37">— Water</span><span class='sep'>|</span>
                <span style="color:#F5ECD7">— Material</span><span class='sep'>|</span>
                <span style="color:#E8C872">— Labor</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class='section-eyebrow'>◆ Live Transmission</div>
            <div class='section-heading'>Strategic Intelligence</div>
            <div class='section-kicker'>Real-time dispatches from the semiconductor frontier.</div>
        """, unsafe_allow_html=True)

        try:
            live_news = fetch_live_intelligence()
            labels = ["Latest Dispatch","Industry Update","Macro Trend","Policy Shift","Tech Breakthrough","Market Dynamics","Strategic Move"]

            st.markdown("""<style>
.live-hover-card { background: linear-gradient(180deg, rgba(22,24,38,0.6), rgba(10,11,16,0.6)); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); padding: 16px 20px; border-radius: 10px; margin-bottom: 10px; border: 1px solid rgba(212,175,55,0.18); border-left: 3px solid rgba(212,175,55,0.45); transition: all 0.4s cubic-bezier(.2,.8,.2,1); cursor: pointer; }
.live-hover-card:hover { border-color: rgba(212,175,55,0.6) !important; border-left-color: #D4AF37 !important; transform: translateX(8px); box-shadow: 0 22px 40px -22px rgba(212,175,55,0.45); background: linear-gradient(180deg, rgba(30,28,18,0.75), rgba(18,16,10,0.75)); }
.live-hover-card:hover .hover-title { color: #F5ECD7 !important; }
.live-hover-card:hover .hover-tag { color: #F5ECD7 !important; }
a.card-link { text-decoration: none; display: block; }
</style>""", unsafe_allow_html=True)

            for i, article in enumerate(live_news):
                label = labels[i % len(labels)]
                clean_title = article.title.rsplit(" - ", 1)[0]
                st.markdown(f"""
<a href='{article.link}' target='_blank' class='card-link'>
<div class='live-hover-card'>
<div class='hover-tag' style='color:#D4AF37;font-family:"JetBrains Mono",monospace;font-size:10.5px;font-weight:500;letter-spacing:0.26em;text-transform:uppercase;transition:color 0.3s;'>◆ {label} &nbsp;·&nbsp; {article.published[5:16]}</div>
<div style='margin-top:8px;'><span class='hover-title' style='color:#E8C872;font-family:"Playfair Display",serif;font-weight:500;font-size:16px;line-height:1.45;transition:color 0.3s;letter-spacing:0.005em;'>{clean_title}</span></div>
</div></a>
""", unsafe_allow_html=True)
        except Exception:
            st.warning("Intelligence feed temporarily offline. Unable to establish uplink.")

        st.markdown("""
            <div class='section-eyebrow'>◆ Visual Intelligence</div>
            <div class='section-heading'>The Silicon Hegemony</div>
            <div class='section-kicker'>Live geopolitical and market intersections rendered as editorial cinema.</div>
        """, unsafe_allow_html=True)

        bg_images = [
            "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1590247813693-5541d1c609fd?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=600&q=80"
        ]

        grid_css = """<style>
.news-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:18px; padding-bottom:18px; }
.news-card-grid { width:100%; height:200px; border-radius:14px; background-size:cover; background-position:center; position:relative; overflow:hidden; border:1px solid rgba(212,175,55,0.2); box-shadow:0 20px 40px -20px rgba(0,0,0,0.85); transition:all 0.5s cubic-bezier(.2,.8,.2,1); }
.news-card-grid::after { content:""; position:absolute; inset:0; background:radial-gradient(circle at 30% 10%, rgba(212,175,55,0.18), transparent 55%); opacity:0; transition:opacity 0.5s; }
.news-card-grid:hover { transform:translateY(-6px) scale(1.01); box-shadow:0 32px 60px -20px rgba(212,175,55,0.35); border-color:rgba(212,175,55,0.55); }
.news-card-grid:hover::after { opacity:1; }
.card-overlay { position:absolute; bottom:0; left:0; right:0; background:linear-gradient(to top, rgba(5,6,10,0.96) 0%, rgba(5,6,10,0.75) 55%, rgba(5,6,10,0) 100%); padding:18px 20px; z-index:2; }
.card-tag { font-family:'JetBrains Mono',monospace; font-size:10px; text-transform:uppercase; letter-spacing:0.26em; padding:4px 10px; border-radius:4px; display:inline-block; margin-bottom:10px; color:#D4AF37; background:rgba(212,175,55,0.12); border:1px solid rgba(212,175,55,0.35); }
.card-title-grid { color:#F5ECD7 !important; font-family:'Playfair Display',serif; font-size:16px; font-weight:500; line-height:1.35; text-shadow:0 2px 8px rgba(0,0,0,0.9); letter-spacing:0.005em; }
a { text-decoration:none; }
</style><div class="news-grid">"""

        try:
            live_news = fetch_live_intelligence()
            labels = ["Latest Dispatch","Industry Update","Macro Trend","Policy Shift","Tech Breakthrough","Market Dynamics","Strategic Move"]
            for i, article in enumerate(live_news[:4]):
                clean_title = article.title.rsplit(" - ", 1)[0]
                img = bg_images[i % len(bg_images)]
                tag = labels[i % len(labels)]
                grid_css += f"""
<a href='{article.link}' target='_blank'>
<div class="news-card-grid" style="background-image:url('{img}');">
<div class="card-overlay"><div class="card-tag">◆ {tag}</div><div class="card-title-grid">{clean_title}</div></div>
</div></a>"""
        except Exception:
            grid_css += "<div style='color:#C9C2B2;padding:20px;'>Live visual feed currently unavailable.</div>"
        grid_css += "</div>"
        st.markdown(grid_css, unsafe_allow_html=True)

        if map_event and map_event.selection.objects:
            if "facility_pins" in map_event.selection.objects:
                clicked_data = map_event.selection.objects["facility_pins"]
                if clicked_data and st.session_state.selected_node != clicked_data[0]:
                    st.session_state.selected_node = clicked_data[0]
                    st.rerun()

    with col_dossier:
        if st.session_state.selected_node:
            n = st.session_state.selected_node
            if st.button("◀ Return to Map Overview", use_container_width=True):
                clear_selection()
                st.rerun()

            st.image(n['img'], use_container_width=True)
            st.markdown(f"<h2 style='margin-top:18px;margin-bottom:8px;'>{n['name']}</h2>", unsafe_allow_html=True)
            st.markdown(
                f"<span class='tag-{n['cap'].lower()}'>{n['cap']} Cap Facility</span> "
                f"<span style='color:var(--text-lo);font-family:\"JetBrains Mono\",monospace;font-size:11.5px;letter-spacing:0.08em;margin-left:10px;'>"
                f"{n['lat']}° N · {n['lon']}° E</span>", unsafe_allow_html=True
            )
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<div class='metric-title' style='margin-bottom:10px;'>◆ Topographical Integration Profile</div>", unsafe_allow_html=True)

            total_dist = n['m_dist'] + n['w_dist']
            x_dist = np.linspace(0, total_dist, len(n['profile']))
            chart_df = pd.DataFrame({"Distance (km)": x_dist, "Elevation (MSL)": n['profile']})

            alt_axis = alt.Axis(labelColor="#8A8470", titleColor="#C9A961", labelFont="JetBrains Mono", titleFont="JetBrains Mono", labelFontSize=10, titleFontSize=11, gridColor="rgba(212,175,55,0.08)", domainColor="rgba(212,175,55,0.25)", tickColor="rgba(212,175,55,0.25)")
            base = alt.Chart(chart_df).encode(
                x=alt.X('Distance (km):Q', title=f"0km ({n['m_name']}) → {n['m_dist']}km (Facility) → {total_dist}km ({n['w_name']})", axis=alt_axis),
                y=alt.Y('Elevation (MSL):Q', title="Elevation (m)", scale=alt.Scale(domain=[0, max(n['profile'])+50]), axis=alt_axis)
            )
            area = base.mark_area(opacity=0.35, color="#D4AF37")
            line = base.mark_line(color="#E8C872", strokeWidth=2)
            facility_mark = pd.DataFrame({"x":[n['m_dist']], "y":[n['elev']]})
            point = alt.Chart(facility_mark).mark_point(color='#F5ECD7', size=170, shape='diamond', filled=True, stroke='#D4AF37', strokeWidth=2).encode(x='x:Q', y='y:Q')
            final_chart = (area + line + point).properties(background="rgba(0,0,0,0)", padding={"left":5,"right":5,"top":5,"bottom":5}).configure_view(stroke=None).configure(background='transparent')
            st.altair_chart(final_chart, use_container_width=True)

            st.markdown(f"<div class='metric-box'><div class='metric-title'>◆ Strategic Breakthrough</div><div class='metric-text'>{n['bt']}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><div class='metric-title'>◆ Topographical Stabilization · Elevation {n['elev']}m MSL</div><div class='metric-text'>{n['rationale']}</div></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='metric-box'>
                <div class='metric-title'>◆ Logistics Matrix · LCP Efficiency {n['lcp']}</div>
                <div class='metric-text'>
                    <b>Material Hub:</b> {n['m_name']} <span style='color:var(--text-lo)'>· {n['m_dist']}km route</span><br>
                    <b>Water Catchment:</b> {n['w_name']} <span style='color:var(--text-lo)'>· {n['w_dist']}km route</span><br>
                    <b>Urban Labor Center:</b> {n['l_name']} <span style='color:var(--text-lo)'>· {n['l_dist']}km route</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div class='metric-title' style='margin-top:18px;margin-bottom:6px;'>◆ Vulnerability &amp; Stability Radar</div>", unsafe_allow_html=True)
            categories = ['Seismic Stability','Water Security','Logistics Efficiency','Geopolitical Safety','Labor Proximity']
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=n['rad'], theta=categories, fill='toself',
                fillcolor='rgba(212,175,55,0.28)',
                line=dict(color='#E8C872', width=2),
                marker=dict(color='#F5ECD7', size=6),
                name=n['name']
            ))
            fig.update_layout(
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(visible=True, range=[0,100], color='#8A8470', gridcolor='rgba(212,175,55,0.12)', tickfont=dict(color='#8A8470', size=9, family='JetBrains Mono')),
                    angularaxis=dict(tickfont=dict(color='#D4AF37', size=11, family='Inter'), gridcolor='rgba(212,175,55,0.15)', linecolor='rgba(212,175,55,0.25)')
                ),
                showlegend=False, margin=dict(l=80,r=80,t=30,b=30),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("◆  Select a location pin on the map to reveal its Technical Dossier and logistics profile.")

# ---- TAB 2 ----
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class='section-eyebrow'>◆ Global View</div>
        <div class='section-heading'>Macro Semiconductor Ecosystem</div>
        <div class='section-kicker'>The sovereign nodes of the silicon era, mapped across the world stage.</div>
    """, unsafe_allow_html=True)

    global_df = df.copy()
    global_layers = [
        pdk.Layer("ScatterplotLayer", global_df, get_position=["lon","lat"], get_fill_color="glow_color", get_radius=_halo_outer*2, opacity=0.18, stroked=False, pickable=False),
        pdk.Layer("ScatterplotLayer", global_df, get_position=["lon","lat"], get_fill_color="glow_color", get_radius=_halo_mid*2,   opacity=0.32, stroked=False, pickable=False),
        pdk.Layer("ScatterplotLayer", global_df, get_position=["lon","lat"], get_fill_color="color",      get_radius=_halo_inner*2, opacity=0.9, stroked=True, get_line_color=[245,236,215], line_width_min_pixels=1),
        pdk.Layer("IconLayer", global_df, get_icon="icon_data", get_size=4, size_scale=10, get_position=["lon","lat"], get_color="color", pickable=True)
    ]
    st.pydeck_chart(pdk.Deck(
        layers=global_layers,
        initial_view_state=pdk.ViewState(latitude=30.0, longitude=20.0, zoom=1.8, pitch=0),
        map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
        tooltip={"text": "{name}\nCap: {cap}", "style": {"backgroundColor": "rgba(10,11,16,0.92)", "border": "1px solid rgba(212,175,55,0.4)", "color": "#F5ECD7", "fontFamily": "JetBrains Mono, monospace", "fontSize": "11px", "padding": "8px 12px", "borderRadius": "6px"}}
    ))

# ---- TAB 3 ----
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class='section-eyebrow'>◆ Inferential Engine</div>
        <div class='section-heading'>Continuous Probability Density &amp; Inference</div>
    """, unsafe_allow_html=True)
    st.markdown(
        "<p style='color:var(--text-md);font-size:15px;line-height:1.7;max-width:1100px;'>"
        "This module applies Kernel Density Estimation (KDE) and rigorous hypothesis testing to the Strategic Topographical Index (STI). "
        "By modeling the variance ($\\sigma^2$) and mean ($\\mu$) across facility classifications, we can mathematically infer India's sovereign site-selection strategy."
        "</p>", unsafe_allow_html=True
    )

    stats_df = df[(df['region'] == 'India')].dropna(subset=['sti','cap']).copy()

    alt_axis = alt.Axis(labelColor="#8A8470", titleColor="#C9A961", labelFont="JetBrains Mono", titleFont="JetBrains Mono", labelFontSize=10, titleFontSize=11, gridColor="rgba(212,175,55,0.06)", domainColor="rgba(212,175,55,0.25)", tickColor="rgba(212,175,55,0.25)")
    density_plot = alt.Chart(stats_df).transform_density(
        'sti', as_=['sti','density'], groupby=['cap'], extent=[60,110], steps=200, bandwidth=4
    ).mark_area(opacity=0.55).encode(
        x=alt.X('sti:Q', title="Strategic Topographical Index (STI %)", scale=alt.Scale(domain=[65,105]), axis=alt_axis),
        y=alt.Y('density:Q', title="Probability Density", axis=alt.Axis(labels=False, ticks=False, titleColor="#C9A961", titleFont="JetBrains Mono", titleFontSize=11, domainColor="rgba(212,175,55,0.25)"), stack=None),
        color=alt.Color('cap:N', scale=alt.Scale(domain=['Large','Mid','Small'], range=['#E04B4B','#E8A23A','#8BBF6B']),
                        legend=alt.Legend(labelColor="#F5ECD7", titleColor="#D4AF37", labelFont="JetBrains Mono", titleFont="JetBrains Mono", labelFontSize=11, titleFontSize=11, orient='top-right'))
    ).properties(height=360, background='transparent').configure_view(stroke="rgba(212,175,55,0.15)").configure(background='transparent')
    st.altair_chart(density_plot, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    col_stats1, col_stats2 = st.columns(2, gap="large")
    with col_stats1:
        st.markdown("<div class='metric-title' style='margin-top:6px;'>◆ MLE-Based Distribution Parameters</div>", unsafe_allow_html=True)
        summary = stats_df.groupby('cap')['sti'].agg(Mean='mean', Variance='var', Std_Dev='std', Count='count').round(2)
        summary['Skewness'] = stats_df.groupby('cap')['sti'].apply(stats.skew).round(3)
        st.dataframe(summary, use_container_width=True)

        st.markdown("<div class='metric-title' style='margin-top:18px;'>◆ ANOVA Test · Mean STI Differences</div>", unsafe_allow_html=True)
        group_values = [group['sti'].values for name, group in stats_df.groupby('cap')]
        if len(group_values) > 1:
            anova_stat, anova_p = stats.f_oneway(*group_values)
            st.markdown(f"<p style='font-family:\"JetBrains Mono\",monospace;font-size:12.5px;color:var(--text-hi);'><b style='color:var(--gold)'>F-statistic:</b> {anova_stat:.4f} &nbsp;·&nbsp; <b style='color:var(--gold)'>p-value:</b> {anova_p:.4f}</p>", unsafe_allow_html=True)
            if anova_p < 0.05: st.success("Reject $H_0$ → Mean STI differs significantly across Cap categories.")
            else: st.info("Fail to reject $H_0$ → Sample size too small or means are similar.")

        st.markdown("<div class='metric-title' style='margin-top:18px;'>◆ Levene's Test · Variance Equality</div>", unsafe_allow_html=True)
        if len(group_values) > 1:
            levene_stat, levene_p = stats.levene(*group_values)
            st.markdown(f"<p style='font-family:\"JetBrains Mono\",monospace;font-size:12.5px;color:var(--text-hi);'><b style='color:var(--gold)'>Statistic:</b> {levene_stat:.4f} &nbsp;·&nbsp; <b style='color:var(--gold)'>p-value:</b> {levene_p:.4f}</p>", unsafe_allow_html=True)
            if levene_p < 0.05: st.success("Reject $H_0$ → Topographical variances ($\\sigma^2$) are significantly different.")
            else: st.info("Fail to reject $H_0$ → Variances are statistically similar.")

    with col_stats2:
        st.markdown("<div class='metric-title' style='margin-top:6px;'>◆ Chi-Square Test · Categorical Dependency</div>", unsafe_allow_html=True)
        bins = [0, 82, 93, 110]
        labels = ['High Friction (<82)','Moderate (82-93)','Optimal (>93)']
        stats_df['sti_bin'] = pd.cut(stats_df['sti'], bins=bins, labels=labels)
        contingency_table = pd.crosstab(stats_df['cap'], stats_df['sti_bin'])
        st.markdown("<p style='color:var(--text-md);font-size:13px;margin-bottom:6px;'>Contingency Table (Count)</p>", unsafe_allow_html=True)
        st.dataframe(contingency_table, use_container_width=True)

        chi2_stat, chi2_p, dof, expected = stats.chi2_contingency(contingency_table)
        st.markdown(f"<p style='font-family:\"JetBrains Mono\",monospace;font-size:12.5px;color:var(--text-hi);margin-top:8px;'><b style='color:var(--gold)'>Chi²:</b> {chi2_stat:.4f} &nbsp;·&nbsp; <b style='color:var(--gold)'>p-value:</b> {chi2_p:.4f}</p>", unsafe_allow_html=True)
        if chi2_p < 0.05: st.success("Reject $H_0$ → STI risk category strictly depends on facility Cap type.")
        else: st.info("Fail to reject $H_0$ → Dependency not strictly proven at current sample size.")

        st.markdown("<div class='metric-title' style='margin-top:18px;'>◆ KDE Distribution Overlap</div>", unsafe_allow_html=True)
        x_grid = np.linspace(60,110,500).reshape(-1,1)
        densities = {}
        for cap, group in stats_df.groupby('cap'):
            kde = KernelDensity(kernel='gaussian', bandwidth=4.0)
            kde.fit(group['sti'].values.reshape(-1,1))
            densities[cap] = np.exp(kde.score_samples(x_grid))
        overlap_results = []
        for cap1, cap2 in combinations(densities.keys(), 2):
            overlap = np.trapezoid(np.minimum(densities[cap1], densities[cap2]), x_grid.flatten())
            overlap_results.append({"Comparison": f"{cap1} vs {cap2}", "Overlap Coefficient": round(overlap,4)})
        st.dataframe(pd.DataFrame(overlap_results), use_container_width=True, hide_index=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
        <div class='section-eyebrow'>◆ Strategic Doctrine</div>
        <div class='section-heading'>Inferences &amp; Recommendations</div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style='color:var(--text-hi);font-size:15px;line-height:1.75;max-width:1100px;'>
    Based on the inferential statistics derived from the current spatial data, we recommend the following frameworks for future Indian semiconductor expansion:

    1. <b style='color:var(--champagne)'>Strict Stratification of STI Requirements</b> (ANOVA &amp; Overlap Inference): The low KDE overlap coefficient between Large and Small Cap facilities proves that India is already operating on a bifurcated strategy. <b>Recommendation:</b> Future Mega-Fabs (Large Cap) must strictly target topographies with an STI $> 92\\%$ (Coastal Plateaus / Stable Plains). Attempting to build a Large Cap fab in a "Moderate" zone will result in catastrophic logistical and vibration friction.

    2. <b style='color:var(--champagne)'>Leveraging Variance for Geographical Hedging</b> (Levene's Inference): The higher variance ($\\sigma^2$) and left-skewed tails in Small/Mid Cap facilities indicate they can survive in high-friction terrain. <b>Recommendation:</b> The government should incentivize future Mid/Small Cap facilities (OSAT, discrete power, defense) to be built in Eastern and Northern river valleys or foothills. This accepts a lower STI but establishes a distributed <i>Defense-in-Depth</i> network, ensuring the entire supply chain cannot be wiped out by a single coastal weather event or naval blockade.

    3. <b style='color:var(--champagne)'>Resource Catchment Thresholds</b> (Chi-Square Inference): The Chi-Square contingency highlights that high-friction topographies cannot support the mass resource consumption of commercial logic nodes. <b>Recommendation:</b> Future infrastructure planning must mandate that any site with an STI $< 82\\%$ be restricted to specialized, low-volume/high-margin fabrication (e.g., Silicon Carbide, Gallium Nitride) where the volume of required Ultra-Pure Water (UPW) and heavy LCP transit is statistically lower.

    4. <b style='color:var(--champagne)'>Cluster Engineering over Isolated Siting</b>: Planners must transition from isolated "site selection" to "cluster engineering." By anchoring a Large Cap fab (like Tata-PSMC) and immediately surrounding it with Mid Cap OSATs (like CG Power or Micron) within a 50km radius, the LCP efficiency approaches 0.99. This creates a frictionless micro-economy, similar to the Hsinchu Science Park in Taiwan.

    5. <b style='color:var(--champagne)'>Integrated Localized Infrastructure</b>: Future Large Cap facility approvals should require integrated, localized infrastructure. Fabs built in high-STI coastal zones (like Gujarat or Tamil Nadu) must be co-located with dedicated modular nuclear (SMRs) or massive solar/wind parks, alongside captive desalination plants. This insulates the fabs from the municipal grid, ensuring that consumer water and power supplies are not drained by industrial tech demands.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
        <div class='section-eyebrow'>◆ Digital Humanities</div>
        <div class='section-heading'>Infrastructure as Destiny</div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style='color:var(--text-hi);max-width:1100px;font-family:"Cormorant Garamond",serif;font-size:18px;line-height:1.75;'>
    <i>For policymakers, historians, and the general public, the statistical variances shown above are not just numbers — they are the physical blueprints of a new geopolitical cold war.</i>
    <br><br>
    <b style='color:var(--champagne);font-family:"Playfair Display",serif;font-style:normal;'>The Architecture of Paranoia vs. Profit</b> — The KDE graph physically illustrates human motives. The tight cluster of 'Large Cap' Mega-Fabs on flat, coastal plains (High STI) represents <b>Profit</b>. These sites demand topographical perfection to manufacture commercial chips with zero failure rates. Conversely, the wide, left-skewed tail of 'Small Cap' facilities represents <b>Paranoia and Survival</b>. By burying strategic defense foundries deep in high-friction valleys and foothills, the state explicitly sacrifices economic efficiency for geographical immunity against naval blockades or coastal climate disasters.
    <br><br>
    <b style='color:var(--champagne);font-family:"Playfair Display",serif;font-style:normal;'>The Spatialization of Power and Labor</b> — Semiconductors do not just process data; they restructure the earth. The routing data in this GIS model proves that these Mega-Fabs act as gravitational black holes. They literally reroute rivers (desalination pipelines) and dictate human migration, pulling elite intellectual labor into highly specific, localized 'techno-enclaves' (like Dholera or the Assam frontier), permanently altering local cultures and economies.
    <br><br>
    <b style='color:var(--champagne);font-family:"Playfair Display",serif;font-style:normal;'>The Sovereign Shield</b> — To the average citizen, a microchip is invisible. But this map proves that the "Cyber Frontline" is deeply physical. Every time the STI variance shifts, it represents billions of dollars poured into concrete, steel, and water routing to ensure that the silicon powering India's hospitals, military radars, and digital economy cannot be turned off by a foreign power. <b>In the 21st century, geographical infrastructure is destiny.</b>
    </div>
    """, unsafe_allow_html=True)
