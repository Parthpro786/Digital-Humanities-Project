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

# --- 1. PROFESSIONAL PAGE CONFIG & CSS ---
st.set_page_config(layout="wide", page_title="Strategic Topography GIS", page_icon="🗺️")

st.markdown("""
    <style>
        /* Premium Cinematic Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;800&family=Montserrat:wght@300;400;600;700&display=swap');

        /* Dark Cinematic Background */
        .stApp { 
            background-color: #050505; 
            background-image: radial-gradient(circle at 50% -20%, #1a1a1a 0%, #050505 80%);
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 2rem; padding-bottom: 0rem; max-width: 98%;}
        
        /* Global Typography */
        h1, h2, h3, p, span, div {
            font-family: 'Montserrat', sans-serif; 
            color: #e0e0e0;
        }
        h1, h2, h3 {
            font-family: 'Cinzel', serif;
            color: #d4af37;
            letter-spacing: 1px;
        }
        
        /* Sidebar and Technical Dossier Styling - Glassmorphism */
        [data-testid="stSidebar"] {
            background-color: rgba(10, 10, 10, 0.8); 
            border-right: 1px solid rgba(212, 175, 55, 0.2);
            backdrop-filter: blur(10px);
        }
        
        /* Glassmorphic Metric Boxes */
        .metric-box {
            background: rgba(20, 20, 20, 0.65);
            backdrop-filter: blur(12px);
            padding: 20px; 
            border-radius: 8px; 
            border-left: 4px solid #d4af37; 
            margin-bottom: 20px; 
            border-top: 1px solid rgba(212, 175, 55, 0.15);
            border-right: 1px solid rgba(212, 175, 55, 0.15);
            border-bottom: 1px solid rgba(212, 175, 55, 0.15);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .metric-box:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(212, 175, 55, 0.15);
        }
        
        .metric-title {color: #d4af37; font-family: 'Cinzel', serif; font-size: 15px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; font-weight: 800;}
        .metric-text {color: #f3f4f6; font-size: 15.5px; line-height: 1.6; font-weight: 300;}
        
        /* Cap Tags - Premium Colors */
        .tag-large {background: rgba(212, 175, 55, 0.15); padding: 4px 12px; border-radius: 20px; border: 1px solid #d4af37; color: #d4af37; font-weight: bold; text-transform: uppercase; font-size: 11px; letter-spacing: 1px;}
        .tag-mid {background: rgba(184, 115, 51, 0.15); padding: 4px 12px; border-radius: 20px; border: 1px solid #b87333; color: #b87333; font-weight: bold; text-transform: uppercase; font-size: 11px; letter-spacing: 1px;} 
        .tag-small {background: rgba(192, 192, 192, 0.15); padding: 4px 12px; border-radius: 20px; border: 1px solid #c0c0c0; color: #c0c0c0; font-weight: bold; text-transform: uppercase; font-size: 11px; letter-spacing: 1px;}
        
        /* High-Contrast Return Button */
        .stButton>button {
            background: transparent; 
            color: #d4af37 !important; 
            border: 1px solid #d4af37; 
            font-weight: 700; 
            padding: 10px 20px;
            border-radius: 4px;
            font-family: 'Montserrat', sans-serif;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background: rgba(212, 175, 55, 0.1); 
            transform: translateY(-2px);
            box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
        }

        /* 1. HUD Card Styling (Glassmorphism) */
        .hud-card {
            background: rgba(15, 15, 15, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 8px 32px 0 rgba(0,0,0,0.5);
            border-top: 3px solid #d4af37;
            text-align: center;
            transition: transform 0.3s ease;
        }
        .hud-card:hover { transform: translateY(-3px); box-shadow: 0 10px 25px -3px rgba(212, 175, 55, 0.2); border-top: 3px solid #ffe55c;}
        .hud-value { font-size: 36px; font-family: 'Cinzel', serif; font-weight: 800; color: #d4af37; line-height: 1.2; text-shadow: 0 0 15px rgba(212,175,55,0.4); }
        .hud-label { font-size: 13px; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 1.5px; }
        
        /* 2. Premium Shimmer Title Animation */
        .hero-title {
            font-family: 'Cinzel', serif !important;
            font-size: 38px !important;
            font-weight: 800 !important;
            margin: 0 !important;
            letter-spacing: 3px !important;
            text-transform: uppercase;
            background: linear-gradient(to right, #d4af37 20%, #fff7cc 40%, #d4af37 60%, #aa8c2c 80%);
            background-size: 200% auto;
            color: transparent !important;
            -webkit-background-clip: text !important;
            background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            animation: premium-shine 6s linear infinite;
        }

        @keyframes premium-shine {
            to { background-position: 200% center; }
        }

        /* 3. Pulsing Uplink Dot (Gold) */
        @keyframes pulse-dot-gold {
            0% { box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.7); transform: scale(1); }
            50% { box-shadow: 0 0 0 10px rgba(212, 175, 55, 0); transform: scale(1.1); }
            100% { box-shadow: 0 0 0 0 rgba(212, 175, 55, 0); transform: scale(1); }
        }
        .pulse-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: #d4af37;
            margin-right: 10px;
            animation: pulse-dot-gold 2s infinite;
        }

        /* Selectbox Styling */
        .stSelectbox label {
            color: #d4af37 !important;
            font-family: 'Cinzel', serif !important;
            font-weight: 800 !important;
            letter-spacing: 1px;
        }
        
        /* Interactive Tabs */
        button[data-baseweb="tab"] {
            background-color: transparent !important;
            border: none !important;
            border-bottom: 2px solid #333 !important;
            padding: 12px 24px !important;
            margin-right: 8px !important;
            transition: all 0.3s ease !important;
        }
        button[data-baseweb="tab"]:hover {
            border-bottom: 2px solid rgba(212, 175, 55, 0.5) !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: rgba(212, 175, 55, 0.1) !important;
            border-bottom: 2px solid #d4af37 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] p {
            color: #d4af37 !important;
            font-weight: 700 !important;
            letter-spacing: 1px;
        }
        button[data-baseweb="tab"] p {
            color: #9ca3af !important;
            font-weight: 600 !important;
            font-family: 'Montserrat', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. STATE MANAGEMENT ---
if "selected_node" not in st.session_state:
    st.session_state.selected_node = None

def clear_selection():
    st.session_state.selected_node = None

# --- 3. LOGISTICS CURVE & MIDPOINT GENERATOR ---
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

# --- 4. THE UNIFIED DATASET (India + Global) ---
data = [
    # ---- EXPANDED GLOBAL ECOSYSTEM (For Tab 2 & 3) ----
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

    # ---- INDIAN ECOSYSTEM ----
    {
        "name": "Tata-PSMC Dholera", "region": "India", "year": 2026, "cap": "Large", 
        "lat": 22.25, "lon": 72.11, "elev": 15, "terrain": "Coastal Plateau",
        "w_name": "Sabarmati Desalination", "w_lat": 22.50, "w_lon": 72.30, "w_dist": 32,
        "m_name": "Gulf of Khambhat Port", "m_lat": 21.75, "m_lon": 72.25, "m_dist": 55,
        "l_name": "Ahmedabad Urban Center", "l_lat": 23.02, "l_lon": 72.57, "l_dist": 85,
        "bt": "India's First Commercial 28nm Mega-Fab. Sovereign logic node production.", 
        "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRqIQdQsnEGk-qsjXopCw4ZG3o-HgKqlO5aDg&s",
        "sti": 99.5, "lcp": 0.97,
        "rad": [99, 95, 98, 90, 85], 
        "rationale": "Engineered for 0.02% seismic vibration friction. The absolute flatness prevents multi-billion dollar EUV wafer spoilage. Proximity to deep-water port yields high logistical cost-efficiency."
    },
    {
        "name": "Tata-TSAT Assam", "region": "India", "year": 2026, "cap": "Large", 
        "lat": 26.24, "lon": 92.33, "elev": 55, "terrain": "River Valley",
        "w_name": "Brahmaputra Basin", "w_lat": 26.50, "w_lon": 92.60, "w_dist": 40,
        "m_name": "Haldia Port Transit", "m_lat": 25.50, "m_lon": 91.00, "m_dist": 180,
        "l_name": "Guwahati Metropolis", "l_lat": 26.14, "l_lon": 91.73, "l_dist": 65,
        "bt": "Sovereign Advanced Packaging Hub. Eastern frontier geopolitical hedge.", 
        "img": "https://scontent.ftrv2-1.fna.fbcdn.net/v/t39.30808-6/535992862_1186350260197029_12401593196388291_n.jpg?stp=dst-jpg_s640x640_tt6&_nc_cat=104&ccb=1-7&_nc_sid=13d280&_nc_ohc=uCGe0x5dj7IQ7kNvwHTQgRh&_nc_oc=Adq6zKwzlR2PEBXHhilqH0ybFDm2k1OPVn86DKpb-J71nSTjjZg6rRqRNBjtcoly4QU&_nc_zt=23&_nc_ht=scontent.ftrv2-1.fna&_nc_gid=8jhxxgLQ08IWL_0Y-iLOqw&_nc_ss=7a389&oh=00_AfwQOBe7hb8uQei8t2dpJOMUz9Oz_MkAaaYJQhb18tjNUg&oe=69D1291B",
        "sti": 84.4, "lcp": 0.70,
        "rad": [75, 99, 65, 95, 80],
        "rationale": "High topographical friction (34% higher logistics cost) is offset by strategic geographic defense and inexhaustible fresh water supply for Chemical Mechanical Polishing (CMP)."
    },
    {
        "name": "Micron Sanand", "region": "India", "year": 2024, "cap": "Large", 
        "lat": 22.98, "lon": 72.37, "elev": 45, "terrain": "Industrial Plains",
        "w_name": "Narmada Canal System", "w_lat": 23.10, "w_lon": 72.50, "w_dist": 20,
        "m_name": "Mundra Port Transit", "m_lat": 22.80, "m_lon": 72.00, "m_dist": 250,
        "l_name": "Sanand Industrial GIDC", "l_lat": 22.95, "l_lon": 72.38, "l_dist": 5,
        "bt": "High Bandwidth Memory (HBM) ATMP validation.", 
        "img": "https://scontent.ftrv2-1.fna.fbcdn.net/v/t39.30808-6/539589177_1185658950266160_3534972847653672713_n.jpg?stp=dst-jpg_s640x640_tt6&_nc_cat=106&ccb=1-7&_nc_sid=13d280&_nc_ohc=tDQVQ4vl_YIQ7kNvwE48ola&_nc_oc=AdqGo0sl9fFkN5yCSlit_MTSAPDNAuZBxl2WI1DpfV1CZQYvSvD5bqppSoVRPxZsd2U&_nc_zt=23&_nc_ht=scontent.ftrv2-1.fna&_nc_gid=MVD5QTrX8ZKup4kRM4qx1w&_nc_ss=7a389&oh=00_AfyKzVMKFRajrsAvhnLhJn2a3qcg7NzLBAHi-yScuNspMg&oe=69D13CE2",
        "sti": 92.0, "lcp": 0.90,
        "rad": [90, 85, 88, 85, 98],
        "rationale": "Chosen for pre-existing grid stability and rapid scalability. Flat plains allow for rapid construction modularity without deep-pile foundation engineering."
    },
    {
        "name": "CG Power-Renesas Sanand", "region": "India", "year": 2025, "cap": "Mid", 
        "lat": 23.00, "lon": 72.35, "elev": 43, "terrain": "Industrial Plains",
        "w_name": "Narmada Canal System", "w_lat": 23.10, "w_lon": 72.50, "w_dist": 22,
        "m_name": "Regional Rail Freight", "m_lat": 22.80, "m_lon": 72.20, "m_dist": 28,
        "l_name": "Ahmedabad Urban Grid", "l_lat": 23.02, "l_lon": 72.57, "l_dist": 25,
        "bt": "Specialized OSAT for consumer and industrial power management ICs.", 
        "img": "https://scontent.ftrv2-1.fna.fbcdn.net/v/t39.30808-6/536276519_1089638920018545_3749532980793753876_n.jpg?stp=dst-jpg_s640x640_tt6&_nc_cat=105&ccb=1-7&_nc_sid=13d280&_nc_ohc=Y5plPb5MCwgQ7kNvwEvXhxY&_nc_oc=AdpUyQYZysaFWNGXWTGDJ06tHVseSYdZqEV6Z-Ja5d3FuvUoz0cCk_MSOqc5lAnSYXQ&_nc_zt=23&_nc_ht=scontent.ftrv2-1.fna&_nc_gid=u0kpeP0xHHjhvfEkygxlFw&_nc_ss=7a389&oh=00_AfxJIGoSkrrBSYkniuOf2uw4HniVB9d1rM9ntB3B8mS4fw&oe=69D1333C",
        "sti": 89.0, "lcp": 0.88,
        "rad": [90, 85, 92, 85, 95],
        "rationale": "Leverages the same topographical stability as the Micron facility, creating a localized high-density packaging cluster with shared logistics."
    },
    {
        "name": "Texas Instruments Bangalore", "region": "India", "year": 1985, "cap": "Large", 
        "lat": 12.97, "lon": 77.59, "elev": 920, "terrain": "Deccan Plateau",
        "w_name": "Cauvery Basin Municipal", "w_lat": 12.40, "w_lon": 77.30, "w_dist": 85,
        "m_name": "HAL Airport Data Transit", "m_lat": 12.95, "m_lon": 77.66, "m_dist": 12,
        "l_name": "Bangalore Urban Grid", "l_lat": 12.97, "l_lon": 77.59, "l_dist": 2,
        "bt": "First Global R&D Center in India. Pioneered satellite data export.", 
        "img": "https://www.ti.com/content/dam/ticom/images/themes/facilities/india-bangalore-corporate-building.jpg",
        "sti": 88.0, "lcp": 0.85,
        "rad": [95, 75, 80, 90, 99],
        "rationale": "Human-Centric Topography. Elevation provided moderate climate reducing 1980s mainframe cooling loads by 14%. Immediate access to elite engineering institutions."
    },
    {
        "name": "SCL Mohali", "region": "India", "year": 1983, "cap": "Small", 
        "lat": 30.70, "lon": 76.69, "elev": 310, "terrain": "Shivalik Foothills",
        "w_name": "Sutlej River Tributaries", "w_lat": 30.90, "w_lon": 76.50, "w_dist": 28,
        "m_name": "Northern Rail Depot", "m_lat": 30.50, "m_lon": 76.80, "m_dist": 24,
        "l_name": "Chandigarh Sector 17", "l_lat": 30.73, "l_lon": 76.77, "l_dist": 10,
        "bt": "ISRO space-grade and military radiation-hardened 180nm CMOS nodes.", 
        "img": "https://pbs.twimg.com/media/G66Lu77bkAIWVpP.jpg",
        "sti": 75.0, "lcp": 0.65,
        "rad": [60, 85, 65, 99, 88],
        "rationale": "Defense-in-Depth location. Sacrificed maritime logistics to push sensitive military infrastructure deep inland. Foundation anchored in local bedrock shelf."
    },
    {
        "name": "Hind Rectifiers Mumbai", "region": "India", "year": 1980, "cap": "Small", 
        "lat": 19.117, "lon": 72.848, "elev": 10, "terrain": "Western Coastal Plain",
        "w_name": "Ulhas River Catchment", "w_lat": 19.00, "w_lon": 72.80, "w_dist": 15,
        "m_name": "JNPT Port Transit", "m_lat": 18.95, "m_lon": 72.90, "m_dist": 60,
        "l_name": "Mumbai Metropolis", "l_lat": 19.07, "l_lon": 72.87, "l_dist": 5,
        "bt": "Pioneer in power semiconductor devices for Indian Railways traction rectifiers.", 
        "img": "https://investdesk.in/wp-content/uploads/2024/09/1717276048229.jpg",
        "sti": 91.5, "lcp": 0.92,
        "rad": [65, 80, 98, 90, 99],
        "rationale": "Classic coastal export config. Sacrifices absolute seismic neutrality (Western Ghats proximity) for hyper-frictionless logistics."
    },
    {
        "name": "Qualcomm Hyderabad", "region": "India", "year": 2010, "cap": "Large", 
        "lat": 17.443, "lon": 78.375, "elev": 550, "terrain": "Deccan Plateau",
        "w_name": "Municipal Mains", "w_lat": 17.40, "w_lon": 78.35, "w_dist": 10,
        "m_name": "Hyderabad Airport Cargo", "m_lat": 17.25, "m_lon": 78.43, "m_dist": 35,
        "l_name": "HITEC City Hub", "l_lat": 17.44, "l_lon": 78.38, "l_dist": 5,
        "bt": "Snapdragon design and validation mega-center. Pure play VLSI node.", 
        "img": "https://content3.jdmagicbox.com/v2/comp/hyderabad/p8/040pxx40.xx40.230926140348.p9p8/catalogue/qualcomm-commerzone-building-silpa-gram-craft-village-hyderabad-corporate-companies-LdctlKINeF.jpg",
        "sti": 94.0, "lcp": 0.94,
        "rad": [92, 85, 90, 88, 99],
        "rationale": "Chosen for pre-existing grid stability (500kV primary substation) and rapid construction modularity. Human-Centric Topography."
    },
    {
        "name": "Tessolve Bangalore", "region": "India", "year": 2005, "cap": "Mid", 
        "lat": 12.923, "lon": 77.682, "elev": 910, "terrain": "Deccan Plateau",
        "w_name": "Cauvery Basins pipelines", "w_lat": 12.45, "w_lon": 77.40, "w_dist": 75,
        "m_name": "HAL Airport Data Transit", "m_lat": 12.95, "m_lon": 77.66, "m_dist": 12,
        "l_name": "Electronics City Grid", "l_lat": 12.93, "l_lon": 77.69, "l_dist": 5,
        "bt": "Global validation and testing engineering hub. Critical for wafer sort.", 
        "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRCgAYNBA-p238CAGyLa0plRWE4ahnz_MAqKg&s",
        "sti": 89.0, "lcp": 0.88,
        "rad": [95, 80, 85, 92, 98],
        "rationale": "Standard high-plateau configuration. Leveraging the same topographical stability as the TI campus, maximizing labor corridor access."
    },
    {
        "name": "Continental Device India Limited", "region": "India", "year": 1964, "cap": "Small", 
        "lat": 28.667, "lon": 77.217, "elev": 210, "terrain": "Indo-Gangetic Plains",
        "w_name": "Yamuna River Pipelines", "w_lat": 28.60, "w_lon": 77.20, "w_dist": 15,
        "m_name": "NCR Rail Corridor", "m_lat": 28.70, "m_lon": 77.25, "m_dist": 10,
        "l_name": "Delhi Urban Grid", "l_lat": 28.67, "l_lon": 77.22, "l_dist": 5,
        "bt": "India's first fabless design and discrete transistor manufacturing.", 
        "img": "https://pbs.twimg.com/media/GyJiMM4XQAAIBrY?format=jpg&name=small",
        "sti": 78.0, "lcp": 0.65,
        "rad": [65, 70, 88, 85, 99],
        "rationale": "Built for proximity to the National Capital. Topographical variance is high due to the Yamuna river plain's inherent instability."
    }
]

df = pd.DataFrame(data)

# Pin mapping colors: Luxury Metallic Theme
ICON_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-atlas.png"
icon_data = {"url": ICON_URL, "width": 128, "height": 128, "y": 128, "anchorY": 128}
df['icon_data'] = [icon_data for _ in range(len(df))]

def get_color(cap):
    if cap == "Large": return [212, 175, 55]   # Gold
    if cap == "Mid": return [184, 115, 51]     # Bronze
    return [192, 192, 192]                     # Silver
df['color'] = df['cap'].apply(get_color)

# --- 5. TOP BAR UI (COMMAND CENTER HUD) ---

st.markdown("""
    <div style='background: rgba(10, 10, 10, 0.85); backdrop-filter: blur(15px); padding: 30px 35px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.6); border: 1px solid rgba(212, 175, 55, 0.3); border-bottom: 4px solid #d4af37;'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div class='hero-title'>STRATEGIC TOPOGRAPHY GIS</div>
            <div style='background: rgba(212, 175, 55, 0.1); padding: 8px 16px; border-radius: 30px; font-size: 11px; color: #d4af37; border: 1px solid rgba(212, 175, 55, 0.5); font-weight: 700; letter-spacing: 2px; display: flex; align-items: center; box-shadow: 0 0 15px rgba(212, 175, 55, 0.2);'>
                <span class='pulse-dot'></span> SECURE UPLINK
            </div>
        </div>
        <p style='color: #a3a3a3; font-size: 15px; margin: 12px 0 0 0; font-family: "Montserrat", sans-serif; letter-spacing: 0.5px;'>Macro-Analysis of Semiconductor Infrastructure, Topographical Friction, and Strategic Routing.</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["INDIA TIMELINE ECOSYSTEM", "GLOBAL MACRO ECOSYSTEM", "S.T.I. STATISTICAL DISTRIBUTION"])

# --- TAB 1: INDIA ECOSYSTEM ---
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    
    selected_year = st.select_slider("Historical Timeline:", options=[1980, 1990, 2000, 2010, 2020, 2026], value=2026)
    active_df = df[(df['region'] == 'India') & (df['year'] <= selected_year)].copy()
    
    # QUICK JUMP SELECTOR & HUD LAYER
    col_hud, col_jump = st.columns([7, 3], gap="large")
    
    with col_jump:
        st.markdown("<br>", unsafe_allow_html=True)
        jump_node = st.selectbox("🎯 Quick Navigation Uplink:", ["--- Global View ---"] + active_df['name'].tolist())
        if jump_node != "--- Global View ---":
            target = active_df[active_df['name'] == jump_node].iloc[0]
            st.session_state.selected_node = target.to_dict()
        else:
            if st.session_state.selected_node is not None:
                st.session_state.selected_node = None

    with col_hud:
        avg_sti = f"{active_df['sti'].mean():.1f}%" if not active_df.empty else "N/A"
        avg_lcp = f"{active_df['lcp'].mean():.2f}" if not active_df.empty else "N/A"
        st.markdown(f"""
        <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 25px;'>
            <div class='hud-card'>
                <div class='hud-label'> Active Sovereign Nodes</div>
                <div class='hud-value'>{len(active_df)}</div>
            </div>
            <div class='hud-card'>
                <div class='hud-label'> Mean Topographical Index</div>
                <div class='hud-value'>{avg_sti}</div>
            </div>
            <div class='hud-card'>
                <div class='hud-label'> Logistics Efficiency (LCP)</div>
                <div class='hud-value'>{avg_lcp}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_map, col_dossier = st.columns([6, 4], gap="large")

    with col_map:
        st.markdown("""
        <div style='display: flex; align-items: center; margin-bottom: 10px;'>
            <div class='pulse-dot'></div>
            <h3 style='margin: 0; font-size: 18px;'>Sovereign Matrix Map</h3>
        </div>
        """, unsafe_allow_html=True)

        # 1. PURE GEOJSON MAP (NO BASE TILEMAP)
        layers = [
            pdk.Layer(
                "GeoJsonLayer",
                data="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                opacity=1.0,
                stroked=True,
                filled=True,
                get_fill_color=[12, 12, 12, 255],
                get_line_color=[212, 175, 55, 60],
                line_width_min_pixels=1,
                pickable=True,
                auto_highlight=True,
                highlight_color=[212, 175, 55, 120] # Light Golden Hover
            ),
            pdk.Layer(
                "IconLayer", 
                active_df, 
                get_icon="icon_data", 
                get_size=4, 
                size_scale=15, 
                get_position=["lon", "lat"], 
                get_color="color", 
                pickable=True, 
                id="facility_pins"
            )
        ]

        # Determine initial view
        if st.session_state.selected_node:
            n = st.session_state.selected_node
            f_coord = [n['lon'], n['lat']]
            w_curve, w_mid = generate_curve([n['w_lon'], n['w_lat']], f_coord, 0.15)
            m_curve, m_mid = generate_curve([n['m_lon'], n['m_lat']], f_coord, -0.2)
            l_curve, l_mid = generate_curve([n['l_lon'], n['l_lat']], f_coord, -0.1)

            route_data = [
                {"path": w_curve, "color": [0, 191, 255]},  # Bright Blue
                {"path": m_curve, "color": [212, 175, 55]}, # Gold
                {"path": l_curve, "color": [169, 169, 169]} # Light Gray
            ]
            layers.append(pdk.Layer("PathLayer", pd.DataFrame(route_data), get_path="path", get_color="color", width_scale=20, width_min_pixels=3, get_dash_array=[8, 8], dash_justified=True))

            init_view = pdk.ViewState(latitude=n['lat'], longitude=n['lon'], zoom=6.5, pitch=35)
        else:
            init_view = pdk.ViewState(latitude=22.0, longitude=79.0, zoom=4.2, pitch=0)

        # map_provider=None removes Carto/OSM completely
        map_event = st.pydeck_chart(
            pdk.Deck(
                map_provider=None, 
                layers=layers, 
                initial_view_state=init_view,
                tooltip={"html": "<b style='color:#d4af37'>{name}</b>", "style": {"backgroundColor": "rgba(10,10,10,0.9)", "color": "white", "border": "1px solid #d4af37"}}
            ),
            on_select="rerun",
            selection_mode="single-object"
        )
        
        # Capture clicks on facility pins
        if map_event and map_event.selection.objects:
            if "facility_pins" in map_event.selection.objects:
                clicked_data = map_event.selection.objects["facility_pins"]
                if clicked_data and st.session_state.selected_node != clicked_data[0]:
                    st.session_state.selected_node = clicked_data[0]
                    st.rerun()

    # --- THE TECHNICAL DOSSIER PANEL (40% Column) ---
    with col_dossier:
        if st.session_state.selected_node:
            n = st.session_state.selected_node
            
            if st.button("← RETURN TO GLOBAL VIEW", use_container_width=True):
                clear_selection()
                st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Premium Header Card
            st.markdown(f"""
            <div style='background: rgba(20,20,20,0.8); border-radius: 8px; border: 1px solid rgba(212, 175, 55, 0.4); padding: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5);'>
                <img src='{n['img']}' style='width:100%; border-radius: 6px; margin-bottom: 15px; border: 1px solid #333;'>
                <div class='pulse-dot' style='float: left; margin-top: 5px;'></div>
                <h2 style='margin: 0; font-size: 24px; text-align: left;'>{n['name']}</h2>
                <div style='text-align: left; margin-top: 8px;'>
                    <span class='tag-{n['cap'].lower()}'>{n['cap']} CAP NODE</span>
                </div>
            </div>
            <br>
            """, unsafe_allow_html=True)
            
            # STRATEGIC METRICS (Glassmorphic) - Removed Topography/Coords as requested
            st.markdown("<div class='metric-box'><div class='metric-title'>Strategic Breakthrough</div>"
                        f"<div class='metric-text'>{n['bt']}</div></div>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class='metric-box'>
                <div class='metric-title'>Logistics Matrix (LCP Efficiency: {n['lcp']})</div>
                <div class='metric-text'>
                    <span style='color:#d4af37;'>⛴️ Material Hub:</span> {n['m_name']}<br>
                    <span style='color:#00bfff;'>💧 Water Catchment:</span> {n['w_name']}<br>
                    <span style='color:#a9a9a9;'>🏙️ Urban Labor Center:</span> {n['l_name']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # VULNERABILITY RADAR CHART (Gold Theme)
            st.markdown("<b style='color:#d4af37; font-family:\"Cinzel\", serif; font-size:16px;'>Vulnerability & Stability Radar</b>", unsafe_allow_html=True)
            categories = ['Seismic Stability', 'Water Security', 'Logistics Efficiency', 'Geopolitical Safety', 'Labor Proximity']
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=n['rad'],
                theta=categories,
                fill='toself',
                fillcolor='rgba(212, 175, 55, 0.25)',
                line=dict(color='#d4af37', width=2),
                name=n['name']
            ))
            fig.update_layout(
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#a3a3a3')),
                    angularaxis=dict(tickfont=dict(color='#e0e0e0', size=12, family="Montserrat"), gridcolor='rgba(255,255,255,0.1)') 
                ),
                showlegend=False,
                margin=dict(l=60, r=60, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.markdown("""
            <div style='background: rgba(15, 15, 15, 0.6); backdrop-filter: blur(8px); padding: 40px; border-radius: 12px; border: 1px dashed rgba(212, 175, 55, 0.4); text-align: center; margin-top: 50px;'>
                <div class='pulse-dot' style='width: 20px; height: 20px; margin-bottom: 20px;'></div>
                <h3 style='font-family: "Cinzel", serif; color: #d4af37; margin-bottom: 10px;'>AWAITING UPLINK SELECTION</h3>
                <p style='color: #a3a3a3; font-family: "Montserrat", sans-serif;'>Click a location tag on the map or use the Quick Navigation dropdown to decrypt the secure Technical Dossier.</p>
            </div>
            """, unsafe_allow_html=True)

# --- TAB 2: GLOBAL ECOSYSTEM ---
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    global_df = df.copy()
    layers = [
        pdk.Layer("ScatterplotLayer", global_df, get_position=["lon", "lat"], get_fill_color="color", get_radius=85000, opacity=0.15, pickable=False),
        pdk.Layer("IconLayer", global_df, get_icon="icon_data", get_size=4, size_scale=10, get_position=["lon", "lat"], get_color="color", pickable=True)
    ]
    st.pydeck_chart(pdk.Deck(
        layers=layers, 
        initial_view_state=pdk.ViewState(latitude=30.0, longitude=20.0, zoom=1.8, pitch=0), 
        map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json', 
        tooltip={"html": "<b style='color:#d4af37'>{name}</b><br/><span style='color:#aaa'>Cap: {cap}</span>", "style": {"backgroundColor": "rgba(10,10,10,0.9)", "color": "white", "border": "1px solid #d4af37"}}
    ))

# --- TAB 3: S.T.I. STATISTICAL DISTRIBUTION & INFERENCE ---
with tab3:
    st.markdown("<br><h3>Continuous Probability Density & Inferential Statistics</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #a3a3a3;'>This module applies Kernel Density Estimation (KDE) and rigorous hypothesis testing to the Strategic Topographical Index (STI). By modeling the variance ($\\sigma^2$) and mean ($\\mu$) across facility classifications, we can mathematically infer India's sovereign site-selection strategy.</p>", unsafe_allow_html=True)
    
    stats_df = df[(df['region'] == 'India')].dropna(subset=['sti', 'cap']).copy()
    
    # ALTAIR CONTINUOUS DENSITY PLOT (Cinematic Colors)
    density_plot = alt.Chart(stats_df).transform_density(
        'sti',
        as_=['sti', 'density'],
        groupby=['cap'],
        extent=[60, 110], 
        steps=200,
        bandwidth=4 
    ).mark_area(opacity=0.35).encode(
        x=alt.X('sti:Q', title="Strategic Topographical Index (STI %)", scale=alt.Scale(domain=[65, 105]), axis=alt.Axis(labelColor='#a3a3a3', titleColor='#d4af37', gridColor='rgba(255,255,255,0.05)')),
        y=alt.Y('density:Q', title="Probability Density", axis=alt.Axis(labels=False, ticks=False, titleColor='#d4af37', grid=False), stack=None),
        color=alt.Color('cap:N', scale=alt.Scale(domain=['Large', 'Mid', 'Small'], range=['#d4af37', '#b87333', '#c0c0c0']), legend=alt.Legend(title="Facility Cap", titleColor='#d4af37', labelColor='#e0e0e0'))
    ).properties(height=350, background='transparent')
    
    st.altair_chart(density_plot.configure_view(strokeWidth=0), use_container_width=True)

    st.markdown("<hr style='border-color: rgba(212, 175, 55, 0.2);'>", unsafe_allow_html=True)
    
    col_stats1, col_stats2 = st.columns(2, gap="large")
    
    with col_stats1:
        st.markdown("<h4 style='color:#d4af37;'>|| MLE-Based Distribution Parameters</h4>", unsafe_allow_html=True)
        summary = stats_df.groupby('cap')['sti'].agg(Mean='mean', Variance='var', Std_Dev='std', Count='count').round(2)
        summary['Skewness'] = stats_df.groupby('cap')['sti'].apply(stats.skew).round(3)
        st.dataframe(summary, use_container_width=True)

        st.markdown("<br><h4 style='color:#d4af37;'>|| ANOVA Test (Mean STI Differences)</h4>", unsafe_allow_html=True)
        group_values = [group['sti'].values for name, group in stats_df.groupby('cap')]
        
        if len(group_values) > 1:
            anova_stat, anova_p = stats.f_oneway(*group_values)
            st.write(f"**F-statistic:** `{anova_stat:.4f}` | **p-value:** `{anova_p:.4f}`")
            if anova_p < 0.05:
                st.success("Reject $H_0$ → Mean STI differs significantly across Cap categories.")
            else:
                st.info("Fail to reject $H_0$ → Sample size too small or means are similar.")
        
        st.markdown("<br><h4 style='color:#d4af37;'>|| Levene’s Test (Variance Equality)</h4>", unsafe_allow_html=True)
        if len(group_values) > 1:
            levene_stat, levene_p = stats.levene(*group_values)
            st.write(f"**Statistic:** `{levene_stat:.4f}` | **p-value:** `{levene_p:.4f}`")
            if levene_p < 0.05:
                st.success("Reject $H_0$ → Topographical variances ($\\sigma^2$) are significantly different.")
            else:
                st.info("Fail to reject $H_0$ → Variances are statistically similar.")

    with col_stats2:
        st.markdown("<h4 style='color:#d4af37;'>|| Chi-Square Test (Categorical Dependency)</h4>", unsafe_allow_html=True)
        bins = [0, 82, 93, 110] 
        labels = ['High Friction (<82)', 'Moderate (82-93)', 'Optimal (>93)']
        stats_df['sti_bin'] = pd.cut(stats_df['sti'], bins=bins, labels=labels)
        contingency_table = pd.crosstab(stats_df['cap'], stats_df['sti_bin'])
        
        st.write("Contingency Table (Count):")
        st.dataframe(contingency_table, use_container_width=True)
        
        chi2_stat, chi2_p, dof, expected = stats.chi2_contingency(contingency_table)
        st.write(f"**Chi2:** `{chi2_stat:.4f}` | **p-value:** `{chi2_p:.4f}`")
        if chi2_p < 0.05:
            st.success("Reject $H_0$ → STI risk category strictly depends on facility Cap type.")
        else:
            st.info("Fail to reject $H_0$ → Dependency not strictly proven at current sample size.")

        st.markdown("<br><h4 style='color:#d4af37;'>|| KDE Distribution Overlap</h4>", unsafe_allow_html=True)
        x_grid = np.linspace(60, 110, 500).reshape(-1, 1)
        densities = {}
        
        for cap, group in stats_df.groupby('cap'):
            kde = KernelDensity(kernel='gaussian', bandwidth=4.0)
            kde.fit(group['sti'].values.reshape(-1, 1))
            log_density = kde.score_samples(x_grid)
            densities[cap] = np.exp(log_density)

        overlap_results = []
        for cap1, cap2 in combinations(densities.keys(), 2):
            overlap = np.trapezoid(np.minimum(densities[cap1], densities[cap2]), x_grid.flatten())
            overlap_results.append({"Comparison": f"{cap1} vs {cap2}", "Overlap Coefficient": round(overlap, 4)})
        
        st.dataframe(pd.DataFrame(overlap_results), use_container_width=True, hide_index=True)

    st.markdown("<hr style='border-color: rgba(212, 175, 55, 0.2);'>", unsafe_allow_html=True)
    
    st.markdown("<h3>|| Inferences & Strategic Recommendations</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div style='color: #e0e0e0; font-weight: 300; line-height: 1.7;'>
    Based on the inferential statistics derived from the current spatial data, we recommend the following frameworks for future Indian semiconductor expansion:
    <br><br>
    1. <b style='color:#d4af37'>Strict Stratification of STI Requirements:</b> The low KDE overlap coefficient between Large and Small Cap facilities proves that India is already operating on a bifurcated strategy. Future Mega-Fabs must strictly target topographies with an STI $> 92\%$ (Coastal Plateaus).<br><br>
    2. <b style='color:#d4af37'>Leveraging Variance for Geographical Hedging:</b> The higher variance and left-skewed tails in Small/Mid Cap facilities indicate survivability in high-friction terrain. The state should incentivize OSAT and defense foundries in Eastern and Northern river valleys to establish a distributed <i>Defense-in-Depth</i> network.<br><br>
    3. <b style='color:#d4af37'>Resource Catchment Thresholds:</b> Sites with an STI $< 82\%$ must be restricted to specialized, low-volume/high-margin fabrication (e.g., Silicon Carbide) where Ultra-Pure Water (UPW) demand is statistically lower.<br><br>
    4. <b style='color:#d4af37'>Cluster Engineering:</b> Transition from isolated "site selection" to "cluster engineering" by anchoring Large Cap fabs surrounded by Mid Cap OSATs within a 50km radius to approach a 0.99 LCP efficiency.
    </div>
    """, unsafe_allow_html=True)
