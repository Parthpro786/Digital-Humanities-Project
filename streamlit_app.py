import streamlit as st
import pandas as pd
import pydeck as pdk
import math

st.set_page_config(layout="wide", page_title="Cyber-Frontline: Strategic Sketch")

# --- 1. THE DATASET ---
data = [
    # GLOBAL
    {"name": "TSMC Fab 18", "lat": 23.10, "lon": 120.28, "cap": "Large", "region": "Global", "sti": 99.2, "slope": 0.5, "water": "Reservoir (12km)", "mat": "Kaohsiung Port (40km)", "breakthrough": "3nm Logic Node Production", "rating": "Global Tier 1"},
    {"name": "Samsung Pyeongtaek", "lat": 37.01, "lon": 127.06, "cap": "Large", "region": "Global", "sti": 95.0, "slope": 1.2, "water": "Piped Mains (5km)", "mat": "Incheon Port (60km)", "breakthrough": "GAA Architecture", "rating": "Global Tier 1"},
    {"name": "Intel Ocotillo", "lat": 33.27, "lon": -111.88, "cap": "Large", "region": "Global", "sti": 88.0, "slope": 0.2, "water": "Recycled Arid (1km)", "mat": "Rail Link (15km)", "breakthrough": "Sovereign Anchor Node", "rating": "US Strategic"},
    
    # INDIA
    {"name": "Tata-PSMC Dholera", "lat": 22.25, "lon": 72.11, "cap": "Large", "region": "India", "year": 2024, "sti": 99.5, "slope": 0.1, "water": "Desalination (8km)", "mat": "Khambhat Port (45km)", "breakthrough": "First Indian Commercial Mega-Fab", "rating": "ISM Platinum"},
    {"name": "Micron Sanand", "lat": 22.98, "lon": 72.37, "cap": "Large", "region": "India", "year": 2023, "sti": 92.0, "slope": 0.8, "water": "Canal Network (15km)", "mat": "Mundra Port (300km)", "breakthrough": "HBM Memory Packaging Hub", "rating": "ISM Gold"},
    {"name": "Tata-TSAT Assam", "lat": 26.24, "lon": 92.33, "cap": "Large", "region": "India", "year": 2025, "sti": 84.4, "slope": 1.5, "water": "Brahmaputra (2km)", "mat": "Haldia Port (900km)", "breakthrough": "Strategic NE Region Hub", "rating": "ISM Gold"},
    {"name": "Kaynes Sanand", "lat": 22.95, "lon": 72.40, "cap": "Mid", "region": "India", "year": 2024, "sti": 87.0, "slope": 1.1, "water": "Recycled (10km)", "mat": "Local Supply (50km)", "breakthrough": "Auto/Power Module OSAT", "rating": "ISM Silver"},
    {"name": "HCL-Foxconn Jewar", "lat": 28.13, "lon": 77.55, "cap": "Mid", "region": "India", "year": 2025, "sti": 91.0, "slope": 0.4, "water": "Yamuna Linked (20km)", "mat": "Air Cargo (5km)", "breakthrough": "Airport Logistics Integration", "rating": "ISM Silver"},
    {"name": "SCL Mohali", "lat": 30.70, "lon": 76.69, "cap": "Small", "region": "India", "year": 1990, "sti": 75.0, "slope": 2.5, "water": "Sutlej Basin (3km)", "mat": "Inland Rail (200km)", "breakthrough": "Space-Grade ASICs", "rating": "ISRO Certified"},
    {"name": "SPEL Chennai", "lat": 12.98, "lon": 80.22, "cap": "Small", "region": "India", "year": 1990, "sti": 80.0, "slope": 1.8, "water": "Metro Mains (5km)", "mat": "Chennai Port (25km)", "breakthrough": "Legacy Node Testing", "rating": "State Approved"},
]

df = pd.DataFrame(data)
df['color'] = df['cap'].map({'Large': [255, 50, 50, 200], 'Mid': [255, 200, 0, 200], 'Small': [0, 255, 100, 200]})

# --- 2. LAYOUT ---
st.title("🛡️ Cyber-Frontline: Strategic Topography")
st.markdown("Red = Large Cap | Yellow = Mid Cap | Green = Small Cap")

col_map, col_sketch = st.columns([6, 4])

# --- 3. LEFT COLUMN: 2D MAPS ---
with col_map:
    tab_global, tab_india = st.tabs(["🌍 Global Frontline", "🇮🇳 India Timeline"])
    
    with tab_global:
        global_df = df[df['region'] == 'Global']
        st.pydeck_chart(pdk.Deck(
            map_style='light', # Basic style, no token needed
            initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=1.5),
            layers=[pdk.Layer("ScatterplotLayer", global_df, get_position=['lon', 'lat'], get_color='color', get_radius=200000, pickable=True)],
            tooltip={"text": "{name}\n{cap} Cap"}
        ))
        
    with tab_india:
        year = st.slider("Select Year", 1990, 2026, 2026)
        india_df = df[(df['region'] == 'India') & (df['year'] <= year)]
        st.pydeck_chart(pdk.Deck(
            map_style='light',
            initial_view_state=pdk.ViewState(latitude=22, longitude=78, zoom=4),
            layers=[pdk.Layer("ScatterplotLayer", india_df, get_position=['lon', 'lat'], get_color='color', get_radius=40000, pickable=True)],
            tooltip={"text": "{name}\n{cap} Cap"}
        ))

# --- 4. RIGHT COLUMN: ABSTRACT SKETCH & MATH ---
with col_sketch:
    st.header("Topographical Sketch")
    
    # Note: Streamlit maps don't send click events back to Python easily, 
    # so we use a selectbox linked to the map data for interaction.
    selected_name = st.selectbox("Inspect Facility:", ["Select a Hub..."] + list(df['name']))
    
    if selected_name != "Select a Hub...":
        hub = df[df['name'] == selected_name].iloc[0]
        
        # Math: Calculate Cos Theta
        cos_theta = math.cos(math.radians(hub['slope']))
        
        # Dynamic SVG Sketch
        svg_sketch = f"""
        <svg viewBox="0 0 300 200" style="background-color: #fcf9f2; border: 2px solid #333; border-radius: 8px; width: 100%;">
            <path d="M 10 190 Q 150 160 290 190 L 290 10 Q 150 40 10 10 Z" fill="#f2eecb" opacity="0.8"/>
            
            <circle cx="50" cy="40" r="35" fill="#a3b86c" opacity="0.5"/>
            <circle cx="80" cy="60" r="25" fill="#a3b86c" opacity="0.4"/>
            <circle cx="260" cy="160" r="40" fill="#a3b86c" opacity="0.5"/>
            
            <path d="M 220 0 Q 250 50 300 80 L 300 0 Z" fill="#b3e0ff" opacity="0.6"/>
            
            <rect x="120" y="80" width="40" height="40" fill="white" stroke="#333" stroke-width="2"/>
            <circle cx="140" cy="100" r="10" fill="red" opacity="0.7"/>
            <text x="110" y="135" font-family="monospace" font-size="10" fill="black" font-weight="bold">{hub['name']}</text>
            
            <path d="M 20 180 Q 80 160 120 100" stroke="black" stroke-width="3" stroke-dasharray="6,4" fill="none"/>
            <circle cx="20" cy="180" r="5" fill="black"/>
            <text x="25" y="185" font-family="monospace" font-size="8">RAW MAT: {hub['mat'].split(' ')[0]}</text>
            
            <path d="M 250 40 Q 190 60 160 80" stroke="#00a8cc" stroke-width="3" stroke-dasharray="6,4" fill="none"/>
            <circle cx="250" cy="40" r="5" fill="#00a8cc"/>
            <text x="180" y="35" font-family="monospace" font-size="8" fill="#00a8cc">WATER</text>
            
            <path d="M 10 50 Q 100 80 290 50" stroke="#999" stroke-width="1" fill="none"/>
            <path d="M 10 150 Q 150 130 290 150" stroke="#999" stroke-width="1" fill="none"/>
        </svg>
        """
        st.components.v1.html(svg_sketch, height=220)
        
        # Technical Data Display
        st.markdown(f"### 📑 Facility Dossier")
        st.write(f"**Classification:** {hub['cap']} Cap")
        st.write(f"**Breakthrough:** {hub['breakthrough']}")
        st.write(f"**Strategic Rating:** :blue[{hub['rating']}]")
        st.write(f"**Water Source:** {hub['water']}")
        st.write(f"**Material LCP:** {hub['mat']}")
        
        # The Mathematics
        st.markdown("---")
        st.markdown("**Geospatial Efficiency Analysis:**")
        st.latex(rf"\text{{Terrain Slope (}}\theta\text{{)}} = {hub['slope']}^\circ")
        st.latex(rf"\text{{Efficiency Matrix (}}\cos \theta\text{{)}} = {cos_theta:.4f}")
        st.caption("A perfectly flat plateau yields an efficiency of 1.0000. Steeper valleys increase friction and reduce efficiency, requiring heavily engineered LCPs.")

    else:
        st.info("Select a facility from the dropdown to generate its Topographical Field Sketch.")
