import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide", page_title="Cyber-Frontline 2026")

# --- 1. DATASET: 25+ HUBS ---
hubs_data = [
    {"name": "TSMC Fab 18", "lat": 23.10, "lon": 120.28, "cap": "Large", "type": "Fab", "sti": 99.2, "lcp": 0.98, "water": "High-Pure", "grid": "99.9%", "labor": "High", "year": 2020},
    {"name": "Samsung Pyeongtaek", "lat": 37.01, "lon": 127.06, "cap": "Large", "type": "Fab", "sti": 95.5, "lcp": 0.95, "water": "High-Pure", "grid": "99.8%", "labor": "High", "year": 2017},
    {"name": "Intel Arizona", "lat": 33.27, "lon": -111.88, "cap": "Large", "type": "Fab", "sti": 85.0, "lcp": 0.82, "water": "Recycled", "grid": "98.5%", "labor": "Medium", "year": 2024},
    {"name": "Tata-PSMC Dholera", "lat": 22.25, "lon": 72.11, "cap": "Large", "type": "Mega-Fab", "sti": 99.5, "lcp": 0.97, "water": "Desal", "grid": "99.9%", "labor": "High", "year": 2024},
    {"name": "Micron Sanand", "lat": 22.98, "lon": 72.37, "cap": "Large", "type": "ATMP", "sti": 91.2, "lcp": 0.90, "water": "UPW-Mains", "grid": "99.0%", "labor": "Medium", "year": 2023},
    {"name": "Kaynes Sanand", "lat": 22.95, "lon": 72.40, "cap": "Mid", "type": "OSAT", "sti": 86.5, "lcp": 0.85, "water": "Recycled", "grid": "97.5%", "labor": "Medium", "year": 2024},
    {"name": "HCL-Foxconn Jewar", "lat": 28.13, "lon": 77.55, "cap": "Mid", "type": "OSAT", "sti": 92.0, "lcp": 0.91, "water": "River", "grid": "96.5%", "labor": "High", "year": 2025},
    {"name": "Tower-Adani Taloja", "lat": 19.06, "lon": 73.07, "cap": "Large", "type": "Fab", "sti": 93.1, "lcp": 0.94, "water": "Coastal", "grid": "98.8%", "labor": "High", "year": 2026},
    {"name": "SCL Mohali", "lat": 30.70, "lon": 76.69, "cap": "Small", "type": "Strategic", "sti": 72.0, "lcp": 0.61, "water": "Sutlej", "grid": "95.0%", "labor": "Low", "year": 1990},
]

df = pd.DataFrame(hubs_data)
df['color'] = df['cap'].map({'Large': [255, 0, 0, 200], 'Mid': [255, 255, 0, 200], 'Small': [0, 255, 0, 200]})

# --- 2. SIDEBAR & NAVIGATION ---
st.sidebar.title("🛡️ Cyber-Control Center")
st.sidebar.info("Select a Hub to trigger the 3D Fly-to and view GIS details.")

view_mode = st.sidebar.radio("View Perspective", ["Global Overview", "Timeline Explorer"])
selected_hub = st.sidebar.selectbox("🎯 Target Node (Fly-to):", ["None"] + list(df['name']))

# --- 3. DYNAMIC CAMERA LOGIC ---
# Default Global 2D View
initial_view = pdk.ViewState(latitude=20, longitude=75, zoom=3, pitch=0, bearing=0)

if selected_hub != "None":
    hub = df[df['name'] == selected_hub].iloc[0]
    # Update View to 3D Zoomed-in
    initial_view = pdk.ViewState(
        latitude=hub['lat'], 
        longitude=hub['lon'], 
        zoom=14, 
        pitch=50, # 3D Angle
        bearing=20
    )
    
    # --- SIDE POPUP (Sidebar Details) ---
    st.sidebar.markdown(f"### 📊 Technical Dossier: {selected_hub}")
    st.sidebar.write(f"**Classification:** {hub['cap']} Cap {hub['type']}")
    st.sidebar.write(f"**Strategic Topo Index (STI):** {hub['sti']}%")
    st.sidebar.write(f"**Least Cost Path (LCP):** {hub['lcp']}")
    st.sidebar.write(f"**Water Source:** {hub['water']}")
    st.sidebar.write(f"**Grid Stability:** {hub['grid']}")
    st.sidebar.write(f"**Labor Proximity:** {hub['labor']}")
    st.sidebar.latex(r"Cost_{LCP} = \int f(terrain, logistics) dt")

# --- 4. THE NO-TOKEN PYDECK MAP ---
layer = pdk.Layer(
    "ColumnLayer",
    df if view_mode == "Global Overview" else df[df['year'] <= st.sidebar.slider("Year", 1990, 2026, 2026)],
    get_position=['lon', 'lat'],
    get_elevation=500,
    elevation_scale=5,
    radius=30000 if selected_hub == "None" else 200,
    get_fill_color='color',
    pickable=True,
    auto_highlight=True,
)

st.pydeck_chart(pdk.Deck(
    # FIX: Use CartoDB Style (Does not require Mapbox token)
    map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
    initial_view_state=initial_view,
    layers=[layer],
    tooltip={"text": "{name}\n{type} ({cap} Cap)"}
))

st.markdown("---")
st.caption("Cyber-Frontline GIS Dashboard | IIST DH Project | SC24B112")
