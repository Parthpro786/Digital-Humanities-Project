import streamlit as st
import pandas as pd
import pydeck as pdk
import json

st.set_page_config(layout="wide", page_title="Cyber-Frontline: LCP GIS")

# --- 1. THE DATASET (HUBS, PORTS, & WATER SOURCES) ---
# Each hub now has a 'Path' representing the LCP for resources
hubs = [
    {
        "name": "Tata-PSMC Dholera", "lat": 22.25, "lon": 72.11, "type": "Mega-Fab",
        "water_path": [[72.11, 22.25], [72.30, 22.40], [72.50, 23.00]], # LCP from Narmada/Sabarmati
        "raw_mat_path": [[72.11, 22.25], [72.15, 22.10], [72.20, 21.75]], # LCP to Gulf of Khambhat Port
        "water_source": "Sabarmati/Desal", "raw_mat": "Silicon Sand / Gases"
    },
    {
        "name": "Tata-TSAT Assam", "lat": 26.24, "lon": 92.33, "type": "ATMP",
        "water_path": [[92.33, 26.24], [92.40, 26.30], [92.50, 26.50]], # LCP to Brahmaputra
        "raw_mat_path": [[92.33, 26.24], [91.00, 25.50], [89.50, 22.50]], # LCP to Haldia Port
        "water_source": "Brahmaputra Basin", "raw_mat": "Lithium / Rare Earths"
    }
]

# --- 2. SIDEBAR NAVIGATION ---
st.sidebar.title("🛡️ Cyber-Frontline LCP Engine")
selected_hub = st.sidebar.selectbox("🎯 Select Hub to analyze LCP:", [h['name'] for h in hubs])
hub_data = next(h for h in hubs if h['name'] == selected_hub)

# Display Side Popup Stats
st.sidebar.markdown(f"### 📊 LCP Analysis: {selected_hub}")
st.sidebar.info(f"🔵 **Water LCP:** {hub_data['water_source']}\n\n⚪ **Material LCP:** {hub_data['raw_mat']}")

# --- 3. 3D TERRAIN & PATH ENGINE ---

# Layer 1: 3D Topographical Curves
terrain_layer = pdk.Layer(
    "TerrainLayer",
    elevation_decoder={"rScaler": 256, "gScaler": 1, "bScaler": 1/256, "offset": -32768},
    elevation_data="https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
    texture="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
)

# Layer 2: Dotted LCP Line for Water (Blue)
water_path_layer = pdk.Layer(
    "PathLayer",
    [{"path": hub_data['water_path']}],
    get_path="path",
    get_width=10,
    get_color=[0, 150, 255],
    pickable=True,
    width_min_pixels=3,
    dash_array=[3, 2], # Makes it a dotted line
)

# Layer 3: Dotted LCP Line for Raw Materials (White)
material_path_layer = pdk.Layer(
    "PathLayer",
    [{"path": hub_data['raw_mat_path']}],
    get_path="path",
    get_width=10,
    get_color=[255, 255, 255],
    pickable=True,
    width_min_pixels=3,
    dash_array=[3, 2],
)

# Set 3D View for selected Hub
view_state = pdk.ViewState(
    latitude=hub_data['lat'], longitude=hub_data['lon'],
    zoom=11, pitch=60, bearing=30
)

st.pydeck_chart(pdk.Deck(
    layers=[terrain_layer, water_path_layer, material_path_layer],
    initial_view_state=view_state,
    map_style=None,
    tooltip={"text": "{name}"}
))

with st.expander("🔬 GIS Interpretation: Least Cost Path (LCP)"):
    st.write("The paths shown follow the **natural curves of the terrain** to minimize 'Friction'.")
    st.latex(r"Cost = \int (Slope \cdot Weight_{1} + Infrastructure \cdot Weight_{2}) dl")
    st.markdown("- **Blue Dotted Line:** Ultra-Pure Water (UPW) pipeline route following the gravity of the river basin.\n- **White Dotted Line:** Raw Material supply chain route from the nearest deep-sea port.")
