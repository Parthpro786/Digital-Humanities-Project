import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide", page_title="Cyber-Frontline: 3D Topo")

# --- 1. DATA: HUBS & RESOURCE NODES ---
hubs = [
    {"name": "Tata-PSMC Dholera", "lat": 22.25, "lon": 72.11, "type": "Mega-Fab", "elev": 15},
    {"name": "SCL Mohali", "lat": 30.70, "lon": 76.69, "type": "Strategic", "elev": 310},
    {"name": "Tata-TSAT Assam", "lat": 26.24, "lon": 92.33, "type": "ATMP", "elev": 55}
]
df = pd.DataFrame(hubs)

# --- 2. THE 3D TERRAIN ENGINE (VERTICAL EXAGGERATION) ---
st.sidebar.title("🛡️ Topographical Controls")
# This slider lets you manually pop the mountains out of the map
exaggeration = st.sidebar.slider("Vertical Exaggeration (3D Height)", 1, 15, 8)

selected_hub = st.sidebar.selectbox("🎯 Target Hub:", ["None"] + list(df['name']))

# Default View
view_state = pdk.ViewState(latitude=22, longitude=78, zoom=4, pitch=0, bearing=0)

if selected_hub != "None":
    hub = df[df['name'] == selected_hub].iloc[0]
    view_state = pdk.ViewState(
        latitude=hub['lat'], longitude=hub['lon'], 
        zoom=11, 
        pitch=75, # High pitch to look ACROSS the landscape
        bearing=45
    )

# THE TERRAIN LAYER: This is where the "Curves" happen
terrain_layer = pdk.Layer(
    "TerrainLayer",
    elevation_decoder={"rScaler": 256, "gScaler": 1, "bScaler": 1/256, "offset": -32768},
    elevation_data="https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
    texture="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    elevation_scale=exaggeration, # THE FIX: This stretches the valleys/plateaus
    mesh_max_error=1 # Lower = Higher detail for valleys
)

# Hub Marker
hub_layer = pdk.Layer(
    "ScatterplotLayer",
    df,
    get_position=['lon', 'lat'],
    get_color=[255, 0, 0],
    get_radius=500 if selected_hub != "None" else 50000,
    pickable=True
)

st.pydeck_chart(pdk.Deck(
    layers=[terrain_layer, hub_layer],
    initial_view_state=view_state,
    map_style=None, # Important: Let the terrain texture show
    tooltip={"text": "{name}"}
))

st.sidebar.markdown("""
**How to see the 3D curves:**
1. Select a Hub.
2. Use **Right-Click + Drag** to rotate the camera.
3. Increase the **Exaggeration slider** to make valleys deeper.
""")
