import streamlit as st

token='fsh_72YnV1lSJwwcijOgRaTK5g'  
json_str='{"New York City":{"lng":-73.9888,"lat":40.7473},"Denver":{"lng":-104.982,"lat":39.739},"San Francisco":{"lng":-122.449385,"lat":37.762968}}' 
# json_str='{"New York City":{"lng":-73.9888,"lat":40.7473},"Denver":{"lng":-104.982,"lat":39.739},"San Francisco":{"lng":-122.449385,"lat":37.762968},"Houston":{"lng":-95.370,"lat":29.756}}' 


st.set_page_config(page_title="Geos Demo", page_icon="🌎", layout="wide")
st.markdown("# Time Series Demo")  
st.write(
    """This app demonstrates how you can use Streamlit to create interactive visualizations. It features DayMet dataset. Use the slider to adjust various parameters.
""") 
colors = [ "#FF3333", "#D1E450", "#00BBFF", "#BB44BB"]
colors_rgba = [[int(c[i:i+2], 16) for i in (1, 3, 5)] + [255] for c in colors]
# colors=["rgba(0,255,255,0.5)", "rgba(255,87,51,0.5)", "rgba(255,215,0,0.5)", "rgba(138,43,226,0.5)", "rgba(255,105,180,0.5)"]
loc_col=' '
old_col_names=['location','lat','lng','year', 'yday', 'tmax', 'tmin', 'prcp', 'dayl', 'srad', 'swe', 'vp']
new_col_names=[loc_col,'lat','lng', "year", "yday", "Maximum temperature (°C)", "Minimum temperature (°C)", "Precipitation (mm/day)", "Daylength (seconds)", "Shortwave radiation (W/m²/day)", "Snow Water Equivalent (mm)", "Vapor pressure (Pa)"]
options=new_col_names[5:]
import micropip
await micropip.install("geopandas") 
await micropip.install("requests") 
await micropip.install("xarray") 
await micropip.install("yarl") 
import asyncio 
import altair as alt
import fused_app    
import pandas as pd 

def fn_draw_map(df_meta, draw_map):
    draw_map.pydeck_chart(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/dark-v9",
            initial_view_state=pdk.ViewState(
                latitude=30,
                longitude=-97,
                zoom=1,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                'ScatterplotLayer',
                df_meta,
                get_position=['lng', 'lat'],
                get_fill_color='color',  
                radiusMinPixels=10,
                pickable=True,
                auto_highlight=False
            )
            ]) 
    )
st.markdown("""<style>section[data-testid="stSidebar"] {
            width: 400px !important; # Set the width to your desired value}</style>""",unsafe_allow_html=True,)
year_start_end = st.sidebar.slider(
        'Select the year range',
        min_value=1980,
        max_value=2023,
        value=(2019, 2023),
        step=1
    ) 
st.sidebar.markdown('Places of Interest table')
df_meta= pd.read_json(json_str) 
df_meta = st.sidebar.data_editor(df_meta.T[['lat','lng']], use_container_width=True) 
json_str=df_meta[['lng','lat']].T.to_json()
# st.write(json_str)
df_meta.sort_index(inplace=True)
df_meta['color'] = colors_rgba[:len(df_meta)]
draw_map=st.sidebar.empty()
await micropip.install("pydeck") 
import pydeck as pdk
fn_draw_map(df_meta, draw_map)


@st.cache_resource 
def func(token, json_str_list, start_year, end_year):
    resutls = []
    for json_str in json_str_list:
        out = asyncio.Task(fused_app.run(token, json_str=json_str, start_year=start_year, end_year=end_year, sync=False))
        resutls.append(out)
    return resutls
option = st.selectbox('Select a parameter to visualize', options)

resutls = func(token, [json_str], start_year=year_start_end[0], end_year=year_start_end[1])   
for v in resutls: 
    df = await v  
    df=df[old_col_names]
    df.columns = new_col_names
    # df = df[df[loc_col]=='Denver']
df['date'] = pd.to_datetime(df['year'].astype(str) + df['yday'].astype(str), format='%Y%j')
df.set_index('date')
chart_title=st.empty()
chart_plot=st.empty()
moving_window=st.slider('Moving Average Window Size',min_value=1, max_value=180, value=90)
df['value'] = a = df.groupby(loc_col)[option].transform(lambda x: x.rolling(window=moving_window).mean())
# df['value'] = df[option].rolling(window=moving_window).mean()
# df=df[df['value']>0]
# df = df.dropna()
chart = alt.Chart(df).mark_line().encode(
    x=alt.X('date:T', title=None),
    color=alt.Color(f'{loc_col}:N', scale=alt.Scale(range=colors),legend=alt.Legend(orient='bottom', offset=0, columns=5, symbolSize=100)),
    y=alt.Y('value', title=option),
    tooltip=['date:T', f'{loc_col}:N', alt.Tooltip(option, format='.2f')]
).properties( 
    width=700,      
    height=400,
    # title=f"{option.capitalize()} Time Series"
).interactive()
# chart_title.write(f"### {option} time series")
chart_plot.altair_chart(chart, use_container_width=True)

loc_list = df[loc_col].value_counts().index
if len(df_meta)!=len(loc_list):
    df_meta=df_meta[df_meta.index.isin(loc_list)]
    df_meta['color'] = colors_rgba[:len(df_meta)]
fn_draw_map(df_meta, draw_map)
