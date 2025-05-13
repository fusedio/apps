import streamlit as st
import pandas as pd
import fused
import micropip
import requests
import numpy as np

st.title("Crop Data Layer Hex Explorer!")
st.write(
    """
    Search and Visualize any crop from the USDA's Crop Data Layer dataset.
    Data taken from the Fused-partitioned dataset hosted on [Source Coop](https://source.coop/repositories/fused/hex/description).
    """)


await micropip.install(['pydeck', 'plotly', 'scikit-learn', 'transformers_js_py'])
import pydeck as pdk
import plotly.express as px
from transformers_js_py import import_transformers_js
from sklearn.metrics.pairwise import cosine_similarity

@st.cache_data
def load_usda_classes():
    url = "https://storage.googleapis.com/earthengine-stac/catalog/USDA/USDA_NASS_CDL.json"
    response = requests.get(url)
    data = response.json()
    crops = data["summaries"]["eo:bands"][0]["gee:classes"]
    
    # Create a dictionary mapping value to description
    cdl_categories = {}
    for crop in crops:
        if "value" in crop and "description" in crop:
            cdl_categories[crop["value"]] = crop["description"]
    
    return cdl_categories

# Initialize app state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.cdl_categories = load_usda_classes()

cdl_categories = st.session_state.cdl_categories

# Initialize embedding model
async def initialize_embeddings():
    with st.spinner("Loading embedding model..."):
        transformers = await import_transformers_js()
        extractor = await transformers.pipeline("feature-extraction", "Xenova/gte-small")
        
        # Generate embeddings for all crop descriptions
        crop_descriptions = list(cdl_categories.values())
        
        progress = st.progress(0)
        results = []
        for i, text in enumerate(crop_descriptions):
            output = await extractor(text, {"pooling": "mean", "normalize": True})
            results.append(output.to_numpy())
            progress.progress(float((i + 1) / len(crop_descriptions)))
        
        crop_embeddings = np.vstack(results)
        return crop_embeddings, extractor, crop_descriptions

# Process search query
async def process_query(query_text, crop_embeddings, extractor, crop_descriptions):
    output = await extractor(query_text, {"pooling": "mean", "normalize": True})
    query_embedding = output.to_numpy().reshape(1, -1)
    similarities = cosine_similarity(query_embedding, crop_embeddings)[0]
    
    # Convert numpy.float32 to Python float
    similarities = [float(s) for s in similarities]
    
    # Get all indices sorted by similarity
    sorted_indices = np.argsort(similarities)[::-1]
    
    return sorted_indices.tolist(), similarities

# Initialize model if not already done
if not st.session_state.initialized:
    crop_embeddings, extractor, crop_descriptions = await initialize_embeddings()
    st.session_state.crop_embeddings = crop_embeddings
    st.session_state.extractor = extractor
    st.session_state.crop_descriptions = crop_descriptions
    st.session_state.initialized = True
    st.rerun()

# Search interface
year = st.selectbox(
    "Select Year",
    options=range(2012, 2025, 2),
    index=6  # Index 6 corresponds to 2024 (7th element in the range)
)

query = st.text_input("🔍 Search for CDL Layer (Using a [light-weight LLM model](https://github.com/whitphx/transformers.js.py) running in your browser to find the closest [CDL crop](https://storage.googleapis.com/earthengine-stac/catalog/USDA/USDA_NASS_CDL.json)):", "Open Water")

if query:
    with st.spinner("Finding similar layer..."):
        sorted_indices, similarities = await process_query(
            query, 
            st.session_state.crop_embeddings, 
            st.session_state.extractor,
            st.session_state.crop_descriptions
        )
    
    # Get crop IDs and descriptions for top matches
    top_matches = []
    for i, idx in enumerate(sorted_indices[:5]):
        crop_description = st.session_state.crop_descriptions[idx]
        # Find the crop ID by description
        crop_id = [k for k, v in cdl_categories.items() if v == crop_description][0]
        similarity = similarities[idx]
        top_matches.append((crop_id, crop_description, similarity))
    
    # Simple selection interface
    options = []
    for crop_id, crop_description, similarity in top_matches:
        options.append(f"{crop_description} (ID: {crop_id}, Similarity from query: {similarity:.2f})")
    
    selected_option = st.selectbox("Select a layer to visualize (Defaults to most similar from query):", options)
    
    # Extract the crop ID from the selected option
    selected_crop_id = int(selected_option.split("ID: ")[1].split(",")[0])
    selected_crop = [v for k, v in cdl_categories.items() if k == selected_crop_id][0]
    
    # Continue with visualization
    min_ratio_in_hex = st.slider("Minimum ratio to keep", min_value=0.0, max_value=1.0, value=0.05, step=0.05)
    
    view_state = pdk.ViewState(
        latitude = 39.8283,
        longitude = -98.5795,
        zoom = 3  # This gives a good view of the continental US
    )
    
    # hex_df = fused.run(
    #     "UDF_Hex5_visualize_CDL_crop", 
    #     vals=[selected_crop_id],
    #     year=2024,
    # )
    hex_df = fused.run(
        "CDL_from_source_coop",
        crop_value_list = [selected_crop_id],
        cell_to_parent_res= 5, # Change this to display at a higher resolution
        # year = 2024, # Change to any supported year on Source Coop
        year = year
    )
    
    # Casting to hex type 
    hex_df['hex']=hex_df['hex'].map(lambda x:hex(x)[2:])
    
    # Filtering out any values below selected ratio
    hex_df = hex_df[hex_df['pct'] > min_ratio_in_hex*100]
    
    # Dynamic colors
    min_val = hex_df['area'].min()
    max_val = hex_df['area'].max()
    
    # Define a layer to display on a map
    def get_color_for_value(val):
        # Normalize the value between 0 and 1
        normalized = (val - min_val) / (max_val - min_val) if max_val > min_val else 0.5
        
        # Create a color gradient (blue to pink)
        r = int(255 * normalized)
        g = 140
        b = int(255 * (1 - normalized))
        
        return [r, g, b, 200]
    
    hex_df['color'] = hex_df['area'].apply(get_color_for_value)
    
    layer = pdk.Layer(
        "H3HexagonLayer",
        hex_df,
        pickable=True,
        stroked=True,
        filled=True,
        extruded=False,
        get_hexagon="hex",
        get_fill_color="color"
    )
    
    # Round the pct column to 2 decimal for tooltip vis
    hex_df['pct'] = hex_df['pct'].round(2)
    
    tooltip = {
        "html": "<b>H3 Index:</b> {hex}<br><b>Value:</b> {data}<br><b>area:</b> {area}<br><b>Percentage:</b> {pct}%",
        "style": {
            "backgroundColor": "white",
            "color": "black",
            "fontSize": "12px",
            "padding": "10px"
        }
    }
    
    st.pydeck_chart(pdk.Deck(
        layers=[layer], 
        initial_view_state=view_state,
        tooltip=tooltip
    ))
    
    # Create interactive histogram
    fig = px.histogram(hex_df, x='area', nbins=50)
    fig.update_layout(
        title="Distribution of Area Values per hexagon",
        xaxis_title="Area",
        yaxis_title="Count"
    )
    st.plotly_chart(fig)