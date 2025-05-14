import streamlit as st
st.markdown("### Choropleth Map Example: Unemployement Rate in US")
st.write("County-level unemployement rate in the US (as per 2009)")

import micropip
await micropip.install('vega_datasets')
import altair as alt
from vega_datasets import data

counties = alt.topo_feature(data.us_10m.url, 'counties')
source = data.unemployment.url
chart = alt.Chart(counties).mark_geoshape().encode(
    color='rate:Q'
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(source, 'id', ['rate'])
).project(
    type='albersUsa'
).properties(
    width=500,
    height=300
)
chart

st.write("Data taken from [vega-datasets](https://vega.github.io/vega-datasets/datapackage.html#path-61)")