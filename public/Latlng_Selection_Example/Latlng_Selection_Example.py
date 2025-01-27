import streamlit as st
st.markdown("### Folium Point Selection Example")
st.markdown("🧭 Where do you want data for?")
import micropip
await micropip.install(['streamlit_folium','geopandas','mercantile'])
import folium
import pandas as pd
from streamlit_folium import st_folium
import fused
col1, col2 = st.columns([1,1])

@fused.udf
def my_udf(lat: float=1, lng: float=1, n=20):
    import pandas as pd
    import numpy as np
    np.random.seed(abs(int(round(lat,2) * round(lng,2))) )
    return pd.DataFrame(np.random.randn(n, 3), columns=["a", "b", "c"])


# Create or reset the map
initial_location = [20, 0]
basemap = col1.selectbox("Select a Basemap", ["Cartodb dark_matter", "OpenStreetMap"])
map = folium.Map(location=initial_location, zoom_start=2, tiles=basemap)

# If click, add marker + run UDF
if 'last_clicked' in st.session_state:
    latlng=st.session_state.last_clicked
    col2.markdown(f'#### Result')
    col2.markdown(f'lat click laltn: ({round(latlng[0],3)},{round(latlng[1],3)})')
    folium.Marker(st.session_state.last_clicked, tooltip="Marker").add_to(map)
    lat, lng = st.session_state.last_clicked
    gdf = fused.run(my_udf, lat=lat, lng=lng, n=10, engine='local')
    col2.area_chart(gdf)

# Render map
with col1:
    output = st_folium(map, width=700, height=400)

if output and output.get('last_clicked') is not None:
    st.session_state.last_clicked = (output['last_clicked']['lat'], output['last_clicked']['lng'])
    st.rerun()

