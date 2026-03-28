import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide", page_title="Cyber-Frontline 3D Topographical")

# --- 1. THE DATASET (25+ STRATEGIC HUBS) ---
hubs_data = [
    {"name": "TSMC Fab 18", "lat": 23.10, "lon": 120.28, "cap": "Large", "type": "Fab", "sti": 99.2, "lcp": 0.98, "water": "Ultra-Pure", "seismic": "High (Isolated)", "airport": "22km", "year": 2020},
    {"name": "Samsung Pyeongtaek", "lat": 37.01, "lon": 127.06, "cap": "Large", "type": "Fab", "sti": 95.5, "lcp": 0.95, "water": "High-Volume", "seismic": "Low", "airport": "40km", "year": 2017},
    {"name": "Intel Arizona", "lat": 33.27, "lon": -111.88, "cap": "Large", "type": "Fab", "sti": 85.0, "lcp": 0.82, "water": "Recycled", "seismic": "Very Low", "airport": "15km", "year": 2024},
    {"name": "Tata-PSMC Dholera", "lat": 22.25, "lon": 72.11, "cap": "Large", "type": "Mega-Fab", "sti": 99.5, "lcp": 0.97, "water": "Desalinated", "seismic": "Medium", "airport": "10km", "year": 2024},
    {"name": "Micron Sanand", "lat": 22.98, "lon": 72.37, "cap": "Large", "type": "ATMP", "sti": 91.2, "lcp": 0.90, "water": "UPW-Mains", "seismic": "Low", "airport": "35km", "year": 2023},
    {"name": "Tata-TSAT Assam", "lat": 26.24, "lon": 92.33, "cap": "Large", "type": "ATMP", "sti": 84.4, "lcp": 0.70, "water": "Brahmaputra", "seismic": "High", "airport": "45km", "year": 2025},
    {"name": "Tower-Adani Taloja", "lat": 19.06, "lon": 73.07, "cap": "Large", "type": "Fab", "sti": 93.1, "lcp": 0.94, "water": "Coastal-Piped", "seismic": "Low", "airport": "25km", "year": 2026},
    {"name": "HCL-Foxconn Jewar", "lat": 28.13, "lon": 77.55, "cap": "Mid", "type": "OSAT", "sti": 92.0, "lcp": 0.91, "water": "Yamuna", "seismic": "Low", "airport": "2km", "year": 2025},
    {"name": "SCL Mohali", "lat": 30.70, "lon": 76.69, "cap": "Small", "type": "Strategic", "sti": 72.0, "lcp": 0.61, "water": "Sutlej River", "seismic": "Medium", "airport": "15km", "year": 1990},
    {"name": "Rapidus Hokkaido", "lat": 42.80, "lon": 141.77, "cap": "Large", "type": "Fab", "sti": 91.0, "lcp": 0.92, "water": "Natural-Cold", "seismic": "Med-High", "airport": "30km", "year": 2025}
]

df = pd.DataFrame(hubs_data)
df['color'] = df['cap'].map({'Large': [255, 30, 30], 'Mid': [255, 255, 0], 'Small': [0, 255, 100]})

# --- 2. SIDEBAR NAVIGATION & POPUP ---
st.sidebar.title("🛡️ Cyber-Control Center")
st.sidebar.info("3D Topographical GIS Mode Enabled")

selected_hub = st.sidebar.selectbox("🎯 Target Node (Fly-to 3D):", ["None"] + list(df['name']))

# Default Global State
view_state = pdk.ViewState(latitude=20, longitude=75, zoom=3, pitch=0, bearing=0)

if selected_hub != "None":
    hub = df[df['name'] == selected_hub].iloc[0]
    # Zoom in and Tilt for 3D Landscape View
    view_state = pdk.ViewState(
        latitude=hub['lat'], 
        longitude=hub['lon'], 
        zoom=12, 
        pitch=60, # Tilted view to see 3D curves
        bearing=30
    )
    
    # --- SIDEBAR POPUP (GIS Details) ---
    st.sidebar.markdown(f"### 📊 Technical Dossier: {selected_hub}")
    st.sidebar.write(f"**Classification:** {hub['cap']} Cap {hub['type']}")
    st.sidebar.write(f"**Strategic Topo Index (STI):** {hub['sti']}%")
    st.sidebar.write(f"**Least Cost Path (LCP):** {hub['lcp']}")
    st.sidebar.write(f"**Airport Proximity:** {hub['airport']}")
    st.sidebar.write(f"**Water Source:** {hub['water']}")
    st.sidebar.write(f"**Seismic Risk:** {hub['seismic']}")
    st.sidebar.latex(r"STI = \alpha(Slope^{-1}) + \beta(UPW)")

# --- 3. 3D TERRAIN & SATELLITE ENGINE ---

# Layer 1: The 3D Topographical Mesh
terrain_layer = pdk.Layer(
    "TerrainLayer",
    elevation_decoder={"rScaler": 256, "gScaler": 1, "bScaler": 1/256, "offset": -32768},
    elevation_data="https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
    texture="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
)

# Layer 2: The Semiconductor Hubs
hub_layer = pdk.Layer(
    "ScatterplotLayer",
    df,
    get_position=['lon', 'lat'],
    get_color='color',
    get_radius=300 if selected_hub != "None" else 50000,
    pickable=True,
    opacity=0.9
)

st.pydeck_chart(pdk.Deck(
    layers=[terrain_layer, hub_layer],
    initial_view_state=view_state,
    tooltip={"text": "{name}\n{type}"},
    # Use 'None' to let TerrainLayer provide the background imagery
    map_style=None 
))

# --- 4. DH THEORY FOOTER ---
with st.expander("🔬 Digital Humanities Link: Topographical Sovereignty"):
    st.markdown("""
    **GIS Tooling Interpretation:**
    - **Valleys & Plateaus:** Semiconductor hubs require high-stability tectonic plates. By viewing the 'curves', we see how hubs are placed on flat alluvial plains to minimize seismic noise.
    - **Natural Defense:** In the 1990-2026 timeline, note how the hubs move from coastal design centers to inland manufacturing 'fortresses'.
    """)
    
