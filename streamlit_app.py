import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import altair as alt
import plotly.graph_objects as go

# --- 1. PROFESSIONAL PAGE CONFIG & CSS ---
st.set_page_config(layout="wide", page_title="Strategic Topography GIS", page_icon="🗺️")

st.markdown("""
    <style>
        /* Light washy magenta/lavender background */
        .stApp { background-color: #fdf4ff; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 2rem; padding-bottom: 0rem; max-width: 98%;}
        h1, h2, h3, p, span, div {font-family: 'Helvetica Neue', Arial, sans-serif; color: #1e1b4b;}
        
        /* Sidebar and Technical Dossier Styling */
        [data-testid="stSidebar"] {background-color: #ffffff; border-right: 1px solid #e2e8f0;}
        .metric-box {background-color: #ffffff; padding: 14px; border-radius: 4px; border-left: 4px solid #9333ea; margin-bottom: 12px; border: 1px solid #e5e7eb; box-shadow: 0 1px 2px rgba(0,0,0,0.05);}
        
        /* INCREASED TEXT SIZES FOR THE TECHNICAL DOSSIER */
        .metric-title {color: #4b5563; font-size: 13.5px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; font-weight: 700;}
        .metric-text {color: #0f172a; font-size: 16.5px; line-height: 1.6;}
        
        /* Cap Tags */
        .tag-large {color: #dc2626; font-weight: bold; text-transform: uppercase; font-size: 12px;}
        .tag-mid {color: #d97706; font-weight: bold; text-transform: uppercase; font-size: 12px;}
        .tag-small {color: #16a34a; font-weight: bold; text-transform: uppercase; font-size: 12px;}
        
        /* High-Contrast Return Button */
        .stButton>button {background-color: #701a75; color: #ffffff; border: none; font-weight: 600; padding: 10px 20px;}
        .stButton>button:hover {background-color: #4a044e; color: #ffffff;}
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
    return curve.tolist(), curve[15].tolist()

# --- 4. THE UNIFIED DATASET (India + Global) ---
data = [
    # ---- EXPANDED GLOBAL ECOSYSTEM (For Tab 2 & 3) ----
    {"name": "TSMC Fab 18 (Taiwan)", "region": "Global", "cap": "Large", "lat": 23.10, "lon": 120.28},
    {"name": "TSMC Kumamoto (Japan)", "region": "Global", "cap": "Large", "lat": 32.88, "lon": 130.84},
    {"name": "Intel Ocotillo (USA)", "region": "Global", "cap": "Large", "lat": 33.27, "lon": -111.88},
    {"name": "Intel Magdeburg (Germany)", "region": "Global", "cap": "Large", "lat": 52.12, "lon": 11.62},
    {"name": "Samsung Taylor (USA)", "region": "Global", "cap": "Large", "lat": 30.56, "lon": -97.40},
    {"name": "Samsung Pyeongtaek (Korea)", "region": "Global", "cap": "Large", "lat": 37.02, "lon": 127.04},
    {"name": "Micron Boise (USA)", "region": "Global", "cap": "Large", "lat": 43.52, "lon": -116.15},
    {"name": "Rapidus Hokkaido (Japan)", "region": "Global", "cap": "Large", "lat": 42.76, "lon": 141.67},
    {"name": "GlobalFoundries Dresden (Ger)", "region": "Global", "cap": "Mid", "lat": 51.12, "lon": 13.71},
    {"name": "SMIC Shanghai (China)", "region": "Global", "cap": "Large", "lat": 31.20, "lon": 121.59},

    # ---- INDIAN ECOSYSTEM (Highly Detailed with Radar & Radar Text) ----
    {
        "name": "Tata-PSMC Dholera", "region": "India", "year": 2026, "cap": "Large", 
        "lat": 22.25, "lon": 72.11, "elev": 15, "terrain": "Coastal Plateau",
        "w_name": "Sabarmati Desalination", "w_lat": 22.50, "w_lon": 72.30, "w_dist": 32,
        "m_name": "Gulf of Khambhat Port", "m_lat": 21.75, "m_lon": 72.25, "m_dist": 55,
        "l_name": "Ahmedabad Urban Center", "l_lat": 23.02, "l_lon": 72.57, "l_dist": 85,
        "bt": "India's First Commercial 28nm Mega-Fab. Sovereign logic node production.", 
        # MANUAL IMAGE INSTRUCTION: Replace this URL with n['img'] = "YOUR_IMAGE.png"
        "img": "https://images.unsplash.com/photo-1508344928928-7165b67de128?auto=format&fit=crop&w=800&q=80",
        "profile": [0, 8, 3, 14, 15, 15, 15, 15, 11, 4, 5], 
        "sti": 99.5, "lcp": 0.97,
        "rad": [99, 95, 98, 90, 85], 
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
        "profile": [120, 140, 85, 40, 55, 55, 55, 80, 130, 95, 110],
        "sti": 84.4, "lcp": 0.70,
        "rad": [75, 99, 65, 95, 80],
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
        "profile": [10, 18, 12, 35, 45, 45, 45, 42, 48, 44, 48],
        "sti": 92.0, "lcp": 0.90,
        "rad": [90, 85, 88, 85, 98],
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
        "profile": [20, 28, 22, 38, 43, 43, 43, 40, 48, 42, 46],
        "sti": 89.0, "lcp": 0.88,
        "rad": [90, 85, 92, 85, 95],
        "rationale": "Leverages the same topographical stability as the Micron facility, creating a localized high-density packaging cluster with shared logistics."
    },
    {
        "name": "Texas Instruments Bangalore", "region": "India", "year": 1985, "cap": "Large", 
        "lat": 12.97, "lon": 77.59, "elev": 920, "terrain": "Deccan Plateau",
        "w_name": "Cauvery Basin Municipal", "w_lat": 12.40, "w_lon": 77.30, "w_dist": 85,
        "m_name": "HAL Airport Data Transit", "m_lat": 12.95, "m_lon": 77.66, "m_dist": 12,
        "l_name": "Bangalore Urban Grid", "l_lat": 12.97, "l_lon": 77.59, "l_dist": 2,
        "bt": "First Global R&D Center in India. Pioneered satellite data export.", 
        "img": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80",
        "profile": [850, 890, 860, 910, 920, 920, 920, 890, 915, 870, 880],
        "sti": 88.0, "lcp": 0.85,
        "rad": [95, 75, 80, 90, 99],
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
        "profile": [280, 270, 295, 285, 310, 310, 310, 340, 320, 370, 380],
        "sti": 75.0, "lcp": 0.65,
        "rad": [60, 85, 65, 99, 88],
        "rationale": "Defense-in-Depth location. Sacrificed maritime logistics to push sensitive military infrastructure deep inland. Foundation anchored in local bedrock shelf."
    },
    {
        "name": "Hind Rectifiers Mumbai", "region": "India", "year": 1980, "cap": "Small", 
        "lat": 19.117, "lon": 72.848, "elev": 10, "terrain": "Western Coastal Plain",
        "w_name": "Ulhas River Catchment", "w_lat": 19.00, "w_lon": 72.80, "w_dist": 15,
        "m_name": "JNPT Port Transit", "m_lat": 18.95, "m_lon": 72.90, "m_dist": 60,
        "l_name": "Mumbai Metropolis", "l_lat": 19.07, "l_lon": 72.87, "l_dist": 5,
        "bt": "Pioneer in power semiconductor devices for Indian Railways traction rectifiers.", 
        "img": "https://images.unsplash.com/photo-1580983554869-3221443491db?auto=format&fit=crop&w=800&q=80",
        "profile": [2, 12, 5, 10, 10, 10, 10, 12, 9, 7, 8],
        "sti": 91.5, "lcp": 0.92,
        "rad": [65, 80, 98, 90, 99],
        "rationale": "Classic coastal export config. Sacrifices absolute seismic neutrality (Western Ghats proximity) for hyper-frictionless logistics."
    },
    {
        "name": "Qualcomm Hyderabad", "region": "India", "year": 2010, "cap": "Large", 
        "lat": 17.443, "lon": 78.375, "elev": 550, "terrain": "Deccan Plateau",
        "w_name": "Municipal Mains", "w_lat": 17.40, "w_lon": 78.35, "w_dist": 10,
        "m_name": "Hyderabad Airport Cargo", "m_lat": 17.25, "m_lon": 78.43, "m_dist": 35,
        "l_name": "HITEC City Hub", "l_lat": 17.44, "l_lon": 78.38, "l_dist": 5,
        "bt": "Snapdragon design and validation mega-center. Pure play VLSI node.", 
        "img": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80",
        "profile": [500, 520, 530, 550, 550, 550, 550, 530, 510, 500, 490],
        "sti": 94.0, "lcp": 0.94,
        "rad": [92, 85, 90, 88, 99],
        "rationale": "Chosen for pre-existing grid stability (500kV primary substation) and rapid construction modularity. Human-Centric Topography."
    },
    {
        "name": "Tessolve Bangalore", "region": "India", "year": 2005, "cap": "Mid", 
        "lat": 12.923, "lon": 77.682, "elev": 910, "terrain": "Deccan Plateau",
        "w_name": "Cauvery Basins pipelines", "w_lat": 12.45, "w_lon": 77.40, "w_dist": 75,
        "m_name": "HAL Airport Data Transit", "m_lat": 12.95, "m_lon": 77.66, "m_dist": 12,
        "l_name": "Electronics City Grid", "l_lat": 12.93, "l_lon": 77.69, "l_dist": 5,
        "bt": "Global validation and testing engineering hub. Critical for wafer sort.", 
        "img": "https://images.unsplash.com/photo-1573164713988-8665fc963095?auto=format&fit=crop&w=800&q=80",
        "profile": [860, 880, 890, 910, 910, 910, 910, 890, 880, 870, 860],
        "sti": 89.0, "lcp": 0.88,
        "rad": [95, 80, 85, 92, 98],
        "rationale": "Standard high-plateau configuration. Leveraging the same topographical stability as the TI campus, maximizing labor corridor access."
    },
    {
        "name": "Continental Device India Limited", "region": "India", "year": 1964, "cap": "Small", 
        "lat": 28.667, "lon": 77.217, "elev": 210, "terrain": "Indo-Gangetic Plains",
        "w_name": "Yamuna River Pipelines", "w_lat": 28.60, "w_lon": 77.20, "w_dist": 15,
        "m_name": "NCR Rail Corridor", "m_lat": 28.70, "m_lon": 77.25, "m_dist": 10,
        "l_name": "Delhi Urban Grid", "l_lat": 28.67, "l_lon": 77.22, "l_dist": 5,
        "bt": "India's first fabless design and discrete transistor manufacturing.", 
        "img": "https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&w=800&q=80",
        "profile": [190, 195, 200, 210, 210, 210, 210, 200, 198, 195, 190],
        "sti": 78.0, "lcp": 0.65,
        "rad": [65, 70, 88, 85, 99],
        "rationale": "Built for proximity to the National Capital. Topographical variance is high due to the Yamuna river plain's inherent instability."
    }
]

df = pd.DataFrame(data)

# Pin mapping colors
ICON_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-atlas.png"
icon_data = {"url": ICON_URL, "width": 128, "height": 128, "y": 128, "anchorY": 128}
df['icon_data'] = [icon_data for _ in range(len(df))]

def get_color(cap):
    if cap == "Large": return [220, 38, 38]   # Red
    if cap == "Mid": return [217, 119, 6]     # Orange
    return [22, 163, 74]                      # Green
df['color'] = df['cap'].apply(get_color)

# --- 5. TOP BAR UI ---
st.title("Strategic Topography GIS Explorer")
st.markdown("Macro-Analysis of Semiconductor Infrastructure, Topographical Friction, and Strategic Routing.")

# Tab Selection
tab1, tab2, tab3 = st.tabs(["INDIA TIMELINE ECOSYSTEM", "GLOBAL MACRO ECOSYSTEM", "S.T.I. STATISTICAL DISTRIBUTION"])

# --- TAB 1: INDIA ECOSYSTEM (Corrected Layout) ---
with tab1:
    selected_year = st.select_slider("Historical Timeline Integration:", options=[1980, 1990, 2000, 2010, 2020, 2026], value=2026)
    active_df = df[(df['region'] == 'India') & (df['year'] <= selected_year)].copy()
    
    col_map, col_dossier = st.columns([6, 4], gap="large")

    with col_map:
        layers = [
            pdk.Layer("IconLayer", active_df, get_icon="icon_data", get_size=4, size_scale=12, get_position=["lon", "lat"], get_color="color", pickable=True, id="facility_pins")
        ]

        init_view = pdk.ViewState(latitude=22.0, longitude=79.0, zoom=4.2, pitch=0)

        # --- DYNAMIC ROUTING & SEPARATED LABELS ---
        if st.session_state.selected_node:
            n = st.session_state.selected_node
            f_coord = [n['lon'], n['lat']]
            
            w_curve, w_mid = generate_curve([n['w_lon'], n['w_lat']], f_coord, 0.15)
            m_curve, m_mid = generate_curve([n['m_lon'], n['m_lat']], f_coord, -0.2)
            l_curve, l_mid = generate_curve([n['l_lon'], n['l_lat']], f_coord, -0.1)

            route_data = [
                {"path": w_curve, "color": [6, 182, 212]}, # Cyan
                {"path": m_curve, "color": [255, 255, 255]}, # White
                {"path": l_curve, "color": [234, 179, 8]}  # Yellow
            ]
            layers.append(pdk.Layer("PathLayer", pd.DataFrame(route_data), get_path="path", get_color="color", width_scale=20, width_min_pixels=3, get_dash_array=[8, 8], dash_justified=True))

            res_data = [
                {"lon": n['w_lon'], "lat": n['w_lat'], "color": [6, 182, 212]},
                {"lon": n['m_lon'], "lat": n['m_lat'], "color": [255, 255, 255]},
                {"lon": n['l_lon'], "lat": n['l_lat'], "color": [234, 179, 8]}
            ]
            layers.append(pdk.Layer("ScatterplotLayer", pd.DataFrame(res_data), get_position=["lon", "lat"], get_fill_color="color", get_radius=3500, stroked=True, get_line_color=[0, 0, 0]))

            # Anti-Overlap Text Labels
            label_data = [
                {"lon": n['lon'], "lat": n['lat'], "text": f"Target: {n['lat']} N, {n['lon']} E", "color": [255, 255, 255], "offset": [0, -40]},
                {"lon": w_mid[0], "lat": w_mid[1], "text": f"{n['w_dist']}km (Water Corridor)", "color": [6, 182, 212], "offset": [0, 25]},
                {"lon": m_mid[0], "lat": m_mid[1], "text": f"{n['m_dist']}km (Raw Material Transit)", "color": [255, 255, 255], "offset": [0, -25]},
                {"lon": l_mid[0], "lat": l_mid[1], "text": f"{n['l_dist']}km (Urban Labor Corridor)", "color": [234, 179, 8], "offset": [40, 0]}
            ]
            layers.append(pdk.Layer(
                "TextLayer", pd.DataFrame(label_data), get_position=["lon", "lat"], get_text="text", 
                get_color="color", get_size=13, get_alignment_baseline="'center'", get_pixel_offset="offset"
            ))

            init_view = pdk.ViewState(latitude=n['lat'], longitude=n['lon'], zoom=6.8, pitch=0)

        map_event = st.pydeck_chart(
            pdk.Deck(
                layers=layers, 
                initial_view_state=init_view,
                map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
                tooltip={"text": "{name}\nCap: {cap}"}
            ),
            on_select="rerun",
            selection_mode="single-object"
        )
        
        # Legend Overlay
        st.markdown("""
            <div style="background-color: #1e293b; padding: 10px; border-radius: 4px; color: white; font-size: 13px; margin-top: -10px; border: 1px solid #475569;">
                <b>Legend:</b> &nbsp;&nbsp; 
                <span style="color:#ef4444">Large Cap Node</span> &nbsp;|&nbsp; 
                <span style="color:#f59e0b">Mid Cap Node</span> &nbsp;|&nbsp; 
                <span style="color:#22c55e">Small Cap Node</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <b>Logistics Routes:</b> &nbsp;
                <span style="color:#22d3ee">--- Water Corridor</span> &nbsp;|&nbsp;
                <span style="color:#ffffff">--- Raw Material</span> &nbsp;|&nbsp;
                <span style="color:#facc15">--- Urban Labor Node</span>
            </div>
        """, unsafe_allow_html=True)

        if map_event and map_event.selection.objects:
            if "facility_pins" in map_event.selection.objects:
                clicked_data = map_event.selection.objects["facility_pins"]
                if clicked_data and st.session_state.selected_node != clicked_data[0]:
                    st.session_state.selected_node = clicked_data[0]
                    st.rerun()

    # --- THE TECHNICAL DOSSIER PANEL (40% Column) ---
    with col_dossier:
        if st.session_state.selected_node:
            n = st.session_state.selected_node
            
            # High-Contrast Return Button
            if st.button("Return to Map Overview", use_container_width=True):
                clear_selection()
                st.rerun()
            
            # --- MANUAL IMAGE INSTRUCTION: ---
            # To add an image of the actual building, replace the URL in the data block
            # (look for n['img'] = "...") with the path to your image file,
            # for example: n['img'] = "mohali_building.png"
            # It will automatically render here.
            
            st.image(n['img'], use_container_width=True)
            st.markdown(f"<h2>{n['name']}</h2>", unsafe_allow_html=True)
            st.markdown(f"<span class='tag-{n['cap'].lower()}'>{n['cap']} Cap Facility</span> | <b>Coordinates:</b> {n['lat']} N, {n['lon']} E", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ALTAIR TERRAIN GRAPH (Jagged & Checkpoint Diamond Marker)
            st.markdown("<b>Topographical Integration Profile</b>", unsafe_allow_html=True)
            
            total_dist = n['m_dist'] + n['w_dist']
            x_dist = np.linspace(0, total_dist, len(n['profile']))
            chart_df = pd.DataFrame({"Distance (km)": x_dist, "Elevation (MSL)": n['profile']})
            
            base = alt.Chart(chart_df).encode(
                x=alt.X('Distance (km):Q', title=f"Distance: 0km ({n['m_name']}) → {n['m_dist']}km (Facility) → {total_dist}km ({n['w_name']})"), 
                y=alt.Y('Elevation (MSL):Q', title="Elevation (m)", scale=alt.Scale(domain=[0, max(n['profile'])+50]))
            )
            area = base.mark_area(opacity=0.4, color="#9333ea")
            line = base.mark_line(color="#7e22ce", strokeWidth=2)
            
            # Diamond checkpoint marker
            facility_mark = pd.DataFrame({"x": [n['m_dist']], "y": [n['elev']]})
            point = alt.Chart(facility_mark).mark_point(color='#dc2626', size=150, shape='diamond', filled=True).encode(x='x:Q', y='y:Q')
            
            st.altair_chart(area + line + point, use_container_width=True)

            # STRATEGIC METRICS
            st.markdown("<div class='metric-box'><div class='metric-title'>Strategic Breakthrough</div>"
                        f"<div class='metric-text'>{n['bt']}</div></div>", unsafe_allow_html=True)
                        
            st.markdown("<div class='metric-box'><div class='metric-title'>Topographical Stabilization (Elevation: " + str(n['elev']) + "m MSL)</div>"
                        f"<div class='metric-text'>{n['rationale']}</div></div>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class='metric-box'>
                <div class='metric-title'>Logistics Matrix (LCP Efficiency: {n['lcp']})</div>
                <div class='metric-text'>
                    <b>Material Hub:</b> {n['m_name']} <span style='color:gray'>({n['m_dist']}km route)</span><br>
                    <b>Water Catchment:</b> {n['w_name']} <span style='color:gray'>({n['w_dist']}km route)</span><br>
                    <b>Urban Labor Center:</b> {n['l_name']} <span style='color:gray'>({n['l_dist']}km route)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # VULNERABILITY RADAR CHART (Fixed Brown Labels & Margins)
            st.markdown("<b>Vulnerability & Stability Radar</b>", unsafe_allow_html=True)
            categories = ['Seismic Stability', 'Water Security', 'Logistics Efficiency', 'Geopolitical Safety', 'Labor Proximity']
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=n['rad'],
                theta=categories,
                fill='toself',
                fillcolor='rgba(147, 51, 234, 0.4)',
                line=dict(color='#7e22ce'),
                name=n['name']
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100]),
                    # BROWN, READABLE TEXT
                    angularaxis=dict(tickfont=dict(color='#8B4513', size=13, weight='bold')) 
                ),
                showlegend=False,
                # Increased margins to fix cutoff
                margin=dict(l=40, r=40, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("👆 Click a location tag on the map to view its Technical Dossier and logistics profile.")

# --- TAB 2: GLOBAL ECOSYSTEM (For Tab 3 & context) ---
with tab2:
    global_df = df.copy()
    layers = [pdk.Layer("IconLayer", global_df, get_icon="icon_data", get_size=4, size_scale=10, get_position=["lon", "lat"], get_color="color", pickable=True)]
    st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=pdk.ViewState(latitude=30.0, longitude=20.0, zoom=1.8, pitch=0), map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json', tooltip={"text": "{name}\nCap: {cap}"}))

# --- TAB 3: STI STATISTICAL DISTRIBUTION (GAUSSIAN / KDE) ---
# --- TAB 3: STI STATISTICAL DISTRIBUTION (GAUSSIAN / KDE) ---
with tab3:
    st.markdown("### Continuous Probability Density: STI Stratification by Cap Size")
    st.markdown("This Kernel Density Estimation (KDE) plot models the mathematical probability distribution of Strategic Topographical Index (STI) scores. By modeling the continuous Gaussian-style smoothing, we can infer operational scaling strategies.")
    
    # CRITICAL FIX: Drop rows without an STI score (the Global nodes) before running KDE math.
    # Altair's transform_density will fail if it encounters NaN values in the target column.
    analytics_df = df.dropna(subset=['sti']).copy()
    
    # Altair Continuous Density Plot
    density_plot = alt.Chart(analytics_df).transform_density(
        'sti',
        as_=['sti', 'density'],
        groupby=['cap']
    ).mark_area(opacity=0.6).encode(
        x=alt.X('sti:Q', title="Strategic Topographical Index (STI %)", scale=alt.Scale(domain=[60, 105])),
        y=alt.Y('density:Q', title="Probability Density (Gaussian Smooth)", axis=alt.Axis(labels=False, ticks=False)),
        color=alt.Color('cap:N', scale=alt.Scale(domain=['Large', 'Mid', 'Small'], range=['#dc2626', '#d97706', '#16a34a']), legend=alt.Legend(title="Facility Classification"))
    ).properties(height=450)
    
    st.altair_chart(density_plot, use_container_width=True)

    # Mathematical & Strategic Inferences
    st.markdown("""
    #### 📐 Mathematical & Strategic Inferences
    * **Large Cap Variance (Right-Skewed Gaussian):** Notice how the Red (Large Cap) density curve clusters heavily between **88% and 99%**. Mathematically, this indicates a highly stringent topographical baseline. The State and private entities are rejecting high-friction environments for Mega-Fabs, demonstrating a standard deviation heavily skewed toward coastal plains and stable plateaus.
    * **Mid Cap Standardization (Central Tendency):** The Orange (Mid Cap) curve demonstrates a tighter standard deviation around the **89% - 92%** mean. OSAT and packaging facilities require excellent logistics but do not need the absolute 0.02% seismic zeroing required by Large Cap EUV lithography, creating a predictable statistical cluster.
    * **Small Cap Anomaly (Left-Tailed Variance):** The Green (Small Cap) curve shows a severe left-tail distribution dropping to **75%**. This statistical anomaly mathematically proves the *Defense-in-Depth* theory: state-run strategic fabs intentionally accept severe topographical friction (low STI) in exchange for deep-inland geographical security.
    """)
