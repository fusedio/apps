import streamlit as st
# st.markdown("### World Projections Example")

import micropip
await micropip.install('vega_datasets')
import altair as alt
from vega_datasets import data

source = alt.topo_feature(data.world_110m.url, 'countries')

input_dropdown = alt.binding_select(options=[
    "albers",
    "albersUsa",
    "azimuthalEqualArea",
    "azimuthalEquidistant",
    "conicEqualArea",
    "conicEquidistant",
    "equalEarth",
    "equirectangular",
    "gnomonic",
    "mercator",
    "naturalEarth1",
    "orthographic",
    "stereographic",
    "transverseMercator"
], name='Projection ')
param_projection = alt.param(value="equalEarth", bind=input_dropdown)

chart = alt.Chart(source, width=500, height=300).mark_geoshape(
    fill='lightgray',
    stroke='gray'
).project(
    type=alt.expr(param_projection.name)
).add_params(param_projection)
chart
# st.altair_chart(chart)
