import streamlit as st
import streamlit.components.v1 as components
import json

# --- INITIAL CONFIG ---
st.set_page_config(layout="wide", page_title="Cyber-Frontline 3D")

# 1. SETUP: Put your Cesium Ion Token here
# The first string is the LABEL (what the user sees), the second is the TYPE
CESIUM_TOKEN = st.sidebar.text_input("Enter Cesium Ion Token", type="password")

# --- DATA: PROFESSIONAL GIS METRICS ---
# STI: Strategic Topographical Index | LCP: Least Cost Path
global_hubs = [
    {"name": "TSMC Fab 18", "lat": 23.10, "lon": 120.28, "elev": 15, "lcp": 0.98, "sti": 99.2, "water": "High-Pure"},
    {"name": "Intel Ocotillo", "lat": 33.27, "lon": -111.88, "elev": 370, "lcp": 0.82, "sti": 88.0, "water": "Arid-Recycled"}
]

india_hubs = [
    {"name": "SCL Mohali", "year": 1990, "lat": 30.70, "lon": 76.69, "lcp": 0.65, "water": "Sutlej", "terrain": "Flat"},
    {"name": "Tata-PSMC Dholera", "year": 2024, "lat": 22.25, "lon": 72.11, "lcp": 0.96, "water": "Narmada/Desal", "terrain": "Optimal"}
]

# --- UI TABS ---
tab1, tab2 = st.tabs(["🌍 Global Frontline", "🇮🇳 India Evolution"])

with tab1:
    selected_global = st.selectbox("Select Hub to 'Fly To':", ["None"] + [h['name'] for h in global_hubs])
    active_data = global_hubs
    target = next((h for h in global_hubs if h['name'] == selected_global), None)

with tab2:
    year = st.slider("Select Year", 1990, 2026, 2026)
    active_data = [h for h in india_hubs if h['year'] <= year]
    selected_india = st.selectbox("Focus on Indian Hub:", ["None"] + [h['name'] for h in active_data])
    target = next((h for h in active_data if h['name'] == selected_india), None)

# --- THE CESIUM COMPONENT (HTML/JS) ---
# This is the "Engine" that creates the 3D Satellite view
# --- THE UPDATED CESIUM COMPONENT ---
cesium_html = f"""
<div id="cesiumContainer" style="width: 100%; height: 600px; background: #000;"></div>
<script src="https://cesium.com/downloads/cesiumjs/releases/1.115/Build/Cesium/Cesium.js"></script>
<link href="https://cesium.com/downloads/cesiumjs/releases/1.115/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
<script>
    try {{
        Cesium.Ion.defaultAccessToken = '{CESIUM_TOKEN}';
        
        // Initialize viewer with the modern 2026 terrain syntax
        const viewer = new Cesium.Viewer('cesiumContainer', {{
            terrain: Cesium.Terrain.fromWorldTerrain(),
            baseLayerPicker: false,
            geocoder: false,
            timeline: false,
            animation: false,
            infoBox: true,
            selectionIndicator: false
        }});

        const data = {json.dumps(active_data)};
        const target = {json.dumps(target)};

        // Add the Semiconductor Hubs
        data.forEach(hub => {{
            viewer.entities.add({{
                position: Cesium.Cartesian3.fromDegrees(hub.lon, hub.lat),
                point: {{ pixelSize: 12, color: Cesium.Color.RED, outlineWidth: 2 }},
                label: {{ text: hub.name, font: '12pt sans-serif', style: Cesium.LabelStyle.FILL_AND_OUTLINE, pixelOffset: new Cesium.Cartesian2(0, -15) }}
            }});
        }});

        // Fly-to Logic
        if (target) {{
            viewer.camera.flyTo({{
                destination: Cesium.Cartesian3.fromDegrees(target.lon, target.lat, 8000),
                orientation: {{ pitch: Cesium.Math.toRadians(-40), heading: 0 }},
                duration: 3
            }});
        }}
    }} catch (err) {{
        console.error("Cesium Load Error:", err);
        document.getElementById('cesiumContainer').innerHTML = "<h2 style='color:white; padding: 20px;'>Error Loading 3D Globe: " + err.message + "</h2>";
    }}
</script>
"""

if not CESIUM_TOKEN:
    st.warning("Please enter your Cesium Ion Token in the sidebar to view the 3D Satellite Globe.")
else:
    components.html(cesium_html, height=600)

# --- PROFESSIONAL GIS DOCUMENTATION ---
with st.expander("📊 Technical GIS Methodology"):
    st.markdown("### Strategic Topographical Index (STI)")
    st.write("Calculated as a weighted sum of terrain stability, power grid proximity, and seismic safety.")
    st.latex(r"STI = \alpha(Slope^{-1}) + \beta(H_{2}O) + \gamma(Grid)")
    st.markdown("### Least Cost Transportation (LCP)")
    st.write("Determined by analyzing the friction surface for heavy machinery transport from the nearest mineral port.")
