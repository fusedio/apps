import streamlit as st

import micropip
await micropip.install("streamlit-folium")

import folium
from streamlit_folium import st_folium
from folium.plugins import SideBySideLayers

st.title("True Color / NDVI Slider comparison")
st.write("Compare a high resolution True Color visualization to its NDVI ([Normalized Difference Vegetation Index](https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index))")

m = folium.Map(height=700,
              location=[37.803972, -122.421297],
            zoom_start=17,
            max_zoom=20,
            min_zoom=10)

left_layer = folium.TileLayer(tiles="https://staging.fused.io/server/v1/realtime-shared/fsh_2Ygdq2tXqnj2RQTY1HMDnE/run/tiles/{z}/{x}/{y}?dtype_out_raster=png&dtype_out_vector=csv&var=RGB", attr="RGB", name="RGB", overlay=True, control=False)
left_layer2 = folium.TileLayer(tiles="https://staging.fused.io/server/v1/realtime-shared/fsh_2Ygdq2tXqnj2RQTY1HMDnE/run/tiles/{z}/{x}/{y}?dtype_out_raster=png&dtype_out_vector=csv&var=RGB", attr="RGB2", name="RGB2", overlay=True, control=False)
right_layer = folium.TileLayer(tiles="https://staging.fused.io/server/v1/realtime-shared/fsh_2Ygdq2tXqnj2RQTY1HMDnE/run/tiles/{z}/{x}/{y}?dtype_out_raster=png&dtype_out_vector=csv&var=NDVI", attr="NDVI", name="NDVI", overlay=True, control=False)

left_layer.add_to(m)
left_layer2.add_to(m)
right_layer.add_to(m)
sbs = SideBySideLayers(left_layer, right_layer)
sbs.add_to(m)

st_folium(m, height=700, key="map3", use_container_width=True)

st.write("Images from [NAIP](https://naip-usdaonline.hub.arcgis.com/)")