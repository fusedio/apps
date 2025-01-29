import micropip
await micropip.install(['folium', 'streamlit-folium', 'geopandas', 'duckdb'])

import json
import folium
import streamlit as st
from streamlit_folium import st_folium
import geopandas as gpd
import fused_app
import pandas as pd
import duckdb
from shapely.wkt import loads

con = duckdb.connect(':memory:')
st.title("✈️ Count airplanes in airports 📊")
col1, col2 = st.columns(2)


# Read the CSV
airports = pd.read_csv('https://fused-asset.s3.amazonaws.com/misc/plinio/airports.csv')[['geometry', 'name']]
airports['geometry'] = airports['geometry'].apply(loads)
airports = gpd.GeoDataFrame(airports, geometry='geometry')
airports['centroids'] = airports.geometry.centroid

@st.cache_resource
def run_udf_async(row_array):
    import asyncio
    outputs = []
    for row in row_array:
        row=gpd.GeoDataFrame.from_features([row])
        out = asyncio.Task(fused_app.run("UDF_Airplane_Detection_AOI", target_gdf=row.to_json(), sync=False))
        outputs.append((row.name.iloc[0], out))
    return outputs

async def run_udf_parallel(row_array):
    func_output = run_udf_async(row_array)
    a = []
    for item in func_output:
        out = await item[1]
        if (out is not None) and len(out) > 0 and ('a' not in out.columns)> 0:
            out['name'] = item[0]
            a.append(out)
    return a

array_of_geojsons = json.loads(airports[['geometry', 'name']].to_json())['features']

udf_outputs = await run_udf_parallel(array_of_geojsons)

df_airplanes = pd.concat(udf_outputs)[['name']]

# Structure output
col1.markdown("## Totals")
out = con.sql("SELECT name, count(*) as cnt FROM df_airplanes GROUP BY all").df()
col1.bar_chart(out, x='name', y='cnt', x_label='Airport', y_label='Count')

# Count airplanes
airport = col2.selectbox("Select airport", airports.name.values)
row = airports[airports.name==airport].iloc[:1][['geometry', 'name']].to_json()
airplanes = fused_app.run("UDF_Airplane_Detection_AOI", target_gdf=row)
airplanes.crs = "EPSG:4326"

# Create map
m = folium.Map(location=[airports[airports.name==airport].centroid.y, airports[airports.name==airport].centroid.x], zoom_start=15, max_zoom=18, min_zoom=15, tiles="Cartodb Positron")
folium.GeoJson(airplanes).add_to(m)
# ArcGIS RGB raster Tile
url_raster = "https://www.fused.io/server/v1/realtime-shared/UDF_Arcgis_Rgb/run/tiles/{z}/{x}/{y}?dtype_out_raster=png"
folium.TileLayer(tiles=url_raster, attr="Fused").add_to(m)  # Base image

with col2:
    # Render map
    st_folium(m, width=300, height=500, use_container_width=True)

