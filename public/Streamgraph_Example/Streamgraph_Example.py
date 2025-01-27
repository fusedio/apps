import streamlit as st
st.markdown("### Streamgraph Example")

import micropip
await micropip.install('vega_datasets')
import altair as alt
from vega_datasets import data

source = data.unemployment_across_industries.url

selection = alt.selection_point(fields=['series'], bind='legend', on='pointerover', nearest=False, empty=True)

chart = alt.Chart(source).mark_area().encode(
    alt.X('yearmonth(date):T').axis(format='%Y', domain=False, tickSize=0),
    alt.Y('sum(count):Q').stack('center').axis(None),
    alt.Color('series:N').scale(scheme='category20b'),
    opacity=alt.condition(selection, alt.value(1), alt.value(0.25)),
).properties(
    width=700, height=300).add_params(
    selection)
chart
