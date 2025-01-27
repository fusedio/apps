import streamlit as st
st.set_page_config(layout="wide") 
st.markdown('### Real Estate Site Selector using Pydeck TileLayer')

import micropip
await micropip.install('pydeck')
import pydeck as pdk

url_nsi = "https://www.fused.io/server/v1/realtime-shared/fsh_38dVZMy7vNoXVu5iiYir3h/run/tiles/{z}/{x}/{y}?dtype_out_vector=geojson&target_metric=val_struct"
lat, lng = 40.750, -73.980

st.pydeck_chart(
    pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v9",
        initial_view_state=pdk.ViewState(latitude=lat, longitude=lng, zoom=14, pitch=50, bearing=-6),
        tooltip={"html": "<b>Structure Value:</b> ${val_struct}","style": {"backgroundColor": "steelblue", "color": "white"},},
        layers=[
            pdk.Layer(
                "TileLayer",
                data=url_nsi,
                get_line_color=[255, 25, 2, 100],
                get_elevation="properties.stats / 20",
                stroked=True,
                get_line_width=2,
                pickable=True,
                extruded=True,
                filled=True,
                get_fill_color="[properties.stats*2, properties.stats*3, properties.stats*3]",
            )
        ],
    )
)
