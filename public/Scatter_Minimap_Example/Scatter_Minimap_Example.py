import streamlit as st
st.markdown("### Scatter Plot with Minimap")

import micropip
await micropip.install('vega_datasets')
import altair as alt
from vega_datasets import data

source = data.seattle_weather()

zoom = alt.selection_interval(encodings=["x", "y"])

minimap = (
    alt.Chart(source)
    .mark_point(size=1)
    .add_params(zoom)
    .encode(
        x="date:T",
        y="temp_max:Q",
        color=alt.condition(zoom, "weather", alt.value("lightgray")),
    )
    .properties(
        width=150,
        height=200,
        title="Minimap -- click and drag to zoom",
    )
)

detail = (
    alt.Chart(source)
    .mark_point()
    .encode(
        alt.X("date:T").scale(domain={"param": zoom.name, "encoding": "x"}),
        alt.Y("temp_max:Q").scale(domain={"param": zoom.name, "encoding": "y"}),
        color="weather",
    )
    .properties(width=300, height=400, title="Seattle weather -- detail view")
)

detail | minimap
