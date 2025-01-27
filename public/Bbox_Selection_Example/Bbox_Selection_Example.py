import streamlit as st
import time
import micropip
await micropip.install(['pydeck','geopandas','streamlit-folium','affine'])
import geopandas as gpd
import fused
from streamlit_folium import st_folium
from folium.plugins import Draw
import folium
st.title("Download overture data")

@fused.cache
def get_data(gdf, overture_type='building', max_area=9):
    with status.status(f"Get Data", expanded=False):
        time.sleep(0.01)
        bbox = list(gdf.total_bounds)
        area=10**4*(bbox[2]-bbox[0])*(bbox[3]-bbox[1])
        if area<max_area:
            st.success(f'Selected area is smaller than max_area: {round(area,2)}<{max_area}')
            gdf = fused.run('UDF_Overture_Maps_Example', min_zoom=1, bbox=bbox, overture_type=overture_type) 
            # st.write(f'{len(gdf)=}')
            # st.write(gdf)
            return gdf
        else:
            st.error(f'Please select smaller area: current_area ({round(area,2)}) >= max_area ({max_area})')
            # st.write(gdf)
            return gdf

# Draw map
start_lat, start_lon = [37.773972, -122.431297]
m = folium.Map(location=[start_lat, start_lon], zoom_start=12, tiles="Cartodb Positron")
Draw(draw_options={'polyline': False,'polygon': True,'circle': False,'marker': False,'circlemarker': False,'rectangle': True,}).add_to(m)
output = st_folium(m, width=300, height=500, use_container_width=True) 

if output['all_drawings']:
    target_gdf = gpd.GeoDataFrame.from_features({'type': 'FeatureCollection','features': output['all_drawings']})
    status = st.empty()
    gdf = get_data(target_gdf)    
    # gdf.sjoin(target_gdf[['geometry']])
    import pydeck as pdk
    # Define the Pydeck Layer
    if 'height' in gdf:
        geojson_layer = pdk.Layer(
            "GeoJsonLayer",
            data=gdf[['geometry','height','roof_color','roof_height']],
            get_fill_color="[200, 30, 0, 160]",  # RGBA
            get_line_color="[255, 255, 255]",    # RGBA
            line_width_min_pixels=1,
            pickable=True,
        )
        
        # Set the Pydeck View
        view_state = pdk.ViewState(
            latitude=gdf.geometry.centroid.y.mean(),
            longitude=gdf.geometry.centroid.x.mean(),
            zoom=14,
            pitch=0,
        )
        
        # Create the Pydeck Deck
        map = pdk.Deck(
            layers=[geojson_layer],
            initial_view_state=view_state,
            tooltip={"text": "height: {height} \roof_color: {roof_color}\roof_height: {roof_height}"},  # Adjust the field to match your GeoJSON properties
        )
        st.pydeck_chart(map)
    
        print(list(gdf.columns))
        st.download_button(
           "Download",
           gdf.to_csv(index=False).encode('utf-8'),
           "file.csv",
           "text/csv",
           key='download-csv'
        )
        status.write(f'Number of records: {len(gdf)}')
    else:
        status.error(f'The selected area is too big. Please select smaller area.')
