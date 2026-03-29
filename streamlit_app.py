import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide", page_title="Isometric Frontline")

# --- 1. DATASET ---
data = [
    {
        "name": "Tata-TSAT Assam", 
        "lat": 26.24, 
        "lon": 92.33, 
        "elev": 800, # Height to place the pin above the mountains
        "desc": "River Valley Hub\nStrategic Node"
    }
]
df = pd.DataFrame(data)

st.title("🛡️ Cyber-Frontline: Isometric Terrain Analysis")
st.markdown("Visualizing the topographical constraints of the Assam region.")

# --- 2. ISOMETRIC CAMERA LOCK ---
# Setting pitch to 60 and bearing to 45 creates the exact "Diamond" isometric 
# angle seen in your Photoshop reference image.
view_state = pdk.ViewState(
    latitude=26.24, 
    longitude=92.33, 
    zoom=11.5, 
    pitch=60, 
    bearing=45 
)

# --- 3. LAYERS ---

# Layer 1: Exaggerated 3D Satellite Terrain
terrain_layer = pdk.Layer(
    "TerrainLayer",
    elevation_decoder={"rScaler": 256, "gScaler": 1, "bScaler": 1/256, "offset": -32768},
    elevation_data="https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
    texture="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    elevation_scale=10, # Exaggerate the mountains like the reference image
)

# Layer 2: The Location Pin (Red Pillar)
pin_layer = pdk.Layer(
    "ColumnLayer",
    df,
    get_position=['lon', 'lat'],
    get_elevation='elev',
    elevation_scale=1,
    radius=150,
    get_fill_color=[255, 60, 0, 255],
    pickable=True,
    auto_highlight=True,
)

# Layer 3: Floating Text Label (Mimicking the reference text box)
text_layer = pdk.Layer(
    "TextLayer",
    df,
    get_position=['lon', 'lat'],
    get_text="name",
    get_size=24,
    get_color=[255, 255, 255, 255],
    get_alignment_baseline="'bottom'",
    # Offset the text high above the pin
    get_pixel_offset=[0, -60], 
    font_family="Helvetica, Arial, sans-serif",
    font_weight="bold"
)

# Layer 4: Floating Sub-text (Coordinates/Info)
sub_text_layer = pdk.Layer(
    "TextLayer",
    df,
    get_position=['lon', 'lat'],
    get_text="desc",
    get_size=16,
    get_color=[0, 200, 255, 255], # Cyan color from reference
    get_alignment_baseline="'bottom'",
    get_pixel_offset=[0, -30], 
)

# --- 4. RENDER MAP ---
st.pydeck_chart(pdk.Deck(
    layers=[terrain_layer, pin_layer, text_layer, sub_text_layer],
    initial_view_state=view_state,
    map_style=None, # Removes background map box
    tooltip={"text": "{name}\nElevation: 800m"}
))
