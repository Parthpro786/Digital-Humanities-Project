import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import altair as alt
import plotly.graph_objects as go

# --- 1. PROFESSIONAL PAGE CONFIG & CSS ---
st.set_page_config(layout="wide", page_title="Strategic Topography GIS")

st.markdown("""
    <style>
        /* Light washy magenta/lavender background */
        .stApp { background-color: #fdf4ff; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 2rem; max-width: 98%;}
        h1, h2, h3, p, span, div {font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif; color: #1e1b4b;}
        
        /* High contrast for the right panel */
        [data-testid="stSidebar"] {background-color: #ffffff; border-right: 1px solid #e2e8f0;}
        .metric-box {background-color: #ffffff; padding: 14px; border-radius: 4px; border-left: 4px solid #9333ea; margin-bottom: 12px; border: 1px solid #e5e7eb; box-shadow: 0 1px 2px rgba(0,0,0,0.05);}
        .metric-title {color: #4b5563; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; font-weight: 700;}
        .metric-text {color: #0f172a; font-size: 13px; line-height: 1.5;}
        
        /* Cap Tags */
        .tag-large {color: #dc2626; font-weight: 800; text-transform: uppercase; font-size: 12px;}
        .tag-mid {color: #d97706; font-weight: 800; text-transform: uppercase; font-size: 12px;}
        .tag-small {color: #16a34a; font-weight: 800; text-transform: uppercase; font-size: 12px;}
        
        /* Fixed Return Button Contrast */
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

    # ---- INDIAN ECOSYSTEM (With Radar Metrics) ----
    {
        "name": "Tata-PSMC Dholera", "region": "India", "year": 2026, "cap": "Large", 
        "lat": 22.25, "lon": 72.11, "elev": 15, "terrain": "Coastal Plateau",
        "w_name": "Sabarmati Desalination", "w_lat": 22.50, "w_lon": 72.30, "w_dist": 32,
        "m_name": "Gulf of Khambhat Port", "m_lat": 21.75, "m_lon": 72.25, "m_dist": 55,
        "l_name": "Ahmedabad Urban Center", "l_lat": 23.02, "l_lon": 72.57, "l_dist": 85,
        "bt": "India's First Commercial 28nm Mega-Fab. Sovereign logic node production.", 
        "img": "https://images.unsplash.com/photo-1508344928928-7165b67de128?auto=format&fit=crop&w=800&q=80",
        "profile": [0, 8, 3, 14, 15, 15, 15, 15, 11, 4, 5], # Jagged representation
        "sti": 99.5, "lcp": 0.97,
        "rad": [99, 95, 98, 90, 85], # Seismic, Water, Logistics, Geopolitics, Labor
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
        "name": "Polymatech Chennai", "region": "India", "year": 2023, "cap": "Mid", 
        "lat": 12.82, "lon": 79.98, "elev": 12, "terrain": "Coastal Plain",
        "w_name": "Palar River Basin", "w_lat": 12.60, "w_lon": 79.90, "w_dist": 25,
        "m_name": "Chennai Port Transit", "m_lat": 13.08, "m_lon": 80.29, "m_dist": 45,
        "l_name": "Kancheepuram Town", "l_lat": 12.83, "l_lon": 79.70, "l_dist": 30,
        "bt": "Opto-semiconductor and specialized photonics manufacturing.", 
        "img": "https://images.unsplash.com/photo-1580983554869-3221443491db?auto=format&fit=crop&w=800&q=80",
        "profile": [2, 10, 4, 15, 12, 12, 12, 8, 14, 5, 6],
        "sti": 91.0, "lcp": 0.90,
        "rad": [82, 88, 94, 80, 90],
        "rationale": "Southern coastal stability. Focuses on opto-electronics which require rigorous dust-free environments supported by coastal wind shear management."
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
    }
]

df = pd.DataFrame(data)

# Pin mapping setup
ICON_URL = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-atlas.png"
icon_data = {"url": ICON_URL, "width": 128, "height": 128, "y": 128, "anchorY": 128}
df['icon_data'] = [icon_data for _ in range(len(df))]

def get_color(cap):
    if cap == "Large": return [220, 38, 38]   # Deep Red
    if cap == "Mid": return [217, 119, 6]     # Orange
    return [22, 163, 74]                      # Green
df['color'] = df['cap'].apply(get_color)


# --- 5. TOP BAR UI ---
st.title("Strategic Topography & GIS Explorer")
st.markdown("Macro-Analysis of Semiconductor Infrastructure, Topographical Friction, and Strategic Routing.")

# Tab Selection
tab1, tab2, tab3 = st.tabs(["INDIA TIMELINE ECOSYSTEM", "GLOBAL MACRO ECOSYSTEM", "S.T.I. ANALYTICS & RANKINGS"])

# --- TAB 1: INDIA ECOSYSTEM (THE 60/40 SPLIT) ---
with tab1:
    selected_year = st.select_slider("Historical Timeline Integration:", options=[1980, 1990, 2000, 2010, 2020, 2026], value=2026)
    active_df = df[(df['region'] == 'India') & (df['year'] <= selected_year)].copy()
    
    if st.session_state.selected_node:
        col_map, col_panel = st.columns([5.5, 4.5], gap="large")
    else:
        col_map = st.container()
        col_panel = st.empty()

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
                {"path": w_curve, "color": [6, 182, 212]}, 
                {"path": m_curve, "color": [255, 255, 255]}, 
                {"path": l_curve, "color": [234, 179, 8]}  
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
                {"lon": w_mid[0], "lat": w_mid[1], "text": f"{n['w_dist']}km (Water)", "color": [6, 182, 212], "offset": [0, 25]},
                {"lon": m_mid[0], "lat": m_mid[1], "text": f"{n['m_dist']}km (Material)", "color": [255, 255, 255], "offset": [0, -25]},
                {"lon": l_mid[0], "lat": l_mid[1], "text": f"{n['l_dist']}km (Labor)", "color": [234, 179, 8], "offset": [40, 0]}
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
                tooltip={"text": "{name}\nClass: {cap} Cap"}
            ),
            on_select="rerun",
            selection_mode="single-object"
        )
        
        # Legend Overlay
        st.markdown("""
            <div style="background-color: #1e293b; padding: 10px; border-radius: 4px; color: white; font-size: 13px; margin-top: -10px; border: 1px solid #475569;">
                <b>Legend:</b> &nbsp; 
                <span style="color:#ef4444">Large Cap</span> &nbsp;|&nbsp; 
                <span style="color:#f59e0b">Mid Cap</span> &nbsp;|&nbsp; 
                <span style="color:#22c55e">Small Cap</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <b>Routes:</b> &nbsp;
                <span style="color:#22d3ee">--- Water Corridor</span> &nbsp;|&nbsp;
                <span style="color:#ffffff">--- Raw Material</span> &nbsp;|&nbsp;
                <span style="color:#facc15">--- Urban Labor</span>
            </div>
        """, unsafe_allow_html=True)

        # Master Data Ledger (Below the Map)
        st.markdown("<br><b>Master Data Ledger (Active Timeline)</b>", unsafe_allow_html=True)
        ledger_df = active_df[['name', 'cap', 'elev', 'sti', 'lcp']].rename(columns={'name': 'Facility', 'cap': 'Classification', 'elev': 'Elevation (MSL)', 'sti': 'STI (%)', 'lcp': 'LCP Matrix'})
        st.dataframe(ledger_df, use_container_width=True, hide_index=True)

        if map_event and map_event.selection.objects:
            if "facility_pins" in map_event.selection.objects:
                clicked_data = map_event.selection.objects["facility_pins"]
                if clicked_data and st.session_state.selected_node != clicked_data[0]:
                    st.session_state.selected_node = clicked_data[0]
                    st.rerun()

    # --- TECHNICAL DOSSIER PANEL ---
    if st.session_state.selected_node:
        with col_panel:
            n = st.session_state.selected_node
            
            if st.button("Return to Map Overview", use_container_width=True):
                clear_selection()
                st.rerun()
                
            st.image(n['img'], use_container_width=True)
            st.markdown(f"<h2>{n['name']}</h2>", unsafe_allow_html=True)
            st.markdown(f"<span class='tag-{n['cap'].lower()}'>{n['cap']} Cap Facility</span> | <b>Coordinates:</b> {n['lat']} N, {n['lon']} E", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ALTAIR TERRAIN GRAPH (Jagged & Checkpoint Marker)
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
            
            # Precise Checkpoint Marker
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
                    <b>Material Hub:</b> {n['m_name']} <span style='color:gray'>({n['m_dist']}km)</span><br>
                    <b>Water Catchment:</b> {n['w_name']} <span style='color:gray'>({n['w_dist']}km)</span><br>
                    <b>Urban Labor Center:</b> {n['l_name']} <span style='color:gray'>({n['l_dist']}km)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # VULNERABILITY RADAR CHART
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
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                margin=dict(l=30, r=30, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: GLOBAL ECOSYSTEM ---
with tab2:
    global_df = df.copy()
    layers = [pdk.Layer("IconLayer", global_df, get_icon="icon_data", get_size=4, size_scale=10, get_position=["lon", "lat"], get_color="color", pickable=True)]
    st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=pdk.ViewState(latitude=30.0, longitude=20.0, zoom=1.8, pitch=0), map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json', tooltip={"text": "{name}\n{cap} Cap"}))

# --- TAB 3: STI ANALYTICS ---
with tab3:
    st.markdown("### Sovereign Topographical Index (STI) Rankings")
    st.markdown("A macro-level comparison of the Strategic Topographical Index across all designated Indian facilities, measuring baseline friction against logistical yield.")
    
    analytics_df = df[df['region'] == 'India'].sort_values('sti', ascending=False)
    
    bar_chart = alt.Chart(analytics_df).mark_bar(color='#9333ea', cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X('name:N', sort='-y', title="Facility Name", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('sti:Q', title="STI Score (%)", scale=alt.Scale(domain=[50, 100])),
        tooltip=['name', 'sti', 'cap', 'terrain']
    ).properties(height=500)
    
    st.altair_chart(bar_chart, use_container_width=True)
