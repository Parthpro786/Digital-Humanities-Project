import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

st.set_page_config(layout="wide", page_title="Cyber-Frontline GIS")

# --- 1. THE UNIFIED DATASET (2000 - 2026) ---
# Each hub includes elevation profiles, LCP data, and historic breakthroughs
data = [
    # 2000 - 2010 ERA
    {"name": "Texas Instruments Bangalore", "lat": 12.97, "lon": 77.59, "cap": "Large", "year": 2000, "sti": 88.0, "lcp": 0.85, "elev": "920m", "terrain": "Deccan Plateau", "w_name": "Cauvery Basin", "w_dist": "85km", "m_name": "HAL Transit", "m_dist": "12km", "bt": "First Global R&D Center in India", "img": "https://placehold.co/600x400?text=Texas+Instruments+Bangalore", "profile": [850, 870, 890, 920, 920, 915]},
    {"name": "STMicroelectronics Noida", "lat": 28.58, "lon": 77.31, "cap": "Large", "year": 2000, "sti": 91.0, "lcp": 0.88, "elev": "200m", "terrain": "Indo-Gangetic Plain", "w_name": "Yamuna River", "w_dist": "15km", "m_name": "Delhi Terminal", "m_dist": "25km", "bt": "Advanced IC Design Anchor", "img": "https://placehold.co/600x400?text=ST+Noida", "profile": [190, 195, 200, 200, 198, 195]},
    {"name": "SCL Mohali", "lat": 30.70, "lon": 76.69, "cap": "Small", "year": 2000, "sti": 75.0, "lcp": 0.65, "elev": "310m", "terrain": "Shivalik Foothills", "w_name": "Sutlej River", "w_dist": "28km", "m_name": "Rail Link", "m_dist": "24km", "bt": "Strategic Radiation-Hardened Wafers", "img": "https://placehold.co/600x400?text=SCL+Mohali", "profile": [280, 295, 310, 310, 325, 350]},
    
    # 2026 ERA
    {"name": "Tata-PSMC Dholera", "lat": 22.25, "lon": 72.11, "cap": "Large", "year": 2026, "sti": 99.5, "lcp": 0.97, "elev": "15m", "terrain": "Coastal Plateau", "w_name": "Sabarmati Desal", "w_dist": "32km", "m_name": "Khambhat Port", "m_dist": "55km", "bt": "India's First Commercial 28nm Fab", "img": "https://placehold.co/600x400?text=Tata+Dholera+Fab", "profile": [0, 5, 12, 15, 15, 12]},
    {"name": "Tata-TSAT Assam", "lat": 26.24, "lon": 92.33, "cap": "Large", "year": 2026, "sti": 84.4, "lcp": 0.70, "elev": "55m", "terrain": "River Valley", "w_name": "Brahmaputra", "w_dist": "40km", "m_name": "Haldia Port", "m_dist": "180km", "bt": "Advanced Packaging Sovereign Hub", "img": "https://placehold.co/600x400?text=Tata+Assam+ATMP", "profile": [120, 85, 55, 55, 65, 110]},
    {"name": "Micron Sanand", "lat": 22.98, "lon": 72.37, "cap": "Large", "year": 2026, "sti": 92.0, "lcp": 0.90, "elev": "45m", "terrain": "Industrial Plain", "w_name": "Narmada Canal", "w_dist": "20km", "m_name": "Mundra Port", "m_dist": "250km", "bt": "HBM Memory Module Packaging", "img": "https://placehold.co/600x400?text=Micron+Sanand", "profile": [10, 30, 45, 45, 46, 48]},
    {"name": "Kaynes Sanand", "lat": 22.95, "lon": 72.40, "cap": "Mid", "year": 2026, "sti": 87.0, "lcp": 0.85, "elev": "40m", "terrain": "Plains", "w_name": "Local Mains", "w_dist": "8km", "m_name": "Regional Rail", "m_dist": "25km", "bt": "Automotive Power Module OSAT", "img": "https://placehold.co/600x400?text=Kaynes+OSAT", "profile": [35, 38, 40, 40, 39, 37]}
]

df = pd.DataFrame(data)

# --- 2. ICON MAPPING (GOOGLE MAPS STYLE) ---
# Icon URL for the markers
ICON_URL = "https://img.icons8.com/plasticine/100/marker.png"
icon_data = {
    "url": ICON_URL, "width": 128, "height": 128, "anchorY": 128
}
df['icon_data'] = [icon_data for _ in range(len(df))]

# Colors for the tags: Red (Large), Yellow (Mid), Green (Small)
def get_color(cap):
    if cap == "Large": return [255, 30, 30]
    if cap == "Mid": return [255, 200, 0]
    return [50, 255, 100]

df['color'] = df['cap'].apply(get_color)

# --- 3. UI TABS & TIMELINE ---
st.sidebar.title("🛡️ Cyber-Frontline HUD")
tab_world, tab_india = st.tabs(["🌎 World Today", "🇮🇳 India Timeline"])

with tab_india:
    year_slider = st.slider("Timeline Analysis", 2000, 2026, 2026, step=10 if st.session_state.get('step') else 1)
    # Snap to the major years requested
    years = [2000, 2010, 2020, 2026]
    target_year = min(years, key=lambda x:abs(x-year_slider))
    active_df = df[(df['region'] == 'India') & (df['year'] <= target_year)]

with tab_world:
    global_df = df[df['region'] == 'Global']

# --- 4. MAP RENDERING ---
selected_hub_name = st.sidebar.selectbox("🎯 Select Hub to Inspect:", ["None"] + list(df['name']))

# Default View
view_state = pdk.ViewState(latitude=22, longitude=78, zoom=4, pitch=0)

if selected_hub_name != "None":
    hub = df[df['name'] == selected_hub_name].iloc[0]
    view_state = pdk.ViewState(latitude=hub['lat'], longitude=hub['lon'], zoom=9, pitch=0)
    
    # --- THE SIDE PANEL (GOOGLE MAPS UI STYLE) ---
    st.sidebar.image(hub['img'], use_container_width=True)
    st.sidebar.header(f"{hub['name']}")
    st.sidebar.markdown(f"**Breakthrough:** {hub['bt']}")
    st.sidebar.markdown("---")
    
    # DISCRETIZED TERRAIN PROFILE
    st.sidebar.subheader("🏔️ Discretized Elevation Profile")
    profile_df = pd.DataFrame(hub['profile'], columns=["Elevation (m)"])
    st.sidebar.area_chart(profile_df, height=150)
    st.sidebar.caption(f"Terrain: {hub['terrain']} | Site MSL: {hub['elev']}")
    
    # LOGISTICS DATA
    st.sidebar.markdown(f"💧 **Water Source:** {hub['w_name']} ({hub['w_dist']})")
    st.sidebar.markdown(f"🚛 **Supply Route:** {hub['m_name']} ({hub['m_dist']})")
    st.sidebar.latex(rf"STI = {hub['sti']}\% \quad LCP = {hub['lcp']}")

# Pydeck Icon Layer
icon_layer = pdk.Layer(
    "IconLayer",
    df if selected_hub_name == "None" else df[df['name'] == selected_hub_name],
    get_icon="icon_data",
    get_size=4,
    size_scale=15,
    get_position=["lon", "lat"],
    get_color="color",
    pickable=True,
)

st.pydeck_chart(pdk.Deck(
    layers=[icon_layer],
    initial_view_state=view_state,
    map_style='mapbox://styles/mapbox/dark-v10',
    tooltip={"text": "{name}\n{cap} Cap"}
))
