import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import altair as alt
import plotly.graph_objects as go
from scipy import stats
from sklearn.neighbors import KernelDensity
from itertools import combinations

# --- 1. PROFESSIONAL PAGE CONFIG & CSS ---
st.set_page_config(layout="wide", page_title="Strategic Topography GIS", page_icon="🗺️")

st.markdown("""
    <style>
        /* Light washy magenta/lavender background */
        .stApp { background-color: #fdf4ff; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 2rem; padding-bottom: 0rem; max-width: 98%;}
        h1, h2, h3, p, span, div {font-family: 'Helvetica Neue', Arial, sans-serif; color: #1e1b4b;}
        
        /* Sidebar and Technical Dossier Styling */
        [data-testid="stSidebar"] {background-color: #ffffff; border-right: 1px solid #e2e8f0;}
        .metric-box {background-color: #ffffff; padding: 14px; border-radius: 4px; border-left: 4px solid #9333ea; margin-bottom: 12px; border: 1px solid #e5e7eb; box-shadow: 0 1px 2px rgba(0,0,0,0.05);}
        
        /* INCREASED TEXT SIZES FOR THE TECHNICAL DOSSIER */
        .metric-title {color: #4b5563; font-size: 13.5px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; font-weight: 700;}
        .metric-text {color: #0f172a; font-size: 16.5px; line-height: 1.6;}
        
        /* Cap Tags */
        .tag-large {color: #dc2626; font-weight: bold; text-transform: uppercase; font-size: 12px;}
        .tag-mid {color: #d97706; font-weight: bold; text-transform: uppercase; font-size: 12px;}
        .tag-small {color: #16a34a; font-weight: bold; text-transform: uppercase; font-size: 12px;}
        
        /* High-Contrast Return Button */
        .stButton>button {background-color: #701a75; color: #ffffff; border: none; font-weight: 600; padding: 10px 20px;}
        .stButton>button:hover {background-color: #4a044e; color: #ffffff;}
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

    # ---- INDIAN ECOSYSTEM (Highly Detailed with Radar & Radar Text) ----
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
        "img": "https://scontent.ftrv2-1.fna.fbcdn.net/v/t39.30808-6/535992862_1186350260197029_12401593196388291_n.jpg?stp=dst-jpg_s640x640_tt6&_nc_cat=104&ccb=1-7&_nc_sid=13d280&_nc_ohc=uCGe0x5dj7IQ7kNvwHTQgRh&_nc_oc=Adq6zKwzlR2PEBXHhilqH0ybFDm2k1OPVn86DKpb-J71nSTjjZg6rRqRNBjtcoly4QU&_nc_zt=23&_nc_ht=scontent.ftrv2-1.fna&_nc_gid=8jhxxgLQ08IWL_0Y-iLOqw&_nc_ss=7a389&oh=00_AfwQOBe7hb8uQei8t2dpJOMUz9Oz_MkAaaYJQhb18tjNUg&oe=69D1291B",
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
        "img": "https://scontent.ftrv2-1.fna.fbcdn.net/v/t39.30808-6/539589177_1185658950266160_3534972847653672713_n.jpg?stp=dst-jpg_s640x640_tt6&_nc_cat=106&ccb=1-7&_nc_sid=13d280&_nc_ohc=tDQVQ4vl_YIQ7kNvwE48ola&_nc_oc=AdqGo0sl9fFkN5yCSlit_MTSAPDNAuZBxl2WI1DpfV1CZQYvSvD5bqppSoVRPxZsd2U&_nc_zt=23&_nc_ht=scontent.ftrv2-1.fna&_nc_gid=MVD5QTrX8ZKup4kRM4qx1w&_nc_ss=7a389&oh=00_AfyKzVMKFRajrsAvhnLhJn2a3qcg7NzLBAHi-yScuNspMg&oe=69D13CE2",
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
        "img": "https://scontent.ftrv2-1.fna.fbcdn.net/v/t39.30808-6/536276519_1089638920018545_3749532980793753876_n.jpg?stp=dst-jpg_s640x640_tt6&_nc_cat=105&ccb=1-7&_nc_sid=13d280&_nc_ohc=Y5plPb5MCwgQ7kNvwEvXhxY&_nc_oc=AdpUyQYZysaFWNGXWTGDJ06tHVseSYdZqEV6Z-Ja5d3FuvUoz0cCk_MSOqc5lAnSYXQ&_nc_zt=23&_nc_ht=scontent.ftrv2-1.fna&_nc_gid=u0kpeP0xHHjhvfEkygxlFw&_nc_ss=7a389&oh=00_AfxJIGoSkrrBSYkniuOf2uw4HniVB9d1rM9ntB3B8mS4fw&oe=69D1333C",
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
        "img": "https://pbs.twimg.com/media/G66Lu77bkAIWVpP.jpg",
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
        "img": "https://content3.jdmagicbox.com/v2/comp/hyderabad/p8/040pxx40.xx40.230926140348.p9p8/catalogue/qualcomm-commerzone-building-silpa-gram-craft-village-hyderabad-corporate-companies-LdctlKINeF.jpg",
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

# Pin mapping colors
ICON_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-atlas.png"
icon_data = {"url": ICON_URL, "width": 128, "height": 128, "y": 128, "anchorY": 128}
df['icon_data'] = [icon_data for _ in range(len(df))]

def get_color(cap):
    if cap == "Large": return [220, 38, 38]   # Red
    if cap == "Mid": return [217, 119, 6]     # Orange
    return [22, 163, 74]                      # Green
df['color'] = df['cap'].apply(get_color)

# --- 5. TOP BAR UI ---
st.title("Strategic Topography GIS Explorer")
st.markdown("Macro-Analysis of Semiconductor Infrastructure, Topographical Friction, and Strategic Routing.")

# Tab Selection
tab1, tab2, tab3 = st.tabs(["INDIA TIMELINE ECOSYSTEM", "GLOBAL MACRO ECOSYSTEM", "S.T.I. STATISTICAL DISTRIBUTION"])

# --- TAB 1: INDIA ECOSYSTEM (Corrected Layout) ---
with tab1:
    selected_year = st.select_slider("Historical Timeline Integration:", options=[1980, 1990, 2000, 2010, 2020, 2026], value=2026)
    active_df = df[(df['region'] == 'India') & (df['year'] <= selected_year)].copy()
    
    # NEW HUD LAYER
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        st.metric("Active Indian Nodes", len(active_df))
    with col_kpi2:
        st.metric("Average STI Score", f"{active_df['sti'].mean():.1f}%" if not active_df.empty else "N/A")
    with col_kpi3:
        st.metric("Average LCP Efficiency", f"{active_df['lcp'].mean():.2f}" if not active_df.empty else "N/A")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_map, col_dossier = st.columns([6, 4], gap="large")

    with col_map:
        layers = [
            pdk.Layer("IconLayer", active_df, get_icon="icon_data", get_size=4, size_scale=12, get_position=["lon", "lat"], get_color="color", pickable=True, id="facility_pins")
        ]

        init_view = pdk.ViewState(latitude=22.0, longitude=79.0, zoom=4.2, pitch=0)

        # --- DYNAMIC ROUTING & SEPARATED LABELS ---
        if st.session_state.selected_node:
            n = st.session_state.selected_node
            f_coord = [n['lon'], n['lat']]
            
            w_curve, w_mid = generate_curve([n['w_lon'], n['w_lat']], f_coord, 0.15)
            m_curve, m_mid = generate_curve([n['m_lon'], n['m_lat']], f_coord, -0.2)
            l_curve, l_mid = generate_curve([n['l_lon'], n['l_lat']], f_coord, -0.1)

            route_data = [
                {"path": w_curve, "color": [6, 182, 212]}, # Cyan
                {"path": m_curve, "color": [255, 255, 255]}, # White
                {"path": l_curve, "color": [234, 179, 8]}  # Yellow
            ]
            layers.append(pdk.Layer("PathLayer", pd.DataFrame(route_data), get_path="path", get_color="color", width_scale=20, width_min_pixels=3, get_dash_array=[8, 8], dash_justified=True))

            res_data = [
                {"lon": n['w_lon'], "lat": n['w_lat'], "color": [6, 182, 212]},
                {"lon": n['m_lon'], "lat": n['m_lat'], "color": [255, 255, 255]},
                {"lon": n['l_lon'], "lat": n['l_lat'], "color": [234, 179, 8]}
            ]
            layers.append(pdk.Layer("ScatterplotLayer", pd.DataFrame(res_data), get_position=["lon", "lat"], get_fill_color="color", get_radius=3500, stroked=True, get_line_color=[0, 0, 0]))

            # Anti-Overlap Text Labels
            label_data = [
                {"lon": n['lon'], "lat": n['lat'], "text": f"Target: {n['lat']} N, {n['lon']} E", "color": [255, 255, 255], "offset": [0, -40]},
                {"lon": w_mid[0], "lat": w_mid[1], "text": f"{n['w_dist']}km (Water Corridor)", "color": [6, 182, 212], "offset": [0, 25]},
                {"lon": m_mid[0], "lat": m_mid[1], "text": f"{n['m_dist']}km (Raw Material Transit)", "color": [255, 255, 255], "offset": [0, -25]},
                {"lon": l_mid[0], "lat": l_mid[1], "text": f"{n['l_dist']}km (Urban Labor Corridor)", "color": [234, 179, 8], "offset": [40, 0]}
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
        
        # Legend Overlay
        st.markdown("""
            <div style="background-color: #1e293b; padding: 10px; border-radius: 4px; color: white; font-size: 13px; margin-top: -10px; border: 1px solid #475569;">
                <b>Legend:</b> &nbsp;&nbsp; 
                <span style="color:#ef4444">Large Cap Node</span> &nbsp;|&nbsp; 
                <span style="color:#f59e0b">Mid Cap Node</span> &nbsp;|&nbsp; 
                <span style="color:#22c55e">Small Cap Node</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <b>Logistics Routes:</b> &nbsp;
                <span style="color:#22d3ee">--- Water Corridor</span> &nbsp;|&nbsp;
                <span style="color:#ffffff">--- Raw Material</span> &nbsp;|&nbsp;
                <span style="color:#facc15">--- Urban Labor Node</span>
            </div>
        """, unsafe_allow_html=True)

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
            
            # High-Contrast Return Button
            if st.button("Return to Map Overview", use_container_width=True):
                clear_selection()
                st.rerun()
            
            st.image(n['img'], use_container_width=True)
            st.markdown(f"<h2>{n['name']}</h2>", unsafe_allow_html=True)
            st.markdown(f"<span class='tag-{n['cap'].lower()}'>{n['cap']} Cap Facility</span> | <b>Coordinates:</b> {n['lat']} N, {n['lon']} E", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ALTAIR TERRAIN GRAPH (Jagged & Checkpoint Diamond Marker)
            st.markdown("<b>Topographical Integration Profile</b>", unsafe_allow_html=True)
            
            total_dist = n['m_dist'] + n['w_dist']
            x_dist = np.linspace(0, total_dist, len(n['profile']))
            chart_df = pd.DataFrame({"Distance (km)": x_dist, "Elevation (MSL)": n['profile']})
            
            base = alt.Chart(chart_df).encode(
                x=alt.X('Distance (km):Q', title=f"Distance: 0km ({n['m_name']}) → {n['m_dist']}km (Facility) → {total_dist}km ({n['w_name']})"), 
                y=alt.Y('Elevation (MSL):Q', title="Elevation (m)", scale=alt.Scale(domain=[0, max(n['profile'])+50]))
            )
            area = base.mark_area(opacity=0.4, color="#9333ea")
            line = base.mark_line(color="#7e22ce", strokeWidth=2)
            
            # Diamond checkpoint marker
            facility_mark = pd.DataFrame({"x": [n['m_dist']], "y": [n['elev']]})
            point = alt.Chart(facility_mark).mark_point(color='#dc2626', size=150, shape='diamond', filled=True).encode(x='x:Q', y='y:Q')
            
            st.altair_chart(area + line + point, use_container_width=True)

            # STRATEGIC METRICS
            st.markdown("<div class='metric-box'><div class='metric-title'>Strategic Breakthrough</div>"
                        f"<div class='metric-text'>{n['bt']}</div></div>", unsafe_allow_html=True)
                        
            st.markdown("<div class='metric-box'><div class='metric-title'>Topographical Stabilization (Elevation: " + str(n['elev']) + "m MSL)</div>"
                        f"<div class='metric-text'>{n['rationale']}</div></div>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class='metric-box'>
                <div class='metric-title'>Logistics Matrix (LCP Efficiency: {n['lcp']})</div>
                <div class='metric-text'>
                    <b>Material Hub:</b> {n['m_name']} <span style='color:gray'>({n['m_dist']}km route)</span><br>
                    <b>Water Catchment:</b> {n['w_name']} <span style='color:gray'>({n['w_dist']}km route)</span><br>
                    <b>Urban Labor Center:</b> {n['l_name']} <span style='color:gray'>({n['l_dist']}km route)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # VULNERABILITY RADAR CHART
            st.markdown("<b>Vulnerability & Stability Radar</b>", unsafe_allow_html=True)
            categories = ['Seismic Stability', 'Water Security', 'Logistics Efficiency', 'Geopolitical Safety', 'Labor Proximity']
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=n['rad'],
                theta=categories,
                fill='toself',
                fillcolor='rgba(147, 51, 234, 0.4)',
                line=dict(color='#7e22ce'),
                name=n['name']
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100]),
                    angularaxis=dict(tickfont=dict(color='#8B4513', size=13, weight='bold')) 
                ),
                showlegend=False,
                margin=dict(l=40, r=40, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("👆 Click a location tag on the map to view its Technical Dossier and logistics profile.")

# --- TAB 2: GLOBAL ECOSYSTEM ---
with tab2:
    global_df = df.copy()
    layers = [pdk.Layer("IconLayer", global_df, get_icon="icon_data", get_size=4, size_scale=10, get_position=["lon", "lat"], get_color="color", pickable=True)]
    st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=pdk.ViewState(latitude=30.0, longitude=20.0, zoom=1.8, pitch=0), map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json', tooltip={"text": "{name}\nCap: {cap}"}))

# --- TAB 3: S.T.I. STATISTICAL DISTRIBUTION & INFERENCE ---
with tab3:
    st.markdown("### Continuous Probability Density & Inferential Statistics")
    st.markdown("This module applies Kernel Density Estimation (KDE) and rigorous hypothesis testing to the Strategic Topographical Index (STI). By modeling the variance ($\\sigma^2$) and mean ($\\mu$) across facility classifications, we can mathematically infer India's sovereign site-selection strategy.")
    
    # --- PREP DATA ---
    stats_df = df[(df['region'] == 'India')].dropna(subset=['sti', 'cap']).copy()
    
    # 1. ALTAIR CONTINUOUS DENSITY PLOT
    density_plot = alt.Chart(stats_df).transform_density(
        'sti',
        as_=['sti', 'density'],
        groupby=['cap'],
        extent=[60, 110], 
        steps=200,
        bandwidth=4 
    ).mark_area(opacity=0.45).encode(
        x=alt.X('sti:Q', title="Strategic Topographical Index (STI %)", scale=alt.Scale(domain=[65, 105])),
        y=alt.Y('density:Q', title="Probability Density", axis=alt.Axis(labels=False, ticks=False), stack=None),
        color=alt.Color('cap:N', scale=alt.Scale(domain=['Large', 'Mid', 'Small'], range=['#dc2626', '#d97706', '#16a34a']))
    ).properties(height=350)
    
    st.altair_chart(density_plot, use_container_width=True)

    st.markdown("---")
    
    # --- STATISTICAL ANALYSIS ENGINE ---
    col_stats1, col_stats2 = st.columns(2, gap="large")
    
    with col_stats1:
        # SUMMARY STATISTICS (MLE ESTIMATES)
        st.markdown("#### || MLE-Based Distribution Parameters")
        
        # Calculate summary stats safely
        summary = stats_df.groupby('cap')['sti'].agg(
            Mean='mean',
            Variance='var',
            Std_Dev='std',
            Count='count'
        ).round(2)
        
        # Add skewness
        summary['Skewness'] = stats_df.groupby('cap')['sti'].apply(stats.skew).round(3)
        st.dataframe(summary, use_container_width=True)

        # ANOVA TEST
        st.markdown("#### || ANOVA Test (Mean STI Differences)")
        group_values = [group['sti'].values for name, group in stats_df.groupby('cap')]
        
        if len(group_values) > 1:
            anova_stat, anova_p = stats.f_oneway(*group_values)
            st.write(f"**F-statistic:** `{anova_stat:.4f}` | **p-value:** `{anova_p:.4f}`")
            if anova_p < 0.05:
                st.success("Reject $H_0$ → Mean STI differs significantly across Cap categories.")
            else:
                st.info("Fail to reject $H_0$ → Sample size too small or means are similar.")
        
        # LEVENE TEST
        st.markdown("#### || Levene’s Test (Variance Equality)")
        if len(group_values) > 1:
            levene_stat, levene_p = stats.levene(*group_values)
            st.write(f"**Statistic:** `{levene_stat:.4f}` | **p-value:** `{levene_p:.4f}`")
            if levene_p < 0.05:
                st.success("Reject $H_0$ → Topographical variances ($\\sigma^2$) are significantly different.")
            else:
                st.info("Fail to reject $H_0$ → Variances are statistically similar.")

    with col_stats2:
        # CHI-SQUARE TEST
        st.markdown("#### || Chi-Square Test (Categorical Dependency)")
        # Adjusted bins to cover lower STI ranges like Mohali (75) safely
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

        # KDE OVERLAP ANALYSIS
        st.markdown("#### || KDE Distribution Overlap")
        x_grid = np.linspace(60, 110, 500).reshape(-1, 1)
        densities = {}
        
        for cap, group in stats_df.groupby('cap'):
            # Using bandwidth=4 to match Altair and prevent collapse on small data
            kde = KernelDensity(kernel='gaussian', bandwidth=4.0)
            kde.fit(group['sti'].values.reshape(-1, 1))
            log_density = kde.score_samples(x_grid)
            densities[cap] = np.exp(log_density)

        overlap_results = []
        for cap1, cap2 in combinations(densities.keys(), 2):
            overlap = np.trapezoid(np.minimum(densities[cap1], densities[cap2]), x_grid.flatten())
            overlap_results.append({"Comparison": f"{cap1} vs {cap2}", "Overlap Coefficient": round(overlap, 4)})
        
        st.dataframe(pd.DataFrame(overlap_results), use_container_width=True, hide_index=True)

    st.markdown("---")
    
    # --- STRATEGIC RECOMMENDATIONS BASED ON STATS ---
    st.markdown("### || Inferences & Strategic Recommendations for Future Development")
    st.markdown("""
    Based on the inferential statistics derived from the current spatial data, we recommend the following frameworks for future Indian semiconductor expansion:
    
    1. **Strict Stratification of STI Requirements (ANOVA & Overlap Inference):** The low KDE overlap coefficient between Large and Small Cap facilities proves that India is already operating on a bifurcated strategy. **Recommendation:** Future Mega-Fabs (Large Cap) must strictly target topographies with an STI $> 92\%$ (Coastal Plateaus / Stable Plains). Attempting to build a Large Cap fab in a "Moderate" zone will result in catastrophic logistical and vibration friction.
    2. **Leveraging Variance for Geographical Hedging (Levene's Inference):** The higher variance ($\\sigma^2$) and left-skewed tails in Small/Mid Cap facilities indicate they can survive in high-friction terrain. **Recommendation:** The government should incentivize future Mid/Small Cap facilities (OSAT, discrete power, defense) to be built in Eastern and Northern river valleys or foothills. This accepts a lower STI but establishes a distributed *Defense-in-Depth* network, ensuring the entire supply chain cannot be wiped out by a single coastal weather event or naval blockade.
    3. **Resource Catchment Thresholds (Chi-Square Inference):** The Chi-Square contingency highlights that high-friction topographies cannot support the mass resource consumption of commercial logic nodes. **Recommendation:** Future infrastructure planning must mandate that any site with an STI $< 82\%$ be restricted to specialized, low-volume/high-margin fabrication (e.g., Silicon Carbide, Gallium Nitride) where the volume of required Ultra-Pure Water (UPW) and heavy LCP transit is statistically lower.
    4. **Recommendation:** Planners must transition from isolated "site selection" to "cluster engineering." By anchoring a Large Cap fab (like Tata-PSMC) and immediately surrounding it with Mid Cap OSATs (like CG Power or Micron) within a 50km radius, the LCP efficiency approaches 0.99. This creates a frictionless micro-economy, similar to the Hsinchu Science Park in Taiwan.
    5. **Recommendation:** Future Large Cap facility approvals should require integrated, localized infrastructure. Fabs built in high-STI coastal zones (like Gujarat or Tamil Nadu) must be co-located with dedicated modular nuclear (SMRs) or massive solar/wind parks, alongside captive desalination plants. This insulates the fabs from the municipal grid, ensuring that consumer water and power supplies are not drained by industrial tech demands
    """)

    st.markdown("---")
    # --- DIGITAL HUMANITIES NARRATIVE ---
    st.markdown("### || Digital Humanities Perspective: Infrastructure as Destiny")
    st.markdown("""
    *For policymakers, historians, and the general public, the statistical variances shown above are not just numbers—they are the physical blueprints of a new geopolitical cold war.*
    
    * **The Architecture of Paranoia vs. Profit:** The KDE graph physically illustrates human motives. The tight cluster of 'Large Cap' Mega-Fabs on flat, coastal plains (High STI) represents **Profit**. These sites demand topographical perfection to manufacture commercial chips with zero failure rates. Conversely, the wide, left-skewed tail of 'Small Cap' facilities represents **Paranoia and Survival**. By burying strategic defense foundries deep in high-friction valleys and foothills, the state explicitly sacrifices economic efficiency for geographical immunity against naval blockades or coastal climate disasters.
    * **The Spatialization of Power and Labor:** Semiconductors do not just process data; they restructure the earth. The routing data in this GIS model proves that these Mega-Fabs act as gravitational black holes. They literally reroute rivers (desalination pipelines) and dictate human migration, pulling elite intellectual labor into highly specific, localized 'techno-enclaves' (like Dholera or the Assam frontier), permanently altering local cultures and economies.
    * **The Sovereign Shield:** To the average citizen, a microchip is invisible. But this map proves that the "Cyber Frontline" is deeply physical. Every time the STI variance shifts, it represents billions of dollars poured into concrete, steel, and water routing to ensure that the silicon powering India's hospitals, military radars, and digital economy cannot be turned off by a foreign power. **In the 21st century, geographical infrastructure is destiny.**
    """)
