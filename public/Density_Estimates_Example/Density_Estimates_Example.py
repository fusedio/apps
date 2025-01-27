import streamlit as st
st.markdown("### Repeated Density Estimates Example")

import micropip
await micropip.install('vega_datasets')
import altair as alt
from vega_datasets import data

source = data.iris()

chart=alt.Chart(source).transform_fold(
    [
        "petalWidth",
        "petalLength",
        "sepalWidth",
        "sepalLength",
    ],
    as_=["Measurement_type", "value"],
).transform_density(
    density="value",
    bandwidth=0.3,
    groupby=["Measurement_type"],
    extent=[0, 8],
).mark_area().encode(
    alt.X("value:Q"),
    alt.Y("density:Q"),
    alt.Row("Measurement_type:N"),
).properties(
    width=500, height=50
)#.interactive()
chart
