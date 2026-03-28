import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide", page_title="Cyber-Frontline 2026")

# --- 1. DATASET: 25+ HUBS (Large, Mid, Small Cap) ---
hubs = [
    # GLOBAL
    {"name": "TSMC Fab 18", "lat": 23.10, "lon": 120.28, "cap": "Large", "type": "Fab", "sti": 99.1, "lcp": 0.98, "elev": 500},
    {"name": "Samsung Pyeongtaek", "lat": 37.01, "lon": 127.06, "cap": "Large", "type": "Fab", "sti": 95.2, "lcp": 0.95, "elev": 450},
    {"name": "Intel Ocotillo", "lat": 33.27, "lon": -111.88, "cap": "Large", "type": "Fab", "sti": 82.0, "lcp": 0.85, "elev": 400},
    {"name": "ASML Veldhoven", "lat": 51.42, "lon": 5.40, "cap": "Large", "type": "Lithography", "sti": 98.5, "lcp": 0.99, "elev": 600},
    
    # INDIA TIMELINE
    {"name": "SCL Mohali", "lat": 30.70, "lon": 76.69, "cap": "Small", "type": "Strategic", "year": 1990, "sti": 75.0, "lcp": 0.60, "elev": 100},
    {"name": "TI Bangalore", "lat": 12.97, "lon": 77.59, "cap": "Mid", "type": "Design", "year": 1995, "sti": 82.1, "lcp": 0.75, "elev": 250},
    {"name": "Micron Sanand", "lat": 22.98, "lon": 72.37, "cap": "Large", "type": "ATMP", "year": 2023, "sti": 92.0, "lcp": 0.92, "elev": 350},
    {"name": "Tata-PSMC Dholera", "lat": 22.25, "lon": 72.11, "cap": "Large", "type": "Mega-Fab", "year": 2024, "sti": 99.5, "lcp": 0.98, "elev": 550},
    {"name": "CG Power Sanand", "lat": 22.95, "lon": 72.40, "cap": "Mid", "type": "ATMP", "year": 2024, "sti": 87.5, "lcp": 0.88, "elev": 300},
    {"name": "Kaynes Sanand", "lat": 22.99, "lon": 72.38, "cap": "Mid", "type": "OSAT", "year": 2024, "sti": 88.0, "lcp": 0.86, "elev": 300},
    {"name": "Tata-TSAT Assam", "lat": 26.24, "lon": 92.33, "cap": "Large", "type": "ATMP", "year": 2025, "sti": 84.4, "lcp": 0.70, "elev": 450},
    {"name": "HCL-Foxconn Jewar", "lat": 28.13, "lon": 77.55, "cap": "Mid", "type": "OSAT", "year": 2025, "sti": 91.2, "lcp": 0.91, "elev": 320},
    {"name": "Vama Semi Noida", "lat": 28.53, "lon": 77.39, "cap": "Small", "type": "Compound", "year": 2025, "sti": 79.0, "lcp": 0.72, "elev": 150},
    {"name": "Tower-Adani Taloja", "lat": 19.06, "lon": 73.07, "cap": "Large", "type": "Fab", "year": 2026, "sti": 93.8, "lcp": 0.95, "elev": 500},
]

# --- 2. LOGIC & NAVIGATION ---
st.title("🛡️ Cyber-Frontline: Semiconductor Sovereignty (1990-2026)")
mode = st.sidebar.radio("Map View", ["Global Choke-Points", "India Evolution Timeline"])

if mode == "India Evolution Timeline":
    year = st.sidebar.slider("Select Year", 1990, 2026, 2026)
    df = pd.DataFrame([h for h in hubs if "year" in h and h['year'] <= year])
    initial_lat, initial_lon, zoom = 22.0, 78.0, 4
else:
    df = pd.DataFrame([h for h in hubs if "year" not in h or h['year'] <= 2026])
    initial_lat, initial_lon, zoom = 20.0, 0.0, 1.5

# Color coding for Classification
df['color'] = df['cap'].map({'Large': [255, 0, 0, 200], 'Mid': [255, 255, 0, 200], 'Small': [0, 255, 100, 200]})

# --- 3. 3D PYDECK ENGINE ---
# The ColumnLayer creates the 3D "protruding" effect for Hub Power
layer = pdk.Layer(
    "ColumnLayer",
    df,
    get_position=['lon', 'lat'],
    get_elevation='elev',
    elevation_scale=1000,
    radius=50000 if mode == "Global Choke-Points" else 20000,
    get_fill_color='color',
    pickable=True,
    auto_highlight=True,
)

view_state = pdk.ViewState(
    latitude=initial_lat,
    longitude=initial_lon,
    zoom=zoom,
    pitch=45, # 3D Tilt
    bearing=0
)

# Professional Tooltip (The GIS Twist)
tooltip = {
    "html": """
        <div style="font-family: monospace; background: #111; color: white; padding: 10px; border: 1px solid cyan;">
            <b style="font-size: 14px; color: cyan;">{name}</b><br/>
            <b>Classification:</b> {cap} Cap {type}<br/>
            <hr/>
            <b>GIS TECHNICALS:</b><br/>
            - Strategic Topo Index: {sti}%<br/>
            - Least Cost Path (LCP): {lcp}<br/>
            - Infrastructure Scale: {elev} units
        </div>
    """,
    "style": {"backgroundColor": "transparent", "color": "white"}
}

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10', # Stable, no-token required style
    initial_view_state=view_state,
    layers=[layer],
    tooltip=tooltip
))

# --- 4. THE DH THEORY (MATH) ---
with st.expander("🔬 Technical Methodology & DH Link"):
    st.markdown("### Digital Humanities: Mapping Infrastructure as Power")
    st.write("By using 3D Columns, we visualize the 'height' of a nation's digital sovereignty.")
    st.latex(r"LCP = \int_{source}^{hub} (Friction_{Terrain} \cdot Energy_{Stability})")
    st.info("Large Cap (Red) | Mid Cap (Yellow) | Small Cap (Green)")
