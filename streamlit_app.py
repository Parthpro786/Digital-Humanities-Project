import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objects as go
from scipy import stats
from sklearn.neighbors import KernelDensity
from itertools import combinations
import feedparser

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(layout="wide", page_title="Strategic Topography GIS")

# --------------------------------------------------
# PREMIUM UI CSS (F1 INTELLIGENCE STYLE)
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Inter:wght@300;400;600&display=swap');

body, .stApp {
    background-color: #0a0a0a;
    color: #e5e5e5;
    font-family: 'Inter', sans-serif;
}

h1,h2,h3 {
    font-family: 'Rajdhani', sans-serif;
    letter-spacing: 1px;
}

/* HERO */
.hero {
    background: linear-gradient(135deg,#000,#111);
    padding: 25px;
    border: 1px solid #222;
    border-radius: 10px;
    margin-bottom: 20px;
}
.hero h1 {
    color: #d4af37;
}

/* HUD CARDS */
.hud {
    background:#111;
    padding:15px;
    border-radius:10px;
    border:1px solid #222;
    transition: all 0.3s ease;
}
.hud:hover {
    transform: translateY(-5px);
    box-shadow: 0 0 20px rgba(212,175,55,0.4);
}
.hud-title {
    font-size:12px;
    color:#aaa;
}
.hud-value {
    font-size:28px;
    color:#d4af37;
}

/* TABS */
button[data-baseweb="tab"] {
    background:#111 !important;
    color:#ccc !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background:#d4af37 !important;
    color:#000 !important;
}

/* NEWS GRID */
.news-grid {
    display:grid;
    grid-template-columns:repeat(2,1fr);
    gap:16px;
}
.news-card {
    background:#111;
    padding:15px;
    border-radius:10px;
    border:1px solid #222;
    transition:0.3s;
}
.news-card:hover {
    transform:translateY(-5px);
    box-shadow:0 0 20px rgba(184,115,51,0.5);
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HERO
# --------------------------------------------------
st.markdown("""
<div class="hero">
<h1>Strategic Topography GIS</h1>
<p>Cinematic Intelligence Dashboard for Semiconductor Infrastructure</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# STATE
# --------------------------------------------------
if "selected_node" not in st.session_state:
    st.session_state.selected_node = None

# --------------------------------------------------
# DATA (UNCHANGED)
# --------------------------------------------------
data = [
    # ---- GLOBAL ECOSYSTEM ----
    {"name": "TSMC Fab 18", "state": "Taiwan", "region": "Global", "cap": "Large", "lat": 23.10, "lon": 120.28, "sti": 95},
    {"name": "TSMC Kumamoto", "state": "Japan", "region": "Global", "cap": "Large", "lat": 32.88, "lon": 130.84, "sti": 93},
    {"name": "Intel Ocotillo", "state": "Arizona", "region": "Global", "cap": "Large", "lat": 33.27, "lon": -111.88, "sti": 92},
    {"name": "Intel Magdeburg", "state": "Germany", "region": "Global", "cap": "Large", "lat": 52.12, "lon": 11.62, "sti": 90},
    {"name": "Samsung Taylor", "state": "Texas", "region": "Global", "cap": "Large", "lat": 30.56, "lon": -97.40, "sti": 91},
    {"name": "Samsung Pyeongtaek", "state": "Korea", "region": "Global", "cap": "Large", "lat": 37.02, "lon": 127.04, "sti": 94},
    {"name": "Micron Boise", "state": "Idaho", "region": "Global", "cap": "Large", "lat": 43.52, "lon": -116.15, "sti": 89},
    {"name": "Rapidus Hokkaido", "state": "Japan", "region": "Global", "cap": "Large", "lat": 42.76, "lon": 141.67, "sti": 90},
    {"name": "GlobalFoundries Dresden", "state": "Germany", "region": "Global", "cap": "Mid", "lat": 51.12, "lon": 13.71, "sti": 88},
    {"name": "SMIC Shanghai", "state": "China", "region": "Global", "cap": "Large", "lat": 31.20, "lon": 121.59, "sti": 92},

    # ---- INDIAN ECOSYSTEM ----
    {
        "name": "Tata-PSMC Dholera", "state": "Gujarat", "region": "India", "year": 2026, "cap": "Large", 
        "lat": 22.25, "lon": 72.11, "elev": 15, "terrain": "Coastal Plateau",
        "w_name": "Sabarmati Desalination", "w_lat": 22.50, "w_lon": 72.30, "w_dist": 32,
        "m_name": "Gulf of Khambhat Port", "m_lat": 21.75, "m_lon": 72.25, "m_dist": 55,
        "l_name": "Ahmedabad Urban Center", "l_lat": 23.02, "l_lon": 72.57, "l_dist": 85,
        "bt": "India's First Commercial 28nm Mega-Fab. Sovereign logic node production.", 
        "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRqIQdQsnEGk-qsjXopCw4ZG3o-HgKqlO5aDg&s",
        "profile": [0, 8, 3, 14, 15, 15, 15, 15, 11, 4, 5], 
        "sti": 99.5, "lcp": 0.97, "rad": [99, 95, 98, 90, 85], 
        "rationale": "Engineered for 0.02% seismic vibration friction. The absolute flatness prevents multi-billion dollar EUV wafer spoilage. Proximity to deep-water port yields high logistical cost-efficiency."
    },
    {
        "name": "Tata-TSAT Assam", "state": "Assam", "region": "India", "year": 2026, "cap": "Large", 
        "lat": 26.24, "lon": 92.33, "elev": 55, "terrain": "River Valley",
        "w_name": "Brahmaputra Basin", "w_lat": 26.50, "w_lon": 92.60, "w_dist": 40,
        "m_name": "Haldia Port Transit", "m_lat": 25.50, "m_lon": 91.00, "m_dist": 180,
        "l_name": "Guwahati Metropolis", "l_lat": 26.14, "l_lon": 91.73, "l_dist": 65,
        "bt": "Sovereign Advanced Packaging Hub. Eastern frontier geopolitical hedge.", 
        "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=600&q=80",
        "profile": [120, 140, 85, 40, 55, 55, 55, 80, 130, 95, 110],
        "sti": 84.4, "lcp": 0.70, "rad": [75, 99, 65, 95, 80],
        "rationale": "High topographical friction (34% higher logistics cost) is offset by strategic geographic defense and inexhaustible fresh water supply for Chemical Mechanical Polishing (CMP)."
    },
    {
        "name": "Micron Sanand", "state": "Gujarat", "region": "India", "year": 2024, "cap": "Large", 
        "lat": 22.98, "lon": 72.37, "elev": 45, "terrain": "Industrial Plains",
        "w_name": "Narmada Canal System", "w_lat": 23.10, "w_lon": 72.50, "w_dist": 20,
        "m_name": "Mundra Port Transit", "m_lat": 22.80, "m_lon": 72.00, "m_dist": 250,
        "l_name": "Sanand Industrial GIDC", "l_lat": 22.95, "l_lon": 72.38, "l_dist": 5,
        "bt": "High Bandwidth Memory (HBM) ATMP validation.", 
        "img": "https://images.unsplash.com/photo-1563207153-f404bf10c0e8?auto=format&fit=crop&w=600&q=80",
        "profile": [10, 18, 12, 35, 45, 45, 45, 42, 48, 44, 48],
        "sti": 92.0, "lcp": 0.90, "rad": [90, 85, 88, 85, 98],
        "rationale": "Chosen for pre-existing grid stability and rapid scalability. Flat plains allow for rapid construction modularity without deep-pile foundation engineering."
    },
    {
        "name": "CG Power-Renesas Sanand", "state": "Gujarat", "region": "India", "year": 2025, "cap": "Mid", 
        "lat": 23.00, "lon": 72.35, "elev": 43, "terrain": "Industrial Plains",
        "w_name": "Narmada Canal System", "w_lat": 23.10, "w_lon": 72.50, "w_dist": 22,
        "m_name": "Regional Rail Freight", "m_lat": 22.80, "m_lon": 72.20, "m_dist": 28,
        "l_name": "Ahmedabad Urban Grid", "l_lat": 23.02, "l_lon": 72.57, "l_dist": 25,
        "bt": "Specialized OSAT for consumer and industrial power management ICs.", 
        "img": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=600&q=80",
        "profile": [20, 28, 22, 38, 43, 43, 43, 40, 48, 42, 46],
        "sti": 89.0, "lcp": 0.88, "rad": [90, 85, 92, 85, 95],
        "rationale": "Leverages the same topographical stability as the Micron facility, creating a localized high-density packaging cluster with shared logistics."
    },
    {
        "name": "Texas Instruments Bangalore", "state": "Karnataka", "region": "India", "year": 1985, "cap": "Large", 
        "lat": 12.97, "lon": 77.59, "elev": 920, "terrain": "Deccan Plateau",
        "w_name": "Cauvery Basin Municipal", "w_lat": 12.40, "w_lon": 77.30, "w_dist": 85,
        "m_name": "HAL Airport Data Transit", "m_lat": 12.95, "m_lon": 77.66, "m_dist": 12,
        "l_name": "Bangalore Urban Grid", "l_lat": 12.97, "l_lon": 77.59, "l_dist": 2,
        "bt": "First Global R&D Center in India. Pioneered satellite data export.", 
        "img": "https://www.ti.com/content/dam/ticom/images/themes/facilities/india-bangalore-corporate-building.jpg",
        "profile": [850, 890, 860, 910, 920, 920, 920, 890, 915, 870, 880],
        "sti": 88.0, "lcp": 0.85, "rad": [95, 75, 80, 90, 99],
        "rationale": "Human-Centric Topography. Elevation provided moderate climate reducing 1980s mainframe cooling loads by 14%. Immediate access to elite engineering institutions."
    },
    {
        "name": "SCL Mohali", "state": "Punjab", "region": "India", "year": 1983, "cap": "Small", 
        "lat": 30.70, "lon": 76.69, "elev": 310, "terrain": "Shivalik Foothills",
        "w_name": "Sutlej River Tributaries", "w_lat": 30.90, "w_lon": 76.50, "w_dist": 28,
        "m_name": "Northern Rail Depot", "m_lat": 30.50, "m_lon": 76.80, "m_dist": 24,
        "l_name": "Chandigarh Sector 17", "l_lat": 30.73, "l_lon": 76.77, "l_dist": 10,
        "bt": "ISRO space-grade and military radiation-hardened 180nm CMOS nodes.", 
        "img": "https://images.unsplash.com/photo-1590247813693-5541d1c609fd?auto=format&fit=crop&w=600&q=80",
        "profile": [280, 270, 295, 285, 310, 310, 310, 340, 320, 370, 380],
        "sti": 75.0, "lcp": 0.65, "rad": [60, 85, 65, 99, 88],
        "rationale": "Defense-in-Depth location. Sacrificed maritime logistics to push sensitive military infrastructure deep inland. Foundation anchored in local bedrock shelf."
    },
    {
        "name": "Hind Rectifiers Mumbai", "state": "Maharashtra", "region": "India", "year": 1980, "cap": "Small", 
        "lat": 19.11, "lon": 72.84, "elev": 10, "terrain": "Western Coastal Plain",
        "w_name": "Ulhas River Catchment", "w_lat": 19.00, "w_lon": 72.80, "w_dist": 15,
        "m_name": "JNPT Port Transit", "m_lat": 18.95, "m_lon": 72.90, "m_dist": 60,
        "l_name": "Mumbai Metropolis", "l_lat": 19.07, "l_lon": 72.87, "l_dist": 5,
        "bt": "Pioneer in power semiconductor devices for Indian Railways traction rectifiers.", 
        "img": "https://investdesk.in/wp-content/uploads/2024/09/1717276048229.jpg",
        "profile": [2, 12, 5, 10, 10, 10, 10, 12, 9, 7, 8],
        "sti": 91.5, "lcp": 0.92, "rad": [65, 80, 98, 90, 99],
        "rationale": "Classic coastal export config. Sacrifices absolute seismic neutrality (Western Ghats proximity) for hyper-frictionless logistics."
    },
    {
        "name": "Qualcomm Hyderabad", "state": "Telangana", "region": "India", "year": 2010, "cap": "Large", 
        "lat": 17.44, "lon": 78.37, "elev": 550, "terrain": "Deccan Plateau",
        "w_name": "Municipal Mains", "w_lat": 17.40, "w_lon": 78.35, "w_dist": 10,
        "m_name": "Hyderabad Airport Cargo", "m_lat": 17.25, "m_lon": 78.43, "m_dist": 35,
        "l_name": "HITEC City Hub", "l_lat": 17.44, "l_lon": 78.38, "l_dist": 5,
        "bt": "Snapdragon design and validation mega-center. Pure play VLSI node.", 
        "img": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=600&q=80",
        "profile": [500, 520, 530, 550, 550, 550, 550, 530, 510, 500, 490],
        "sti": 94.0, "lcp": 0.94, "rad": [92, 85, 90, 88, 99],
        "rationale": "Chosen for pre-existing grid stability (500kV primary substation) and rapid construction modularity. Human-Centric Topography."
    },
    {
        "name": "Tessolve Bangalore", "state": "Karnataka", "region": "India", "year": 2005, "cap": "Mid", 
        "lat": 12.92, "lon": 77.68, "elev": 910, "terrain": "Deccan Plateau",
        "w_name": "Cauvery Basins pipelines", "w_lat": 12.45, "w_lon": 77.40, "w_dist": 75,
        "m_name": "HAL Airport Data Transit", "m_lat": 12.95, "m_lon": 77.66, "m_dist": 12,
        "l_name": "Electronics City Grid", "l_lat": 12.93, "l_lon": 77.69, "l_dist": 5,
        "bt": "Global validation and testing engineering hub. Critical for wafer sort.", 
        "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRCgAYNBA-p238CAGyLa0plRWE4ahnz_MAqKg&s",
        "profile": [860, 880, 890, 910, 910, 910, 910, 890, 880, 870, 860],
        "sti": 89.0, "lcp": 0.88, "rad": [95, 80, 85, 92, 98],
        "rationale": "Standard high-plateau configuration. Leveraging the same topographical stability as the TI campus, maximizing labor corridor access."
    },
    {
        "name": "Continental Device India Limited", "state": "Delhi", "region": "India", "year": 1964, "cap": "Small", 
        "lat": 28.66, "lon": 77.21, "elev": 210, "terrain": "Indo-Gangetic Plains",
        "w_name": "Yamuna River Pipelines", "w_lat": 28.60, "w_lon": 77.20, "w_dist": 15,
        "m_name": "NCR Rail Corridor", "m_lat": 28.70, "m_lon": 77.25, "m_dist": 10,
        "l_name": "Delhi Urban Grid", "l_lat": 28.67, "l_lon": 77.22, "l_dist": 5,
        "bt": "India's first fabless design and discrete transistor manufacturing.", 
        "img": "https://pbs.twimg.com/media/GyJiMM4XQAAIBrY?format=jpg&name=small",
        "profile": [190, 195, 200, 210, 210, 210, 210, 200, 198, 195, 190],
        "sti": 78.0, "lcp": 0.65, "rad": [65, 70, 88, 85, 99],
        "rationale": "Built for proximity to the National Capital. Topographical variance is high due to the Yamuna river plain's inherent instability."
    }
]
df = pd.DataFrame(data)# KEEP YOUR FULL ORIGINAL DATA EXACTLY HERE



# --------------------------------------------------
# LIVE FEED
# --------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_news():
    url = "https://news.google.com/rss/search?q=India+semiconductor&hl=en-IN&gl=IN&ceid=IN:en"
    return feedparser.parse(url).entries[:4]

# --------------------------------------------------
# MAP FUNCTION (PLOTLY)
# --------------------------------------------------
def plot_map(df):

    color_map = {
        "Large": "#d4af37",
        "Mid": "#b87333",
        "Small": "#708090"
    }

    fig = go.Figure()

    for cap in df['cap'].unique():
        subset = df[df['cap'] == cap]

        # glow layer
        fig.add_trace(go.Scattermapbox(
            lat=subset['lat'],
            lon=subset['lon'],
            mode='markers',
            marker=dict(size=20, color=color_map[cap], opacity=0.2),
            hoverinfo='none'
        ))

        # main pins
        fig.add_trace(go.Scattermapbox(
            lat=subset['lat'],
            lon=subset['lon'],
            mode='markers',
            marker=dict(size=8, color=color_map[cap]),
            text=subset['name'],
            customdata=subset.to_dict('records'),
            hovertemplate="""
<b>%{text}</b><br>
Cap: %{customdata.cap}<br>
Terrain: %{customdata.terrain}<br>
STI: %{customdata.sti}
"""
        ))

    fig.update_layout(
        mapbox_style="carto-darkmatter",
        mapbox_zoom=3,
        mapbox_center={"lat":20,"lon":80},
        margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor="#0a0a0a"
    )

    return fig

# --------------------------------------------------
# MODAL DOSSIER
# --------------------------------------------------
@st.dialog("Technical Dossier")
def show_dossier(n):

    col1,col2 = st.columns(2)

    with col1:
        st.image(n['img'], use_container_width=True)

    with col2:
        st.markdown(f"### {n['name']}")
        st.write(n['bt'])

        st.write(f"**Terrain:** {n['terrain']}")
        st.write(f"**STI:** {n['sti']}")

    # elevation profile
    chart_df = pd.DataFrame({
        "x": range(len(n['profile'])),
        "y": n['profile']
    })

    area = alt.Chart(chart_df).mark_area(
        color="#d4af37",
        opacity=0.5
    ).encode(x='x', y='y')

    st.altair_chart(area, use_container_width=True)

    # radar
    categories = ['Seismic','Water','Logistics','Geo','Labor']
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=n['rad'],
        theta=categories,
        fill='toself',
        fillcolor='rgba(212,175,55,0.3)',
        line=dict(color='#d4af37')
    ))

    fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])))
    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# TABS
# --------------------------------------------------
tab1,tab2,tab3 = st.tabs(["INDIA","GLOBAL","STATISTICS"])

# --------------------------------------------------
# TAB 1
# --------------------------------------------------
with tab1:

    india_df = df[df['region']=="India"]

    col1,col2,col3 = st.columns(3)

    col1.markdown(f"<div class='hud'><div class='hud-title'>Nodes</div><div class='hud-value'>{len(india_df)}</div></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='hud'><div class='hud-title'>Mean STI</div><div class='hud-value'>{india_df['sti'].mean():.1f}</div></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='hud'><div class='hud-title'>Mean LCP</div><div class='hud-value'>{india_df['lcp'].mean():.2f}</div></div>", unsafe_allow_html=True)

    fig = plot_map(india_df)
    click = st.plotly_chart(fig, use_container_width=True)

    # click detection workaround
    if st.button("Open Selected Dossier"):
        if len(india_df) > 0:
            show_dossier(india_df.iloc[0].to_dict())

    # NEWS GRID
    st.markdown("### Live Strat-Intel Feed")

    news = fetch_news()
    st.markdown("<div class='news-grid'>", unsafe_allow_html=True)

    for n in news:
        st.markdown(f"""
        <div class='news-card'>
        <b>{n.title}</b><br>
        <a href='{n.link}' target='_blank'>Read More</a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# TAB 2 GLOBAL
# --------------------------------------------------
with tab2:
    fig = plot_map(df)
    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# TAB 3 (UNCHANGED STATS ENGINE)
# --------------------------------------------------
with tab3:

    stats_df = df[df['region']=="India"].dropna()

    density = alt.Chart(stats_df).transform_density(
        'sti',
        groupby=['cap']
    ).mark_area(opacity=0.4).encode(
        x='value:Q',
        y='density:Q',
        color='cap:N'
    )

    st.altair_chart(density, use_container_width=True)

    summary = stats_df.groupby('cap')['sti'].agg(['mean','var','std'])
    st.dataframe(summary)

    groups = [g['sti'].values for _,g in stats_df.groupby('cap')]

    if len(groups)>1:
        f,p = stats.f_oneway(*groups)
        st.write(f"ANOVA p-value: {p}")

    bins=[0,82,93,110]
    stats_df['bin']=pd.cut(stats_df['sti'],bins)
    cont=pd.crosstab(stats_df['cap'],stats_df['bin'])
    st.dataframe(cont)

    chi2,p,_,_=stats.chi2_contingency(cont)
    st.write(f"Chi2 p-value: {p}")

    x=np.linspace(60,110,500).reshape(-1,1)
    densities={}

    for cap,g in stats_df.groupby('cap'):
        kde=KernelDensity(bandwidth=4).fit(g['sti'].values.reshape(-1,1))
        densities[cap]=np.exp(kde.score_samples(x))

    results=[]
    for c1,c2 in combinations(densities.keys(),2):
        overlap=np.trapz(np.minimum(densities[c1],densities[c2]),x.flatten())
        results.append([c1,c2,overlap])

    st.dataframe(pd.DataFrame(results,columns=["A","B","Overlap"]))
