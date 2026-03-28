import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(layout="wide", page_title="Cyber-Frontline 2026 GIS")

# --- 1. CONFIG & DATA ---
CESIUM_TOKEN = st.sidebar.text_input("Enter Cesium Ion Token", type="password")

# Extended Professional Data Set for 2026
facilities = [
    # --- GLOBAL (Large Cap) ---
    {"name": "TSMC Fab 18", "lat": 23.10, "lon": 120.28, "cap": "Large", "type": "Fab", "url": "https://www.tsmc.com", "lcp": 0.98, "sti": 99.2, "water": "High-Pure", "terrain": "Optimal"},
    {"name": "Samsung Pyeongtaek", "lat": 37.01, "lon": 127.06, "cap": "Large", "type": "Fab", "url": "https://www.samsung.com", "lcp": 0.95, "sti": 94.5, "water": "High-Pure", "terrain": "Stable"},
    {"name": "Intel Ocotillo", "lat": 33.27, "lon": -111.88, "cap": "Large", "type": "Fab", "url": "https://www.intel.com", "lcp": 0.88, "sti": 89.1, "water": "Arid-Recycled", "terrain": "Flat"},
    {"name": "Rapidus Hokkaido", "lat": 42.80, "lon": 141.77, "cap": "Large", "type": "Fab", "url": "https://www.rapidus.inc", "lcp": 0.92, "sti": 91.0, "water": "Mountain-Source", "terrain": "Seismic-Stable"},
    {"name": "GlobalFoundries Dresden", "lat": 51.12, "lon": 13.72, "cap": "Large", "type": "Fab", "url": "https://gf.com", "lcp": 0.94, "sti": 95.8, "water": "Elbe-Recycled", "terrain": "High-Density"},
    
    # --- INDIA (Large, Mid, Small Cap) ---
    {"name": "Tata-PSMC Dholera", "lat": 22.25, "lon": 72.11, "cap": "Large", "type": "Fab", "year": 2024, "url": "https://www.tata.com", "lcp": 0.96, "sti": 97.5, "water": "Narmada/Desal", "terrain": "Custom-Levelled"},
    {"name": "Micron Sanand", "lat": 22.98, "lon": 72.37, "cap": "Large", "type": "ATMP", "year": 2023, "url": "https://www.micron.com", "lcp": 0.89, "sti": 90.2, "water": "UPW-Municipal", "terrain": "Industrial-Park"},
    {"name": "Tata-TSAT Assam", "lat": 26.24, "lon": 92.33, "cap": "Large", "type": "ATMP", "year": 2025, "url": "https://www.tata.com", "lcp": 0.75, "sti": 84.4, "water": "Brahmaputra", "terrain": "Riverine-Plains"},
    {"name": "Tower-Adani Taloja", "lat": 19.06, "lon": 73.07, "cap": "Large", "type": "Fab", "year": 2026, "url": "https://www.adani.com", "lcp": 0.97, "sti": 93.8, "water": "Coastal-Piped", "terrain": "High-Moisture"},
    {"name": "Kaynes Semicon", "lat": 22.99, "lon": 72.38, "cap": "Mid", "type": "OSAT", "year": 2024, "url": "https://www.kaynestechnology.co.in", "lcp": 0.85, "sti": 88.5, "water": "Recycled", "terrain": "Flat"},
    {"name": "HCL-Foxconn Jewar", "lat": 28.13, "lon": 77.55, "cap": "Mid", "type": "OSAT", "year": 2025, "url": "https://www.hcltech.com", "lcp": 0.91, "sti": 92.1, "water": "Yamuna-Linked", "terrain": "Airport-Proximity"},
    {"name": "SPEL Semiconductor", "lat": 13.00, "lon": 80.20, "cap": "Small", "type": "OSAT", "year": 1990, "url": "https://www.spel.com", "lcp": 0.70, "sti": 78.5, "water": "City-Mains", "terrain": "Coastal-Urban"},
    {"name": "Sahasra Memory", "lat": 28.15, "lon": 76.80, "cap": "Small", "type": "ATMP", "year": 2023, "url": "http://sahasraelectronics.com", "lcp": 0.78, "sti": 81.0, "water": "Groundwater", "terrain": "Arid"},
]

# --- 2. TABS & SELECTION ---
tab1, tab2 = st.tabs(["🌍 Global Choke-Points (Today)", "🇮🇳 India Frontiers (Timeline)"])

with tab1:
    selected_node = st.selectbox("🎯 Target Node (Fly-to 3D):", ["None"] + [f['name'] for f in facilities if 'year' not in f or f['year'] <= 2026])
    active_data = [f for f in facilities if 'year' not in f] # Global data

with tab2:
    year = st.slider("Timeline Explorer", 1990, 2026, 2026)
    india_data = [f for f in facilities if 'year' in f and f['year'] <= year]
    selected_node = st.selectbox("🇮🇳 Focus Hub:", ["None"] + [f['name'] for f in india_data])
    active_data = india_data

# --- 3. THE CESIUM CORE ENGINE ---
target = next((f for f in facilities if f['name'] == selected_node), None)

cesium_html = f"""
<div id="cesiumContainer" style="width: 100%; height: 700px; background: #000;"></div>
<script src="https://cesium.com/downloads/cesiumjs/releases/1.115/Build/Cesium/Cesium.js"></script>
<link href="https://cesium.com/downloads/cesiumjs/releases/1.115/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
<script>
    Cesium.Ion.defaultAccessToken = '{CESIUM_TOKEN}';
    
    // 1. Force Earth Visibility and Satellite Imagery
    const viewer = new Cesium.Viewer('cesiumContainer', {{
        terrain: Cesium.Terrain.fromWorldTerrain(),
        baseLayerPicker: false, 
        geocoder: false, 
        timeline: false, 
        animation: false,
        skyAtmosphere: true
    }});

    const data = {json.dumps(active_data)};
    const target = {json.dumps(target)};

    // 2. Add Stylized Nodes based on CAP
    data.forEach(hub => {{
        let nodeColor = Cesium.Color.RED;
        if(hub.cap === "Mid") nodeColor = Cesium.Color.YELLOW;
        if(hub.cap === "Small") nodeColor = Cesium.Color.GREEN;

        viewer.entities.add({{
            position: Cesium.Cartesian3.fromDegrees(hub.lon, hub.lat),
            point: {{ pixelSize: hub.cap === "Large" ? 15 : 10, color: nodeColor, outlineWidth: 2 }},
            label: {{ text: hub.name, font: '12pt Helvetica', style: Cesium.LabelStyle.FILL_AND_OUTLINE, pixelOffset: new Cesium.Cartesian2(0, -20) }},
            description: `
                <div style="font-family: sans-serif; color: white;">
                    <h3>${{hub.name}} (${{hub.type}})</h3>
                    <p><b>Market Cap:</b> ${{hub.cap}}</p>
                    <hr>
                    <b>TECHNICAL GIS METRICS:</b><br>
                    - Strategic Topo Index (STI): ${{hub.sti}}%<br>
                    - Least Cost Path (LCP): ${{hub.lcp}}<br>
                    - UPW Quality Index: ${{hub.water}}<br>
                    - Terrain: ${{hub.terrain}}<br>
                    <br>
                    <a href="${{hub.url}}" target="_blank" style="color: cyan;">Visit Facility Website</a>
                </div>
            `
        }});
    }});

    // 3. Google Earth Style Transitions & Rotation
    if (target) {{
        viewer.camera.flyTo({{
            destination: Cesium.Cartesian3.fromDegrees(target.lon, target.lat, 5000),
            orientation: {{ pitch: Cesium.Math.toRadians(-45), heading: 0 }},
            duration: 3,
            complete: () => {{
                // REVOLVE: Continuously rotate around the hub
                viewer.clock.onTick.addEventListener(function(clock) {{
                    viewer.scene.camera.rotateRight(0.005);
                }});
            }}
        }});
    }} else {{
        // Reset to global view if no hub selected
        viewer.camera.setView({{
            destination: Cesium.Cartesian3.fromDegrees(20, 10, 20000000)
        }});
    }}
</script>
"""

if not CESIUM_TOKEN:
    st.error("❌ MAP DISCONNECTED: Please paste your Cesium Ion Token into the sidebar.")
else:
    components.html(cesium_html, height=720)

# --- 4. DH THEORY SECTION ---
with st.expander("🔬 Digital Humanities & The Cyber-Frontline Theory"):
    st.write("**Spatial Sovereignty:** This map treats semiconductor hubs as the 'new hills' of the medieval era—the places from which control is exerted.")
    st.latex(r"STI = \alpha(Slope^{-1}) + \beta(H_{2}O) + \gamma(Seismic\_Stability)")
    st.write("**LCP (Least Cost Path):** A mathematical value calculating the minimum friction for transporting massive, delicate photolithography machines over uneven terrain.")
