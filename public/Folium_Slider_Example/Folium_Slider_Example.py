import streamlit as st
# st.markdown('### Map Slider using Folium SideBySide Layers Example')

import micropip
await micropip.install('streamlit_folium')
import folium
from streamlit_folium import st_folium

# Create map
lat, lng = 39.62155304762678, -90.78627106190022
m = folium.Map(location=[lat, lng], zoom_start=10, max_zoom=16, min_zoom=10, tiles=None)

# Layer left: LULC
url_raster = "https://www.fused.io/server/v1/realtime-shared/UDF_LULC_Tile_Example/run/tiles/{z}/{x}/{y}?dtype_out_raster=png" 
layer_left = folium.TileLayer(tiles=url_raster,attr="LULC",name="LULC",overlay=True,control=True,show=True).add_to(m)

# Layer right: Sentinel
url_raster = "https://www.fused.io/server/v1/realtime-shared/UDF_Sentinel_Tile_Example/run/tiles/{z}/{x}/{y}?dtype_out_raster=png"
layer_right = folium.TileLayer(tiles=url_raster,attr="Sentinel",name="Sentinel",overlay=True,control=True,show=True).add_to(m)

# SideBySideLayers
sbs = folium.plugins.SideBySideLayers(layer_left=layer_left, layer_right=layer_right)
layer_left.add_to(m)
layer_right.add_to(m)
sbs.add_to(m)

st_folium(m, width=1000, height=600)
