import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide", page_title="Cyber-Frontline 3D GIS")

# --- 1. DATASET WITH PRECISE RESOURCE COORDINATES ---
# w_lat/w_lon = Water Source | m_lat/m_lon = Material Source
data = [
    {
        "name": "TSMC Fab 18", "lat": 23.10, "lon": 120.28, "cap": "Large", "type": "Fab", "sti": 99.8, 
        "w_name": "Reservoir", "w_lat": 23.15, "w_lon": 120.40, 
        "m_name": "Kaohsiung Port", "m_lat": 22.62, "m_lon": 120.27,
        "desc": "Built on the flat Chianan Plain. Notice how flat the terrain is under the facility."
    },
    {
        "name": "Tata-TSAT Assam", "lat": 26.24, "lon": 92.33, "cap": "Large", "type": "ATMP", "sti": 84.4, 
        "w_name": "Brahmaputra River", "w_lat": 26.30, "w_lon": 92.45, 
        "m_name": "Haldia Port", "m_lat": 22.03, "m_lon": 88.06,
        "desc": "Surrounded by Himalayan foothills and river valleys. High terrain friction."
    },
    {
        "name": "Tata-PSMC Dholera", "lat": 22.25, "lon": 72.11, "cap": "Large", "type": "Mega-Fab", "sti": 99.5, 
        "w_name": "Desalination Plant", "w_lat": 22.15, "w_lon": 72.20, 
        "m_name": "Gulf of Khambhat", "m_lat": 21.75, "m_lon": 72.25,
        "desc": "Flat coastal plateau. The perfect geometric defense against seismic vibration."
    },
    {
        "name": "Intel Ocotillo", "lat": 33.27, "lon": -111.88, "cap": "Large", "type": "Fab", "sti": 88.0, 
        "w_name": "Recycled Water Plant", "w_lat": 33.30, "w_lon": -111.85, 
        "m_name": "Rail Link", "m_lat": 33.20, "m_lon": -111.95,
        "desc": "Arid, flat desert terrain functioning as a sovereign anchor node."
    },
    {
        "name": "SCL Mohali", "lat": 30.70, "lon": 76.69, "cap": "Small", "type": "Strategic", "sti": 75.0, 
        "w_name": "Sutlej River Basin", "w_lat": 30.80, "w_lon": 76.60, 
        "m_name": "Inland Rail", "m_lat": 30.50, "m_lon": 76.80,
        "desc": "Nestled near the foothills. State-run space/defense fab."
    }
]

df = pd.DataFrame(data)
df['color'] = df['cap'].map({'Large': [255, 30, 30, 255], 'Small': [50, 255, 100, 255]})

# --- 2. SIDEBAR CONTROLS ---
st.sidebar.title("🛡️ Cyber-Control Center")
st.sidebar.markdown("Select a facility to fly in and view the 3D topography and supply curves.")

selected_hub = st.sidebar.selectbox("🎯 Target Node:", ["Select a Hub..."] + list(df['name']))

# --- 3. DYNAMIC 3D CAMERA ---
# Default global view
view_state = pdk.ViewState(latitude=22, longitude=78, zoom=3, pitch=0, bearing=0)

if selected_hub != "Select a Hub...":
    hub = df[df['name'] == selected_hub].iloc[0]
    
    # ZOOM FIX: Zoom level 12 gets you close enough to see the facility as a building, not a continent.
    # PITCH FIX: 65 degrees looks "across" the landscape to reveal mountains.
    view_state = pdk.ViewState(
        latitude=hub['lat'], 
        longitude=hub['lon'], 
        zoom=12, 
        pitch=65, 
        bearing=25
    )
    
    # Technical Dossier
    st.sidebar.markdown(f"### 📑 Technical Dossier")
    st.sidebar.write(f"**Facility:** {hub['name']}")
    st.sidebar.write(f"**Classification:** {hub['cap']} Cap {hub['type']}")
    st.sidebar.write(f"**Strategic Topo Index (STI):** {hub['sti']}%")
    st.sidebar.write(f"**Water Source:** {hub['w_name']}")
    st.sidebar.write(f"**Material Source:** {hub['m_name']}")
    st.sidebar.info(hub['desc'])

# --- 4. THE 3D LAYERS ---

# 1. 3D Terrain Base (AWS Elevation + Esri Satellite)
terrain_layer = pdk.Layer(
    "TerrainLayer",
    elevation_decoder={"rScaler": 256, "gScaler": 1, "bScaler": 1/256, "offset": -32768},
    elevation_data="https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
    texture="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    elevation_scale=6, # Pops the mountains up perfectly
)

# 2. Facility Building (Properly Scaled)
facility_layer = pdk.Layer(
    "ColumnLayer",
    df,
    get_position=['lon', 'lat'],
    get_elevation=300, # Realistic 300m structure
    elevation_scale=1,
    radius=200, # SCALED DOWN: 200 meters wide, won't cover the whole map
    get_fill_color='color',
    pickable=True,
    auto_highlight=True,
)

# 3. Water Source Node & LCP Curve (Cyan)
water_node = pdk.Layer("ScatterplotLayer", df, get_position=['w_lon', 'w_lat'], get_radius=150, get_fill_color=[0, 255, 255])
water_arc = pdk.Layer(
    "ArcLayer",
    data=df,
    get_source_position=['w_lon', 'w_lat'],
    get_target_position=['lon', 'lat'],
    get_source_color=[0, 255, 255, 200], # Cyan
    get_target_color=[255, 30, 30, 200],
    get_width=5,
    tilt=15 # Gives it that 3D curve over the terrain
)

# 4. Material Source Node & LCP Curve (Black)
mat_node = pdk.Layer("ScatterplotLayer", df, get_position=['m_lon', 'm_lat'], get_radius=150, get_fill_color=[20, 20, 20])
mat_arc = pdk.Layer(
    "ArcLayer",
    data=df,
    get_source_position=['m_lon', 'm_lat'],
    get_target_position=['lon', 'lat'],
    get_source_color=[20, 20, 20, 255], # Black curve
    get_target_color=[255, 30, 30, 255],
    get_width=5,
    tilt=-15
)

# Render everything
st.pydeck_chart(pdk.Deck(
    layers=[terrain_layer, facility_layer, water_node, water_arc, mat_node, mat_arc],
    initial_view_state=view_state,
    map_style=None, 
    tooltip={"text": "{name}"}
))
