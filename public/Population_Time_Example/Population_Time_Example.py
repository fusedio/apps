import streamlit as st
st.markdown("### US Population Pyramid Over Time")

import micropip
await micropip.install('vega_datasets')
import altair as alt
from vega_datasets import data

source = data.population.url

slider = alt.binding_range(min=1850, max=2000, step=10)
select_year = alt.selection_point(name='year', fields=['year'],
                                   bind=slider, value={'year': 2000})

base = alt.Chart(source).add_params(
    select_year
).transform_filter(
    select_year
).transform_calculate(
    gender=alt.expr.if_(alt.datum.sex == 1, 'Male', 'Female')
).properties(
    width=250
)


color_scale = alt.Scale(domain=['Male', 'Female'],
                        range=['#1f77b4', '#e377c2'])

left = base.transform_filter(
    alt.datum.gender == 'Female'
).encode(
    alt.Y('age:O').axis(None),
    alt.X('sum(people):Q')
        .title('population')
        .sort('descending'),
    alt.Color('gender:N')
        .scale(color_scale)
        .legend(None)
).mark_bar().properties(title='Female')

middle = base.encode(
    alt.Y('age:O').axis(None),
    alt.Text('age:Q'),
).mark_text(color='gray').properties(width=20)

right = base.transform_filter(
    alt.datum.gender == 'Male'
).encode(
    alt.Y('age:O').axis(None),
    alt.X('sum(people):Q').title('population'),
    alt.Color('gender:N').scale(color_scale).legend(None)
).mark_bar().properties(title='Male')
chart = left | middle | right
# chart = alt.concat(left, middle, right)
chart