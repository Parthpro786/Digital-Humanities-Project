import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

# --- 1. PROFESSIONAL PAGE CONFIG & CSS ---
st.set_page_config(layout="wide", page_title="Cyber-Frontline GIS", page_icon="🗺️")

# Custom CSS to make it look sleek and not like a generic Streamlit app
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 1.5rem; padding-bottom: 0rem;}
        .stTabs [data-baseweb="tab-list"] {gap: 24px;}
        .stTabs [data-baseweb="tab"] {height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 4px; padding: 0 16px; font-weight: 600;}
        .st-emotion-cache-1v0mbdj > img {border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);}
        h1, h2, h3 {font-family: 'Helvetica Neue', sans-serif;}
    </style>
""", unsafe_allow_html=True)

# --- 2. BEZIER CURVE LOGIC (For smooth supply routes) ---
def generate_curve(start, end, bend=0.2):
    p0, p2 = np.array(start), np.array(end)
    mid = (p0 + p2) / 2
    perp = np.array([-(p2[1]-p0[1]), p2[0]-p0[0]]) 
    p1 = mid + perp * bend
    t = np.linspace(0, 1, 30)
    curve = np.outer((1-t)**2, p0) + np.outer(2*(1-t)*t, p1) + np.outer(t**2, p2)
    return curve.tolist()

# --- 3. THE MASTER DATASET ---
data = [
    # 2000 Era
    {"name": "Texas Instruments Bangalore", "region": "India", "year": 2000, "cap": "Large", "lat": 12.97, "lon": 77.59, "elev": "920m", "terrain": "Deccan Plateau", "w_name": "Cauvery Basin", "w_lat": 12.40, "w_lon": 77.30, "w_dist": "85km", "m_name": "HAL Transit", "m_lat": 12.95, "m_lon": 77.66, "m_dist": "12km", "bt": "First Global R&D Center in India", "img": "https://images.unsplash.com/photo-1517077304055-6e89abbf09b0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", "profile": [850, 870, 890, 920, 920, 915, 900]},
    {"name": "SCL Mohali", "region": "India", "year": 2000, "cap": "Small", "lat": 30.70, "lon": 76.69, "elev": "310m", "terrain": "Shivalik Foothills", "w_name": "Sutlej River", "w_lat": 30.90, "w_lon": 76.50, "w_dist": "28km", "m_name": "Rail Link", "m_lat": 30.50, "m_lon": 76.80, "m_dist": "24km", "bt": "ISRO Strategic Radiation-Hardened Wafers", "img": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", "profile": [280, 295, 310, 310, 325, 350, 380]},
    
    # 2010 Era
    {"name": "Intel R&D Bangalore", "region": "India", "year": 2010, "cap": "Large", "lat": 12.93, "lon": 77.68, "elev": "900m", "terrain": "Deccan Plateau", "w_name": "Cauvery Pipelines", "w_lat": 12.45, "w_lon": 77.35, "w_dist": "80km", "m_name": "Airport Cargo", "m_lat": 13.20, "m_lon": 77.70, "m_dist": "40km", "bt": "Core Processor Architecture Design", "img": "https://images.unsplash.com/photo-1555664424-778a1e5e1b48?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", "profile": [860, 880, 900, 900, 900, 890, 880]},
    
    # 2026 Era (Modern Fabs)
    {"name": "Tata-PSMC Dholera", "region": "India", "year": 2026, "cap": "Large", "lat": 22.25, "lon": 72.11, "elev": "15m", "terrain": "Coastal Plateau", "w_name": "Sabarmati Desalination", "w_lat": 22.50, "w_lon": 72.30, "w_dist": "32km", "m_name": "Gulf of Khambhat Port", "m_lat": 21.75, "m_lon": 72.25, "m_dist": "55km", "bt": "India's First Commercial 28nm Mega-Fab", "img": "https://images.unsplash.com/photo-1573164713988-8665fc963095?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", "profile": [0, 5, 12, 15, 15, 15, 12]},
    {"name": "Tata-TSAT Assam", "region": "India", "year": 2026, "cap": "Large", "lat": 26.24, "lon": 92.33, "elev": "55m", "terrain": "River Valley", "w_name": "Brahmaputra Basin", "w_lat": 26.50, "w_lon": 92.60, "w_dist": "40km", "m_name": "Haldia Port Transit", "m_lat": 25.50, "m_lon": 91.00, "m_dist": "180km", "bt": "Advanced Packaging Sovereign Hub", "img": "https://images.unsplash.com/photo-1537498425277-c283d32ef9db?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", "profile": [120, 85, 55, 55, 65, 90, 110]},
    {"name": "Kaynes Sanand", "region": "India", "year": 2026, "cap": "Mid", "lat": 22.95, "lon": 72.40, "elev": "40m", "terrain": "Industrial Plains", "w_name": "Narmada Canal Hub", "w_lat": 23.10, "w_lon": 72.50, "w_dist": "20km", "m_name": "Regional Rail Freight", "m_lat": 22.80, "m_lon": 72.20, "m_dist": "25km", "bt": "Automotive Power Module OSAT", "img": "https://images.unsplash.com/photo-1563770660941-20978e870e26?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", "profile": [35, 38, 40, 40, 40, 39, 37]},
    
    # Global Benchmark
    {"name": "TSMC Fab 18", "region": "Global", "year": 2020, "cap": "Large", "lat": 23.10, "lon": 120.28, "elev": "12m", "terrain": "Chianan Plain", "w_name": "Southern Reservoir", "w_lat": 23.30, "w_lon": 120.50, "w_dist": "30km", "m_name": "Kaohsiung Port", "m_lat": 22.62, "m_lon": 120.27, "m_dist": "53km", "bt": "Global 3nm Logic Node Production", "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", "profile": [2, 5, 10, 12, 12, 12, 10]}
]

df = pd.DataFrame(data)

# High-Quality Location Pin Marker Configuration
ICON_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-atlas.png"
icon_data = {"url": ICON_URL, "width": 128, "height": 128, "y": 128, "anchorY": 128}
df['icon_data'] = [icon_data for _ in range(len(df))]

# Color coding
def get_color(cap):
    if cap == "Large": return [255, 60, 60]  # Red
    if cap == "Mid": return [255, 200, 50]   # Yellow
    return [50, 220, 100]                    # Green
df['color'] = df['cap'].apply(get_color)


# --- 4. TOP BAR UI ---
st.title("🛡️ Cyber-Frontline: Strategic Topography")
tab_india, tab_world = st.tabs(["🇮🇳 INDIA TIMELINE ANALYSIS", "🌍 GLOBAL ECOSYSTEM"])

# State Tracking for Selected Node
selected_node = st.selectbox("🎯 Search / Select Semiconductor Hub:", ["Select a facility..."] + list(df['name']))

# Determine active dataset based on tab
with tab_india:
    selected_year = st.select_slider("Select Timeline Era:", options=[2000, 2010, 2020, 2026], value=2026)
    active_df = df[(df['region'] == 'India') & (df['year'] <= selected_year)]
with tab_world:
    if selected_node == "Select a facility...":
        active_df = df[df['region'] == 'Global']

# --- 5. THE 70/30 SPLIT LAYOUT ---
col_map, col_panel = st.columns([7, 3], gap="large")

with col_map:
    # Set Map View
    if selected_node != "Select a facility...":
        hub = df[df['name'] == selected_node].iloc[0]
        view_state = pdk.ViewState(latitude=hub['lat'], longitude=hub['lon'], zoom=8, pitch=0)
        render_df = df[df['name'] == selected_node]
    else:
        view_state = pdk.ViewState(latitude=22, longitude=78, zoom=4, pitch=0)
        render_df = active_df

    layers = []
    
    # Base Nodes (Location Tags)
    layers.append(pdk.Layer(
        "IconLayer", render_df, get_icon="icon_data", get_size=4, size_scale=12,
        get_position=["lon", "lat"], get_color="color", pickable=True
    ))

    # --- DYNAMIC ROUTING (Only shows when a node is selected) ---
    if selected_node != "Select a facility...":
        fac_coord = [hub['lon'], hub['lat']]
        w_coord = [hub['w_lon'], hub['w_lat']]
        m_coord = [hub['m_lon'], hub['m_lat']]
        
        # Supply Curves
        route_data = [
            {"path": generate_curve(w_coord, fac_coord, bend=0.15), "color": [0, 200, 255]}, # Water = Cyan
            {"path": generate_curve(m_coord, fac_coord, bend=-0.2), "color": [255, 255, 255]} # Material = White
        ]
        layers.append(pdk.Layer(
            "PathLayer", pd.DataFrame(route_data), get_path="path", get_color="color",
            width_scale=20, width_min_pixels=3, get_dash_array=[10, 15], dash_justified=True
        ))
        
        # Resource Nodes (Light Blue = Water, White = Material)
        res_data = [
            {"name": hub['w_name'], "lon": hub['w_lon'], "lat": hub['w_lat'], "color": [0, 200, 255]},
            {"name": hub['m_name'], "lon": hub['m_lon'], "lat": hub['m_lat'], "color": [255, 255, 255]}
        ]
        layers.append(pdk.Layer(
            "ScatterplotLayer", pd.DataFrame(res_data), get_position=["lon", "lat"],
            get_fill_color="color", get_radius=3000, stroked=True, get_line_color=[0, 0, 0]
        ))

    # Render Map
    st.pydeck_chart(pdk.Deck(
        layers=layers, initial_view_state=view_state,
        map_style='mapbox://styles/mapbox/dark-v10',
        tooltip={"text": "{name}"}
    ))
    st.markdown("📍 **Red:** Large Cap | **Yellow:** Mid Cap | **Green:** Small Cap | 💧 **Cyan:** Water Source | ⚪ **White:** Raw Material")

# --- 6. RIGHT HUD: GOOGLE MAPS STYLE PANEL ---
with col_panel:
    if selected_node == "Select a facility...":
        st.info("👆 Select a facility from the map or dropdown to view its Technical Dossier.")
    else:
        # Hero Image (Uses high-quality industrial placeholders to look real)
        st.image(hub['img'], use_container_width=True)
        
        st.header(hub['name'])
        st.markdown(f"**Classification:** `{hub['cap']} Cap`  |  **Established:** `{hub['year']}`")
        st.success(f"**Breakthrough:** {hub['bt']}")
        
        st.markdown("---")
        
        # Graphical Terrain Profile
        st.subheader("🏔️ Discretized Elevation Profile")
        chart_data = pd.DataFrame(hub['profile'], columns=["Elevation (MSL)"])
        # Customizing the area chart to look smooth and professional
        st.area_chart(chart_data, height=180, color="#2563eb")
        st.caption(f"**Terrain Type:** {hub['terrain']} | **Facility Elevation:** {hub['elev']}")
        
        st.markdown("---")
        
        # Supply Routes & Distances
        st.subheader("⚙️ Logistics Infrastructure")
        st.markdown(f"💧 **Water Hub:** {hub['w_name']}<br><span style='color:gray; font-size:14px'>└─ Distance: {hub['w_dist']} (Dotted Cyan Route)</span>", unsafe_allow_html=True)
        st.markdown(f"📦 **Raw Materials:** {hub['m_name']}<br><span style='color:gray; font-size:14px'>└─ Distance: {hub['m_dist']} (Dotted White Route)</span>", unsafe_allow_html=True)
