import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide", page_title="Cyber-Frontline: Strategic Sketch")

# --- 1. THE DATASET (GLOBAL & INDIA) ---
# Cap: Large (Red), Mid (Yellow), Small (Green)
data = [
    {"name": "TSMC Fab 18", "lat": 23.10, "lon": 120.28, "cap": "Large", "type": "Fab", "region": "Global", "sti": 99, "lcp": 0.98, "slope": 0.5, "water_dist": "12km", "breakthrough": "2nm Logic Production", "rating": "A+"},
    {"name": "Samsung Pyeongtaek", "lat": 37.01, "lon": 127.06, "cap": "Large", "type": "Fab", "region": "Global", "sti": 95, "lcp": 0.95, "slope": 1.2, "water_dist": "5km", "breakthrough": "GAA Architecture", "rating": "A"},
    {"name": "Tata-PSMC Dholera", "lat": 22.25, "lon": 72.11, "cap": "Large", "type": "Mega-Fab", "region": "India", "year": 2024, "sti": 99.5, "lcp": 0.97, "slope": 0.1, "water_dist": "8km", "breakthrough": "First Indian Commercial Fab", "rating": "ISM Platinum"},
    {"name": "Micron Sanand", "lat": 22.98, "lon": 72.37, "cap": "Large", "type": "ATMP", "region": "India", "year": 2023, "sti": 92.0, "lcp": 0.90, "slope": 0.8, "water_dist": "15km", "breakthrough": "HBM Memory Packaging", "rating": "ISM Gold"},
    {"name": "Kaynes Sanand", "lat": 22.95, "lon": 72.40, "cap": "Mid", "type": "OSAT", "region": "India", "year": 2024, "sti": 87.0, "lcp": 0.85, "slope": 1.1, "water_dist": "10km", "breakthrough": "Power Module OSAT", "rating": "ISM Silver"},
    {"name": "SCL Mohali", "lat": 30.70, "lon": 76.69, "cap": "Small", "type": "Strategic", "region": "India", "year": 1990, "sti": 75.0, "lcp": 0.65, "slope": 2.5, "water_dist": "3km", "breakthrough": "Space-Grade ASIC", "rating": "ISRO Certified"},
    {"name": "Tower-Adani Taloja", "lat": 19.06, "lon": 73.07, "cap": "Large", "type": "Fab", "region": "India", "year": 2026, "sti": 93.8, "lcp": 0.94, "slope": 0.4, "water_dist": "20km", "breakthrough": "Analog Power Fab", "rating": "ISM Gold"},
]

df = pd.DataFrame(data)
df['color'] = df['cap'].map({'Large': [255, 0, 50, 200], 'Mid': [255, 200, 0, 200], 'Small': [0, 255, 100, 200]})

# --- 2. LAYOUT: MAP (LEFT) & SKETCH (RIGHT) ---
col_map, col_sketch = st.columns([7, 3])

with col_map:
    tab_global, tab_india = st.tabs(["🌍 Global Frontline", "🇮🇳 India Timeline"])
    
    # Global Tab
    with tab_global:
        view_global = pdk.ViewState(latitude=20, longitude=0, zoom=1.5, pitch=0)
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/dark-v10',
            initial_view_state=view_global,
            layers=[pdk.Layer("ScatterplotLayer", df[df['region']=='Global'], get_position=['lon', 'lat'], get_color='color', get_radius=150000, pickable=True)]
        ))

    # India Tab
    with tab_india:
        timeline_year = st.slider("Select Timeline Year", 1990, 2026, 2026)
        filtered_india = df[(df['region']=='India') & (df['year'] <= timeline_year)]
        view_india = pdk.ViewState(latitude=22, longitude=78, zoom=4, pitch=0)
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v10',
            initial_view_state=view_india,
            layers=[pdk.Layer("ScatterplotLayer", filtered_india, get_position=['lon', 'lat'], get_color='color', get_radius=50000, pickable=True)]
        ))

# --- 3. THE "CRAZY PART": PENCIL DRAWING POPUP ---
with col_sketch:
    st.header("Strategic Sketch")
    selected_name = st.selectbox("Click to Inspect Hub:", ["None"] + list(df['name']))
    
    if selected_name != "None":
        hub = df[df['name'] == selected_name].iloc[0]
        
        # Calculate Math
        import math
        cos_theta = math.cos(math.radians(hub['slope']))
        
        # THE SVG SKETCH GENERATOR
        svg_sketch = f"""
        <svg viewBox="0 0 200 200" style="background-color: #fdf6e3; border: 2px solid #555; border-radius: 10px;">
            <path d="M 20 180 Q 100 150 180 180 L 180 20 Q 100 50 20 20 Z" fill="#eee8d5" opacity="0.6"/>
            <circle cx="150" cy="50" r="30" fill="#859900" opacity="0.3" />
            <circle cx="170" cy="70" r="20" fill="#859900" opacity="0.3" />
            
            <rect x="90" y="90" width="20" height="20" fill="none" stroke="black" stroke-width="2" />
            <text x="85" y="125" font-family="monospace" font-size="8" fill="black">FACILITY</text>
            
            <path d="M 10 100 Q 50 80 90 100" stroke="black" stroke-width="2" stroke-dasharray="4,4" fill="none" />
            <text x="10" y="90" font-family="monospace" font-size="6">RAW MAT SOURCE</text>
            
            <path d="M 100 10 Q 120 50 100 90" stroke="#268bd2" stroke-width="2" stroke-dasharray="4,4" fill="none" />
            <text x="80" y="20" font-family="monospace" font-size="6" fill="#268bd2">WATER SOURCE</text>
            
            <text x="140" y="180" font-family="serif" font-style="italic" font-size="6" fill="#555">Topographical Field Sketch v.2.1</text>
        </svg>
        """
        st.components.v1.html(svg_sketch, height=220)
        
        # TECHNICAL DOSSIER
        st.markdown(f"### 📊 Hub Dossier: {selected_name}")
        st.write(f"**Classification:** {hub['cap']} Cap")
        st.write(f"**Strategic Location:** {hub['sti']}%")
        st.write(f"**Water Dist:** {hub['water_dist']}")
        st.write(f"**Government Rating:** :blue[{hub['rating']}]")
        st.info(f"**Breakthrough:** {hub['breakthrough']}")
        
        # MATH SECTION
        st.latex(rf"\cos \theta = {cos_theta:.4f}")
        st.caption(f"Calculated for average terrain slope of {hub['slope']}°")
        st.latex(r"LCP_{eff} = \int_{source}^{hub} f(z) dz")

    else:
        st.write("Select a node on the map or use the dropdown to view the topographical sketch.")
