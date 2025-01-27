import streamlit as st
st.markdown("### Histogram with Gradient Color Example")

import micropip
await micropip.install('vega_datasets')
import altair as alt
from vega_datasets import data

source = data.movies.url

chart = alt.Chart(source).mark_bar().encode(
    alt.X("IMDB_Rating:Q").bin(maxbins=20).scale(domain=[1, 10]),
    alt.Y('count()'),
    alt.Color("IMDB_Rating:Q").bin(maxbins=20).scale(scheme='pinkyellowgreen')
).properties(
    width=650,
    height=350
)#.interactive()
chart

