import streamlit as st
import time
import micropip

await micropip.install(["pydeck", "geopandas", "streamlit-folium"])
import geopandas as gpd
import fused
from streamlit_folium import st_folium
from folium.plugins import Draw
import folium

st.set_page_config(page_title="Overture Maps Downloader")
st.title("Overture Maps Downloader")


def get_data(gdf, overture_type, buffer):
    result = fused.run(
        "UDF_Overture_Maps_Example", bounds=list(gdf.total_bounds), overture_type=overture_type, clip=True
    )
    if buffer:
        result.geometry = result.geometry.buffer(buffer)
    return result


# Draw map
start_lat, start_lon = [37.773972, -122.431297]
import shapely

p = shapely.Point(start_lon, start_lat)
bounds = p.buffer(0.01).bounds

all_drawings = st.session_state.get("all_drawings", None)

overture_type = st.selectbox("Type", ["building", "segment"], disabled=bool(all_drawings))

if not all_drawings:
    st.markdown(
        f"Draw a rectangle below to select {overture_type}s from the [Overture Maps](https://www.fused.io/workbench/catalog/Overture_Maps_Example-64071fb8-2c96-4015-adb9-596c3bac6787) dataset."
    )

    m = folium.Map(location=[start_lat, start_lon], min_zoom=13, tiles="Cartodb Positron")
    m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
    Draw(
        draw_options={
            "polyline": False,
            "polygon": False,
            "circle": False,
            "marker": False,
            "circlemarker": False,
            "rectangle": True,
        }
    ).add_to(m)
    output = st_folium(m, width=300, height=500, use_container_width=True)

    if output["all_drawings"]:
        st.session_state["all_drawings"] = output["all_drawings"]
        st.rerun()

else:
    st.markdown(
        f"Querying {overture_type}s from the [Overture Maps](https://www.fused.io/workbench/catalog/Overture_Maps_Example-64071fb8-2c96-4015-adb9-596c3bac6787) dataset:"
    )

    with st.expander("Operations"):
        buffer = st.number_input("Building buffer", min_value=0.0, max_value=1.0, step=0.0001, format="%0.5f")

    with st.spinner():
        time.sleep(1)

        if st.button("Clear spatial selection", type="secondary"):
            st.session_state.clear()
            st.rerun()

        target_gdf = gpd.GeoDataFrame.from_features({"type": "FeatureCollection", "features": all_drawings})

        gdf = get_data(target_gdf, overture_type, buffer)
        import pydeck as pdk

        # Define the Pydeck Layer
        if "id" in gdf:
            geojson_layer = pdk.Layer(
                "GeoJsonLayer",
                data=gdf[
                    ["geometry", *(["height", "roof_color", "roof_height"] if overture_type == "building" else [])]
                ],
                get_fill_color="[200, 30, 0, 160]",  # RGBA
                get_line_color="[255, 255, 255]",  # RGBA
                line_width_min_pixels=1,
                pickable=True,
            )

            # Set the Pydeck View
            view_state = pdk.ViewState(
                latitude=gdf.geometry.centroid.y.mean(),
                longitude=gdf.geometry.centroid.x.mean(),
                zoom=15,
                pitch=0,
            )

            # Create the Pydeck Deck
            map = pdk.Deck(
                layers=[geojson_layer],
                initial_view_state=view_state,
                tooltip={"text": "height: {height}"},  # Adjust the field to match your GeoJSON properties
            )
            st.pydeck_chart(map)

            st.download_button(
                "Download CSV",
                gdf.to_csv(index=False).encode("utf-8"),
                "file.csv",
                "text/csv",
                key="download-csv",
                type="primary",
            )
            st.write(f"Number of records: {len(gdf)}")
            # TODO: segments has some numpy fields
            if overture_type == "building":
                with st.expander("Table"):
                    st.dataframe(gdf.drop(columns=["geometry"]))

        else:
            st.error(f"The selected area is too big. Please select smaller area.")
