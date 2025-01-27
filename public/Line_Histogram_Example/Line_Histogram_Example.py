import streamlit as st
st.markdown("### Bar Chart with Line on Dual Axis Example")

import micropip
await micropip.install('vega_datasets')
import altair as alt
from vega_datasets import data

source = data.wheat()

base = alt.Chart(source).encode(x='year:O')

bar = base.mark_bar().encode(y='wheat:Q')

line =  base.mark_line(color='red').encode(
    y='wages:Q'
)

bar_line = (bar + line).properties(width=600)#.interactive()
bar_line
