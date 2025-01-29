import micropip
await micropip.install(['pydeck'])

import streamlit as st
import pydeck as pdk

st.title("🌲 Zonal Stats of Forest observations by global municipalities")

st.markdown("""
This app shows the output of a workflow to quantify forest cover for municipal areas around the world. The workflow aggregates a raster of global forest cover across zones defined by a vector table of municipalities. 

The final result, which you see here, is a table with records for every municipality and columns with summary metrics such as percent forest coverage. This type of analysis can help identify regions with significant forest loss to prioritize conservation efforts or support sustainable land-use planning. 

""")

url="https://www.fused.io/server/v1/realtime-shared/UDF_Zonal_Stats_Forest_Obs_Viewer/run/tiles/{z}/{x}/{y}?dtype_out_vector=geojson"


lat, lng = 28.3949, 84.1240

st.pydeck_chart(
    pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v9",
        initial_view_state=pdk.ViewState(latitude=lat, longitude=lng, zoom=5, pitch=0, bearing=-6),
        tooltip={"html": "<b>Value:</b> {stats_mean}","style": {"backgroundColor": "steelblue", "color": "white"},},
        layers=[
            pdk.Layer(
                "TileLayer",
                data=url,
                get_line_color=[255, 25, 2, 1000],
                get_elevation="properties.stats_mean",
                stroked=True,
                get_line_width=2,
                pickable=True,
                extruded=True,
                filled=True,
                get_fill_color="[properties.stats_mean*25, properties.stats_mean*256, properties.stats_mean*25]",
            )
        ],
    )
)
