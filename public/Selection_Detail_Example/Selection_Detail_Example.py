import streamlit as st
st.markdown("### Selection Detail Example")

import altair as alt
import pandas as pd
import numpy as np

np.random.seed(0)

n_objects = 20
n_times = 50

# Create one (x, y) pair of metadata per object
locations = pd.DataFrame({
    'id': range(n_objects),
    'x': np.random.randn(n_objects),
    'y': np.random.randn(n_objects)
})

# Create a 50-element time-series for each object
timeseries = pd.DataFrame(np.random.randn(n_times, n_objects).cumsum(0),
                          columns=locations['id'],
                          index=pd.RangeIndex(0, n_times, name='time'))

# Melt the wide-form timeseries into a long-form view
timeseries = timeseries.reset_index().melt('time')

# Merge the (x, y) metadata into the long-form view
timeseries['id'] = timeseries['id'].astype(int)  # make merge not complain
data = pd.merge(timeseries, locations, on='id')

# Data is prepared, now make a chart

# selector = alt.selection_point(fields=['id'])
selector = alt.selection_point(fields=['id'], on='pointerover', nearest=False, empty=False)
opacity=alt.condition(selector, alt.value(1), alt.value(0.25))
# color=alt.condition(selector, 'id:N', alt.value('gray'), legend=None)
base = alt.Chart(data).properties(
    width=250,
    height=250
).add_params(selector)
points = base.mark_point(filled=True, size=200).encode(
    x='mean(x)',
    y='mean(y)',
    color= 'id:N',
    # color=color,
    opacity=opacity
).encode(
    order=alt.condition(selector, alt.value(1), alt.value(0))
)
line = base.mark_line().encode(
    x=alt.X('time'),
    y=alt.Y('value').scale(domain=(-15, 15)),
    color=alt.Color('id:N', legend=None),
    opacity=opacity
)#.transform_filter(selector)

points | line