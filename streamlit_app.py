import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(layout="wide", page_title="Cyber-Frontline 2026")

# --- 1. CONFIG & EXPANDED DATASET ---
CESIUM_TOKEN = st.sidebar.text_input("Enter Cesium Ion Token", type="password")

# Large, Mid, Small Cap Semiconductor Facilities (2026 Global Frontline)
data = [
    # --- GLOBAL POWERHOUSES (Large Cap) ---
    {"name": "TSMC Fab 18", "lat": 23.10, "lon": 120.28, "cap": "Large", "type": "Fab", "sti": 99, "lcp": 0.98, "desc": "World's most advanced 2nm/3nm node hub."},
    {"name": "Samsung Pyeongtaek", "lat": 37.01, "lon": 127.06, "cap": "Large", "type": "Fab", "sti": 95, "lcp": 0.95, "desc": "Massive memory and logic cluster."},
    {"name": "Intel Ocotillo", "lat": 33.27, "lon": -111.88, "cap": "Large", "type": "Fab", "sti": 88, "lcp": 0.89, "desc": "US domestic sovereignty anchor."},
    {"name": "Rapidus Hokkaido", "lat": 42.80, "lon": 141.77, "cap": "Large", "type": "Fab", "sti": 91, "lcp": 0.92, "desc": "Japan's 2nm state-backed initiative."},
    {"name": "TI Sherman", "lat": 33.63, "lon": -96.61, "cap": "Large", "type": "Fab", "sti": 85, "lcp": 0.87, "desc": "Leading analog chip manufacturing."},

    # --- INDIA FRONT (Timeline & Scale) ---
    {"name": "Tata-PSMC (Dholera)", "lat": 22.25, "lon": 72.11, "cap": "Large", "type": "Mega-Fab", "sti": 98, "lcp": 0.97, "year": 2024, "desc": "India's flagship commercial fab."},
    {"name": "Micron (Sanand)", "lat": 22.98, "lon": 72.37, "cap": "Large", "type": "ATMP", "sti": 92, "lcp": 0.90, "year": 2023, "desc": "Key global memory packaging node."},
    {"name": "Tata-TSAT (Assam)", "lat": 26.24, "lon": 92.33, "cap": "Large", "type": "ATMP", "sti": 82, "lcp": 0.75, "year": 2025, "desc": "Strategic hub for NE region."},
    {"name": "Tower-Adani (Taloja)", "lat": 19.06, "lon": 73.07, "cap": "Large", "type": "Fab", "sti": 90, "lcp": 0.94, "year": 2026, "desc": "Massive analog/power fab JV."},
    {"name": "Kaynes (Sanand)", "lat": 22.95, "lon": 72.40, "cap": "Mid", "type": "OSAT", "sti": 86, "lcp": 0.88, "year": 2024, "desc": "Automotive chip specialization."},
    {"name": "CG Power (Gujarat)", "lat": 22.99, "lon": 72.38, "cap": "Mid", "type": "ATMP", "sti": 87, "lcp": 0.85, "year": 2024, "desc": "Industrial power electronics hub."},
    {"name": "HCL-Foxconn (Jewar)", "lat": 28.13, "lon": 77.55, "cap": "Mid", "type": "OSAT", "sti": 91, "lcp": 0.91, "year": 2025, "desc": "Strategic airport-adjacent OSAT."},
    {"name": "SCL (Mohali)", "lat": 30.70, "lon": 76.69, "cap": "Small", "type": "Strategic", "sti": 75, "lcp": 0.60, "year": 1990, "desc": "State-run defense/space chip fab."},
    {"name": "Sahasra (Bhiwadi)", "lat": 28.21, "lon": 76.84, "cap": "Small", "type": "ATMP", "sti": 80, "lcp": 0.78, "year": 2023, "desc": "Niche memory assembly focus."},
    {"name": "Vama Semi (Noida)", "lat": 28.53, "lon": 77.39, "cap": "Small", "type": "Design", "sti": 79, "lcp": 0.70, "year": 2025, "desc": "Compound semiconductor pioneer."},
]

# --- 2. NAVIGATION ---
st.sidebar.header("🛡️ Cyber-Control Center")
mode = st.sidebar.radio("View Mode", ["Global", "India"])
selected_name = st.sidebar.selectbox("🎯 Fly-to Target:", ["None"] + [f['name'] for f in data])

if mode == "India":
    year = st.sidebar.slider("Timeline", 1990, 2026, 2026)
    filtered_data = [f for f in data if "year" in f and f['year'] <= year]
else:
    filtered_data = [f for f in data if "year" not in f or f['year'] <= 2026]

target = next((f for f in data if f['name'] == selected_name), None)

# --- 3. THE "ASYNC BOOT" ENGINE ---
# Using a 100% stable initialization script for 2026
cesium_html = f"""
<div id="cesiumContainer" style="width: 100%; height: 750px; background: #000;"></div>
<script src="https://cesium.com/downloads/cesiumjs/releases/1.115/Build/Cesium/Cesium.js"></script>
<link href="https://cesium.com/downloads/cesiumjs/releases/1.115/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
<script>
    (async function() {{
        try {{
            Cesium.Ion.defaultAccessToken = '{CESIUM_TOKEN}';
            
            // Step 1: Initialize Viewer without a promise
            const viewer = new Cesium.Viewer('cesiumContainer', {{
                baseLayerPicker: false, 
                geocoder: false, 
                timeline: false, 
                animation: false,
                skyAtmosphere: true,
                shouldAnimate: true
            }});

            // Step 2: Inject Imagery and Terrain Async to prevent 'setDynamicLighting' error
            const terrainProvider = await Cesium.Terrain.fromWorldTerrain();
            viewer.scene.globe.terrainProvider = terrainProvider;

            const hubs = {json.dumps(filtered_data)};
            const focus = {json.dumps(target)};

            // Step 3: Map classification colors
            hubs.forEach(h => {{
                let color = Cesium.Color.RED;
                if(h.cap === "Mid") color = Cesium.Color.YELLOW;
                if(h.cap === "Small") color = Cesium.Color.LIME;

                viewer.entities.add({{
                    position: Cesium.Cartesian3.fromDegrees(h.lon, h.lat),
                    point: {{ pixelSize: h.cap === "Large" ? 12 : 8, color: color, outlineWidth: 1 }},
                    label: {{ text: h.name, font: '10pt monospace', style: Cesium.LabelStyle.FILL_AND_OUTLINE, pixelOffset: new Cesium.Cartesian2(0, -15) }},
                    description: `<div style="padding:10px;">
                        <h3>${{h.name}} (${{h.cap}} Cap)</h3>
                        <p><b>Type:</b> ${{h.type}}</p>
                        <hr>
                        <b>GIS METRICS:</b><br>
                        - Topo Index (STI): ${{h.sti}}%<br>
                        - Transport Cost (LCP): ${{h.lcp}}<br>
                        <br><i>${{h.desc}}</i></div>`
                }});
            }});

            // Step 4: Logic for 3D Fly-to and Orbit
            if (focus) {{
                viewer.camera.flyTo({{
                    destination: Cesium.Cartesian3.fromDegrees(focus.lon, focus.lat, 4000),
                    orientation: {{ pitch: Cesium.Math.toRadians(-45), heading: 0 }},
                    duration: 3,
                    complete: () => {{
                        viewer.clock.onTick.addEventListener(function(clock) {{
                            viewer.scene.camera.rotateRight(0.005);
                        }});
                    }}
                }});
            }} else {{
                viewer.camera.setView({{ destination: Cesium.Cartesian3.fromDegrees(78, 20, 8000000) }});
            }}

        }} catch (e) {{
            document.getElementById('cesiumContainer').innerHTML = "<div style='color:red; padding:20px;'>FATAL BOOT ERROR: " + e.message + "</div>";
        }}
    }})();
</script>
"""

if not CESIUM_TOKEN:
    st.error("❌ TOKEN REQUIRED: Paste your Cesium Ion Token in the sidebar.")
else:
    components.html(cesium_html, height=760)
