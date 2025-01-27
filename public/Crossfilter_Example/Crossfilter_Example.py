import streamlit as st
st.markdown("### Interactive Crossfilter Example")

import micropip
await micropip.install('vega_datasets')
import altair as alt
from vega_datasets import data

source = alt.UrlData(
    data.flights_2k.url,
    format={'parse': {'date': 'date'}}
)
brush = alt.selection_interval(encodings=['x'])

charts=[]
for column in ['distance', 'delay', 'time']:
    # Define the base chart, with the common parts of the
    # background and highlights
    base = alt.Chart(source, width=160, height=130).mark_bar().encode(
        x=alt.X(f'{column}:Q').bin(maxbins=20),
        y='count()'
    )
    # gray background with selection
    background = base.encode(
        color=alt.value('#444'),
        opacity=alt.value(0.5)
    ).add_params(brush)
    
    # blue highlights on the transformed data
    highlight = base.transform_filter(brush)
    
    # layer the two charts & repeat
    chart = alt.layer(
        background,
        highlight,
        data=source
    ).transform_calculate(
        "time",
        "hours(datum.date)"
    ).properties(
        width=150,
        height=150
    )
    charts.append(chart)

chart_combined=charts[0]
for chart in charts[1:]:
    chart_combined = chart_combined|chart
chart_combined

