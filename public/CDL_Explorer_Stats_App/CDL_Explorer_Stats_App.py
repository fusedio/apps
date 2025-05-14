import streamlit as st
import pandas as pd
import fused
import micropip
import requests
import numpy as np

st.title("Crop Data Layer Explorer & Time Series Analysis")
st.write(
    """
    Search, visualize, and analyze trends for any crop from the USDA's Crop Data Layer dataset.
    Data from the Fused-partitioned dataset hosted on [Source Coop](https://source.coop/repositories/fused/hex/description).
    """
)

# Load dependencies
await micropip.install(['plotly', 'scikit-learn', 'transformers_js_py'])
import plotly.express as px
from transformers_js_py import import_transformers_js
from sklearn.metrics.pairwise import cosine_similarity
import plotly.graph_objects as go

# Initialize token
TOKEN = "fsh_3cy84FGNDO1CD8NpTRXPKy"

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

# Load state/county level data
@st.cache_data
def load_crop_data(crop_value, cell_to_parent_res, min_ratio, admin_level):
    with st.spinner(f"Loading {cdl_categories[crop_value]} data at {admin_level} level..."):
        df = fused.run(
            TOKEN,
            crop_value=crop_value,
            cell_to_parent_res=cell_to_parent_res,
            min_ratio=min_ratio,
            admin_level=admin_level
        )
        return df

# Initialize model if not already done
if not st.session_state.initialized:
    crop_embeddings, extractor, crop_descriptions = await initialize_embeddings()
    st.session_state.crop_embeddings = crop_embeddings
    st.session_state.extractor = extractor
    st.session_state.crop_descriptions = crop_descriptions
    st.session_state.initialized = True
    st.rerun()

# Layout with sidebar
with st.sidebar:
    st.header("Search Parameters")
    query = st.text_input("🔍 Search for CDL Layer:", "Open Water")
    year = st.selectbox(
        "Select Year",
        options=range(2012, 2025, 2),
        index=6  # Index 6 corresponds to 2024
    )
    min_ratio_in_hex = st.slider("Minimum ratio to keep", min_value=0.0, max_value=1.0, value=0.05, step=0.05)
    
    st.header("Analysis Parameters")
    cell_to_parent_res = st.slider("Resolution (H3 Level)", min_value=4, max_value=8, value=6)
    min_ratio_stats = st.slider("Minimum ratio for statistics", min_value=0.0, max_value=0.5, value=0.0, step=0.01)

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
        options.append(f"{crop_description} (ID: {crop_id}, Similarity: {similarity:.2f})")
    
    selected_option = st.selectbox("Select a layer to visualize:", options)
    
    # Extract the crop ID from the selected option
    selected_crop_id = int(selected_option.split("ID: ")[1].split(",")[0])
    selected_crop = [v for k, v in cdl_categories.items() if k == selected_crop_id][0]
    
    st.write(f"## {selected_crop} (ID: {selected_crop_id})")
    
    # Create tabs for different visualizations
    tabs = st.tabs(["Distribution", "State Time Series", "County Time Series", "State Rankings", "County Rankings"])
    
    with tabs[0]:
        # Load hexagon data for the histogram
        with st.spinner(f"Loading hexagon data for {selected_crop}..."):
            hex_df = fused.run(
                "UDF_CDL_from_source_coop",
                crop_value_list=[selected_crop_id],
                cell_to_parent_res=5,
                year=year
            )
            
            # Casting to hex type 
            hex_df['hex'] = hex_df['hex'].map(lambda x: hex(x)[2:])
            
            # Filtering out any values below selected ratio
            hex_df = hex_df[hex_df['pct'] > min_ratio_in_hex*100]
        
        # Create interactive histogram
        fig = px.histogram(hex_df, x='pct', nbins=100)
        fig.update_layout(
            title=f"Distribution of {selected_crop} Percentage per Hexagon ({year})",
            xaxis_title="Percentage",
            yaxis_title="Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:
        # Load state-level time series data
        state_data = load_crop_data(selected_crop_id, cell_to_parent_res, min_ratio_stats, "state")
        
        if state_data is None or len(state_data) == 0:
            st.warning(f"No state-level data found for {selected_crop}.")
        else:
            # Get years from columns
            years = [int(col.split('_')[1]) for col in state_data.columns if col.startswith('area_')]
            years.sort()
            
            # Check if state_name column exists, otherwise use state_id
            name_col = 'state_name' if 'state_name' in state_data.columns else 'state_id'
            
            # Fill missing names with ID values
            if name_col == 'state_name':
                state_data[name_col] = state_data[name_col].fillna(state_data['state_id'].astype(str))
            
            # Get top 5 states by most recent year area
            latest_year = max(years)
            latest_col = f'area_{latest_year}'
            top_states = state_data.sort_values(by=latest_col, ascending=False).head(5)[name_col].tolist()
            
            # Multi-select for states (with top 5 pre-selected)
            all_states = sorted(state_data[name_col].unique().tolist())
            selected_states = st.multiselect(
                "Select states to compare:",
                options=all_states,
                default=top_states
            )
            
            if not selected_states:
                st.info("Please select at least one state to display time series.")
            else:
                # Filter data for selected states
                filtered_state_data = state_data[state_data[name_col].isin(selected_states)]
                
                # Create area time series
                area_fig = go.Figure()
                
                for state_name in selected_states:
                    state_row = filtered_state_data[filtered_state_data[name_col] == state_name].iloc[0]
                    area_values = [state_row[f'area_{year}'] for year in years]
                    area_fig.add_trace(go.Scatter(
                        x=years,
                        y=area_values,
                        mode='lines+markers',
                        name=state_name
                    ))
                
                area_fig.update_layout(
                    title=f"{selected_crop} Area by State",
                    xaxis_title="Year",
                    yaxis_title="Area (sq meters)",
                    legend_title="State",
                    hovermode="x unified"
                )
                
                st.plotly_chart(area_fig, use_container_width=True)
                
                # Create percentage time series if available
                if any(f'pct_{year}' in state_data.columns for year in years):
                    pct_fig = go.Figure()
                    
                    for state_name in selected_states:
                        state_row = filtered_state_data[filtered_state_data[name_col] == state_name].iloc[0]
                        pct_values = [state_row.get(f'pct_{year}', 0) for year in years]
                        pct_fig.add_trace(go.Scatter(
                            x=years,
                            y=pct_values,
                            mode='lines+markers',
                            name=state_name
                        ))
                    
                    pct_fig.update_layout(
                        title=f"{selected_crop} Percentage by State",
                        xaxis_title="Year",
                        yaxis_title="Percentage",
                        legend_title="State",
                        hovermode="x unified"
                    )
                    
                    st.plotly_chart(pct_fig, use_container_width=True)
    
    with tabs[2]:
        # Load county-level time series data
        county_data = load_crop_data(selected_crop_id, cell_to_parent_res, min_ratio_stats, "county")
        
        if county_data is None or len(county_data) == 0:
            st.warning(f"No county-level data found for {selected_crop}.")
        else:
            # Get years from columns
            years = [int(col.split('_')[1]) for col in county_data.columns if col.startswith('area_')]
            years.sort()
            
            # Check if county_name column exists, otherwise use county_id
            county_name_col = 'county_name' if 'county_name' in county_data.columns else 'county_id'
            state_name_col = 'state_name' if 'state_name' in county_data.columns else 'state_id'
            
            # Fill missing names with ID values
            if county_name_col == 'county_name':
                county_data[county_name_col] = county_data[county_name_col].fillna("County " + county_data['county_id'].astype(str))
            if state_name_col == 'state_name':
                county_data[state_name_col] = county_data[state_name_col].fillna("State " + county_data['state_id'].astype(str))
            
            # Create display names for counties that include state information
            county_data['display_name'] = county_data.apply(
                lambda row: f"{row[county_name_col]} ({row[state_name_col]})",
                axis=1
            )
            
            # Get top 5 counties by most recent year area
            latest_year = max(years)
            latest_col = f'area_{latest_year}'
            top_county_data = county_data.sort_values(by=latest_col, ascending=False).head(5)
            top_county_displays = top_county_data['display_name'].tolist()
            
            # Multi-select for counties
            all_counties = sorted(county_data['display_name'].unique().tolist())
            
            selected_counties = st.multiselect(
                "Select counties to compare:",
                options=all_counties,
                default=top_county_displays
            )
            
            if not selected_counties:
                st.info("Please select at least one county to display time series.")
            else:
                # Filter data for selected counties
                filtered_county_data = county_data[county_data['display_name'].isin(selected_counties)]
                
                # Create area time series for selected counties
                county_fig = go.Figure()
                
                for _, county_row in filtered_county_data.iterrows():
                    display_name = county_row['display_name']
                    area_values = [county_row[f'area_{year}'] for year in years]
                    county_fig.add_trace(go.Scatter(
                        x=years,
                        y=area_values,
                        mode='lines+markers',
                        name=display_name
                    ))
                
                county_fig.update_layout(
                    title=f"{selected_crop} Area by County",
                    xaxis_title="Year",
                    yaxis_title="Area (sq meters)",
                    legend_title="County",
                    hovermode="x unified"
                )
                
                st.plotly_chart(county_fig, use_container_width=True)
                
                # Create percentage time series if available
                if any(f'pct_{year}' in county_data.columns for year in years):
                    pct_county_fig = go.Figure()
                    
                    for _, county_row in filtered_county_data.iterrows():
                        display_name = county_row['display_name']
                        pct_values = [county_row.get(f'pct_{year}', 0) for year in years]
                        pct_county_fig.add_trace(go.Scatter(
                            x=years,
                            y=pct_values,
                            mode='lines+markers',
                            name=display_name
                        ))
                    
                    pct_county_fig.update_layout(
                        title=f"{selected_crop} Percentage by County",
                        xaxis_title="Year",
                        yaxis_title="Percentage",
                        legend_title="County",
                        hovermode="x unified"
                    )
                    
                    st.plotly_chart(pct_county_fig, use_container_width=True)
    
    with tabs[3]:
        if state_data is None or len(state_data) == 0:
            st.warning(f"No state-level data found for {selected_crop}.")
        else:
            # Use year from sidebar
            area_col = f'area_{year}'
            
            # Fixed top 10 states
            top_n = 10
            
            # Use state_name instead of state_id if available
            name_col = 'state_name' if 'state_name' in state_data.columns else 'state_id'
            
            # Sort and get top states
            top_states_df = state_data.sort_values(by=area_col, ascending=False).head(top_n)
            
            # Create bar chart
            state_bar = px.bar(
                top_states_df,
                x=name_col,
                y=area_col,
                title=f"Top {top_n} States by {selected_crop} Area ({year})",
                labels={name_col: 'State', area_col: 'Area (sq meters)'}
            )
            state_bar.update_layout(xaxis={'categoryorder': 'total descending'})
            
            st.plotly_chart(state_bar, use_container_width=True)
            
            # Percentage bar chart if available
            pct_col = f'pct_{year}'
            if pct_col in state_data.columns:
                pct_top_states = state_data.sort_values(by=pct_col, ascending=False).head(top_n)
                
                pct_bar = px.bar(
                    pct_top_states,
                    x=name_col,
                    y=pct_col,
                    title=f"Top {top_n} States by {selected_crop} Percentage ({year})",
                    labels={name_col: 'State', pct_col: 'Percentage'}
                )
                pct_bar.update_layout(xaxis={'categoryorder': 'total descending'})
                
                st.plotly_chart(pct_bar, use_container_width=True)
    
    with tabs[4]:
        if county_data is None or len(county_data) == 0:
            st.warning(f"No county-level data found for {selected_crop}.")
        else:
            # Use year from sidebar
            area_col = f'area_{year}'
            
            # Fixed top 10 counties
            top_n = 10
            
            # Sort and get top counties
            top_counties_df = county_data.sort_values(by=area_col, ascending=False).head(top_n)
            
            # Create bar chart
            county_bar = px.bar(
                top_counties_df,
                x='display_name',
                y=area_col,
                color=state_name_col,
                title=f"Top {top_n} Counties by {selected_crop} Area ({year})",
                labels={'display_name': 'County', area_col: 'Area (sq meters)', state_name_col: 'State'}
            )
            county_bar.update_layout(xaxis={'categoryorder': 'total descending'})
            
            st.plotly_chart(county_bar, use_container_width=True)
            
            # Percentage bar chart if available
            pct_col = f'pct_{year}'
            if pct_col in county_data.columns:
                pct_top_counties = county_data.sort_values(by=pct_col, ascending=False).head(top_n)
                
                pct_bar = px.bar(
                    pct_top_counties,
                    x='display_name',
                    y=pct_col,
                    color=state_name_col,
                    title=f"Top {top_n} Counties by {selected_crop} Percentage ({year})",
                    labels={'display_name': 'County', pct_col: 'Percentage', state_name_col: 'State'}
                )
                pct_bar.update_layout(xaxis={'categoryorder': 'total descending'})
                
                st.plotly_chart(pct_bar, use_container_width=True)