import streamlit as st
st.title("Fused Geospatial Data Ingestion")

from typing import Union, Sequence, Optional, Tuple, Dict, Any
from pathlib import Path
import micropip
await micropip.install('geopandas')
import geopandas as gpd
import fused
import json
login=st.empty()
# Inputs for the parameters
input = st.text_input("Input (url, list of url)", help="A GeoPandas `GeoDataFrame` or a path to file or files on S3 to ingest. Files may be Parquet or another geo data format.")
try:
    user=fused.api.whoami()['name'].split('@')[0]
    path = fused.api.FusedAPI()._resolve("fd://")+f'{user}/TABLE_NAME'

except:
    login.error('Please open this app in a brower that is authenticated to Fused')
    path = "s3://NEED_LOGING_IN/TABLE_NAME"
output = st.text_input("Output (s3 bucket)", value=path, help="Location on S3 to write the `main` table to.", placeholder="s3://fused-users/...") 
if len(output) > 0 and not output.startswith('s3://'):
    st.error("Invalid output. Must start with `s3://`")
partitioning_method = st.selectbox("Partitioning Method", ["rows","area", "length", "coords"], help="The method to use for grouping rows into partitions.")
target= st.empty()
if st.checkbox('Customize Partitioning', False):  
    target_num_chunks=0 #it will get ignored
    partitioning_maximum_per_file = st.number_input("Partitioning Maximum per File", value=100_000, step=1, min_value=0, help="Maximum value for `partitioning_method` to use per file. If `None`, defaults to _1/10th_ of the total value of `partitioning_method`. So if the value is `None` and `partitioning_method` is `area`, then each file will be have no more than 1/10th the total area of all geometries. Defaults to `None`.")    
    partitioning_maximum_per_chunk = st.number_input("Partitioning Maximum per Chunk", value=5000, step=1, min_value=0, help="Maximum value for `partitioning_method` to use per chunk. If `None`, defaults to _1/100th_ of the total value of `partitioning_method`. So if the value is `None` and `partitioning_method` is `area`, then each file will be have no more than 1/100th the total area of all geometries. Defaults to `None`.")
    partitioning_split_method = st.selectbox("Partitioning Split Method", ["mean", "median"])
    partitioning_max_width_ratio = st.number_input("Partitioning Max Width Ratio", value=2.0, step=0.1)
    partitioning_max_height_ratio = st.number_input("Partitioning Max Height Ratio", value=2.0, step=0.1)
    partitioning_force_utm = st.selectbox("Partitioning Force UTM", ["chunk", "file", None], help="Whether to force partitioning within UTM zones. If set to `file`, this will ensure that the centroid of all geometries per _file_ are contained in the same UTM zone. If set to `chunk`, this will ensure that the centroid of all geometries per _chunk_ are contained in the same UTM zone. If set to `None`, then no UTM-based partitioning will be done. Defaults to `chunk`.")
    if st.checkbox("Subdivide by area", False, help="The method to use for subdividing large geometries into multiple rows. Currently the only option is `area`, where geometries will be subdivided based on their area (in WGS84 degrees)."):
        subdivide_method = "area"
        subdivide_start = st.number_input("Subdivide Start", value=0.0, help="The value above which geometries will be subdivided into smaller parts, according to `subdivide_method`.")
        subdivide_stop = st.number_input("Subdivide Stop", value=0.0, help="The value below which geometries will not be subdivided into smaller parts, according to `subdivide_method`. Recommended to be equal to subdivide_start. If `None`, geometries will be subdivided up to a recursion depth of 100 or until the subdivided geometry is rectangular.")
    else:
        subdivide_method = subdivide_start = subdivide_stop = None
    if st.checkbox('Parition based on lat & lon', help="Does the file contain `lat` & `lon` columns instead of a `geometry` column?"):
        lon = st.text_input("Lon column name", "lon", help="Names of longitude, latitude columns to construct point geometries from.")
        lat = st.text_input("Lat column name", "lat")
        lonlat_cols = (lon, lat)
    else:
        lonlat_cols=None
    
else:
    target_num_chunks = target.number_input("Target Number of Chunks", value=1000, help="The target for the number of files if `partitioning_maximum_per_file` is None. ")
    partitioning_maximum_per_file = None
    partitioning_maximum_per_chunk = None
    partitioning_split_method='mean'
    partitioning_max_width_ratio=2
    partitioning_max_height_ratio=2
    partitioning_force_utm='chunk'
    subdivide_method = subdivide_start = subdivide_stop = None
    lonlat_cols=None
    
    
    
with st.expander("Additional configuration"):
    # output_metadata = st.text_input("Output Metadata (optional)")
    # schema = st.text_input("Schema (optional)")

    load_columns = st.text_input("Load Columns (comma-separated)", "", placeholder="column_1, column_2")
    load_columns = [i.strip(" ") for i in load_columns.split(",")] if load_columns else None
    remove_cols = st.text_input("Remove Columns (comma-separated)", "", placeholder="column_1, column_2")
    remove_cols = [i.strip(" ") for i in remove_cols.split(",")] if remove_cols else None
    print(remove_cols)
    explode_geometries = st.checkbox("Explode Geometries", False)
    split_identical_centroids = st.checkbox("Split Identical Centroids", True)
    drop_out_of_bounds = st.checkbox("Drop Out of Bounds", True)
    if st.checkbox('Input file Suffix'):  
        file_suffix = st.text_input("Input file Suffix (optional)", help="Filter which files are used for ingest. If `file_suffix` is not None, it will be used to filter paths by checking the trailing characters of each filename. E.g. pass `file_suffix='.geojson'` to include only GeoJSON files inside the directory.") or None
    else:
        file_suffix=None
    if st.checkbox('Gdal Config'):
        gdal_config = st.text_area("GDAL Config (as dictionary format)", "")
        gdal_config = json.loads(gdal_config) if gdal_config else None
    else:
        gdal_config=None

# Run the function with the inputs
if st.button("Ingest Data", type="primary"):
    
    if 'job_id' in st.session_state:
        del st.session_state['job_id']

    try:
        with st.spinner('Running...'):
            job_id = fused.ingest(
                input=input,
                output=output,
                # output_metadata=output_metadata,
                # schema=schema,
                file_suffix=file_suffix,
                load_columns=load_columns,
                remove_cols=remove_cols,
                explode_geometries=explode_geometries,
                drop_out_of_bounds=drop_out_of_bounds,
                partitioning_method=partitioning_method,
                partitioning_maximum_per_file=partitioning_maximum_per_file,
                partitioning_maximum_per_chunk=partitioning_maximum_per_chunk,
                partitioning_max_width_ratio=partitioning_max_width_ratio,
                partitioning_max_height_ratio=partitioning_max_height_ratio,
                partitioning_force_utm=partitioning_force_utm,
                partitioning_split_method=partitioning_split_method,
                subdivide_method=subdivide_method,
                subdivide_start=subdivide_start or None,
                subdivide_stop=subdivide_stop or None,
                split_identical_centroids=split_identical_centroids,
                target_num_chunks=target_num_chunks,
                lonlat_cols=lonlat_cols,
                # gdal_config=gdal_config,
            ).run_remote()

            st.session_state['job_id'] = job_id
        st.markdown(f'[Here](https://www.fused.io/job_status/{job_id.job_id}) is job progress.')
    except Exception as e:
        st.write(f"Error: {str(e)}")
    
# if st.button("Show logs", disabled=True if not 'job_id' in st.session_state else False):
#     st.write("Logs:", st.session_state['job_id'].print_logs() or "Pending...")

# if 'job_id' in st.session_state:
#     st.write('Job id: ', st.session_state['job_id'])



