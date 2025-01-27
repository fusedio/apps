import streamlit as st
st.markdown("### Selection Histogram Example")

import micropip
await micropip.install('vega_datasets')
import altair as alt
from vega_datasets import data

cars = data.cars()
brush = alt.selection_interval()
scatter = (
    alt.Chart(cars)
    .mark_point()
    .encode(
        x="Horsepower",
        y="Miles_per_Gallon",
        color="Origin",
    )
    .add_params(brush)
)
bars = (
    alt.Chart(cars)
    .mark_bar()
    .encode(y="Origin:N", color="Origin:N", x="count(Origin):Q")
    .transform_filter(brush)
)
chart = st.altair_chart(scatter & bars)
