import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide", page_title="Cyber-Frontline 3D GIS")

# --- 1. CUSTOM 3D BUILDING GEOMETRY GENERATORS ---
# These functions draw the actual 3D footprints of the factories

def get_t_shape(lon, lat, scale=0.003):
    """Generates a massive 'T' shaped building footprint for TATA"""
    return [[
        [lon - scale, lat + scale], [lon + scale, lat + scale], # Top bar
        [lon + scale, lat + scale/3], [lon + scale/3, lat + scale/3],
        [lon + scale/3, lat - scale], [lon - scale/3, lat - scale], # Stem
        [lon - scale/3, lat + scale/3], [lon - scale, lat + scale/3]
    ]]

def get_h_shape(lon, lat, scale=0.003):
    """Generates an 'H' shaped mega-complex for TSMC/Intel"""
    return [[
        [lon-scale, lat+scale], [lon-scale/3, lat+scale], [lon-scale/3, lat+scale/3], 
        [lon+scale/3, lat+scale/3], [lon+scale/3, lat+scale], [lon+scale, lat+scale], 
        [lon+scale, lat-scale], [lon+scale/3, lat-scale], [lon+scale/3, lat-scale/3], 
        [lon-scale/3, lat-scale/3], [lon-scale/3, lat-scale], [lon-scale, lat-scale]
    ]]

# --- 2. DATASET: DRAPED PATHS AND 3D BUILDINGS ---
data = [
    {
        "name": "Tata-TSAT Assam", "lat": 26.24, "lon": 92.33, "cap": "Large", "type": "ATMP", "sti": 84.4, 
        "w_name": "Brahmaputra", "m_name": "Haldia Port",
        "building_shape": get_t_shape(92.33, 26.24), # TATA "T" Shape
        "building_color": [255, 50, 50],
        # Paths follow the ground (interpolated points for draping)
        "water_path": [[92.45, 26.30], [92.40, 26.28], [92.36, 26.26], [92.33, 26.24]], 
        "mat_path": [[88.06, 22.03], [90.00, 24.00], [91.50, 25.50], [92.33, 26.24]],
        "desc": "Observe the 'T' shaped facility in the river valley. The paths crawl through the lowest terrain points."
    },
    {
        "name": "TSMC Fab 18", "lat": 23.10, "lon": 120.28, "cap": "Large", "type": "Fab", "sti": 99.8, 
        "w_name": "Reservoir", "m_name": "Kaohsiung Port",
        "building_shape": get_h_shape(120.28, 23.10), # TSMC "H" Complex
        "building_color": [50, 100, 255],
        "water_path": [[120.40, 23.15], [120.35, 23.12], [120.28, 23.10]], 
        "mat_path": [[120.27, 22.62], [120.28, 22.80], [120.28, 23.10]],
        "desc": "Massive 'H' complex on the flat Chianan Plain. The imprinted paths are perfectly straight due to zero terrain friction."
    },
    {
        "name": "Tata-PSMC Dholera", "lat": 22.25, "lon": 72.11, "cap": "Large", "type": "Mega-Fab", "sti": 99.5, 
        "w_name": "Desalination", "m_name": "Gulf of Khambhat",
        "building_shape": get_t_shape(72.11, 22.25), # TATA "T" Shape
        "building_color": [255, 50, 50],
        "water_path": [[72.20, 22.15], [72.15, 22.20], [72.11, 22.25]], 
        "mat_path": [[72.25, 21.75], [72.20, 22.00], [72.11, 22.25]],
        "desc": "Flat coastal plateau. The perfect geometric defense against seismic vibration."
    }
]

df = pd.DataFrame(data)

# --- 3. UI CONTROLS ---
st.sidebar.title("🛡️ Cyber-Control Center")
st.sidebar.markdown("Select a hub to fly in and analyze the topographical imprint.")

selected_hub = st.sidebar.selectbox("🎯 Target Node:", ["Select a Hub..."] + list(df['name']))

view_state = pdk.ViewState(latitude=22, longitude=78, zoom=4, pitch=0, bearing=0)

if selected_hub != "Select a Hub...":
    hub = df[df['name'] == selected_hub].iloc[0]
    
    # Aggressive Zoom and Pitch to see the 3D Buildings and Mountains
    view_state = pdk.ViewState(
        latitude=hub['lat'], 
        longitude=hub['lon'], 
        zoom=13.5,  # Much closer to see the building shape
        pitch=75,   # Highly angled to see the terrain exaggeration
        bearing=45
    )
    
    st.sidebar.markdown(f"### 📑 Technical Dossier")
    st.sidebar.write(f"**Facility:** {hub['name']}")
    st.sidebar.write(f"**Strategic Topo Index (STI):** {hub['sti']}%")
    st.sidebar.write(f"**Water Source:** {hub['w_name']}")
    st.sidebar.write(f"**Material Source:** {hub['m_name']}")
    st.sidebar.info(hub['desc'])

# --- 4. THE 3D LAYERS ---

# 1. EXAGGERATED TERRAIN
terrain_layer = pdk.Layer(
    "TerrainLayer",
    elevation_decoder={"rScaler": 256, "gScaler": 1, "bScaler": 1/256, "offset": -32768},
    elevation_data="https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
    texture="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    elevation_scale=12, # MASSIVE EXAGGERATION: Mountains will look huge
)

# 2. CUSTOM 3D BUILDINGS (T-Shapes & H-Shapes)
building_layer = pdk.Layer(
    "PolygonLayer",
    df,
    get_polygon="building_shape",
    extruded=True,
    get_elevation=150, # 150 meters tall
    get_fill_color="building_color",
    wireframe=True,
    pickable=True,
    auto_highlight=True,
)

# 3. IMPRINTED WATER LCP (Cyan Line on the ground)
water_path = pdk.Layer(
    "PathLayer",
    df,
    get_path="water_path",
    get_color=[0, 255, 255, 255], # Cyan
    width_scale=20,
    width_min_pixels=4,
    cap_rounded=True,
    joint_rounded=True,
)

# 4. IMPRINTED MATERIAL LCP (Black/Dark Grey Line on the ground)
mat_path = pdk.Layer(
    "PathLayer",
    df,
    get_path="mat_path",
    get_color=[20, 20, 20, 255], # Thick Black
    width_scale=20,
    width_min_pixels=4,
    cap_rounded=True,
    joint_rounded=True,
)

# Render
st.pydeck_chart(pdk.Deck(
    layers=[terrain_layer, building_layer, water_path, mat_path],
    initial_view_state=view_state,
    map_style=None, 
    tooltip={"text": "{name}"}
))
