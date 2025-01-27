import streamlit as st
import pandas as pd
import fused
import micropip

st.title("🖼️ Hexify any image!")

st.markdown("""
This app calls the ["Hexify Image"](https://www.fused.io/workbench/catalog/Hexify_Image-b817f7fd-cd52-40d3-a601-d0fcc36d0f86) UDF by [Jennings Anderson](https://www.linkedin.com/in/jenningsanderson/). The H3 resolution and URL of your image are passed as input parameters to the UDF.
""")
st.info("""
Instructions: Paste a URL to your favorite `.png` image below and see it get processed to H3.
""")

h3_res = st.selectbox("H3 resolution", [5, 6, 7, 8, 9, 10, 11, 12],2)
image_url = st.text_input('URL of image to Hexify:', value="https://fused-magic.s3.us-west-2.amazonaws.com/thumbnails/udfs-staging/jennings.png")

# Initialize session state for map data
if 'map_data' not in st.session_state:
    st.session_state.map_data = None

# Button to run the hexify function and update the map
if st.button("Run!"):
    try:
        df = fused.run('UDF_Hexify_Image', path=image_url, res=h3_res)
        df['hex'] = df['hex'].apply(lambda x: hex(x)[2:].lower())
        st.session_state.map_data = df  # Store the map data in session state
    except Exception as e:
        st.write('😅 It seems this image is not supported. Please try another. ')
        st.session_state.map_data = None

# Check if map data is available before rendering
await micropip.install('pydeck')
import pydeck as pdk
if st.session_state.map_data is not None:
    df = st.session_state.map_data
    
    # Define a layer to display on a map
    layer = pdk.Layer(
        "H3HexagonLayer",
        df,
        pickable=True,
        stroked=True,
        filled=True,
        extruded=True,
        get_hexagon="hex",
        get_fill_color="[value, value, value]",
        get_line_color=[25, 25, 255],
        line_width_min_pixels=2,
        get_elevation='value^2',
        elevation_scale=50
    )
    
    # Set the viewport location
    view_state = pdk.ViewState(latitude=0.4, longitude=0.5, zoom=9.5, bearing=10, pitch=45)
    
    # Render the map with stored data
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))
