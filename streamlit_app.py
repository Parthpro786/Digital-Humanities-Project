import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import altair as alt

# --- 1. PROFESSIONAL PAGE CONFIG & CSS ---
st.set_page_config(layout="wide", page_title="Cyber-Frontline GIS", page_icon="🗺️")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 1.5rem; max-width: 98%;}
        h1, h2, h3, p {font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;}
        .st-emotion-cache-1v0mbdj > img {border-radius: 6px; border: 1px solid #333;}
        .metric-box {background-color: #1e1e1e; padding: 15px; border-radius: 8px; border-left: 4px solid #2563eb; margin-bottom: 15px;}
        .metric-title {color: #9ca3af; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;}
        .metric-text {color: #f3f4f6; font-size: 14px; line-height: 1.5;}
    </style>
""", unsafe_allow_html=True)

# --- 2. STATE MANAGEMENT ---
if "selected_node" not in st.session_state:
    st.session_state.selected_node = None

def clear_selection():
    st.session_state.selected_node = None

# --- 3. LOGISTICS CURVE GENERATOR ---
def generate_curve(start, end, bend=0.2):
    p0, p2 = np.array(start), np.array(end)
    mid = (p0 + p2) / 2
    perp = np.array([-(p2[1]-p0[1]), p2[0]-p0[0]]) 
    p1 = mid + perp * bend
    t = np.linspace(0, 1, 30)
    curve = np.outer((1-t)**2, p0) + np.outer(2*(1-t)*t, p1) + np.outer(t**2, p2)
    return curve.tolist()

# --- 4. THE MASTER DATASET ---
data = [
    # ---- GLOBAL ECOSYSTEM (Large, Mid, Small) ----
    {"name": "TSMC Fab 18", "region": "Global", "cap": "Large", "lat": 23.10, "lon": 120.28, "img": "https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&w=800&q=80"},
    {"name": "Intel Ocotillo", "region": "Global", "cap": "Large", "lat": 33.27, "lon": -111.88, "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80"},
    {"name": "Samsung Pyeongtaek", "region": "Global", "cap": "Large", "lat": 37.02, "lon": 127.04, "img": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=800&q=80"},
    {"name": "GlobalFoundries Dresden", "region": "Global", "cap": "Mid", "lat": 51.12, "lon": 13.71, "img": "https://images.unsplash.com/photo-1563770660941-20978e870e26?auto=format&fit=crop&w=800&q=80"},
    {"name": "SMIC Shanghai", "region": "Global", "cap": "Mid", "lat": 31.20, "lon": 121.59, "img": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?auto=format&fit=crop&w=800&q=80"},
    {"name": "X-Fab Sarawak", "region": "Global", "cap": "Small", "lat": 1.55, "lon": 110.35, "img": "https://images.unsplash.com/photo-1580983554869-3221443491db?auto=format&fit=crop&w=800&q=80"},

    # ---- INDIAN ECOSYSTEM (Highly Detailed) ----
    {
        "name": "Tata-PSMC Dholera", "region": "India", "year": 2026, "cap": "Large", "lat": 22.25, "lon": 72.11, "elev": "15m MSL", "terrain": "Coastal Plateau",
        "w_name": "Sabarmati Desalination", "w_lat": 22.50, "w_lon": 72.30, "w_dist": 32,
        "m_name": "Gulf of Khambhat Port", "m_lat": 21.75, "m_lon": 72.25, "m_dist": 55,
        "l_name": "Ahmedabad Urban Center", "l_lat": 23.02, "l_lon": 72.57, "l_dist": 85,
        "bt": "India's First Commercial 28nm Mega-Fab", 
        "img": "https://images.unsplash.com/photo-1508344928928-7165b67de128?auto=format&fit=crop&w=800&q=80",
        "profile": [0, 5, 8, 12, 15, 15, 15, 15, 12, 8, 5],
        "sti": 99.5, "lcp": 0.97,
        "desc_elev": "Sitting at an elevation of exactly **15m MSL**, this coastal plateau was engineered for extreme topological stability. The terrain registers a seismic vibration friction coefficient of less than **0.02%**, making it an impeccable geometric fortress. Advanced EUV lithography machines, which print silicon pathways merely atoms wide, require this absolute flatness to prevent multi-billion dollar wafer spoilage during production.",
        "desc_log": "The Least Cost Path (LCP) efficiency here is an astounding **0.97**. Raw materials transit **55km** from the deep-water Gulf of Khambhat port over flat, unyielding terrain, requiring zero mountain-pass routing. Simultaneously, Ultra-Pure Water (UPW) is piped **32km** from the Sabarmati Desalination hub, utilizing gravity-assisted gradients that reduce pumping energy costs by **18%** annually.",
        "desc_sti": "With a Strategic Topographical Index of **99.5%**, Dholera represents the pinnacle of modern semiconductor urban planning. It achieves absolute sovereignty by isolating itself from major tectonic fault lines while maintaining immediate proximity to the **85km** labor corridor of Ahmedabad, seamlessly bridging the gap between heavy industrial logistics and specialized human capital."
    },
    {
        "name": "Tata-TSAT Assam", "region": "India", "year": 2026, "cap": "Large", "lat": 26.24, "lon": 92.33, "elev": "55m MSL", "terrain": "River Valley",
        "w_name": "Brahmaputra Basin", "w_lat": 26.50, "w_lon": 92.60, "w_dist": 40,
        "m_name": "Haldia Port Transit", "m_lat": 25.50, "m_lon": 91.00, "m_dist": 180,
        "l_name": "Guwahati Metropolis", "l_lat": 26.14, "l_lon": 91.73, "l_dist": 65,
        "bt": "Sovereign Advanced Packaging Hub", 
        "img": "https://images.unsplash.com/photo-1587292231267-27b2b8089457?auto=format&fit=crop&w=800&q=80",
        "profile": [120, 100, 80, 55, 55, 55, 70, 95, 110],
        "sti": 84.4, "lcp": 0.70,
        "desc_elev": "Nestled in a river valley at **55m MSL**, this facility trades perfect flatness for geographic defense. The surrounding Himalayan foothills provide natural atmospheric shielding, but induce a **34%** higher terrain friction coefficient. Ground stabilization required deep-pile driving to isolate the massive ATMP (Assembly, Testing, Marking, and Packaging) equipment from the alluvial soil's natural micro-resonances.",
        "desc_log": "Logistics here face high topographical resistance, reflected in an LCP of **0.70**. The raw material corridor must snake **180km** through changing elevations from the Haldia transit zone, increasing transportation fuel burn and vibration risk to delicate substrates. However, the proximity to the Brahmaputra Basin (**40km**) guarantees an inexhaustible, high-volume water source critical for chemical mechanical polishing (CMP) processes.",
        "desc_sti": "Scoring an STI of **84.4%**, the Assam node is a geopolitical hedge. It pushes India's high-tech manufacturing frontier eastward, tapping into the **65km** labor pipeline of Guwahati. While the logistics math is challenging, the strategic dispersion of sovereign tech infrastructure away from the western coast drastically improves the national ecosystem's overall survivability."
    },
    {
        "name": "Texas Instruments Bangalore", "region": "India", "year": 2000, "cap": "Large", "lat": 12.97, "lon": 77.59, "elev": "920m MSL", "terrain": "Deccan Plateau",
        "w_name": "Cauvery Basin", "w_lat": 12.40, "w_lon": 77.30, "w_dist": 85,
        "m_name": "HAL Airport Data Transit", "m_lat": 12.95, "m_lon": 77.66, "m_dist": 12,
        "l_name": "Bangalore Tech Hub", "l_lat": 12.97, "l_lon": 77.59, "l_dist": 0,
        "bt": "First Global R&D Center in India (1985)", 
        "img": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80",
        "profile": [850, 875, 900, 920, 920, 920, 910, 895, 880],
        "sti": 88.0, "lcp": 0.85,
        "desc_elev": "Perched on the Deccan Plateau at a commanding **920m MSL**, this heritage facility was immune to coastal flooding. In the 1990s, physical vibration metrics were irrelevant as this was purely a VLSI design center, not a physical fab. The high altitude provided a moderate climate, reducing the massive HVAC cooling loads required for their early server mainframes by roughly **14%**.",
        "desc_log": "As a design hub, 'Raw Materials' consisted of data. The LCP of **0.85** reflects the **12km** physical distance to the HAL airport where magnetic data tapes were originally flown out, before satellite uplinks became standard. Physical water draw was minimal, sourced primarily from municipal pipelines linked to the Cauvery Basin **85km** away, posing zero operational bottlenecks for a non-manufacturing site.",
        "desc_sti": "The STI of **88.0%** perfectly represents early 'Human-Centric Topography'. TI chose this site not for flat land or water routes, but because the immediate **0km** proximity to Indian engineering institutions provided a frictionless pipeline of elite intellectual labor. It proved that strategic tech nodes could be anchored entirely by human capital rather than maritime logistics."
    },
    {
        "name": "SCL Mohali", "region": "India", "year": 2000, "cap": "Small", "lat": 30.70, "lon": 76.69, "elev": "310m MSL", "terrain": "Shivalik Foothills",
        "w_name": "Sutlej River", "w_lat": 30.90, "w_lon": 76.50, "w_dist": 28,
        "m_name": "Northern Rail Depot", "m_lat": 30.50, "m_lon": 76.80, "m_dist": 24,
        "l_name": "Chandigarh Urban Grid", "l_lat": 30.73, "l_lon": 76.77, "l_dist": 10,
        "bt": "ISRO Strategic Radiation-Hardened Wafers", 
        "img": "https://images.unsplash.com/photo-1513828742140-ccaa28f3eda0?auto=format&fit=crop&w=800&q=80",
        "profile": [280, 290, 300, 310, 310, 310, 330, 350, 380],
        "sti": 75.0, "lcp": 0.65,
        "desc_elev": "Built at **310m MSL** at the edge of the Shivalik foothills, SCL required intense geological surveying to map fault lines. While the terrain profile ramps up aggressively toward the Himalayas, the specific fab foundation was blasted into a localized stable bedrock shelf. This prevents ground-shear during minor tremors, critical for producing 180nm CMOS sensors used in orbital satellites.",
        "desc_log": "The **0.65** LCP is the lowest in the network due to deliberate isolation. Security overrode logistical efficiency. Raw silicon and specialty gases navigate a highly controlled **24km** rail-to-road network. The facility draws immense cooling capacity from the Sutlej river tributaries **28km** away, utilizing high-pressure pump systems to overcome the steep 30-meter elevation delta.",
        "desc_sti": "With an STI of **75.0%**, Mohali is a textbook 'Defense-in-Depth' location. It sacrifices maritime supply chain speed to place highly classified ISRO and defense fabrication deep inland, away from vulnerable coastal zones. The highly structured **10km** proximity to Chandigarh provides a secure, organized grid for its specialized workforce and military liaisons."
    }
]

df = pd.DataFrame(data)

# High-Quality Location Pin Mapping
ICON_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-atlas.png"
icon_data = {"url": ICON_URL, "width": 128, "height": 128, "y": 128, "anchorY": 128}
df['icon_data'] = [icon_data for _ in range(len(df))]

def get_color(cap):
    if cap == "Large": return [255, 60, 60]  
    if cap == "Mid": return [255, 200, 50]   
    return [50, 220, 100]                    
df['color'] = df['cap'].apply(get_color)


# --- 5. TOP BAR UI ---
st.title("🛡️ Cyber-Frontline: Strategic Topography")

col_tabs, col_legend = st.columns([7, 3])
with col_tabs:
    view_mode = st.radio("Select Operational Theater:", ["🇮🇳 India Ecosystem (Interactive)", "🌍 Global Map (Display Only)"], horizontal=True, label_visibility="collapsed")
with col_legend:
    st.markdown("<div style='text-align: right; padding-top: 10px;'>📍 <b><span style='color:#ff3c3c'>Large</span> | <span style='color:#ffc832'>Mid</span> | <span style='color:#32dc64'>Small</span></b></div>", unsafe_allow_html=True)

# Data Filtering based on view mode
if "India" in view_mode:
    active_df = df[df['region'] == 'India'].copy()
    init_view = pdk.ViewState(latitude=22.0, longitude=79.0, zoom=4.2, pitch=0)
else:
    active_df = df.copy() # Show all
    init_view = pdk.ViewState(latitude=20.0, longitude=10.0, zoom=1.5, pitch=0)
    clear_selection() # Ensure sidebar is hidden for global view

# --- 6. 70/30 SPLIT ARCHITECTURE ---
if st.session_state.selected_node and "India" in view_mode:
    # If a node is selected, split the screen
    col_map, col_panel = st.columns([6, 4], gap="large")
else:
    # If no node is selected, map is full width
    col_map = st.container()
    col_panel = st.empty()

with col_map:
    # Base Nodes
    layers = [
        pdk.Layer("IconLayer", active_df, get_icon="icon_data", get_size=4, size_scale=12, get_position=["lon", "lat"], get_color="color", pickable=True, id="facility_pins")
    ]

    # --- DYNAMIC ROUTES (Draws Dotted Lines when Clicked) ---
    if st.session_state.selected_node:
        n = st.session_state.selected_node
        f_coord = [n['lon'], n['lat']]
        
        # Professional Dotted Bezier Curves
        route_data = [
            {"path": generate_curve([n['w_lon'], n['w_lat']], f_coord, 0.15), "color": [0, 200, 255]}, # Water = Cyan
            {"path": generate_curve([n['m_lon'], n['m_lat']], f_coord, -0.2), "color": [255, 255, 255]}, # Material = White
            {"path": generate_curve([n['l_lon'], n['l_lat']], f_coord, -0.1), "color": [255, 200, 0]}  # Labor = Yellow
        ]
        res_data = [
            {"name": "Water", "lon": n['w_lon'], "lat": n['w_lat'], "color": [0, 200, 255]},
            {"name": "Material", "lon": n['m_lon'], "lat": n['m_lat'], "color": [255, 255, 255]},
            {"name": "Labor", "lon": n['l_lon'], "lat": n['l_lat'], "color": [255, 200, 0]}
        ]
        
        # Add PathLayer (Dotted) and Scatterplot (Source Nodes)
        layers.append(pdk.Layer("PathLayer", pd.DataFrame(route_data), get_path="path", get_color="color", width_scale=20, width_min_pixels=3, get_dash_array=[8, 12], dash_justified=True))
        layers.append(pdk.Layer("ScatterplotLayer", pd.DataFrame(res_data), get_position=["lon", "lat"], get_fill_color="color", get_radius=3000, stroked=True, get_line_color=[0, 0, 0]))

        # Smooth camera zoom to the selected node
        init_view = pdk.ViewState(latitude=n['lat'], longitude=n['lon'], zoom=6.5, pitch=0)

    # Render Map
    map_event = st.pydeck_chart(
        pdk.Deck(
            layers=layers, 
            initial_view_state=init_view,
            map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
            tooltip={"text": "{name}\n{cap} Cap"}
        ),
        on_select="rerun",
        selection_mode="single-object"
    )

    # Handle Click Events
    if map_event and map_event.selection.objects and "India" in view_mode:
        if "facility_pins" in map_event.selection.objects:
            clicked_data = map_event.selection.objects["facility_pins"]
            if clicked_data and st.session_state.selected_node != clicked_data[0]:
                st.session_state.selected_node = clicked_data[0]
                st.rerun()

# --- 7. THE TECHNICAL DOSSIER PANEL ---
if st.session_state.selected_node and "India" in view_mode:
    with col_panel:
        n = st.session_state.selected_node
        
        # Back Button
        if st.button("🔙 Return to Map Overview", use_container_width=True):
            clear_selection()
            st.rerun()
            
        st.image(n['img'], use_container_width=True)
        st.header(n['name'])
        st.markdown(f"**Classification:** `{n['cap']} Cap`  |  **Sovereign Benchmark:** `{n['bt']}`")
        st.markdown("---")
        
        # ALTAIR GRAPH (Distance vs Elevation)
        st.subheader("🏔️ Discretized Elevation Profile")
        # Generate X-axis data based on total material-to-water distance approximation
        total_points = len(n['profile'])
        x_dist = np.linspace(0, n['m_dist'] + n['w_dist'], total_points)
        chart_df = pd.DataFrame({"Distance (km)": x_dist, "Elevation (MSL)": n['profile']})
        
        base = alt.Chart(chart_df).encode(x=alt.X('Distance (km):Q', title=f"Distance (0km = {n['m_name']})"), y=alt.Y('Elevation (MSL):Q', scale=alt.Scale(domain=[0, max(n['profile'])+50])))
        area = base.mark_area(opacity=0.5, color="#2563eb")
        line = base.mark_line(color="#60a5fa", strokeWidth=3)
        st.altair_chart(area + line, use_container_width=True)

        st.markdown("---")

        # STRATEGIC METRICS
        st.markdown("<div class='metric-box'><div class='metric-title'>Topographical Stabilization (Elevation & Friction)</div>"
                    f"<div class='metric-text'>{n['desc_elev']}</div></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='metric-box'><div class='metric-title'>Logistics Matrix (LCP: " + str(n['lcp']) + ")</div>"
                    f"<div class='metric-text'><b>Raw Material:</b> {n['m_name']} ({n['m_dist']}km route)<br>"
                    f"<b>Water Hub:</b> {n['w_name']} ({n['w_dist']}km route)<br><br>{n['desc_log']}</div></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='metric-box'><div class='metric-title'>Strategic Topographical Index (STI: " + str(n['sti']) + "%)</div>"
                    f"<div class='metric-text'><b>Labor Node:</b> {n['l_name']} ({n['l_dist']}km route)<br><br>{n['desc_sti']}</div></div>", unsafe_allow_html=True)
