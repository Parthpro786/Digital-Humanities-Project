import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(layout="wide", page_title="Cyber-Frontline 2026")

# --- 1. TOKEN & DATASET ---
CESIUM_TOKEN = st.sidebar.text_input("Enter Cesium Ion Token", type="password")

# Extensive 2026 Dataset (Small, Mid, Large Cap)
facilities = [
    # --- LARGE CAP (The Giants) ---
    {"name": "Tata-PSMC (Dholera)", "lat": 22.25, "lon": 72.11, "cap": "Large", "type": "Mega-Fab", "lcp": 0.98, "sti": 99.1, "water": "UPW-Desal", "desc": "India's first commercial 28nm/40nm fab."},
    {"name": "Micron (Sanand)", "lat": 22.98, "lon": 72.37, "cap": "Large", "type": "ATMP", "lcp": 0.92, "sti": 94.5, "water": "Municipal-UPW", "desc": "Global memory hub for assembly/testing."},
    {"name": "TSMC (Hsinchu)", "lat": 24.77, "lon": 121.01, "cap": "Large", "type": "Fab", "lcp": 0.99, "sti": 99.8, "water": "Recycled-High", "desc": "Global Choke-Point for 3nm production."},
    {"name": "Intel (Arizona)", "lat": 33.30, "lon": -111.90, "cap": "Large", "type": "Fab", "lcp": 0.85, "sti": 82.0, "water": "Arid-Optimized", "desc": "US Strategic Sovereign Hub."},
    {"name": "Samsung (Pyeongtaek)", "lat": 37.01, "lon": 127.06, "cap": "Large", "type": "Fab", "lcp": 0.96, "sti": 95.2, "water": "High-Volume", "desc": "Largest semiconductor facility globally."},

    # --- MID CAP (The Growth Engines) ---
    {"name": "Kaynes Semicon (Gujarat)", "lat": 22.99, "lon": 72.38, "cap": "Mid", "type": "OSAT", "lcp": 0.88, "sti": 89.0, "water": "Recycled", "desc": "Focused on power modules and automotive."},
    {"name": "CG Power (Sanand)", "lat": 22.95, "lon": 72.40, "cap": "Mid", "type": "ATMP", "lcp": 0.86, "sti": 87.5, "water": "Industrial", "desc": "JV with Renesas for specialized chips."},
    {"name": "HCL-Foxconn (Jewar)", "lat": 28.13, "lon": 77.55, "cap": "Mid", "type": "OSAT", "lcp": 0.91, "sti": 92.0, "water": "River-Linked", "desc": "Strategically placed near upcoming airport."},
    {"name": "Suchi Semi (Gujarat)", "lat": 21.17, "lon": 72.83, "cap": "Mid", "type": "OSAT", "lcp": 0.82, "sti": 85.0, "water": "Coastal", "desc": "Expanding local supply chains."},
    {"name": "Murugappa (Tamil Nadu)", "lat": 13.08, "lon": 80.27, "cap": "Mid", "type": "ATMP", "lcp": 0.89, "sti": 90.1, "water": "Metro-UPW", "desc": "Pivoting legacy industrial power to tech."},

    # --- SMALL CAP / STRATEGIC (Critical Specialization) ---
    {"name": "SCL (Mohali)", "lat": 30.70, "lon": 76.69, "cap": "Small", "type": "R&D Fab", "lcp": 0.65, "sti": 75.0, "water": "State-Sourced", "desc": "Strategic site for space/defense chips."},
    {"name": "Sahasra Memory (Bhiwadi)", "lat": 28.21, "lon": 76.84, "cap": "Small", "type": "ATMP", "lcp": 0.72, "sti": 79.2, "water": "Borewell-UPW", "desc": "First private memory assembly in India."},
    {"name": "SPEL (Chennai)", "lat": 12.98, "lon": 80.22, "cap": "Small", "type": "OSAT", "lcp": 0.78, "sti": 81.5, "water": "Urban-Linked", "desc": "Specialized in testing older nodes."},
    {"name": "Vama Semi (Noida)", "lat": 28.53, "lon": 77.39, "cap": "Small", "type": "Design/Fab", "lcp": 0.74, "sti": 80.0, "water": "Urban", "desc": "Niche compound semiconductor focus."}
]

# --- 2. LAYOUT ---
st.title("🛡️ Cyber-Frontline: 2026 GIS Dashboard")
st.sidebar.info("Select a Hub to trigger a 3D Google Earth 'Fly-to' and Orbit.")

selected_node = st.sidebar.selectbox("🎯 Fly-to Node:", ["None"] + [f['name'] for f in facilities])
target = next((f for f in facilities if f['name'] == selected_node), None)

# --- 3. THE ASYNC CESIUM ENGINE ---
cesium_html = f"""
<div id="cesiumContainer" style="width: 100%; height: 750px; background: #000;"></div>
<script src="https://cesium.com/downloads/cesiumjs/releases/1.115/Build/Cesium/Cesium.js"></script>
<link href="https://cesium.com/downloads/cesiumjs/releases/1.115/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
<script>
    (async function() {{
        try {{
            Cesium.Ion.defaultAccessToken = '{CESIUM_TOKEN}';
            
            // FIX: Await the terrain provider to prevent 'setDynamicLighting' crash
            const terrainProvider = await Cesium.Terrain.fromWorldTerrain();
            
            const viewer = new Cesium.Viewer('cesiumContainer', {{
                terrain: terrainProvider,
                baseLayerPicker: false, 
                geocoder: false, 
                timeline: false, 
                animation: false,
                skyAtmosphere: true,
                shouldAnimate: true
            }});

            const data = {json.dumps(facilities)};
            const target = {json.dumps(target)};

            // Add Nodes with classification logic
            data.forEach(hub => {{
                let nodeColor = Cesium.Color.RED; // Large
                if(hub.cap === "Mid") nodeColor = Cesium.Color.YELLOW;
                if(hub.cap === "Small") nodeColor = Cesium.Color.LIME;

                viewer.entities.add({{
                    position: Cesium.Cartesian3.fromDegrees(hub.lon, hub.lat),
                    point: {{ pixelSize: hub.cap === "Large" ? 14 : 10, color: nodeColor, outlineWidth: 2, outlineColor: Cesium.Color.WHITE }},
                    label: {{ text: hub.name, font: '10pt monospace', style: Cesium.LabelStyle.FILL_AND_OUTLINE, pixelOffset: new Cesium.Cartesian2(0, -15) }},
                    description: `
                        <div style="background: rgba(0,0,0,0.8); padding: 10px; border-radius: 5px;">
                            <h3 style="color:cyan;">${{hub.name}}</h3>
                            <p><b>Cap:</b> ${{hub.cap}} | <b>Type:</b> ${{hub.type}}</p>
                            <hr>
                            <b>GIS METRICS:</b><br>
                            - Strategic Index (STI): ${{hub.sti}}%<br>
                            - Transport Cost (LCP): ${{hub.lcp}}<br>
                            - Water: ${{hub.water}}<br>
                            <br>
                            <i>${{hub.desc}}</i>
                        </div>
                    `
                }});
            }});

            // Fly-to and Continuous Orbit
            if (target) {{
                viewer.camera.flyTo({{
                    destination: Cesium.Cartesian3.fromDegrees(target.lon, target.lat, 4000),
                    orientation: {{ pitch: Cesium.Math.toRadians(-45), heading: 0 }},
                    duration: 3,
                    complete: () => {{
                        viewer.clock.onTick.addEventListener(function(clock) {{
                            viewer.scene.camera.rotateRight(0.005);
                        }});
                    }}
                }});
            }} else {{
                // Default View: Focus on India
                viewer.camera.setView({{
                    destination: Cesium.Cartesian3.fromDegrees(78.96, 20.59, 5000000)
                }});
            }}
        }} catch (e) {{
            document.getElementById('cesiumContainer').innerHTML = "<div style='color:red; padding:20px;'>ASYNC ERROR: " + e.message + "</div>";
        }}
    }})();
</script>
"""

if not CESIUM_TOKEN:
    st.error("❌ TOKEN MISSING: Please enter your Cesium Ion Token in the sidebar.")
else:
    components.html(cesium_html, height=760)

# --- 4. TECHNICAL DOCUMENTATION ---
with st.expander("🔬 Mathematical & Strategic Methodology"):
    st.write("For this 4th-semester DH project, we utilize **Spatial Justice** and **Infrastructure Power** theories.")
    st.latex(r"LCP = \int_{source}^{hub} (Friction_{Terrain} + Distance \cdot Cost_{Energy}) dt")
    st.markdown("""
    - **Strategic Topographical Index (STI):** A weighted metric where $STI > 90\%$ indicates optimal flatness ($<0.1$ degree slope) and proximity to state-guaranteed power grids.
    - **Ultra-Pure Water (UPW):** Necessary for 3nm/5nm nodes; mapped relative to the Narmada and Brahmaputra river basins.
    """)
