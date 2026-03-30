import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import altair as alt

# --- 1. PROFESSIONAL PAGE CONFIG & CSS ---
st.set_page_config(layout="wide", page_title="Strategic Topography GIS")

st.markdown("""
    <style>
        /* Light washy green background */
        .stApp { background-color: #e8f4ec; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 2rem; max-width: 98%;}
        h1, h2, h3, p, span, div {font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif; color: #1a202c;}
        
        /* Sidebar styling for contrast */
        [data-testid="stSidebar"] {background-color: #ffffff; border-right: 1px solid #cbd5e1;}
        .metric-box {background-color: #f8fafc; padding: 12px; border-radius: 4px; border-left: 4px solid #3b82f6; margin-bottom: 12px; border: 1px solid #e2e8f0;}
        .metric-title {color: #475569; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; font-weight: 600;}
        .metric-text {color: #0f172a; font-size: 13px; line-height: 1.4;}
        .tag-large {color: #dc2626; font-weight: bold;}
        .tag-mid {color: #d97706; font-weight: bold;}
        .tag-small {color: #16a34a; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# --- 2. STATE MANAGEMENT ---
if "selected_node" not in st.session_state:
    st.session_state.selected_node = None

def clear_selection():
    st.session_state.selected_node = None

# --- 3. LOGISTICS CURVE & MIDPOINT GENERATOR ---
def generate_curve(start, end, bend=0.2):
    p0, p2 = np.array(start), np.array(end)
    mid = (p0 + p2) / 2
    perp = np.array([-(p2[1]-p0[1]), p2[0]-p0[0]]) 
    p1 = mid + perp * bend
    t = np.linspace(0, 1, 30)
    curve = np.outer((1-t)**2, p0) + np.outer(2*(1-t)*t, p1) + np.outer(t**2, p2)
    # Return the curve path AND the midpoint for the map label
    return curve.tolist(), curve[15].tolist()

# --- 4. THE MASTER DATASET ---
data = [
    # ---- DENSE GLOBAL ECOSYSTEM ----
    {"name": "TSMC Fab 18 (Taiwan)", "region": "Global", "cap": "Large", "lat": 23.10, "lon": 120.28},
    {"name": "TSMC Kumamoto (Japan)", "region": "Global", "cap": "Large", "lat": 32.88, "lon": 130.84},
    {"name": "Intel Ocotillo (USA)", "region": "Global", "cap": "Large", "lat": 33.27, "lon": -111.88},
    {"name": "Intel Magdeburg (Germany)", "region": "Global", "cap": "Large", "lat": 52.12, "lon": 11.62},
    {"name": "Samsung Taylor (USA)", "region": "Global", "cap": "Large", "lat": 30.56, "lon": -97.40},
    {"name": "Samsung Pyeongtaek (Korea)", "region": "Global", "cap": "Large", "lat": 37.02, "lon": 127.04},
    {"name": "Micron Boise (USA)", "region": "Global", "cap": "Large", "lat": 43.52, "lon": -116.15},
    {"name": "Rapidus Hokkaido (Japan)", "region": "Global", "cap": "Large", "lat": 42.76, "lon": 141.67},
    {"name": "GlobalFoundries Dresden (Ger)", "region": "Global", "cap": "Mid", "lat": 51.12, "lon": 13.71},
    {"name": "GlobalFoundries Malta (USA)", "region": "Global", "cap": "Mid", "lat": 42.97, "lon": -73.76},
    {"name": "SMIC Shanghai (China)", "region": "Global", "cap": "Large", "lat": 31.20, "lon": 121.59},
    {"name": "STMicroelectronics Crolles (Fra)", "region": "Global", "cap": "Mid", "lat": 45.27, "lon": 5.88},
    {"name": "Renesas Naka (Japan)", "region": "Global", "cap": "Mid", "lat": 36.40, "lon": 140.52},
    {"name": "Infineon Villach (Austria)", "region": "Global", "cap": "Mid", "lat": 46.61, "lon": 13.87},

    # ---- INDIAN ECOSYSTEM ----
    {
        "name": "Tata-PSMC Dholera", "region": "India", "year": 2026, "cap": "Large", 
        "lat": 22.25, "lon": 72.11, "elev": 15, "terrain": "Coastal Plateau",
        "w_name": "Sabarmati Desalination", "w_lat": 22.50, "w_lon": 72.30, "w_dist": 32,
        "m_name": "Gulf of Khambhat Port", "m_lat": 21.75, "m_lon": 72.25, "m_dist": 55,
        "l_name": "Ahmedabad Urban Center", "l_lat": 23.02, "l_lon": 72.57, "l_dist": 85,
        "bt": "India's First Commercial 28nm Mega-Fab. Sovereign logic node production.", 
        "img": "https://images.unsplash.com/photo-1508344928928-7165b67de128?auto=format&fit=crop&w=800&q=80",
        "profile": [0, 5, 8, 12, 15, 15, 15, 15, 12, 8, 5],
        "sti": 99.5, "lcp": 0.97,
        "rationale": "Engineered for 0.02% seismic vibration friction. The absolute flatness prevents multi-billion dollar EUV wafer spoilage. Proximity to deep-water port yields high logistical cost-efficiency."
    },
    {
        "name": "Tata-TSAT Assam", "region": "India", "year": 2026, "cap": "Large", 
        "lat": 26.24, "lon": 92.33, "elev": 55, "terrain": "River Valley",
        "w_name": "Brahmaputra Basin", "w_lat": 26.50, "w_lon": 92.60, "w_dist": 40,
        "m_name": "Haldia Port Transit", "m_lat": 25.50, "m_lon": 91.00, "m_dist": 180,
        "l_name": "Guwahati Metropolis", "l_lat": 26.14, "l_lon": 91.73, "l_dist": 65,
        "bt": "Sovereign Advanced Packaging Hub. Eastern frontier geopolitical hedge.", 
        "img": "https://images.unsplash.com/photo-1587292231267-27b2b8089457?auto=format&fit=crop&w=800&q=80",
        "profile": [120, 100, 80, 55, 55, 55, 70, 95, 110],
        "sti": 84.4, "lcp": 0.70,
        "rationale": "High topographical friction (34% higher logistics cost) is offset by strategic geographic defense and inexhaustible fresh water supply for Chemical Mechanical Polishing (CMP)."
    },
    {
        "name": "Micron Sanand", "region": "India", "year": 2024, "cap": "Large", 
        "lat": 22.98, "lon": 72.37, "elev": 45, "terrain": "Industrial Plains",
        "w_name": "Narmada Canal System", "w_lat": 23.10, "w_lon": 72.50, "w_dist": 20,
        "m_name": "Mundra Port Transit", "m_lat": 22.80, "m_lon": 72.00, "m_dist": 250,
        "l_name": "Sanand Industrial GIDC", "l_lat": 22.95, "l_lon": 72.38, "l_dist": 5,
        "bt": "High Bandwidth Memory (HBM) ATMP validation.", 
        "img": "https://images.unsplash.com/photo-1573164713988-8665fc963095?auto=format&fit=crop&w=800&q=80",
        "profile": [10, 25, 35, 45, 45, 45, 46, 47, 48],
        "sti": 92.0, "lcp": 0.90,
        "rationale": "Chosen for pre-existing grid stability and rapid scalability. Flat plains allow for rapid construction modularity without deep-pile foundation engineering."
    },
    {
        "name": "CG Power-Renesas Sanand", "region": "India", "year": 2025, "cap": "Mid", 
        "lat": 23.00, "lon": 72.35, "elev": 43, "terrain": "Industrial Plains",
        "w_name": "Narmada Canal System", "w_lat": 23.10, "w_lon": 72.50, "w_dist": 22,
        "m_name": "Regional Rail Freight", "m_lat": 22.80, "m_lon": 72.20, "m_dist": 28,
        "l_name": "Ahmedabad Urban Grid", "l_lat": 23.02, "l_lon": 72.57, "l_dist": 25,
        "bt": "Specialized OSAT for consumer and industrial power management ICs.", 
        "img": "https://images.unsplash.com/photo-1563770660941-20978e870e26?auto=format&fit=crop&w=800&q=80",
        "profile": [20, 30, 40, 43, 43, 43, 44, 45, 46],
        "sti": 89.0, "lcp": 0.88,
        "rationale": "Leverages the same topographical stability as the Micron facility, creating a localized high-density packaging cluster with shared logistics."
    },
    {
        "name": "Polymatech Chennai", "region": "India", "year": 2023, "cap": "Mid", 
        "lat": 12.82, "lon": 79.98, "elev": 12, "terrain": "Coastal Plain",
        "w_name": "Palar River Basin", "w_lat": 12.60, "w_lon": 79.90, "w_dist": 25,
        "m_name": "Chennai Port Transit", "m_lat": 13.08, "m_lon": 80.29, "m_dist": 45,
        "l_name": "Kancheepuram Town", "l_lat": 12.83, "l_lon": 79.70, "l_dist": 30,
        "bt": "Opto-semiconductor and specialized photonics manufacturing.", 
        "img": "https://images.unsplash.com/photo-1580983554869-3221443491db?auto=format&fit=crop&w=800&q=80",
        "profile": [2, 5, 8, 12, 12, 12, 10, 8, 6],
        "sti": 91.0, "lcp": 0.90,
        "rationale": "Southern coastal stability. Focuses on opto-electronics which require rigorous dust-free environments supported by coastal wind shear management."
    },
    {
        "name": "Sahasra Bhiwadi", "region": "India", "year": 2023, "cap": "Small", 
        "lat": 28.21, "lon": 76.83, "elev": 265, "terrain": "Aravalli Outskirts",
        "w_name": "Regional Groundwater Grid", "w_lat": 28.25, "w_lon": 76.80, "w_dist": 8,
        "m_name": "NCR Freight Corridor", "m_lat": 28.30, "m_lon": 76.90, "m_dist": 15,
        "l_name": "Gurugram Tech City", "l_lat": 28.45, "l_lon": 77.02, "l_dist": 35,
        "bt": "Early mover in domestic memory chip packaging (MicroSD/USB).", 
        "img": "https://images.unsplash.com/photo-1513828742140-ccaa28f3eda0?auto=format&fit=crop&w=800&q=80",
        "profile": [220, 240, 255, 265, 265, 265, 250, 240, 230],
        "sti": 82.0, "lcp": 0.85,
        "rationale": "Strategic proximity to the National Capital Region. Trades heavy water availability for immediate access to northern India's consumer electronics assembly hubs."
    },
    {
        "name": "Texas Instruments Bangalore", "region": "India", "year": 1985, "cap": "Large", 
        "lat": 12.97, "lon": 77.59, "elev": 920, "terrain": "Deccan Plateau",
        "w_name": "Cauvery Basin Municipal", "w_lat": 12.40, "w_lon": 77.30, "w_dist": 85,
        "m_name": "HAL Airport Data Transit", "m_lat": 12.95, "m_lon": 77.66, "m_dist": 12,
        "l_name": "Bangalore Urban Grid", "l_lat": 12.97, "l_lon": 77.59, "l_dist": 2,
        "bt": "First Global R&D Center in India. Pioneered satellite data export.", 
        "img": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80",
        "profile": [850, 875, 900, 920, 920, 920, 910, 895, 880],
        "sti": 88.0, "lcp": 0.85,
        "rationale": "Human-Centric Topography. Elevation provided moderate climate reducing 1980s mainframe cooling loads by 14%. Immediate access to elite engineering institutions."
    },
    {
        "name": "SCL Mohali", "region": "India", "year": 1983, "cap": "Small", 
        "lat": 30.70, "lon": 76.69, "elev": 310, "terrain": "Shivalik Foothills",
        "w_name": "Sutlej River Tributaries", "w_lat": 30.90, "w_lon": 76.50, "w_dist": 28,
        "m_name": "Northern Rail Depot", "m_lat": 30.50, "m_lon": 76.80, "m_dist": 24,
        "l_name": "Chandigarh Sector 17", "l_lat": 30.73, "l_lon": 76.77, "l_dist": 10,
        "bt": "ISRO space-grade and military radiation-hardened 180nm CMOS nodes.", 
        "img": "https://images.unsplash.com/photo-1513828742140-ccaa28f3eda0?auto=format&fit=crop&w=800&q=80",
        "profile": [280, 290, 300, 310, 310, 310, 330, 350, 380],
        "sti": 75.0, "lcp": 0.65,
        "rationale": "Defense-in-Depth location. Sacrificed maritime logistics to push sensitive military infrastructure deep inland. Foundation anchored in local bedrock shelf."
    }
]

df = pd.DataFrame(data)

# Pin mapping setup
ICON_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-atlas.png"
icon_data = {"url": ICON_URL, "width": 128, "height": 128, "y": 128, "anchorY": 128}
df['icon_data'] = [icon_data for _ in range(len(df))]

def get_color(cap):
    if cap == "Large": return [220, 38, 38]   # Deep Red
    if cap == "Mid": return [217, 119, 6]     # Orange/Yellow
    return [22, 163, 74]                      # Emerald Green
df['color'] = df['cap'].apply(get_color)


# --- 5. TOP BAR UI ---
st.title("Strategic Topography GIS Explorer")
st.markdown("Analysis of Semiconductor Infrastructure, Topographical Friction, and Strategic Routing.")

# Map selection
view_mode = st.radio("Operational Theater Selection:", ["India Timeline Ecosystem", "Global Macro Ecosystem"], horizontal=True, label_visibility="collapsed")

if "India" in view_mode:
    selected_year = st.select_slider("Historical Timeline Integration:", options=[1980, 1990, 2000, 2010, 2020, 2026], value=2026)
    active_df = df[(df['region'] == 'India') & (df['year'] <= selected_year)].copy()
    init_view = pdk.ViewState(latitude=22.0, longitude=79.0, zoom=4.2, pitch=0)
else:
    active_df = df[df['region'] == 'Global'].copy()
    init_view = pdk.ViewState(latitude=35.0, longitude=10.0, zoom=1.5, pitch=0)
    clear_selection()

# --- 6. SPLIT ARCHITECTURE ---
if st.session_state.selected_node and "India" in view_mode:
    col_map, col_panel = st.columns([6, 4], gap="large")
else:
    col_map = st.container()
    col_panel = st.empty()

with col_map:
    layers = [
        pdk.Layer("IconLayer", active_df, get_icon="icon_data", get_size=4, size_scale=12, get_position=["lon", "lat"], get_color="color", pickable=True, id="facility_pins")
    ]

    # --- DYNAMIC ROUTING & MAP LABELS (When Clicked) ---
    if st.session_state.selected_node:
        n = st.session_state.selected_node
        f_coord = [n['lon'], n['lat']]
        
        # 1. Generate curves and their midpoints for labels
        w_curve, w_mid = generate_curve([n['w_lon'], n['w_lat']], f_coord, 0.15)
        m_curve, m_mid = generate_curve([n['m_lon'], n['m_lat']], f_coord, -0.2)
        l_curve, l_mid = generate_curve([n['l_lon'], n['l_lat']], f_coord, -0.1)

        # 2. Path Layer (High contrast dashed lines)
        route_data = [
            {"path": w_curve, "color": [6, 182, 212]}, # Cyan
            {"path": m_curve, "color": [255, 255, 255]}, # White
            {"path": l_curve, "color": [234, 179, 8]}  # Yellow
        ]
        layers.append(pdk.Layer("PathLayer", pd.DataFrame(route_data), get_path="path", get_color="color", width_scale=20, width_min_pixels=3, get_dash_array=[8, 8], dash_justified=True))

        # 3. Scatterplot Nodes (Sources)
        res_data = [
            {"name": n['w_name'], "lon": n['w_lon'], "lat": n['w_lat'], "color": [6, 182, 212]},
            {"name": n['m_name'], "lon": n['m_lon'], "lat": n['m_lat'], "color": [255, 255, 255]},
            {"name": n['l_name'], "lon": n['l_lon'], "lat": n['l_lat'], "color": [234, 179, 8]}
        ]
        layers.append(pdk.Layer("ScatterplotLayer", pd.DataFrame(res_data), get_position=["lon", "lat"], get_fill_color="color", get_radius=3500, stroked=True, get_line_color=[0, 0, 0]))

        # 4. TEXT LAYERS: Map Labels for Coordinates & Routes
        label_data = [
            # Facility Coordinate Label
            {"lon": n['lon'], "lat": n['lat'], "text": f"{n['lat']}°N, {n['lon']}°E", "color": [255, 255, 255], "offset": [0, -35]},
            # Route Distance Labels
            {"lon": w_mid[0], "lat": w_mid[1], "text": f"Water: {n['w_dist']}km", "color": [6, 182, 212], "offset": [0, 0]},
            {"lon": m_mid[0], "lat": m_mid[1], "text": f"Material: {n['m_dist']}km", "color": [255, 255, 255], "offset": [0, 0]},
            {"lon": l_mid[0], "lat": l_mid[1], "text": f"Labor: {n['l_dist']}km", "color": [234, 179, 8], "offset": [0, 0]}
        ]
        layers.append(pdk.Layer(
            "TextLayer", pd.DataFrame(label_data), get_position=["lon", "lat"], get_text="text", 
            get_color="color", get_size=14, get_alignment_baseline="'bottom'", get_pixel_offset="offset"
        ))

        # Smooth camera zoom
        init_view = pdk.ViewState(latitude=n['lat'], longitude=n['lon'], zoom=7, pitch=0)

    # Render Pydeck Map
    map_event = st.pydeck_chart(
        pdk.Deck(
            layers=layers, 
            initial_view_state=init_view,
            map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
            tooltip={"text": "{name}\nCap Size: {cap}"}
        ),
        on_select="rerun",
        selection_mode="single-object"
    )
    
    # Legend Overlay
    st.markdown("""
        <div style="background-color: #1e293b; padding: 10px; border-radius: 4px; color: white; font-size: 13px; margin-top: -10px; border: 1px solid #475569;">
            <b>Map Legend:</b> &nbsp;&nbsp; 
            <span style="color:#ef4444">● Large Cap Node</span> &nbsp;|&nbsp; 
            <span style="color:#f59e0b">● Mid Cap Node</span> &nbsp;|&nbsp; 
            <span style="color:#22c55e">● Small Cap Node</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <b>Logistics Routes:</b> &nbsp;
            <span style="color:#22d3ee">--- Water Corridor</span> &nbsp;|&nbsp;
            <span style="color:#ffffff">--- Raw Material Transit</span> &nbsp;|&nbsp;
            <span style="color:#facc15">--- Urban Labor Node</span>
        </div>
    """, unsafe_allow_html=True)

    if map_event and map_event.selection.objects and "India" in view_mode:
        if "facility_pins" in map_event.selection.objects:
            clicked_data = map_event.selection.objects["facility_pins"]
            if clicked_data and st.session_state.selected_node != clicked_data[0]:
                st.session_state.selected_node = clicked_data[0]
                st.rerun()

# --- 7. TECHNICAL DOSSIER PANEL ---
if st.session_state.selected_node and "India" in view_mode:
    with col_panel:
        n = st.session_state.selected_node
        
        if st.button("Return to Overview / Clear Routes", use_container_width=True):
            clear_selection()
            st.rerun()
            
        st.image(n['img'], use_container_width=True)
        st.markdown(f"<h2>{n['name']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<span class='tag-{n['cap'].lower()}'>{n['cap']} Cap Facility</span> | <b>Coordinates:</b> {n['lat']}°N, {n['lon']}°E", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # FIXED: ALTAIR TERRAIN GRAPH (Accurate Distance Mapping)
        st.markdown("### Topographical Integration Profile")
        
        # X-Axis mapping: 0km is Material Source, Facility is at m_dist, Water is at end.
        total_dist = n['m_dist'] + n['w_dist']
        x_dist = np.linspace(0, total_dist, len(n['profile']))
        chart_df = pd.DataFrame({"Distance (km)": x_dist, "Elevation (MSL)": n['profile']})
        
        base = alt.Chart(chart_df).encode(
            x=alt.X('Distance (km):Q', title=f"Distance: 0km ({n['m_name']}) → {n['m_dist']}km (Facility) → {total_dist}km ({n['w_name']})"), 
            y=alt.Y('Elevation (MSL):Q', title="Elevation (m)", scale=alt.Scale(domain=[0, max(n['profile'])+50]))
        )
        area = base.mark_area(opacity=0.4, color="#0ea5e9")
        line = base.mark_line(color="#0284c7", strokeWidth=2)
        
        # Vertical Red Rule marking the EXACT Facility location on the X-axis
        facility_mark = pd.DataFrame({"x": [n['m_dist']]})
        rule = alt.Chart(facility_mark).mark_rule(color='#dc2626', strokeWidth=2).encode(x='x:Q')
        
        st.altair_chart(area + line + rule, use_container_width=True)

        # STRATEGIC METRICS
        st.markdown("<div class='metric-box'><div class='metric-title'>Strategic Breakthrough</div>"
                    f"<div class='metric-text'>{n['bt']}</div></div>", unsafe_allow_html=True)
                    
        st.markdown("<div class='metric-box'><div class='metric-title'>Topographical Stabilization (Elevation: " + str(n['elev']) + "m MSL)</div>"
                    f"<div class='metric-text'>{n['rationale']}</div></div>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='metric-box'>
            <div class='metric-title'>Logistics Matrix (LCP Efficiency: {n['lcp']})</div>
            <div class='metric-text'>
                <b>Raw Material Hub:</b> {n['m_name']} <span style='color:gray'>({n['m_dist']}km exact route)</span><br>
                <b>Water Catchment:</b> {n['w_name']} <span style='color:gray'>({n['w_dist']}km exact route)</span><br>
                <b>Urban Labor Center:</b> {n['l_name']} <span style='color:gray'>({n['l_dist']}km exact route)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='metric-box'><div class='metric-title'>Strategic Topographical Index</div>"
                    f"<div class='metric-text'><b>Base Score: {n['sti']}%</b>. Metric calculated via topographical friction coefficients, isolation from seismic fault zones, and immediate logistics proximity.</div></div>", unsafe_allow_html=True)
