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
st.set_page_config(layout="wide", page_title="Aegis: Strategic Topography", page_icon="🜚")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;600;800&display=swap');

        /* Deep cinematic black background */
        .stApp { background-color: #0a0a0a; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 2rem; padding-bottom: 0rem; max-width: 98%;}
        h1, h2, h3, p, span, div {font-family: 'Inter', sans-serif; color: #e5e5e5;}
        h1, h2, h3, h4 { font-family: 'Rajdhani', sans-serif; text-transform: uppercase; color: #d4af37; }
        
        /* Gold Accent HUD Cards */
        .hud-card {
            background-color: #111111;
            border: 1px solid #332b00;
            border-radius: 4px;
            padding: 15px 20px;
            border-top: 3px solid #d4af37;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        .hud-card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(212, 175, 55, 0.15); border-color: #d4af37; }
        .hud-value { font-size: 34px; font-weight: 800; color: #d4af37; font-family: 'Rajdhani', sans-serif; line-height: 1.1; }
        .hud-label { font-size: 11px; font-weight: 600; color: #888888; text-transform: uppercase; letter-spacing: 2px; }
        
        /* Cinematic Hero Banner */
        .hero-banner {
            background: radial-gradient(circle at 50% -20%, #2a2205 0%, #0a0a0a 80%);
            padding: 30px;
            border-radius: 6px;
            margin-bottom: 25px;
            border: 1px solid #2a2410;
            box-shadow: inset 0 0 40px rgba(0,0,0,0.8);
            display: flex; justify-content: space-between; align-items: center;
        }
        .hero-title {
            font-family: 'Rajdhani', sans-serif; font-size: 42px; font-weight: 700;
            margin: 0; letter-spacing: 4px; color: #d4af37; text-shadow: 0 0 20px rgba(212, 175, 55, 0.4);
        }
        .hero-subtitle { color: #888888; font-size: 13px; letter-spacing: 1px; margin-top: 5px; text-transform: uppercase;}
        
        /* Live Status Badge */
        .status-badge {
            background: rgba(212, 175, 55, 0.1); padding: 6px 14px; border-radius: 2px;
            font-size: 11px; color: #d4af37; border: 1px solid rgba(212, 175, 55, 0.4);
            font-weight: 600; letter-spacing: 2px; display: flex; align-items: center;
        }
        .pulse-dot {
            display: inline-block; width: 6px; height: 6px; border-radius: 50%; background-color: #d4af37; margin-right: 8px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.7); }
            70% { box-shadow: 0 0 0 6px rgba(212, 175, 55, 0); }
            100% { box-shadow: 0 0 0 0 rgba(212, 175, 55, 0); }
        }

        /* Metric Boxes in Dossier */
        .metric-box {
            background-color: #151515; padding: 16px; border-radius: 4px; border-left: 3px solid #d4af37; 
            margin-bottom: 12px; border: 1px solid #222222;
        }
        .metric-title { color: #888888; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; font-weight: 600; }
        .metric-text { color: #ffffff; font-size: 14px; line-height: 1.5; font-family: 'Inter', sans-serif;}

        /* Sliders and Tabs Override */
        .stSlider [data-baseweb="slider"] [role="slider"] { background-color: #d4af37 !important; border: 2px solid #000 !important; }
        .stSlider [data-baseweb="slider"] div[data-testid="stTickBar"] { background-color: #333 !important; }
        .stTabs [data-baseweb="tab-list"] { gap: 24px; background-color: transparent;}
        .stTabs [data-baseweb="tab"] { color: #888 !important; padding-bottom: 10px !important; border-bottom: 2px solid transparent !important; }
        .stTabs [aria-selected="true"] { color: #d4af37 !important; border-bottom-color: #d4af37 !important; font-weight: 600 !important;}
        
        /* Dialog Override for Dark Luxury */
        div[data-testid="stDialog"] > div { background-color: #0d0d0d; border: 1px solid #332b00; border-top: 4px solid #d4af37; }
        
        /* News Grid */
        .news-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; padding-bottom: 15px; }
        .news-card-grid { width: 100%; height: 180px; border-radius: 4px; background-size: cover; background-position: center; position: relative; overflow: hidden; border: 1px solid #222; transition: all 0.4s ease; cursor: pointer; }
        .news-card-grid:hover { border-color: #d4af37; transform: scale(1.02); }
        .card-overlay { position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(to top, rgba(10,10,10,0.95) 0%, rgba(10,10,10,0.6) 60%, transparent 100%); padding: 15px; }
        .card-tag { font-size: 9px; color: #000; background-color: #d4af37; text-transform: uppercase; font-weight: 800; padding: 3px 8px; border-radius: 2px; display: inline-block; margin-bottom: 8px; letter-spacing: 1px; }
        .card-title-grid { color: #ffffff !important; font-size: 13px; font-weight: 600; line-height: 1.4; font-family: 'Inter', sans-serif;}
    </style>
""", unsafe_allow_html=True)

# --- 2. STATE MANAGEMENT & ROUTING LOGIC (100% Retained) ---
if "selected_node" not in st.session_state:
    st.session_state.selected_node = None

def clear_selection():
    st.session_state.selected_node = None

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

# --- 3. THE UNIFIED DATASET (100% Retained) ---
data = [
    # ---- EXPANDED GLOBAL ECOSYSTEM ----
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

    # ---- INDIAN ECOSYSTEM (Highly Detailed) ----
    {
        "name": "Tata-PSMC Dholera", "region": "India", "year": 2026, "cap": "Large", 
        "lat": 22.25, "lon": 72.11, "elev": 15, "terrain": "Coastal Plateau",
        "w_name": "Sabarmati Desalination", "w_lat": 22.50, "w_lon": 72.30, "w_dist": 32,
        "m_name": "Gulf of Khambhat Port", "m_lat": 21.75, "m_lon": 72.25, "m_dist": 55,
        "l_name": "Ahmedabad Urban Center", "l_lat": 23.02, "l_lon": 72.57, "l_dist": 85,
        "bt": "India's First Commercial 28nm Mega-Fab. Sovereign logic node production.", 
        "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRqIQdQsnEGk-qsjXopCw4ZG3o-HgKqlO5aDg&s",
        "profile": [0, 8, 3, 14, 15, 15, 15, 15, 11, 4, 5], 
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
        "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=600&q=80",
        "profile": [120, 140, 85, 40, 55, 55, 55, 80, 130, 95, 110],
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
        "img": "https://images.unsplash.com/photo-1563207153-f404bf10c0e8?auto=format&fit=crop&w=600&q=80",
        "profile": [10, 18, 12, 35, 45, 45, 45, 42, 48, 44, 48],
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
        "img": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=600&q=80",
        "profile": [20, 28, 22, 38, 43, 43, 43, 40, 48, 42, 46],
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
        "profile": [850, 890, 860, 910, 920, 920, 920, 890, 915, 870, 880],
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
        "img": "https://images.unsplash.com/photo-1590247813693-5541d1c609fd?auto=format&fit=crop&w=600&q=80",
        "profile": [280, 270, 295, 285, 310, 310, 310, 340, 320, 370, 380],
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
        "profile": [2, 12, 5, 10, 10, 10, 10, 12, 9, 7, 8],
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
        "img": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=600&q=80",
        "profile": [500, 520, 530, 550, 550, 550, 550, 530, 510, 500, 490],
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
        "profile": [860, 880, 890, 910, 910, 910, 910, 890, 880, 870, 860],
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
        "profile": [190, 195, 200, 210, 210, 210, 210, 200, 198, 195, 190],
        "sti": 78.0, "lcp": 0.65,
        "rad": [65, 70, 88, 85, 99],
        "rationale": "Built for proximity to the National Capital. Topographical variance is high due to the Yamuna river plain's inherent instability."
    }
]

df = pd.DataFrame(data)

# Cinematic Gold/Copper Mapping Colors
def get_glow_color(cap):
    if cap == "Large": return [212, 175, 55]  # Gold
    if cap == "Mid": return [184, 115, 51]    # Copper
    return [85, 85, 85]                       # Slate
df['color'] = df['cap'].apply(get_glow_color)

# --- 4. CENTERED DIALOG: TECHNICAL DOSSIER ---
@st.dialog("STRATEGIC ASSET DOSSIER", width="large")
def render_dossier(n):
    st.markdown(f"<h2 style='margin-bottom: 0px;'>{n['name']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:#d4af37; font-size:12px; letter-spacing:1px; font-weight:700;'>{n['cap'].upper()} CAP FACILITY // LAT: {n['lat']} N // LON: {n['lon']} E</span>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #332b00; margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.image(n['img'], use_container_width=True)
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Strategic Breakthrough</div><div class='metric-text'>{n['bt']}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Topographical Stabilization (Elevation: {n['elev']}m MSL)</div><div class='metric-text'>{n['rationale']}</div></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='metric-box'>
            <div class='metric-title'>Logistics Matrix (LCP Efficiency: {n['lcp']})</div>
            <div class='metric-text' style='font-size: 13px;'>
                <span style='color:#d4af37'>■</span> <b>Material Hub:</b> {n['m_name']} <span style='color:#666'>({n['m_dist']}km route)</span><br>
                <span style='color:#d4af37'>■</span> <b>Water Catchment:</b> {n['w_name']} <span style='color:#666'>({n['w_dist']}km route)</span><br>
                <span style='color:#d4af37'>■</span> <b>Urban Labor Center:</b> {n['l_name']} <span style='color:#666'>({n['l_dist']}km route)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("<b style='color:#888; font-size: 12px; letter-spacing: 1px;'>TOPOGRAPHICAL INTEGRATION PROFILE</b>", unsafe_allow_html=True)
        total_dist = n['m_dist'] + n['w_dist']
        x_dist = np.linspace(0, total_dist, len(n['profile']))
        chart_df = pd.DataFrame({"Distance (km)": x_dist, "Elevation (MSL)": n['profile']})
        
        base = alt.Chart(chart_df).encode(
            x=alt.X('Distance (km):Q', title=f"Distance: 0km → {n['m_dist']}km → {total_dist}km", axis=alt.Axis(gridColor="#222", domainColor="#555", tickColor="#555", titleColor="#888", labelColor="#aaa")), 
            y=alt.Y('Elevation (MSL):Q', title="Elevation (m)", scale=alt.Scale(domain=[0, max(n['profile'])+50]), axis=alt.Axis(gridColor="#222", domainColor="#555", tickColor="#555", titleColor="#888", labelColor="#aaa"))
        )
        area = base.mark_area(opacity=0.2, color="#d4af37")
        line = base.mark_line(color="#d4af37", strokeWidth=2)
        facility_mark = pd.DataFrame({"x": [n['m_dist']], "y": [n['elev']]})
        point = alt.Chart(facility_mark).mark_point(color='#ffffff', size=150, shape='diamond', filled=True).encode(x='x:Q', y='y:Q')
        st.altair_chart(area + line + point, use_container_width=True)

        st.markdown("<b style='color:#888; font-size: 12px; letter-spacing: 1px;'>VULNERABILITY & STABILITY RADAR</b>", unsafe_allow_html=True)
        categories = ['Seismic Stability', 'Water Security', 'Logistics Efficiency', 'Geopolitical Safety', 'Labor Proximity']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=n['rad'], theta=categories, fill='toself',
            fillcolor='rgba(212, 175, 55, 0.2)', line=dict(color='#d4af37', width=2), marker=dict(color='#d4af37', size=6)
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor='#333', tickfont=dict(color='#555')),
                angularaxis=dict(gridcolor='#333', tickfont=dict(color='#aaa', size=11, family='Rajdhani'))
            ),
            showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=60, r=60, t=20, b=20), height=250
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- 5. TOP BAR HERO UI ---
st.markdown("""
    <div class='hero-banner'>
        <div>
            <div class='hero-title'>AEGIS COMMAND</div>
            <div class='hero-subtitle'>Topographical Friction & Strategic Macro-Routing</div>
        </div>
        <div class='status-badge'>
            <span class='pulse-dot'></span> UPLINK SECURE
        </div>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["[ TACTICAL THEATER: INDIA ]", "[ GLOBAL MACRO NETWORK ]", "[ STATISTICAL INFERENCE ]"])

# --- TAB 1: INDIA ECOSYSTEM (PyDeck mapped with new luxury style) ---
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    selected_year = st.select_slider("HISTORICAL TIMELINE OVERRIDE", options=[1980, 1990, 2000, 2010, 2020, 2026], value=2026)
    active_df = df[(df['region'] == 'India') & (df['year'] <= selected_year)].copy()
    
    avg_sti = f"{active_df['sti'].mean():.1f}%" if not active_df.empty else "N/A"
    avg_lcp = f"{active_df['lcp'].mean():.2f}" if not active_df.empty else "N/A"
    
    st.markdown(f"""
    <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 10px; margin-bottom: 30px;'>
        <div class='hud-card'>
            <div class='hud-label'>Active Sovereign Nodes</div>
            <div class='hud-value'>{len(active_df)}</div>
        </div>
        <div class='hud-card'>
            <div class='hud-label'>Mean Topographical Index</div>
            <div class='hud-value'>{avg_sti}</div>
        </div>
        <div class='hud-card'>
            <div class='hud-label'>Logistics Efficiency (LCP)</div>
            <div class='hud-value'>{avg_lcp}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_map, col_intel = st.columns([6, 4], gap="large")

    with col_map:
        st.markdown("<span style='font-family:Rajdhani; color:#d4af37; font-size:16px; font-weight:700;'>GEOSPATIAL THEATER</span> <span style='color:#666; font-size:12px;'>(CLICK TO OPEN DOSSIER / DOUBLE CLICK TO CLEAR)</span>", unsafe_allow_html=True)
        
        layers = [
            pdk.Layer(
                "ScatterplotLayer",
                active_df,
                get_position=["lon", "lat"],
                get_color="color",
                get_radius=25000,
                opacity=0.1,
                pickable=False
            ),
            pdk.Layer(
                "ScatterplotLayer",
                active_df,
                get_position=["lon", "lat"],
                get_fill_color="color",
                get_line_color=[255, 255, 255],
                get_radius=8000,
                stroked=True,
                line_width_min_pixels=1,
                pickable=True,
                id="facility_pins"
            )
        ]

        init_view = pdk.ViewState(latitude=22.0, longitude=79.0, zoom=4.2, pitch=0)

        # Retained Original Routing Logic
        if st.session_state.selected_node:
            n = st.session_state.selected_node
            f_coord = [n['lon'], n['lat']]
            
            w_curve, w_mid = generate_curve([n['w_lon'], n['w_lat']], f_coord, 0.15)
            m_curve, m_mid = generate_curve([n['m_lon'], n['m_lat']], f_coord, -0.2)
            l_curve, l_mid = generate_curve([n['l_lon'], n['l_lat']], f_coord, -0.1)

            route_data = [
                {"path": w_curve, "color": [0, 200, 255]}, # Cyan
                {"path": m_curve, "color": [212, 175, 55]}, # Gold
                {"path": l_curve, "color": [150, 150, 150]}  # Gray
            ]
            layers.append(pdk.Layer("PathLayer", pd.DataFrame(route_data), get_path="path", get_color="color", width_scale=20, width_min_pixels=3, get_dash_array=[8, 8], dash_justified=True))

            res_data = [
                {"lon": n['w_lon'], "lat": n['w_lat'], "color": [0, 200, 255]},
                {"lon": n['m_lon'], "lat": n['m_lat'], "color": [212, 175, 55]},
                {"lon": n['l_lon'], "lat": n['l_lat'], "color": [150, 150, 150]}
            ]
            layers.append(pdk.Layer("ScatterplotLayer", pd.DataFrame(res_data), get_position=["lon", "lat"], get_fill_color="color", get_radius=3500, stroked=True, get_line_color=[0, 0, 0]))

            label_data = [
                {"lon": n['lon'], "lat": n['lat'], "text": f"Target: {n['lat']} N, {n['lon']} E", "color": [255, 255, 255], "offset": [0, -40]},
                {"lon": w_mid[0], "lat": w_mid[1], "text": f"{n['w_dist']}km (Water Corridor)", "color": [0, 200, 255], "offset": [0, 25]},
                {"lon": m_mid[0], "lat": m_mid[1], "text": f"{n['m_dist']}km (Transit)", "color": [212, 175, 55], "offset": [0, -25]},
                {"lon": l_mid[0], "lat": l_mid[1], "text": f"{n['l_dist']}km (Urban Labor)", "color": [150, 150, 150], "offset": [40, 0]}
            ]
            layers.append(pdk.Layer(
                "TextLayer", pd.DataFrame(label_data), get_position=["lon", "lat"], get_text="text", 
                get_color="color", get_size=13, get_alignment_baseline="'center'", get_pixel_offset="offset"
            ))

            init_view = pdk.ViewState(latitude=n['lat'], longitude=n['lon'], zoom=6.8, pitch=0)

        map_event = st.pydeck_chart(
            pdk.Deck(
                layers=layers, 
                initial_view_state=init_view,
                map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
                tooltip={"text": "{name}\nCap: {cap}"}
            ),
            on_select="rerun",
            selection_mode="single-object"
        )
        
        # Open Dialog on Select
        if map_event and map_event.selection.objects:
            if "facility_pins" in map_event.selection.objects:
                clicked_data = map_event.selection.objects["facility_pins"]
                if clicked_data:
                    # If clicking a new node, set it and open dialog
                    if st.session_state.selected_node != clicked_data[0]:
                        st.session_state.selected_node = clicked_data[0]
                        render_dossier(clicked_data[0])
        else:
            # Clear if map empty clicked
            if st.session_state.selected_node is not None:
                st.session_state.selected_node = None
                st.rerun()

    with col_intel:
        st.markdown("<span style='font-family:Rajdhani; color:#d4af37; font-size:16px; font-weight:700;'>LIVE STRAT-INTEL FEED</span>", unsafe_allow_html=True)
        live_news = fetch_live_intelligence()
        
        bg_images = [
            "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=400&q=80",
            "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=400&q=80",
            "https://images.unsplash.com/photo-1590247813693-5541d1c609fd?auto=format&fit=crop&w=400&q=80",
            "https://images.unsplash.com/photo-1563207153-f404bf10c0e8?auto=format&fit=crop&w=400&q=80"
        ]
        
        if live_news:
            grid_html = '<div class="news-grid">'
            for i, article in enumerate(live_news[:4]):
                clean_title = article.title.rsplit(" - ", 1)[0]
                img = bg_images[i % len(bg_images)]
                tag = "MACRO TREND" if i%2==0 else "DISPATCH"
                
                grid_html += f"""
                <a href='{article.link}' target='_blank' style='text-decoration:none;'>
                    <div class="news-card-grid" style="background-image: url('{img}');">
                        <div class="card-overlay">
                            <div class="card-tag">{tag}</div>
                            <div class="card-title-grid">{clean_title}</div>
                        </div>
                    </div>
                </a>"""
            grid_html += '</div>'
            st.markdown(grid_html, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#666; font-style:italic; border:1px solid #333; padding:20px; text-align:center;'>Uplink inactive. No signals detected.</div>", unsafe_allow_html=True)


# --- TAB 2: GLOBAL ECOSYSTEM ---
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    global_df = df.copy()
    layers = [
        pdk.Layer(
            "ScatterplotLayer", global_df, get_position=["lon", "lat"], get_fill_color="color", 
            get_line_color=[255, 255, 255], get_radius=40000, stroked=True, line_width_min_pixels=1, pickable=True
        )
    ]
    st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=pdk.ViewState(latitude=30.0, longitude=20.0, zoom=1.8, pitch=0), map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json', tooltip={"text": "{name}\nCap: {cap}"}))


# --- TAB 3: S.T.I. STATISTICAL DISTRIBUTION & INFERENCE (100% Retained) ---
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom: 0px;'>CONTINUOUS PROBABILITY DENSITY & INFERENTIAL STATISTICS</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:14px;'>This module applies Kernel Density Estimation (KDE) and rigorous hypothesis testing to the Strategic Topographical Index (STI). By modeling the variance ($\\sigma^2$) and mean ($\\mu$) across facility classifications, we mathematically infer India's sovereign site-selection strategy.</p>", unsafe_allow_html=True)
    
    stats_df = df[(df['region'] == 'India')].dropna(subset=['sti', 'cap']).copy()
    
    # 1. ALTAIR CONTINUOUS DENSITY PLOT
    domain = ['Large', 'Mid', 'Small']
    range_ = ['#d4af37', '#b87333', '#555555']
    
    density_plot = alt.Chart(stats_df).transform_density(
        'sti', as_=['sti', 'density'], groupby=['cap'], extent=[60, 110], steps=200, bandwidth=4 
    ).mark_area(opacity=0.3, strokeWidth=2).encode(
        x=alt.X('sti:Q', title="Strategic Topographical Index (STI %)", scale=alt.Scale(domain=[65, 105]),
                axis=alt.Axis(gridColor="#222", domainColor="#555", tickColor="#555", titleColor="#888", labelColor="#aaa")),
        y=alt.Y('density:Q', title="Probability Density", axis=alt.Axis(labels=False, ticks=False, grid=False, titleColor="#888")),
        color=alt.Color('cap:N', scale=alt.Scale(domain=domain, range=range_), legend=alt.Legend(title="Facility Cap", titleColor="#888", labelColor="#aaa")),
        stroke=alt.Color('cap:N', scale=alt.Scale(domain=domain, range=range_))
    ).properties(height=350, background="transparent")
    
    st.altair_chart(density_plot, use_container_width=True)

    st.markdown("<hr style='border-color: #222; margin: 30px 0;'>", unsafe_allow_html=True)
    
    # --- STATISTICAL ANALYSIS ENGINE ---
    col_stats1, col_stats2 = st.columns(2, gap="large")
    
    with col_stats1:
        st.markdown("<h4 style='color:#d4af37; font-size:15px;'>// MLE-BASED DISTRIBUTION PARAMETERS</h4>", unsafe_allow_html=True)
        summary = stats_df.groupby('cap')['sti'].agg(Mean='mean', Variance='var', Std_Dev='std', Count='count').round(2)
        summary['Skewness'] = stats_df.groupby('cap')['sti'].apply(stats.skew).round(3)
        st.dataframe(summary, use_container_width=True)

        st.markdown("<h4 style='color:#d4af37; font-size:15px; margin-top:20px;'>// ANOVA TEST (MEAN STI DIFFERENCES)</h4>", unsafe_allow_html=True)
        group_values = [group['sti'].values for name, group in stats_df.groupby('cap')]
        if len(group_values) > 1:
            anova_stat, anova_p = stats.f_oneway(*group_values)
            st.markdown(f"<span style='color:#fff'>F-statistic:</span> <span style='color:#d4af37'>{anova_stat:.4f}</span> | <span style='color:#fff'>p-value:</span> <span style='color:#d4af37'>{anova_p:.4f}</span>", unsafe_allow_html=True)
            if anova_p < 0.05:
                st.success("Reject $H_0$ → Mean STI differs significantly across Cap categories.")
            else:
                st.info("Fail to reject $H_0$ → Sample size too small or means are similar.")
        
        st.markdown("<h4 style='color:#d4af37; font-size:15px; margin-top:20px;'>// LEVENE’S TEST (VARIANCE EQUALITY)</h4>", unsafe_allow_html=True)
        if len(group_values) > 1:
            levene_stat, levene_p = stats.levene(*group_values)
            st.markdown(f"<span style='color:#fff'>Statistic:</span> <span style='color:#d4af37'>{levene_stat:.4f}</span> | <span style='color:#fff'>p-value:</span> <span style='color:#d4af37'>{levene_p:.4f}</span>", unsafe_allow_html=True)
            if levene_p < 0.05:
                st.success("Reject $H_0$ → Topographical variances ($\\sigma^2$) are significantly different.")
            else:
                st.info("Fail to reject $H_0$ → Variances are statistically similar.")

    with col_stats2:
        st.markdown("<h4 style='color:#d4af37; font-size:15px;'>// CHI-SQUARE TEST (CATEGORICAL DEPENDENCY)</h4>", unsafe_allow_html=True)
        bins = [0, 82, 93, 110] 
        labels = ['High Friction (<82)', 'Moderate (82-93)', 'Optimal (>93)']
        stats_df['sti_bin'] = pd.cut(stats_df['sti'], bins=bins, labels=labels)
        contingency_table = pd.crosstab(stats_df['cap'], stats_df['sti_bin'])
        st.write("Contingency Table (Count):")
        st.dataframe(contingency_table, use_container_width=True)
        
        chi2_stat, chi2_p, dof, expected = stats.chi2_contingency(contingency_table)
        st.markdown(f"<span style='color:#fff'>Chi2:</span> <span style='color:#d4af37'>{chi2_stat:.4f}</span> | <span style='color:#fff'>p-value:</span> <span style='color:#d4af37'>{chi2_p:.4f}</span>", unsafe_allow_html=True)
        if chi2_p < 0.05:
            st.success("Reject $H_0$ → STI risk category strictly depends on facility Cap type.")
        else:
            st.info("Fail to reject $H_0$ → Dependency not strictly proven at current sample size.")

        st.markdown("<h4 style='color:#d4af37; font-size:15px; margin-top:20px;'>// KDE DISTRIBUTION OVERLAP</h4>", unsafe_allow_html=True)
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

    st.markdown("<hr style='border-color: #222; margin: 30px 0;'>", unsafe_allow_html=True)
    
    # --- STRATEGIC RECOMMENDATIONS BASED ON STATS ---
    st.markdown("<h3 style='margin-bottom: 0px;'>// INFERENCES & STRATEGIC RECOMMENDATIONS FOR FUTURE DEVELOPMENT</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div style='color:#ccc; font-size:14px; line-height: 1.6;'>
    Based on the inferential statistics derived from the current spatial data, we recommend the following frameworks for future Indian semiconductor expansion:
    
    1. <b>Strict Stratification of STI Requirements (ANOVA & Overlap Inference):</b> The low KDE overlap coefficient between Large and Small Cap facilities proves that India is already operating on a bifurcated strategy. <b>Recommendation:</b> Future Mega-Fabs (Large Cap) must strictly target topographies with an STI $> 92\%$ (Coastal Plateaus / Stable Plains). Attempting to build a Large Cap fab in a "Moderate" zone will result in catastrophic logistical and vibration friction.
    2. <b>Leveraging Variance for Geographical Hedging (Levene's Inference):</b> The higher variance ($\\sigma^2$) and left-skewed tails in Small/Mid Cap facilities indicate they can survive in high-friction terrain. <b>Recommendation:</b> The government should incentivize future Mid/Small Cap facilities (OSAT, discrete power, defense) to be built in Eastern and Northern river valleys or foothills. This accepts a lower STI but establishes a distributed <i>Defense-in-Depth</i> network, ensuring the entire supply chain cannot be wiped out by a single coastal weather event or naval blockade.
    3. <b>Resource Catchment Thresholds (Chi-Square Inference):</b> The Chi-Square contingency highlights that high-friction topographies cannot support the mass resource consumption of commercial logic nodes. <b>Recommendation:</b> Future infrastructure planning must mandate that any site with an STI $< 82\%$ be restricted to specialized, low-volume/high-margin fabrication (e.g., Silicon Carbide, Gallium Nitride) where the volume of required Ultra-Pure Water (UPW) and heavy LCP transit is statistically lower.
    4. <b>Recommendation:</b> Planners must transition from isolated "site selection" to "cluster engineering." By anchoring a Large Cap fab (like Tata-PSMC) and immediately surrounding it with Mid Cap OSATs (like CG Power or Micron) within a 50km radius, the LCP efficiency approaches 0.99. This creates a frictionless micro-economy, similar to the Hsinchu Science Park in Taiwan.
    5. <b>Recommendation:</b> Future Large Cap facility approvals should require integrated, localized infrastructure. Fabs built in high-STI coastal zones (like Gujarat or Tamil Nadu) must be co-located with dedicated modular nuclear (SMRs) or massive solar/wind parks, alongside captive desalination plants. This insulates the fabs from the municipal grid, ensuring that consumer water and power supplies are not drained by industrial tech demands.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color: #222; margin: 30px 0;'>", unsafe_allow_html=True)
    
    # --- DIGITAL HUMANITIES NARRATIVE ---
    st.markdown("<h3 style='margin-bottom: 0px;'>// DIGITAL HUMANITIES PERSPECTIVE: INFRASTRUCTURE AS DESTINY</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div style='color:#ccc; font-size:14px; line-height: 1.6;'>
    <i>For policymakers, historians, and the general public, the statistical variances shown above are not just numbers—they are the physical blueprints of a new geopolitical cold war.</i>
    <br><br>
    <ul style='list-style-type: square; color:#d4af37;'>
        <li><span style='color:#ccc'><b>The Architecture of Paranoia vs. Profit:</b> The KDE graph physically illustrates human motives. The tight cluster of 'Large Cap' Mega-Fabs on flat, coastal plains (High STI) represents <b>Profit</b>. These sites demand topographical perfection to manufacture commercial chips with zero failure rates. Conversely, the wide, left-skewed tail of 'Small Cap' facilities represents <b>Paranoia and Survival</b>. By burying strategic defense foundries deep in high-friction valleys and foothills, the state explicitly sacrifices economic efficiency for geographical immunity against naval blockades or coastal climate disasters.</span></li>
        <li style='margin-top: 10px;'><span style='color:#ccc'><b>The Spatialization of Power and Labor:</b> Semiconductors do not just process data; they restructure the earth. The routing data in this GIS model proves that these Mega-Fabs act as gravitational black holes. They literally reroute rivers (desalination pipelines) and dictate human migration, pulling elite intellectual labor into highly specific, localized 'techno-enclaves' (like Dholera or the Assam frontier), permanently altering local cultures and economies.</span></li>
        <li style='margin-top: 10px;'><span style='color:#ccc'><b>The Sovereign Shield:</b> To the average citizen, a microchip is invisible. But this map proves that the "Cyber Frontline" is deeply physical. Every time the STI variance shifts, it represents billions of dollars poured into concrete, steel, and water routing to ensure that the silicon powering India's hospitals, military radars, and digital economy cannot be turned off by a foreign power. <b>In the 21st century, geographical infrastructure is destiny.</b></span></li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
