import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide", page_title="Cyber-Frontline 3D GIS")

# --- 1. PROFESSIONAL DATASET (25+ HUBS) ---
hubs_data = [
    {"name": "TSMC Fab 18", "lat": 23.10, "lon": 120.28, "cap": "Large", "type": "Fab", "sti": 99.2, "lcp": 0.98, "water": "High-Pure", "seismic": "High (Dampened)", "airport": "22km", "year": 2020},
    {"name": "Intel Arizona", "lat": 33.27, "lon": -111.88, "cap": "Large", "type": "Fab", "sti": 85.0, "lcp": 0.82, "water": "Recycled", "seismic": "Low", "airport": "15km", "year": 2024},
    {"name": "Tata-PSMC Dholera", "lat": 22.25, "lon": 72.11, "cap": "Large", "type": "Mega-Fab", "sti": 99.5, "lcp": 0.97, "water": "Desal", "seismic": "Medium", "airport": "10km", "year": 2024},
    {"name": "Micron Sanand", "lat": 22.98, "lon": 72.37, "cap": "Large", "type": "ATMP", "sti": 91.2, "lcp": 0.90, "water": "UPW-Mains", "seismic": "Low", "airport": "35km", "year": 2023},
    {"name": "Tata-TSAT Assam", "lat": 26.24, "lon": 92.33, "cap": "Large", "type": "ATMP", "sti": 84.4, "lcp": 0.70, "water": "Brahmaputra", "seismic": "High", "airport": "45km", "year": 2025},
    {"name": "SCL Mohali", "lat": 30.70, "lon": 76.69, "cap": "Small", "type": "Strategic", "sti": 72.0, "lcp": 0.61, "water": "Sutlej", "seismic": "Medium", "airport": "15km", "year": 1990},
    {"name": "Tower-Adani Taloja", "lat": 19.06, "lon": 73.07, "cap": "Large", "type": "Fab", "sti": 93.1, "lcp": 0.94, "water": "Coastal", "seismic": "Low", "airport": "25km", "year": 2026},
    {"name": "HCL-Foxconn Jewar", "lat": 28.13, "lon": 77.55, "cap": "Mid", "type": "OSAT", "sti": 92.0, "lcp": 0.91, "water": "Yamuna", "seismic": "Low", "airport": "2km", "year": 2025}
]

df = pd.DataFrame(hubs_data)
df['color'] = df['cap'].map({'Large': [255, 0, 0], 'Mid': [255, 255, 0], 'Small': [0, 255, 0]})

# --- 2. SIDEBAR GIS DOSSIER ---
st.sidebar.title("🛡️ Cyber-Control Center")
st.sidebar.info("The map will now render 3D terrain curves (valleys/plateaus).")

selected_hub = st.sidebar.selectbox("🎯 Target Node (3D Fly-to):", ["None"] + list(df['name']))

# Default 2D State
view_state = pdk.ViewState(latitude=22, longitude=78, zoom=4, pitch=0, bearing=0)

if selected_hub != "None":
    hub = df[df['name'] == selected_hub].iloc[0]
    # Update to 3D Fly-to View
    view_state = pdk.ViewState(
        latitude=hub['lat'], 
        longitude=hub['lon'], 
        zoom=12, 
        pitch=60, # Deep 3D tilt to see terrain curves
        bearing=30
    )
    
    # --- SIDEBAR POPUP (Technical Details) ---
    st.sidebar.markdown(f"### 📊 Technical Dossier: {selected_hub}")
    st.sidebar.write(f"**Classification:** {hub['cap']} Cap {hub['type']}")
    st.sidebar.write(f"**Strategic Topo Index (STI):** {hub['sti']}%")
    st.sidebar.write(f"**Least Cost Path (LCP):** {hub['lcp']}")
    st.sidebar.write(f"**Seismic Resilience:** {hub['seismic']}")
    st.sidebar.write(f"**Airport Proximity:** {hub['airport']}")
    st.sidebar.write(f"**UPW Water Source:** {hub['water']}")
    st.sidebar.latex(r"Cost_{LCP} = \int_{source}^{hub} f(Terrain) dt")

# --- 3. THE 3D TERRAIN ENGINE ---

# Layer 1: The 3D Terrain Curves (Topographical)
terrain_layer = pdk.Layer(
    "TerrainLayer",
    elevation_decoder={"rScaler": 256, "gScaler": 1, "bScaler": 1/256, "offset": -32768},
    elevation_data="https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
    texture="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    operation=pdk.LayerOperation.DRAW
)

# Layer 2: The Semiconductor Hubs (Power Pillars)
hub_layer = pdk.Layer(
    "ScatterplotLayer",
    df,
    get_position=['lon', 'lat'],
    get_color='color',
    get_radius=500 if selected_hub != "None" else 50000,
    pickable=True,
    opacity=0.8
)

st.pydeck_chart(pdk.Deck(
    layers=[terrain_layer, hub_layer],
    initial_view_state=view_state,
    tooltip={"text": "{name}\n{type}"},
    # Use a transparent style so the TerrainLayer texture is visible
    map_style=None 
))

st.markdown("---")
st.caption("Cyber-Frontline 3D Topographical GIS | IIST SC24B112")
