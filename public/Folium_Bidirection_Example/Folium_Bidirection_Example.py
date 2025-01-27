import streamlit as st
st.set_page_config(layout="wide") 
st.markdown('### Folium Bi-direction Example')

import micropip
await micropip.install('streamlit_folium')
import folium
from streamlit_folium import st_folium

col1, col2  = st.columns([1,1])
with col1:
    st.markdown('''`streamlit-folium` combines Streamlit and Folium to create map with bi-directional interactivity, allowing for both display and data transfer between the web app and Python.''')
    m = folium.Map(zoom_start=5, location=[37.7749, -122.4194], tiles="cartodbdark_matter")
    draw = folium.plugins.Draw(
                export=False,
                position="topleft",
                draw_options={
                    "polyline": False,
                    "polygon": True,
                    "circle": False,
                    "marker": False,
                    "circlemarker": False,
                    "rectangle": False,
                },
                )
    m.add_child(draw)
    output = st_folium(m, width=None, height=400)
with col2:
    st.write(output)
