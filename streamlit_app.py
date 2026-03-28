import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide", page_title="Cyber-Frontline GIS")

# --- 1. THE DATASET (25+ STRATEGIC HUBS) ---
hubs = [
    # GLOBAL LEADERS
    {"name": "TSMC Fab 18", "lat": 23.10, "lon": 120.28, "cap": "Large", "type": "Fab", "sti": 99.2, "lcp": 0.98, "water": "High-Pure", "vibe": "Choke-Point"},
    {"name": "Samsung Pyeongtaek", "lat": 37.01, "lon": 127.06, "cap": "Large", "type": "Fab", "sti": 95.5, "lcp": 0.95, "water": "Industrial", "vibe": "Cluster-Lead"},
    {"name": "Intel Ocotillo", "lat": 33.27, "lon": -111.88, "cap": "Large", "type": "Fab", "sti": 85.0, "lcp": 0.82, "water": "Recycled", "vibe": "Sovereign-Base"},
    
    # INDIA EVOLUTION (1990-2026)
    {"name": "SCL Mohali", "lat": 30.70, "lon": 76.69, "cap": "Small", "type": "Strategic", "year": 1990, "sti": 72.0, "lcp": 0.61, "water": "River", "vibe": "Heritage-Node"},
    {"name": "Tata-PSMC Dholera", "lat": 22.25, "lon": 72.11, "cap": "Large", "type": "Mega-Fab", "year": 2024, "sti": 99.5, "lcp": 0.97, "water": "Desal", "vibe": "New-Frontier"},
    {"name": "Micron Sanand", "lat": 22.98, "lon": 72.37, "cap": "Large", "type": "ATMP", "year": 2023, "sti": 91.2, "lcp": 0.90, "water": "UPW-Mains", "vibe": "Memory-Hub"},
    {"name": "Kaynes Sanand", "lat": 22.95, "lon": 72.40, "cap": "Mid", "type": "OSAT", "year": 2024, "sti": 86.5, "lcp": 0.85, "water": "Recycled", "vibe": "Auto-Specialist"},
    {"name": "HCL-Foxconn Jewar", "lat": 28.13, "lon": 77.55, "cap": "Mid", "type": "OSAT", "year": 2025, "sti": 92.0, "lcp": 0.91, "water": "Yamuna", "vibe": "Logistics-Link"},
    {"name": "Tower-Adani Taloja", "lat": 19.06, "lon": 73.07, "cap": "Large", "type": "Fab", "year": 2026, "sti": 93.1, "lcp": 0.94, "water": "Coastal", "vibe": "Analog-Core"}
]

df = pd.DataFrame(hubs)

# --- 2. SIDEBAR CONTROLS (THE "POPUP" LOGIC) ---
st.sidebar.title("🛡️ Cyber-Control Center")
st.sidebar.markdown("---")

view_mode = st.sidebar.radio("Navigation View", ["2D Global Overview", "3D India Timeline"])
selected_hub = st.sidebar.selectbox("🎯 Target Hub (Fly-to 3D):", ["None"] + [h['name'] for h in hubs])

# Color Mapping
df['color'] = df['cap'].map({'Large': [255, 30, 30, 200], 'Mid': [255, 255, 0, 200], 'Small': [0, 255, 120, 200]})

# --- 3. 3D DYNAMIC VIEWSTATE ---
# Default 2D
initial_lat, initial_lon, initial_zoom, initial_pitch = 20.0, 70.0, 2, 0

if selected_hub != "None":
    hub_info = df[df['name'] == selected_hub].iloc[0]
    initial_lat, initial_lon, initial_zoom, initial_pitch = hub_info['lat'], hub_info['lon'], 14, 50
    
    # THE SIDE POPUP (Inside the Sidebar when a hub is clicked)
    st.sidebar.success(f"**TECHNICAL DOSSIER: {selected_hub}**")
    st.sidebar.write(f"**Classification:** {hub_info['cap']} Cap {hub_info['type']}")
    st.sidebar.write(f"**Strategic Topo Index (STI):** {hub_info['sti']}%")
    st.sidebar.write(f"**Least Cost Path (LCP):** {hub_info['lcp']}")
    st.sidebar.write(f"**UPW Water Source:** {hub_info['water']}")
    st.sidebar.write(f"**Geopolitical Role:** {hub_info['vibe']}")
    st.sidebar.markdown("---")
    st.sidebar.latex(r"STI = \alpha(Slope^{-1}) + \beta(H_{2}O)")

# --- 4. THE PYDECK ENGINE ---
# ColumnLayer provides the 3D "Power Pillars"
layer = pdk.Layer(
    "ColumnLayer",
    df if view_mode == "2D Global Overview" else df[df['year'].notnull()],
    get_position=['lon', 'lat'],
    get_elevation=500,
    elevation_scale=100 if selected_hub == "None" else 5, # Flattens when zoomed in
    radius=30000 if selected_hub == "None" else 200,
    get_fill_color='color',
    pickable=True,
    auto_highlight=True,
)

view_state = pdk.ViewState(
    latitude=initial_lat,
    longitude=initial_lon,
    zoom=initial_zoom,
    pitch=initial_pitch,
    bearing=10 if selected_hub != "None" else 0
)

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    initial_view_state=view_state,
    layers=[layer],
    tooltip={"text": "{name}\n{type} ({cap} Cap)"}
))

# --- 5. DH THEORY FOOTER ---
with st.expander("🔬 DH Methodology: Infrastructure as War"):
    st.write("This map visualizes the **Cyber Frontline**. Red pillars represent 'Large Cap' sovereign nodes—territories that are more valuable than oil fields in 2026.")
