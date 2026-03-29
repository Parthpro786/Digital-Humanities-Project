import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide", page_title="Cyber-Frontline 3D")

# --- 1. DATASET (Small, Mid, Large Cap) ---
data = [
    {"name": "TSMC Fab 18", "lat": 23.10, "lon": 120.28, "cap": "Large", "type": "Fab", "region": "Global", "sti": 99.8, "lcp": 0.99, "water": "High-Pure (15km)", "mat": "Kaohsiung Port", "desc": "Flat alluvial plain. Ultimate vibration control."},
    {"name": "Intel Ocotillo", "lat": 33.27, "lon": -111.88, "cap": "Large", "type": "Fab", "region": "Global", "sti": 88.0, "lcp": 0.85, "water": "Arid-Recycled", "mat": "Rail Network", "desc": "Sovereign anchor node in stable desert terrain."},
    {"name": "Samsung Pyeongtaek", "lat": 37.01, "lon": 127.06, "cap": "Large", "type": "Fab", "region": "Global", "sti": 95.0, "lcp": 0.95, "water": "Piped Mains", "mat": "Incheon Port", "desc": "Massive cluster on engineered flatlands."},
    {"name": "Tata-PSMC Dholera", "lat": 22.25, "lon": 72.11, "cap": "Large", "type": "Mega-Fab", "region": "India", "year": 2024, "sti": 99.5, "lcp": 0.97, "water": "Desalination", "mat": "Gulf of Khambhat", "desc": "India's flagship commercial fab on a flat coastal plateau."},
    {"name": "Micron Sanand", "lat": 22.98, "lon": 72.37, "cap": "Large", "type": "ATMP", "region": "India", "year": 2023, "sti": 92.0, "lcp": 0.90, "water": "Narmada Canal", "mat": "Mundra Port", "desc": "Key global memory packaging node."},
    {"name": "Tata-TSAT Assam", "lat": 26.24, "lon": 92.33, "cap": "Large", "type": "ATMP", "region": "India", "year": 2025, "sti": 84.4, "lcp": 0.70, "water": "Brahmaputra", "mat": "Haldia Port", "desc": "River valley location; rugged logistics path."},
    {"name": "Kaynes Sanand", "lat": 22.95, "lon": 72.40, "cap": "Mid", "type": "OSAT", "region": "India", "year": 2024, "sti": 87.0, "lcp": 0.85, "water": "Recycled", "mat": "Local Supply", "desc": "Automotive chip specialization."},
    {"name": "HCL-Foxconn Jewar", "lat": 28.13, "lon": 77.55, "cap": "Mid", "type": "OSAT", "region": "India", "year": 2025, "sti": 91.0, "lcp": 0.91, "water": "Yamuna Linked", "mat": "Air Cargo", "desc": "Strategic airport-adjacent facility."},
    {"name": "SCL Mohali", "lat": 30.70, "lon": 76.69, "cap": "Small", "type": "Strategic", "region": "India", "year": 1990, "sti": 75.0, "lcp": 0.65, "water": "Sutlej Basin", "mat": "Inland Rail", "desc": "Himalayan foothills. State-run defense/space chip fab."},
    {"name": "Tower-Adani Taloja", "lat": 19.06, "lon": 73.07, "cap": "Large", "type": "Fab", "region": "India", "year": 2026, "sti": 93.8, "lcp": 0.94, "water": "Coastal Piped", "mat": "JNPT Port", "desc": "Massive analog/power fab near western coast."}
]

df = pd.DataFrame(data)
# Colors: Large = Red, Mid = Yellow, Small = Green
df['color'] = df['cap'].map({'Large': [255, 50, 50, 255], 'Mid': [255, 200, 0, 255], 'Small': [50, 255, 100, 255]})

# --- 2. SIDEBAR CONTROLS & POPUP ---
st.sidebar.title("🛡️ Cyber-Control Center")

view_mode = st.sidebar.radio("View Perspective", ["Global Overview", "India Timeline"])
if view_mode == "India Timeline":
    current_year = st.sidebar.slider("Select Year", 1990, 2026, 2026)
    active_df = df[(df['region'] == 'India') & (df['year'] <= current_year)]
else:
    active_df = df[df['region'] == 'Global']

selected_hub = st.sidebar.selectbox("🎯 Target Node (Fly-to 3D):", ["None"] + list(active_df['name']))

# --- 3. DYNAMIC 3D CAMERA ---
# Default high-altitude view
view_state = pdk.ViewState(latitude=22, longitude=78, zoom=4, pitch=0, bearing=0)

if selected_hub != "None":
    hub = active_df[active_df['name'] == selected_hub].iloc[0]
    # "Fly-to" effect: zooms in and tilts 60 degrees to show mountains/valleys
    view_state = pdk.ViewState(
        latitude=hub['lat'], 
        longitude=hub['lon'], 
        zoom=11, 
        pitch=60, 
        bearing=30
    )
    
    # The Side Popup with Technical Details
    st.sidebar.markdown(f"### 📑 Technical Dossier: {selected_hub}")
    st.sidebar.write(f"**Classification:** {hub['cap']} Cap {hub['type']}")
    st.sidebar.write(f"**Strategic Topo Index (STI):** {hub['sti']}%")
    st.sidebar.write(f"**Least Cost Path (LCP):** {hub['lcp']}")
    st.sidebar.write(f"**Water Source:** {hub['water']}")
    st.sidebar.write(f"**Material Route:** {hub['mat']}")
    st.sidebar.info(hub['desc'])

# --- 4. THE 3D GOOGLE EARTH ENGINE ---

# Layer 1: True 3D Topographical Texture (No tokens required)
# This creates the actual mountains and valleys using AWS elevation data and Esri satellite images.
terrain_layer = pdk.Layer(
    "TerrainLayer",
    elevation_decoder={"rScaler": 256, "gScaler": 1, "bScaler": 1/256, "offset": -32768},
    elevation_data="https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
    texture="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    elevation_scale=8, # Exaggerates the Z-axis so valleys and plateaus are highly visible
)

# Layer 2: The Semiconductor Facilities (Glowing Pillars)
# Using ColumnLayer so the buildings stand up vertically from the 3D terrain
node_layer = pdk.Layer(
    "ColumnLayer",
    active_df,
    get_position=['lon', 'lat'],
    get_elevation=500, # Height of the building marker
    elevation_scale=5,
    radius=1500 if selected_hub != "None" else 40000, # Scales down when you zoom in
    get_fill_color='color',
    pickable=True,
    auto_highlight=True,
)

# Render the Map
st.pydeck_chart(pdk.Deck(
    layers=[terrain_layer, node_layer],
    initial_view_state=view_state,
    map_style=None, # Setting to None forces it to use the satellite texture instead of a blank Mapbox style
    tooltip={"html": "<b>{name}</b><br/>{cap} Cap {type}", "style": {"color": "white"}}
))
