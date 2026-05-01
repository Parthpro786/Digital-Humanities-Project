import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objects as go
from scipy import stats
from sklearn.neighbors import KernelDensity
from itertools import combinations
import feedparser
import requests
import datetime
import folium
from streamlit_folium import st_folium

# --- 1. PROFESSIONAL PAGE CONFIG & CSS ---
st.set_page_config(layout="wide", page_title="Strategic Topography GIS", page_icon="🗺️")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Rajdhani:wght@500;600;700&display=swap');

        .stApp { background-color: #0a0a0a; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Rajdhani', sans-serif !important; color: #d4af37 !important; }
        p, span, div, li { font-family: 'Inter', sans-serif; color: #e2e8f0; }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 2rem; padding-bottom: 2rem; max-width: 98%;}
        
        /* --- ANIMATED HERO BANNER --- */
        .hero-banner {
            background: linear-gradient(135deg, #111111 0%, #050505 100%);
            padding: 30px 40px;
            border-radius: 6px;
            margin-bottom: 30px;
            border-top: 2px solid #d4af37;
            border-bottom: 1px solid #1a1a1a;
            box-shadow: 0 15px 35px rgba(0,0,0,0.9), inset 0 0 20px rgba(212, 175, 55, 0.05);
            position: relative;
            overflow: hidden;
        }

        /* Subtle Radar Scanline Overlay */
        .hero-banner::after {
            content: "";
            position: absolute;
            top: -100%; left: 0; width: 100%; height: 200%;
            background: linear-gradient(to bottom, rgba(255,255,255,0) 0%, rgba(212, 175, 55, 0.03) 50%, rgba(255,255,255,0) 100%);
            animation: radar-scan 6s infinite linear;
            pointer-events: none;
        }
        @keyframes radar-scan {
            0% { transform: translateY(-50%); }
            100% { transform: translateY(50%); }
        }

        /* Shimmering Title Text */
        .hero-title {
            font-family: 'Rajdhani', sans-serif !important;
            font-size: 44px !important;
            font-weight: 800 !important;
            margin: 0 !important;
            text-transform: uppercase;
            letter-spacing: 3px;
            background: linear-gradient(90deg, #d4af37 0%, #fff2c8 20%, #d4af37 40%, #b87333 80%, #d4af37 100%);
            background-size: 200% auto;
            color: transparent;
            -webkit-background-clip: text;
            background-clip: text;
            animation: gold-shimmer 5s linear infinite;
            text-shadow: 0px 0px 25px rgba(212, 175, 55, 0.2);
        }
        @keyframes gold-shimmer {
            to { background-position: 200% center; }
        }

        .hero-subtitle {
            color: #888;
            font-size: 14px;
            margin-top: 8px;
            letter-spacing: 2px;
            text-transform: uppercase;
            font-family: 'Inter', sans-serif;
        }

        /* Breathing Border on the Badge */
        .uplink-badge {
            background: rgba(212, 175, 55, 0.05);
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 12px;
            color: #d4af37;
            border: 1px solid rgba(212, 175, 55, 0.3);
            font-weight: 700;
            letter-spacing: 2px;
            display: flex;
            align-items: center;
            font-family: 'Rajdhani', sans-serif;
            animation: border-breathe 3s infinite alternate ease-in-out;
            z-index: 2; /* Keeps it above the scanline */
            position: relative;
        }
        @keyframes border-breathe {
            0% { box-shadow: 0 0 5px rgba(212, 175, 55, 0.1); border-color: rgba(212, 175, 55, 0.3); }
            100% { box-shadow: 0 0 15px rgba(212, 175, 55, 0.4); border-color: rgba(212, 175, 55, 0.8); }
        }

        /* Heartbeat Connection Dot */
        .pulse-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #22c55e; /* Uplink Green */
            margin-right: 10px;
            animation: uplink-ping 1.5s infinite ease-in-out;
        }
        @keyframes uplink-ping {
            0% { transform: scale(0.8); opacity: 0.6; box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
            50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 10px 4px rgba(34, 197, 94, 0); }
            100% { transform: scale(0.8); opacity: 0.6; box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
        }
        
        .hud-card {
            background-color: #111111;
            border: 1px solid #222;
            border-radius: 6px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5);
            border-top: 3px solid #d4af37;
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .hud-card:hover { transform: translateY(-4px); box-shadow: 0 12px 20px -3px rgba(212, 175, 55, 0.15); }
        .hud-value { font-size: 36px; font-family: 'Rajdhani', sans-serif; font-weight: 700; color: #fff; line-height: 1.2; }
        .hud-label { font-size: 11px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 1.5px; }

        .metric-box {
            background-color: #111111; padding: 16px; border-radius: 4px; 
            border-left: 3px solid #d4af37; margin-bottom: 15px; 
            border-top: 1px solid #222; border-right: 1px solid #222; border-bottom: 1px solid #222;
        }
        .metric-title { color: #888; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; font-weight: 600; }
        .metric-text { color: #ccc; font-size: 15px; line-height: 1.6; }

        .tag-large { color: #d4af37; font-weight: bold; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; }
        .tag-mid { color: #b87333; font-weight: bold; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; }
        .tag-small { color: #708090; font-weight: bold; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; }

        .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 20px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #111111 !important; border: 1px solid #222 !important;
            border-bottom: none !important; border-radius: 6px 6px 0 0 !important;
            padding: 12px 24px !important; color: #888 !important;
            font-family: 'Rajdhani', sans-serif !important; font-size: 16px !important;
            letter-spacing: 1px; transition: all 0.3s ease !important;
        }
        .stTabs [data-baseweb="tab"]:hover { color: #d4af37 !important; background-color: #1a1a1a !important; }
        .stTabs [aria-selected="true"] {
            background-color: #1a1a1a !important; color: #d4af37 !important;
            border-top: 3px solid #d4af37 !important; border-color: #d4af37 #222 transparent #222 !important;
        }
        
        .stSlider label { color: #d4af37 !important; font-family: 'Rajdhani', sans-serif !important; font-size: 16px !important;}
        .stSlider [data-baseweb="slider"] div[data-testid="stTickBar"] { background-color: #333 !important; }
        .stSlider [data-baseweb="slider"] [role="slider"] { background-color: #d4af37 !important; border: 2px solid #000 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA FETCHING ---
@st.cache_data(ttl=3600)
def fetch_live_intelligence():
    try:
        url = "https://news.google.com/rss/search?q=India+semiconductor+manufacturing&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(url)
        return feed.entries[:4]
    except:
        return []

@st.cache_data(ttl=86400)
def get_india_geojson():
    try:
        url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        response = requests.get(url, timeout=5)
        return response.json()
    except:
        return None

# --- 3. THE UNIFIED DATASET (India + Global) ---
data = [
    {"name": "TSMC Fab 18 (Taiwan)", "region": "Global", "cap": "Large", "lat": 23.10, "lon": 120.28, "terrain": "Island Coastal", "sti": 82.0},
    {"name": "TSMC Kumamoto (Japan)", "region": "Global", "cap": "Large", "lat": 32.88, "lon": 130.84, "terrain": "Volcanic Island", "sti": 80.5},
    {"name": "Intel Ocotillo (USA)", "region": "Global", "cap": "Large", "lat": 33.27, "lon": -111.88, "terrain": "Desert Flat", "sti": 95.0},
    {"name": "Intel Magdeburg (Germany)", "region": "Global", "cap": "Large", "lat": 52.12, "lon": 11.62, "terrain": "Continental Plain", "sti": 94.5},
    {"name": "Samsung Taylor (USA)", "region": "Global", "cap": "Large", "lat": 30.56, "lon": -97.40, "terrain": "Texas Plain", "sti": 92.0},
    {"name": "Samsung Pyeongtaek (Korea)", "region": "Global", "cap": "Large", "lat": 37.02, "lon": 127.04, "terrain": "Coastal Plain", "sti": 89.0},
    {"name": "Micron Boise (USA)", "region": "Global", "cap": "Large", "lat": 43.52, "lon": -116.15, "terrain": "High Desert", "sti": 88.0},
    {"name": "Rapidus Hokkaido (Japan)", "region": "Global", "cap": "Large", "lat": 42.76, "lon": 141.67, "terrain": "Northern Island", "sti": 81.0},
    {"name": "GlobalFoundries Dresden (Ger)", "region": "Global", "cap": "Mid", "lat": 51.12, "lon": 13.71, "terrain": "River Valley", "sti": 85.0},
    {"name": "SMIC Shanghai (China)", "region": "Global", "cap": "Large", "lat": 31.20, "lon": 121.59, "terrain": "Delta Plain", "sti": 91.0},
    # ---- ADDITIONAL GLOBAL/RUSSIAN NODES ----
    {
        "name": "Mikron Fab (Zelenograd)", "region": "Russia", "cap": "Mid", 
        "lat": 55.98, "lon": 37.21, "terrain": "Continental Plain", "sti": 75.0
    },
    {
        "name": "Angstrem-T (Zelenograd)", "region": "Russia", "cap": "Mid", 
        "lat": 55.99, "lon": 37.20, "terrain": "Continental Plain", "sti": 72.0
    },
    {
        "name": "NXP Semiconductors (Freising)", "region": "Global", "cap": "Mid", 
        "lat": 48.39, "lon": 11.73, "terrain": "Bavarian Alpine Foreland", "sti": 86.0
    },
    {
        "name": "STMicroelectronics (Crolles)", "region": "Global", "cap": "Large", 
        "lat": 45.28, "lon": 5.88, "terrain": "Alpine Valley", "sti": 84.0
    },
    {
        "name": "Infineon (Villach)", "region": "Global", "cap": "Mid", 
        "lat": 46.61, "lon": 13.84, "terrain": "Alpine Basin", "sti": 82.5
    },
    {
        "name": "Tower Semiconductor (Migdal HaEmek)", "region": "Global", "cap": "Mid", 
        "lat": 32.67, "lon": 35.24, "terrain": "Jezreel Valley", "sti": 78.0
    },
    {
        "name": "SilTerra (Migdal HaEmek)", "region": "Global", "cap": "Small", 
        "lat": 5.23, "lon": 100.56, "terrain": "Kulim Coastal Plain", "sti": 85.0
    },

    
    # ---- INDIAN ECOSYSTEM ----
    {
        "name": "Tata-PSMC Dholera", "region": "India", "year": 2026, "cap": "Large", 
        "lat": 22.25, "lon": 72.11, "elev": 15, "terrain": "Coastal Plateau",
        "w_name": "Sabarmati Desalination", "w_lat": 22.50, "w_lon": 72.30, "w_dist": 32,
        "m_name": "Gulf of Khambhat Port", "m_lat": 21.75, "m_lon": 72.25, "m_dist": 55,
        "l_name": "Ahmedabad Urban Center", "l_lat": 23.02, "l_lon": 72.57, "l_dist": 85,
        "bt": "India's First Commercial 28nm Mega-Fab.", 
        "imgs": [
            "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1563770660941-20978e870e26?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=800&q=80"
        ],
        "profile": [0, 8, 3, 14, 15, 15, 15, 15, 11, 4, 5], 
        "sti": 99.5, "lcp": 0.97,
        "rad": [99, 95, 98, 90, 85], 
        "rationale": "Engineered for 0.02% seismic vibration friction.",
        "snc": 78, "dsc": 85, "iso": 92
    },
    {
        "name": "Tata-TSAT Assam", "region": "India", "year": 2026, "cap": "Large", 
        "lat": 26.24, "lon": 92.33, "elev": 55, "terrain": "River Valley",
        "w_name": "Brahmaputra Basin", "w_lat": 26.50, "w_lon": 92.60, "w_dist": 40,
        "m_name": "Haldia Port Transit", "m_lat": 25.50, "m_lon": 91.00, "m_dist": 180,
        "l_name": "Guwahati Metropolis", "l_lat": 26.14, "l_lon": 91.73, "l_dist": 65,
        "bt": "Sovereign Advanced Packaging Hub.", 
        "imgs": [
            "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092580497-e0d23cbdf1dc?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1573164713988-8665fc963095?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092795360-fd1ca04f0952?auto=format&fit=crop&w=800&q=80"
        ],
        "profile": [120, 140, 85, 40, 55, 55, 55, 80, 130, 95, 110],
        "sti": 84.4, "lcp": 0.70,
        "rad": [75, 99, 65, 95, 80],
        "rationale": "High topographical friction offset by strategic geographic defense.",
        "snc": 65, "dsc": 70, "iso": 88
    },
    {
        "name": "Micron Sanand", "region": "India", "year": 2024, "cap": "Large", 
        "lat": 22.98, "lon": 72.37, "elev": 45, "terrain": "Industrial Plains",
        "w_name": "Narmada Canal System", "w_lat": 23.10, "w_lon": 72.50, "w_dist": 20,
        "m_name": "Mundra Port Transit", "m_lat": 22.80, "m_lon": 72.00, "m_dist": 250,
        "l_name": "Sanand Industrial GIDC", "l_lat": 22.95, "l_lon": 72.38, "l_dist": 5,
        "bt": "High Bandwidth Memory (HBM) ATMP validation.", 
        "imgs": [
            "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092335397-9583eb92d232?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092580497-e0d23cbdf1dc?auto=format&fit=crop&w=800&q=80"
        ],
        "profile": [10, 18, 12, 35, 45, 45, 45, 42, 48, 44, 48],
        "sti": 92.0, "lcp": 0.90,
        "rad": [90, 85, 88, 85, 98],
        "rationale": "Chosen for pre-existing grid stability and rapid scalability.",
        "snc": 92, "dsc": 40, "iso": 85
    },
    {
        "name": "CG Power-Renesas Sanand", "region": "India", "year": 2025, "cap": "Mid", 
        "lat": 23.00, "lon": 72.35, "elev": 43, "terrain": "Industrial Plains",
        "w_name": "Narmada Canal System", "w_lat": 23.10, "w_lon": 72.50, "w_dist": 22,
        "m_name": "Regional Rail Freight", "m_lat": 22.80, "m_lon": 72.20, "m_dist": 28,
        "l_name": "Ahmedabad Urban Grid", "l_lat": 23.02, "l_lon": 72.57, "l_dist": 25,
        "bt": "Specialized OSAT for consumer and industrial ICs.", 
        "imgs": [
            "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092335397-9583eb92d232?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092795360-fd1ca04f0952?auto=format&fit=crop&w=800&q=80"
        ],
        "profile": [20, 28, 22, 38, 43, 43, 43, 40, 48, 42, 46],
        "sti": 89.0, "lcp": 0.88,
        "rad": [90, 85, 92, 85, 95],
        "rationale": "Leverages localized high-density packaging clusters.",
        "snc": 75, "dsc": 60, "iso": 50
    },
    {
        "name": "Texas Instruments Bangalore", "region": "India", "year": 1985, "cap": "Large", 
        "lat": 12.97, "lon": 77.59, "elev": 920, "terrain": "Deccan Plateau",
        "w_name": "Cauvery Basin Municipal", "w_lat": 12.40, "w_lon": 77.30, "w_dist": 85,
        "m_name": "HAL Airport Data Transit", "m_lat": 12.95, "m_lon": 77.66, "m_dist": 12,
        "l_name": "Bangalore Urban Grid", "l_lat": 12.97, "l_lon": 77.59, "l_dist": 2,
        "bt": "First Global R&D Center in India.", 
        "imgs": [
            "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1573164713988-8665fc963095?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=800&q=80"
        ],
        "profile": [850, 890, 860, 910, 920, 920, 920, 890, 915, 870, 880],
        "sti": 88.0, "lcp": 0.85,
        "rad": [95, 75, 80, 90, 99],
        "rationale": "Elevation provided moderate climate for 1980s mainframes.",
        "snc": 95, "dsc": 10, "iso": 0
    },
    {
        "name": "SCL Mohali", "region": "India", "year": 1983, "cap": "Small", 
        "lat": 30.70, "lon": 76.69, "elev": 310, "terrain": "Shivalik Foothills",
        "w_name": "Sutlej River Tributaries", "w_lat": 30.90, "w_lon": 76.50, "w_dist": 28,
        "m_name": "Northern Rail Depot", "m_lat": 30.50, "m_lon": 76.80, "m_dist": 24,
        "l_name": "Chandigarh Sector 17", "l_lat": 30.73, "l_lon": 76.77, "l_dist": 10,
        "bt": "ISRO space-grade military 180nm CMOS nodes.", 
        "imgs": [
            "https://images.unsplash.com/photo-1581092335397-9583eb92d232?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092580497-e0d23cbdf1dc?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092795360-fd1ca04f0952?auto=format&fit=crop&w=800&q=80"
        ],
        "profile": [280, 270, 295, 285, 310, 310, 310, 340, 320, 370, 380],
        "sti": 75.0, "lcp": 0.65,
        "rad": [60, 85, 65, 99, 88],
        "rationale": "Defense-in-Depth location sacrificing maritime access.",
        "snc": 100, "dsc": 99, "iso": 100
    },
    {
        "name": "Hind Rectifiers Mumbai", "region": "India", "year": 1980, "cap": "Small", 
        "lat": 19.117, "lon": 72.848, "elev": 10, "terrain": "Western Coastal Plain",
        "w_name": "Ulhas River Catchment", "w_lat": 19.00, "w_lon": 72.80, "w_dist": 15,
        "m_name": "JNPT Port Transit", "m_lat": 18.95, "m_lon": 72.90, "m_dist": 60,
        "l_name": "Mumbai Metropolis", "l_lat": 19.07, "l_lon": 72.87, "l_dist": 5,
        "bt": "Power semiconductor devices for Indian Railways.", 
        "imgs": [
            "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092795360-fd1ca04f0952?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092335397-9583eb92d232?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&w=800&q=80"
        ],
        "profile": [2, 12, 5, 10, 10, 10, 10, 12, 9, 7, 8],
        "sti": 91.5, "lcp": 0.92,
        "rad": [65, 80, 98, 90, 99],
        "rationale": "Classic coastal export config sacrificing seismic neutrality.",
        "snc": 40, "dsc": 95, "iso": 30
    },
    {
        "name": "Qualcomm Hyderabad", "region": "India", "year": 2010, "cap": "Large", 
        "lat": 17.443, "lon": 78.375, "elev": 550, "terrain": "Deccan Plateau",
        "w_name": "Municipal Mains", "w_lat": 17.40, "w_lon": 78.35, "w_dist": 10,
        "m_name": "Hyderabad Airport Cargo", "m_lat": 17.25, "m_lon": 78.43, "m_dist": 35,
        "l_name": "HITEC City Hub", "l_lat": 17.44, "l_lon": 78.38, "l_dist": 5,
        "bt": "Snapdragon design and validation mega-center.", 
        "imgs": [
            "image_3ee2fa.jpg",
            "https://images.unsplash.com/photo-1497215842964-222b430dc094?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=800&q=80"
        ],
        "profile": [500, 520, 530, 550, 550, 550, 550, 530, 510, 500, 490],
        "sti": 94.0, "lcp": 0.94,
        "rad": [92, 85, 90, 88, 99],
        "rationale": "Chosen for pre-existing grid stability (500kV primary substation).",
        "snc": 99, "dsc": 15, "iso": 0
    },
    {
        "name": "Tessolve Bangalore", "region": "India", "year": 2005, "cap": "Mid", 
        "lat": 12.923, "lon": 77.682, "elev": 910, "terrain": "Deccan Plateau",
        "w_name": "Cauvery Basins pipelines", "w_lat": 12.45, "w_lon": 77.40, "w_dist": 75,
        "m_name": "HAL Airport Data Transit", "m_lat": 12.95, "m_lon": 77.66, "m_dist": 12,
        "l_name": "Electronics City Grid", "l_lat": 12.93, "l_lon": 77.69, "l_dist": 5,
        "bt": "Global validation and testing engineering hub.", 
        "imgs": [
            "https://images.unsplash.com/photo-1563770660941-20978e870e26?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092580497-e0d23cbdf1dc?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=800&q=80"
        ],
        "profile": [860, 880, 890, 910, 910, 910, 910, 890, 880, 870, 860],
        "sti": 89.0, "lcp": 0.88,
        "rad": [95, 80, 85, 92, 98],
        "rationale": "Standard high-plateau configuration maximizing labor access.",
        "snc": 85, "dsc": 50, "iso": 10
    },
    {
        "name": "Continental Device India Limited", "region": "India", "year": 1964, "cap": "Small", 
        "lat": 28.667, "lon": 77.217, "elev": 210, "terrain": "Indo-Gangetic Plains",
        "w_name": "Yamuna River Pipelines", "w_lat": 28.60, "w_lon": 77.20, "w_dist": 15,
        "m_name": "NCR Rail Corridor", "m_lat": 28.70, "m_lon": 77.25, "m_dist": 10,
        "l_name": "Delhi Urban Grid", "l_lat": 28.67, "l_lon": 77.22, "l_dist": 5,
        "bt": "India's first fabless design and discrete transistor manufacturing.", 
        "imgs": [
            "https://images.unsplash.com/photo-1581092335397-9583eb92d232?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&w=800&q=80"
        ],
        "profile": [190, 195, 200, 210, 210, 210, 210, 200, 198, 195, 190],
        "sti": 78.0, "lcp": 0.65,
        "rad": [65, 70, 88, 85, 99],
        "rationale": "Topographical variance is high due to river plain instability.",
        "snc": 30, "dsc": 90, "iso": 20
    }
]

df = pd.DataFrame(data)

def get_color_hex(cap):
    if cap == "Large": return "#d4af37" 
    if cap == "Mid": return "#b87333"   
    return "#708090"                    

df['hex_color'] = df['cap'].apply(get_color_hex)

# --- 4. THE TECHNICAL DOSSIER MODAL ---
@st.dialog("TECHNICAL DOSSIER", width="large")
def show_technical_dossier(facility_name):
    n = df[df['name'] == facility_name].iloc[0]
    
    st.markdown(f"<h2>{n['name']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<span class='tag-{n['cap'].lower()}'>{n['cap']} Cap Facility</span> | <span style='color:#aaa;'><b>State/Coords:</b> {n['lat']} N, {n['lon']} E</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1], gap="medium")
    
    with col1:
        # Cinematic Image Carousel (Horizontal Scroll Snap)
        if 'imgs' in n and isinstance(n['imgs'], list):
            carousel_html = f"""
            <style>
            .slider-container {{
                display: flex; overflow-x: auto; scroll-snap-type: x mandatory;
                gap: 10px; padding-bottom: 10px; margin-bottom: 15px;
            }}
            .slider-container::-webkit-scrollbar {{ height: 6px; }}
            .slider-container::-webkit-scrollbar-thumb {{ background: #d4af37; border-radius: 3px; }}
            .slider-img {{
                flex: 0 0 100%; scroll-snap-align: center; border-radius: 4px;
                object-fit: cover; height: 260px; border: 1px solid #333;
            }}
            </style>
            <div class="slider-container">
                {"".join([f'<img class="slider-img" src="{img_url}">' for img_url in n['imgs']])}
            </div>
            """
            st.markdown(carousel_html, unsafe_allow_html=True)
            
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Strategic Payload</div><div class='metric-text'>{n.get('bt', 'Classified / N/A')}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Topographical Stabilization (Elev: {n.get('elev', 'N/A')}m MSL)</div><div class='metric-text'>{n.get('rationale', 'No terrain data available.')}</div></div>", unsafe_allow_html=True)
        
        if 'lcp' in n:
            st.markdown(f"""
            <div class='metric-box'>
                <div class='metric-title'>Logistics Matrix (Least Cost Path: {n['lcp']})</div>
                <div class='metric-text'>
                    <span style='color:#d4af37;'>►</span> <b>Material Hub:</b> {n['m_name']} ({n['m_dist']}km)<br>
                    <span style='color:#d4af37;'>►</span> <b>Water Catchment:</b> {n['w_name']} ({n['w_dist']}km)<br>
                    <span style='color:#d4af37;'>►</span> <b>Urban Labor Center:</b> {n['l_name']} ({n['l_dist']}km)
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        if 'profile' in n:
            st.markdown("<b style='color:#d4af37;'>Topographical Elevation Profile</b>", unsafe_allow_html=True)
            
            total_dist = float(n['m_dist'] + n['w_dist'])
            x_dist = [float(x) for x in np.linspace(0, total_dist, len(n['profile']))]
            y_elev = [float(y) for y in n['profile']]
            
            chart_df = pd.DataFrame({"Distance": x_dist, "Elevation": y_elev})
            
            base = alt.Chart(chart_df).encode(
                x=alt.X('Distance:Q', title='Distance (km)', axis=alt.Axis(gridColor='#222', labelColor='#888', titleColor='#888')), 
                y=alt.Y('Elevation:Q', title='Elevation (MSL)', scale=alt.Scale(domain=[0, max(y_elev)+50]), axis=alt.Axis(gridColor='#222', labelColor='#888', titleColor='#888'))
            )
            area = base.mark_area(opacity=0.3, color="#d4af37")
            line = base.mark_line(color="#d4af37", strokeWidth=2)
            
            mark_df = pd.DataFrame({"x": [float(n['m_dist'])], "y": [float(n['elev'])]})
            point = alt.Chart(mark_df).mark_point(
                color='#ffffff', size=150, shape='diamond', filled=True, opacity=1.0
            ).encode(x='x:Q', y='y:Q')
            
            final_chart = alt.layer(area, line, point).properties(height=230).configure(background='#0a0a0a').configure_view(strokeWidth=0)
            st.altair_chart(final_chart, use_container_width=True, theme=None)

        if 'rad' in n:
            st.markdown("<b style='color:#d4af37;'>Vulnerability & Stability Radar</b>", unsafe_allow_html=True)
            categories = ['Seismic Stability', 'Water Security', 'Logistics Efficiency', 'Geopolitical Safety', 'Labor Proximity']
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=n['rad'], theta=categories, fill='toself', fillcolor='rgba(212, 175, 55, 0.3)', line=dict(color='#d4af37'), name=n['name']))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor='#333', linecolor='#333', tickfont=dict(color='#888')),
                    angularaxis=dict(tickfont=dict(color='#ccc', size=12, family='Rajdhani'), gridcolor='#333', linecolor='#333')
                ),
                showlegend=False, margin=dict(l=40, r=40, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=230
            )
            st.plotly_chart(fig, use_container_width=True)

        # F1-Style Mini Metrics for Capability
        if 'snc' in n:
            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; margin-top: 5px; gap: 8px;'>
                <div title="Strategic Node Capability: The facility's capacity to produce advanced, sovereign, defense-grade silicon." style='text-align: center; background: #111; padding: 12px 5px; border-top: 2px solid #d4af37; flex: 1; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); cursor: help;'>
                    <div style='color: #888; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px;'>Strat. Node Cap.</div>
                    <div style='color: #fff; font-size: 22px; font-weight: 700; font-family: Rajdhani;'>{n['snc']}%</div>
                </div>
                <div title="Domestic Supply Contribution: The percentage of the facility's output dedicated to sustaining the internal Indian market." style='text-align: center; background: #111; padding: 12px 5px; border-top: 2px solid #b87333; flex: 1; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); cursor: help;'>
                    <div style='color: #888; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px;'>Dom. Supply</div>
                    <div style='color: #fff; font-size: 22px; font-weight: 700; font-family: Rajdhani;'>{n['dsc']}%</div>
                </div>
                <div title="Import Substitution: The estimated percentage by which this facility reduces India's reliance on foreign semiconductor imports." style='text-align: center; background: #111; padding: 12px 5px; border-top: 2px solid #708090; flex: 1; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); cursor: help;'>
                    <div style='color: #888; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px;'>Import Sub.</div>
                    <div style='color: #fff; font-size: 22px; font-weight: 700; font-family: Rajdhani;'>{n['iso']}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# --- 5. TOP BAR UI ---
st.markdown("""
    <div class='hero-banner'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div class='hero-title'>Strategic Topography GIS</div>
            <div class='uplink-badge'>
                <span class='pulse-dot'></span> SECURE UPLINK
            </div>
        </div>
        <p class='hero-subtitle'>Macro-Analysis of Semiconductor Infrastructure, Topographical Friction, and Strategic Routing.</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["INDIA TIMELINE ECOSYSTEM", "GLOBAL MACRO ECOSYSTEM", "S.T.I. STATISTICAL DISTRIBUTION"])

# --- TAB 1: INDIA ECOSYSTEM ---
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    
    selected_year = st.select_slider("Historical Timeline:", options=[1980, 1990, 2000, 2010, 2020, 2026], value=2026)
    active_df = df[(df['region'] == 'India') & (df['year'] <= selected_year)].copy()
    
    avg_sti = f"{active_df['sti'].mean():.1f}%" if not active_df.empty else "N/A"
    avg_lcp = f"{active_df['lcp'].mean():.2f}" if not active_df.empty else "N/A"
    
    st.markdown(f"""
    <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 15px; margin-bottom: 30px;'>
        <div class='hud-card'><div class='hud-label'> Active Sovereign Nodes</div><div class='hud-value'>{len(active_df)}</div></div>
        <div class='hud-card'><div class='hud-label'> Mean Topographical Index</div><div class='hud-value'>{avg_sti}</div></div>
        <div class='hud-card'><div class='hud-label'> Logistics Efficiency (LCP)</div><div class='hud-value'>{avg_lcp}</div></div>
    </div>
    """, unsafe_allow_html=True)
    
    col_map, col_feed = st.columns([6, 4], gap="large")

    # --- REPLACE INSIDE TAB 1 (TACTICAL MAP) ---
    with col_map:
        st.markdown("<h3 style='font-size:18px; color:#d4af37; font-family:Rajdhani;'>TACTICAL MAP (CLICK PIN FOR DOSSIER)</h3>", unsafe_allow_html=True)
        
        # Initialize high-res CartoDB Dark Matter map (zoom disabled as requested)
        m = folium.Map(location=[22.0, 79.0], zoom_start=4.4, tiles="CartoDB dark_matter", zoom_control=False, scrollWheelZoom=False)

        for cap, color in [("Large", "#d4af37"), ("Mid", "#b87333"), ("Small", "#708090")]:
            subset = active_df[active_df['cap'] == cap]
            if subset.empty: continue
            
            for _, row in subset.iterrows():
                # Pure CSS Heartbeat Animation injected into the map marker
                pulse_html = f"""
                <div style="
                    width: 14px; height: 14px; 
                    background-color: {color};
                    border-radius: 50%; 
                    border: 2px solid #fff;
                    box-shadow: 0 0 10px {color};
                    animation: map-ping 1.5s infinite ease-in-out alternate;
                "></div>
                <style>
                    @keyframes map-ping {{
                        0% {{ transform: scale(0.8); opacity: 0.8; box-shadow: 0 0 5px {color}; }}
                        100% {{ transform: scale(1.6); opacity: 1; box-shadow: 0 0 25px {color}; }}
                    }}
                </style>
                """
                
                folium.Marker(
                    location=[row['lat'], row['lon']],
                    tooltip=row['name'], # Tooltip acts as our clickable ID
                    icon=folium.DivIcon(html=pulse_html, icon_size=(14, 14), icon_anchor=(7, 7))
                ).add_to(m)

        # Render the map and capture the tooltip of the clicked node
        map_data = st_folium(m, width=650, height=500, returned_objects=["last_object_clicked_tooltip"])
        
        # Trigger the Dossier Dialog on click
        if map_data and map_data.get("last_object_clicked_tooltip"):
            clicked_name = map_data["last_object_clicked_tooltip"]
            show_technical_dossier(clicked_name)

    # --- LIVE STRATEGIC INTELLIGENCE FEED ---
    with col_feed:
        st.markdown("<h3 style='font-size:18px;'>📡 LIVE STRAT-INTEL FEED</h3>", unsafe_allow_html=True)
        st.markdown("<span style='font-size: 13px; color: #888;'>Live geopolitical and market intersections.</span><br><br>", unsafe_allow_html=True)

        bg_images = [
            "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1590247813693-5541d1c609fd?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=600&q=80"
        ]

        live_news = fetch_live_intelligence()
        
        # Fix: Flush-left HTML generation prevents Streamlit from parsing as a code block.
        html_output = """<style>
.news-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; padding-bottom: 15px; }
.news-card-grid { width: 100%; height: 210px; border-radius: 4px; background-size: cover; background-position: center; position: relative; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); border: 1px solid #333; transition: transform 0.3s ease, box-shadow 0.3s ease, border 0.3s ease; }
.news-card-grid:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(212, 175, 55, 0.2); border: 1px solid #d4af37; }
.card-overlay { position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(to top, rgba(10,10,10,0.95) 0%, rgba(10,10,10,0.8) 50%, rgba(10,10,10,0) 100%); padding: 15px; }
.card-tag { font-size: 10px; color: #0a0a0a; text-transform: uppercase; font-weight: 800; padding: 3px 6px; border-radius: 2px; display: inline-block; margin-bottom: 6px; letter-spacing: 0.5px; }
.card-title-grid { color: #ffffff !important; font-size: 14px; font-weight: 600; line-height: 1.3; font-family: 'Inter', sans-serif; text-shadow: 1px 1px 4px rgba(0,0,0,0.9); }
.card-date { color: #888; font-size: 10px; margin-top: 5px; font-family: 'Rajdhani', sans-serif; }
a { text-decoration: none; }
</style>
<div class="news-grid">"""

        if not live_news:
             html_output += "<div>Live visual feed currently offline.</div>"
        else:
            colors = ["#d4af37", "#b87333", "#708090", "#888"] 
            labels = ["LATEST DISPATCH", "INDUSTRY UPDATE", "MACRO TREND", "POLICY SHIFT"]
            
            for i, article in enumerate(live_news[:4]):
                clean_title = getattr(article, 'title', 'Encrypted Transmission Intercepted').rsplit(" - ", 1)[0]
                raw_date = getattr(article, 'published', datetime.datetime.now().strftime("%a, %d %b %Y"))
                clean_date = raw_date[:16] if len(raw_date) > 16 else raw_date
                
                img = bg_images[i % len(bg_images)]
                color = colors[i % len(colors)]
                tag = labels[i % len(labels)]
                link = getattr(article, 'link', '#')
                
                html_output += f"""
<a href='{link}' target='_blank'>
<div class="news-card-grid" style="background-image: url('{img}');">
<div class="card-overlay">
<div class="card-tag" style="background-color: {color};">{tag}</div>
<div class="card-title-grid">{clean_title}</div>
<div class="card-date">{clean_date}</div>
</div></div></a>"""

        html_output += "</div>"
        st.markdown(html_output, unsafe_allow_html=True)


# --- REPLACE TAB 2 (GLOBAL MACRO MAP) ---
# --- TAB 2: GLOBAL ECOSYSTEM ---
with tab2:
    st.markdown("<h3 style='font-size:18px; color:#d4af37; font-family:Rajdhani;'>GLOBAL MACRO MAP</h3>", unsafe_allow_html=True)
    global_df = df.copy()
    
    # Initialize high-res global map
    m_global = folium.Map(location=[30.0, 20.0], zoom_start=2, tiles="CartoDB dark_matter", zoom_control=False, scrollWheelZoom=False)

    for cap, color in [("Large", "#d4af37"), ("Mid", "#b87333"), ("Small", "#708090")]:
        subset = global_df[global_df['cap'] == cap]
        if subset.empty: continue
        
        for _, row in subset.iterrows():
            pulse_html = f"""
            <div style="
                width: 10px; height: 10px; 
                background-color: {color};
                border-radius: 50%; 
                border: 1px solid #fff;
                animation: map-ping-global 2s infinite ease-in-out alternate;
            "></div>
            <style>
                @keyframes map-ping-global {{
                    0% {{ transform: scale(0.8); opacity: 0.6; box-shadow: 0 0 2px {color}; }}
                    100% {{ transform: scale(1.4); opacity: 1; box-shadow: 0 0 15px {color}; }}
                }}
            </style>
            """
            
            folium.Marker(
                location=[row['lat'], row['lon']],
                tooltip=f"<b>{row['name']}</b><br>Region: {row['region']}<br>Cap: {row['cap']}",
                icon=folium.DivIcon(html=pulse_html, icon_size=(10, 10), icon_anchor=(5, 5))
            ).add_to(m_global)

    st_folium(m_global, width=1200, height=600, returned_objects=[])

# --- TAB 3: S.T.I. STATISTICAL DISTRIBUTION & INFERENCE ---
with tab3:
    st.markdown("### Continuous Probability Density & Inferential Statistics")
    st.markdown("This module applies Kernel Density Estimation (KDE) and rigorous hypothesis testing to the Strategic Topographical Index (STI). By modeling the variance and mean across facility classifications, we can mathematically infer India's sovereign site-selection strategy.")
    
    # Fix: Safely cast to numeric to prevent Altair density crashes
    stats_df = df[(df['region'] == 'India')].dropna(subset=['sti', 'cap']).copy()
    stats_df['sti'] = pd.to_numeric(stats_df['sti'], errors='coerce')
    stats_df = stats_df.dropna(subset=['sti'])
    
    density_plot = alt.Chart(stats_df).transform_density(
        'sti', as_=['sti', 'density'], groupby=['cap'], extent=[60, 110], steps=200, bandwidth=4 
    ).mark_area(opacity=0.45).encode(
        x=alt.X('sti:Q', title="Strategic Topographical Index (STI %)", scale=alt.Scale(domain=[65, 105])),
        y=alt.Y('density:Q', title="Probability Density", axis=alt.Axis(labels=False, ticks=False)),
        color=alt.Color('cap:N', scale=alt.Scale(domain=['Large', 'Mid', 'Small'], range=['#d4af37', '#b87333', '#708090']))
    ).properties(height=350)
    
    st.altair_chart(density_plot, use_container_width=True, theme="streamlit")

    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
    col_stats1, col_stats2 = st.columns(2, gap="large")
    
    with col_stats1:
        st.markdown("#### || MLE-Based Distribution Parameters")
        summary = stats_df.groupby('cap')['sti'].agg(Mean='mean', Variance='var', Std_Dev='std', Count='count').round(2)
        summary['Skewness'] = stats_df.groupby('cap')['sti'].apply(stats.skew).round(3)
        st.dataframe(summary, use_container_width=True)

        st.markdown("#### || ANOVA Test (Mean STI Differences)")
        group_values = [group['sti'].astype(float).values for name, group in stats_df.groupby('cap') if len(group) > 0]
        if len(group_values) > 1:
            anova_stat, anova_p = stats.f_oneway(*group_values)
            st.write(f"**F-statistic:** `{anova_stat:.4f}` | **p-value:** `{anova_p:.4f}`")
            if pd.notna(anova_p) and anova_p < 0.05:
                st.success("Reject Null Hypothesis → Mean STI differs significantly across Cap categories.")
            else:
                st.info("Fail to reject Null Hypothesis → Sample size too small or means are similar.")
        
        st.markdown("#### || Levene’s Test (Variance Equality)")
        if len(group_values) > 1:
            levene_stat, levene_p = stats.levene(*group_values)
            st.write(f"**Statistic:** `{levene_stat:.4f}` | **p-value:** `{levene_p:.4f}`")
            if pd.notna(levene_p) and levene_p < 0.05:
                st.success("Reject Null Hypothesis → Topographical variances are significantly different.")
            else:
                st.info("Fail to reject Null Hypothesis → Variances are statistically similar.")

    with col_stats2:
        st.markdown("#### || Chi-Square Test (Categorical Dependency)")
        bins = [0, 82, 93, 110] 
        labels = ['High Friction (<82)', 'Moderate (82-93)', 'Optimal (>93)']
        stats_df['sti_bin'] = pd.cut(stats_df['sti'], bins=bins, labels=labels)
        
        # Streamlit safe crosstab rendering
        contingency_table = pd.crosstab(stats_df['cap'], stats_df['sti_bin'])
        st.write("Contingency Table (Count):")
        st.dataframe(contingency_table, use_container_width=True)
        
        chi2_stat, chi2_p, dof, expected = stats.chi2_contingency(contingency_table)
        st.write(f"**Chi2:** `{chi2_stat:.4f}` | **p-value:** `{chi2_p:.4f}`")
        if pd.notna(chi2_p) and chi2_p < 0.05:
            st.success("Reject Null Hypothesis → STI risk category strictly depends on facility Cap type.")
        else:
            st.info("Fail to reject Null Hypothesis → Dependency not strictly proven at current sample size.")

        st.markdown("#### || KDE Distribution Overlap")
        x_grid = np.linspace(60, 110, 500).reshape(-1, 1)
        densities = {}
        for cap, group in stats_df.groupby('cap'):
            if len(group) > 0:
                kde = KernelDensity(kernel='gaussian', bandwidth=4.0)
                kde.fit(group['sti'].astype(float).values.reshape(-1, 1))
                densities[cap] = np.exp(kde.score_samples(x_grid))

        overlap_results = []
        for cap1, cap2 in combinations(densities.keys(), 2):
            overlap = np.trapezoid(np.minimum(densities[cap1], densities[cap2]), x_grid.flatten())
            overlap_results.append({"Comparison": f"{cap1} vs {cap2}", "Overlap Coefficient": round(overlap, 4)})
        
        if overlap_results:
            st.dataframe(pd.DataFrame(overlap_results), use_container_width=True, hide_index=True)

    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
    st.markdown("### || Strategic Recommendations")
    st.markdown("""
    1. **Strict Stratification of STI Requirements:** The low KDE overlap coefficient between Large and Small Cap facilities proves a bifurcated strategy. Future Mega-Fabs (Large Cap) must strictly target topographies with an STI $> 92\%$ (Coastal Plateaus).
    2. **Leveraging Variance for Geographical Hedging:** The higher variance and left-skewed tails in Small/Mid Cap facilities indicate they can survive in high-friction terrain, establishing a distributed *Defense-in-Depth* network.
    3. **Resource Catchment Thresholds:** The Chi-Square contingency highlights that high-friction topographies cannot support commercial logic nodes. Planning must mandate that sites with an STI $< 82\%$ be restricted to specialized, low-volume fabrication (e.g., Silicon Carbide).
    """)


# --- ADD THIS TO THE VERY BOTTOM OF TAB 3 ---
    st.markdown("<hr style='border-color: #333; margin-top: 40px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#d4af37; font-family:Rajdhani;'>DIGITAL HUMANITIES PERSPECTIVE</h3>", unsafe_allow_html=True)
    
    # Import the components library to allow full HTML/JS interactivity
    import streamlit.components.v1 as components
    
    dh_chip_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&family=Inter:wght@300;400;600&family=Share+Tech+Mono&display=swap');

    body {
        margin: 0; padding: 10px;
        background-color: #0a0a0a;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
        display: flex; gap: 40px;
    }
    
    /* LEFT: The Physical Chip Interface */
    .chip-container {
        flex: 0.7;
        display: flex; align-items: center; justify-content: center;
    }
    .motherboard {
        width: 240px; height: 240px;
        background: radial-gradient(circle, #1a1a1a 0%, #0a0a0a 100%);
        border: 1px solid #222; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        box-shadow: inset 0 0 40px rgba(0,0,0,0.8);
        position: relative;
    }
    /* Gold Circuit Traces */
    .trace { position: absolute; background: #333; z-index: 1; transition: background 0.3s, box-shadow 0.3s; }
    .trace.active { background: #d4af37; box-shadow: 0 0 10px #d4af37; }
    .t1 { width: 2px; height: 60px; top: 0; left: 50%; transform: translateX(-50%); }
    .t2 { width: 60px; height: 2px; right: 0; top: 50%; transform: translateY(-50%); }
    .t3 { width: 2px; height: 60px; bottom: 0; left: 50%; transform: translateX(-50%); }

    /* The Main Processor */
    .chip {
        width: 140px; height: 140px;
        background: #0f0f0f;
        border: 2px solid #444; border-radius: 8px;
        position: relative; z-index: 2;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.9);
    }
    .chip-core {
        width: 80px; height: 80px;
        background: linear-gradient(135deg, #111, #000);
        border: 2px solid #d4af37; color: #d4af37;
        font-family: 'Orbitron', sans-serif; font-size: 13px; font-weight: 700;
        text-align: center; letter-spacing: 1px;
        display: flex; align-items: center; justify-content: center;
        box-shadow: inset 0 0 15px rgba(212,175,55,0.1), 0 0 15px rgba(212,175,55,0.2);
    }
    /* Processing Nodes */
    .node {
        position: absolute; width: 12px; height: 12px;
        background: #444; border-radius: 50%; border: 2px solid #222;
        transition: all 0.3s;
    }
    .node.active { background: #d4af37; box-shadow: 0 0 15px #d4af37, 0 0 5px #fff; border-color: #fff; }
    #node1 { top: -7px; left: 50%; transform: translateX(-50%); }
    #node2 { right: -7px; top: 50%; transform: translateY(-50%); }
    #node3 { bottom: -7px; left: 50%; transform: translateX(-50%); }

    /* RIGHT: The Digital Readout & Controls */
    .interface-container {
        flex: 1.5; display: flex; flex-direction: column;
    }
    .controls { display: flex; gap: 10px; margin-bottom: 20px; }
    
    .sector-btn {
        flex: 1; background: #111; border: 1px solid #333; color: #888;
        padding: 12px 10px; font-family: 'Rajdhani', sans-serif; font-size: 14px; font-weight: 600;
        text-transform: uppercase; cursor: pointer; transition: all 0.3s;
        border-radius: 4px; border-bottom: 3px solid #333;
    }
    .sector-btn:hover { background: #1a1a1a; color: #b87333; border-bottom-color: #b87333; }
    .sector-btn.active { 
        background: rgba(212,175,55,0.1); color: #d4af37; border-color: #d4af37; 
        border-bottom: 3px solid #d4af37; box-shadow: 0 5px 15px rgba(212,175,55,0.1); 
    }
    
    /* Decrypted Data Terminal */
    .readout-panel {
        flex: 1; background: #111; border: 1px solid #333; border-left: 4px solid #d4af37;
        padding: 25px; border-radius: 4px; box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
    }
    .readout-title {
        color: #d4af37; font-family: 'Share Tech Mono', monospace; font-size: 18px;
        border-bottom: 1px dashed #444; padding-bottom: 10px; margin-bottom: 15px; margin-top: 0;
    }
    .readout-body {
        color: #a0aec0; font-family: 'Share Tech Mono', monospace; font-size: 14px; line-height: 1.6;
    }
    .cursor { 
        display: inline-block; width: 8px; height: 15px; background: #d4af37; 
        animation: blink 1s infinite; vertical-align: middle; margin-left: 4px; 
    }
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
    </style>
    </head>
    <body>

    <!-- VISUAL CHIP -->
    <div class="chip-container">
        <div class="motherboard">
            <div class="trace t1" id="trace1"></div>
            <div class="trace t2" id="trace2"></div>
            <div class="trace t3" id="trace3"></div>
            <div class="chip">
                <div class="node" id="node1"></div>
                <div class="node" id="node2"></div>
                <div class="node" id="node3"></div>
                <div class="chip-core">DH<br>CORE<br>v1.0</div>
            </div>
        </div>
    </div>

    <!-- DATA INTERFACE -->
    <div class="interface-container">
        <div class="controls">
            <button class="sector-btn" id="btn1" onclick="loadSector(1)">Sector 01: Motive</button>
            <button class="sector-btn" id="btn2" onclick="loadSector(2)">Sector 02: Power</button>
            <button class="sector-btn" id="btn3" onclick="loadSector(3)">Sector 03: Destiny</button>
        </div>
        <div class="readout-panel">
            <h4 class="readout-title" id="readout-title">AWAITING SECTOR UPLINK...</h4>
            <div class="readout-body">
                <span id="readout-text">Select a memory sector above to decrypt DH-CORE-v1 payload.</span><span class="cursor"></span>
            </div>
        </div>
    </div>

    <script>
    // The Digital Humanities text mapped to the chip sectors
    const data = {
        1: { 
            title: "SECTOR 01 // ARCHITECTURE OF PARANOIA", 
            text: "The spatial clustering reveals human motive. Mega-Fabs on flat coastal plains (High STI) signify absolute economic efficiency—demanding topographical perfection for zero failure rates.\\n\\nConversely, the scattered Small/Mid Cap nodes in high-friction valleys represent pure survival mechanics. By burying defense foundries inland, the state consciously sacrifices profit to forge geographic immunity against naval blockades and climate disasters." 
        },
        2: { 
            title: "SECTOR 02 // SPATIALIZATION OF POWER", 
            text: "Semiconductors do not just process data; they rewrite the earth.\\n\\nThese Mega-Fabs function as gravitational anomalies. They literally reroute rivers via desalination pipelines and trigger mass intellectual migration, erecting hyper-localized 'techno-enclaves' that permanently rewrite indigenous cultural economies." 
        },
        3: { 
            title: "SECTOR 03 // INFRASTRUCTURE AS DESTINY", 
            text: "To the civilian, a microchip is invisible. This GIS framework proves the 'Cyber Frontline' is deeply terrestrial.\\n\\nEvery shifting STI variance maps billions poured into concrete and water routing. In the 21st century, geographical infrastructure is destiny." 
        }
    };

    let typingTimer;

    function loadSector(id) {
        // Reset all styles
        for(let i=1; i<=3; i++) {
            document.getElementById('btn'+i).classList.remove('active');
            document.getElementById('node'+i).classList.remove('active');
            document.getElementById('trace'+i).classList.remove('active');
        }
        
        // Illuminate selected sector, trace, and node
        document.getElementById('btn'+id).classList.add('active');
        document.getElementById('node'+id).classList.add('active');
        document.getElementById('trace'+id).classList.add('active');

        // Typewriter Effect Logic
        document.getElementById('readout-title').innerHTML = data[id].title;
        const textContainer = document.getElementById('readout-text');
        textContainer.innerHTML = "";
        
        clearInterval(typingTimer);
        let txt = data[id].text;
        let i = 0;
        
        typingTimer = setInterval(() => {
            if(i < txt.length) {
                // Handle newlines formatting for HTML
                if(txt.charAt(i) === '\\n') {
                    textContainer.innerHTML += "<br>";
                } else {
                    textContainer.innerHTML += txt.charAt(i);
                }
                i++;
            } else {
                clearInterval(typingTimer);
            }
        }, 15); // Adjust typing speed here
    }
    </script>
    </body>
    </html>
    """
    
    # Render the interactive HTML component inside Streamlit
    components.html(dh_chip_html, height=350)
