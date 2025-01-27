import streamlit as st
# st.set_page_config(layout="wide") 
st.title("🍿 Video Overlay ")
import micropip
await micropip.install('streamlit_folium')
from streamlit_folium import st_folium
import folium

m = folium.Map(location=[27, -105], zoom_start=4)
bounds=[[-59, -180], [78, -65.5]]

# Video Layer
video = folium.raster_layers.VideoOverlay(
    video_url="https://d3trz6orl8ssjq.cloudfront.net/marketing-site-assets/dynamic-banner-video.mp4",
    bounds=bounds,
    opacity=0.8,
    attr="fused.io",
    autoplay=True,
    loop=True,
).add_to(m)

basemap = st.radio('Choose Basemap', ['None','World Imagery' , 'Digital Evelation Model'], 1)

if basemap == 'World Imagery':
    url_raster = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    folium.raster_layers.TileLayer(tiles=url_raster, attr='fu', interactive=True).add_to(m)
    
elif basemap == 'Digital Evelation Model':
    url_raster = 'https://www.fused.io/server/v1/realtime-shared/UDF_DEM_Tile_Hexify/run/tiles/{z}/{x}/{y}?dtype_out_raster=png&type=png&color_scale=1'
    folium.raster_layers.TileLayer(tiles=url_raster, attr='fu', interactive=True).add_to(m)

out = st_folium(m, width=800, height=500)
