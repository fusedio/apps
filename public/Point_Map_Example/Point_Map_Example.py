import streamlit as st
st.markdown("### Point Map Example")

import micropip
await micropip.install('vega_datasets')
import altair as alt
from vega_datasets import data

# Read in points
airports = data.airports()

# Read in polygons from topojson
states = alt.topo_feature(data.us_10m.url, feature='states')

# US states background
background = alt.Chart(states).mark_geoshape(
    fill='lightgray',
    stroke='white'
).properties(
    width=500,
    height=300
).project('albersUsa')

# airport positions on background
points = alt.Chart(airports).mark_circle(
    size=10,
    color='steelblue'
).encode(
    longitude='longitude:Q',
    latitude='latitude:Q',
    tooltip=['name', 'city', 'state']
)

background + points