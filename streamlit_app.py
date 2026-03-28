import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide", page_title="Cyber-Frontline GIS")

# --- DATA WRAPPING ---
# Global Hubs (Today)
global_data = pd.DataFrame({
    'name': ['TSMC (Taiwan)', 'Samsung (S. Korea)', 'Intel (USA)', 'ASML (Netherlands)', 'SMIC (China)'],
    'lat': [24.77, 37.00, 33.30, 51.42, 31.23],
    'lon': [121.01, 127.05, -111.90, 5.40, 121.47],
    'elevation': [112, 45, 350, 20, 15], # Meters above sea level
    'strategic_score': [98, 92, 85, 99, 88], # % Topographical advantage
    'url': 'https://www.google.com/search?q=' # Placeholder for facility search
})

# India Timeline (1990-2026)
india_timeline = pd.DataFrame({
    'name': ['SCL Mohali', 'TI Design', 'Micron Sanand', 'Tata-PSMC Dholera', 'Tata-TSAT Assam', 'Adani-Tower'],
    'year': [1990, 1995, 2023, 2024, 2025, 2026],
    'lat': [30.70, 12.97, 22.98, 22.25, 26.24, 19.06],
    'lon': [76.69, 77.59, 72.37, 72.11, 92.33, 73.07],
    'raw_material_dist': [450, 800, 120, 80, 200, 90], # km
    'elevation': [310, 920, 25, 12, 55, 10]
})

# --- UI HEADER ---
st.title("🛡️ Cyber-Frontline: Semiconductor Sovereignty")
st.markdown("Mapping Choke Points as the New Territories of War (1990–2026)")

tab1, tab2 = st.tabs(["🌍 Global Frontline (3D View)", "🇮🇳 India Evolution (Timeline)"])

# --- TAB 1: GLOBAL ---
with tab1:
    st.info("Hover to see GIS details. Use Right-Click + Drag to rotate the 3D map.")
    
    # 3D Column Layer
    layer = pdk.Layer(
        "ColumnLayer",
        global_data,
        get_position=['lon', 'lat'],
        get_elevation='elevation',
        elevation_scale=5000, # Exaggerates height for 3D effect
        radius=100000,
        get_fill_color=[245, 39, 39, 180], # War Red
        pickable=True,
        auto_highlight=True,
    )

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/satellite-v9',
        initial_view_state=pdk.ViewState(latitude=20, longitude=30, zoom=1.5, pitch=45),
        layers=[layer],
        tooltip={
            "html": """
                <b>Facility:</b> {name} <br/>
                <b>Elevation:</b> {elevation}m ASL <br/>
                <b>Strategic Match:</b> {strategic_score}% <br/>
                <b>Transport Logic:</b> Least Cost Path Optimized
            """,
            "style": {"backgroundColor": "#1a1a1a", "color": "white"}
        }
    ))

# --- TAB 2: INDIA ---
with tab2:
    year_slider = st.slider("Move the slider to see the 'Frontline' expand in India", 1990, 2026, 2026)
    filtered_india = india_timeline[india_timeline['year'] <= year_slider]

    # Scatter Layer for India
    india_layer = pdk.Layer(
        "ScatterplotLayer",
        filtered_india,
        get_position=['lon', 'lat'],
        get_radius=40000,
        get_fill_color=[0, 255, 150, 200],
        pickable=True,
    )

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/dark-v10',
        initial_view_state=pdk.ViewState(latitude=22, longitude=78, zoom=4, pitch=30),
        layers=[india_layer],
        tooltip={"text": "{name}\nEstablished: {year}\nDist to Raw Material: {raw_material_dist}km"}
    ))

# --- FOOTER ---
st.sidebar.title("DH Project Info")
st.sidebar.write("**Topic:** Semiconductor Sovereignty")
st.sidebar.write("**Student:** Parth (SC24B112)")
st.sidebar.info("This project links Spatial Humanities with Geopolitics.")
