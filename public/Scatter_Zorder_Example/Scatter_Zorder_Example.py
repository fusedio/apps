import streamlit as st
st.markdown("### Scatter Selection (Hover) Zorder Example")

import micropip
await micropip.install('vega_datasets')
import altair as alt
from vega_datasets import data

cars = data.cars.url

hover = alt.selection_point(on='pointerover', nearest=True, empty=False)

chart = alt.Chart(cars, title='Selection obscured by other points').mark_circle(opacity=1).encode(
    x='Horsepower:Q',
    y='Miles_per_Gallon:Q',
    color=alt.condition(hover, alt.value('coral'), alt.value('lightgray')),
    size=alt.condition(hover, alt.value(300), alt.value(30))
).add_params(
    hover
)
chart2=chart.encode(
    order=alt.condition(hover, alt.value(1), alt.value(0))
).properties(
    title='Selection brought to front'
).properties(
    width=600,
    height=400
)
chart2 #| chart