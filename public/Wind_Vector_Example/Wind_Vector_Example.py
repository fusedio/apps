import streamlit as st
st.markdown("### Wind Vector Map Example")

import micropip
await micropip.install('vega_datasets')
import altair as alt
from vega_datasets import data

df_wind = data.windvectors()
data_world = alt.topo_feature(data.world_110m.url, "countries")

wedge = alt.Chart(df_wind).mark_point(shape="wedge", filled=True).encode(
    alt.Latitude("latitude"),
    alt.Longitude("longitude"),
    alt.Color("dir")
        .scale(domain=[0, 360], scheme="rainbow")
        .legend(None),
    alt.Angle("dir").scale(domain=[0, 360], range=[180, 540]),
    alt.Size("speed").scale(rangeMax=500)
).project("equalEarth")

xmin, xmax, ymin, ymax = (
    df_wind.longitude.min(),
    df_wind.longitude.max(),
    df_wind.latitude.min(),
    df_wind.latitude.max(),
)

# extent as feature or featurecollection
extent = {
    "type": "Feature",
    "geometry": {"type": "Polygon",
                 "coordinates": [[
                     [xmax, ymax],
                     [xmax, ymin],
                     [xmin, ymin],
                     [xmin, ymax],
                     [xmax, ymax]]]
                },
    "properties": {}
}

# use fit combined with clip=True
base = (
    alt.Chart(data_world)
    .mark_geoshape(clip=True, fill="lightgray", stroke="black", strokeWidth=0.5)
    .project(type="equalEarth", fit=extent)
)

base + wedge
