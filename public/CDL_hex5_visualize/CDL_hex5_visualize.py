import streamlit as st
import pandas as pd
import fused
import micropip

st.title("2024 Crop Data Layer Hex Explorer!")
st.write(
    """
    Visualize any crop from the USDA's 2024 Crop Data Layer dataset.
    Data taken from the Fused-partitioned dataset hosted on [Source Coop](https://source.coop/repositories/fused/hex/description).
    """)

await micropip.install(['pydeck', 'plotly'])
import pydeck as pdk
import plotly.express as px

cdl_categories = {
    2: "Cotton", # Putting this as first so it shows up as default
    0: "Background",
    1: "Corn",
    3: "Rice",
    4: "Sorghum",
    5: "Soybeans",
    6: "Sunflower",
    10: "Peanuts",
    11: "Tobacco",
    12: "Sweet Corn",
    13: "Pop or Orn Corn",
    14: "Mint",
    21: "Barley",
    22: "Durum Wheat",
    23: "Spring Wheat",
    24: "Winter Wheat",
    25: "Other Small Grains",
    26: "Dbl Crop WinWht/Soybeans",
    27: "Rye",
    28: "Oats",
    29: "Millet",
    30: "Speltz",
    31: "Canola",
    32: "Flaxseed",
    33: "Safflower",
    34: "Rape Seed",
    35: "Mustard",
    36: "Alfalfa",
    37: "Other Hay/Non Alfalfa",
    38: "Camelina",
    39: "Buckwheat",
    41: "Sugarbeets",
    42: "Dry Beans",
    43: "Potatoes",
    44: "Other Crops",
    45: "Sugarcane",
    46: "Sweet Potatoes",
    47: "Misc Vegs & Fruits",
    48: "Watermelons",
    49: "Onions",
    50: "Cucumbers",
    51: "Chick Peas",
    52: "Lentils",
    53: "Peas",
    54: "Tomatoes",
    55: "Caneberries",
    56: "Hops",
    57: "Herbs",
    58: "Clover/Wildflowers",
    59: "Sod/Grass Seed",
    60: "Switchgrass",
    61: "Fallow/Idle Cropland",
    62: "Pasture/Grass",
    63: "Forest",
    64: "Shrubland",
    65: "Barren",
    66: "Cherries",
    67: "Peaches",
    68: "Apples",
    69: "Grapes",
    70: "Christmas Trees",
    71: "Other Tree Crops",
    72: "Citrus",
    74: "Pecans",
    75: "Almonds",
    76: "Walnuts",
    77: "Pears",
    81: "Clouds/No Data",
    82: "Developed",
    83: "Water",
    87: "Wetlands",
    88: "Nonag/Undefined",
    92: "Aquaculture",
    111: "Open Water",
    112: "Perennial Ice/Snow",
    121: "Developed/Open Space",
    122: "Developed/Low Intensity",
    123: "Developed/Med Intensity",
    124: "Developed/High Intensity",
    131: "Barren",
    141: "Deciduous Forest",
    142: "Evergreen Forest",
    143: "Mixed Forest",
    152: "Shrubland",
    176: "Grass/Pasture",
    190: "Woody Wetlands",
    195: "Herbaceous Wetlands",
    204: "Pistachios",
    205: "Triticale",
    206: "Carrots",
    207: "Asparagus",
    208: "Garlic",
    209: "Cantaloupes",
    210: "Prunes",
    211: "Olives",
    212: "Oranges",
    213: "Honeydew Melons",
    214: "Broccoli",
    215: "Avocados",
    216: "Peppers",
    217: "Pomegranates",
    218: "Nectarines",
    219: "Greens",
    220: "Plums",
    221: "Strawberries",
    222: "Squash",
    223: "Apricots",
    224: "Vetch",
    225: "Dbl Crop WinWht/Corn",
    226: "Dbl Crop Oats/Corn",
    227: "Lettuce",
    228: "Dbl Crop Triticale/Corn",
    229: "Pumpkins",
    230: "Dbl Crop Lettuce/Durum Wht",
    231: "Dbl Crop Lettuce/Cantaloupe",
    232: "Dbl Crop Lettuce/Cotton",
    233: "Dbl Crop Lettuce/Barley",
    234: "Dbl Crop Durum Wht/Sorghum",
    235: "Dbl Crop Barley/Sorghum",
    236: "Dbl Crop WinWht/Sorghum",
    237: "Dbl Crop Barley/Corn",
    238: "Dbl Crop WinWht/Cotton",
    239: "Dbl Crop Soybeans/Cotton",
    240: "Dbl Crop Soybeans/Oats",
    241: "Dbl Crop Corn/Soybeans",
    242: "Blueberries",
    243: "Cabbage",
    244: "Cauliflower",
    245: "Celery",
    246: "Radishes",
    247: "Turnips",
    248: "Eggplants",
    249: "Gourds",
    250: "Cranberries",
    254: "Dbl Crop Barley/Soybeans"
}

# Extract the values (crop names) from the dictionary
crop_options = list(cdl_categories.values())
selected_crop = st.selectbox("Select Crop Type", crop_options)
selected_crop_id = list(cdl_categories.keys())[list(cdl_categories.values()).index(selected_crop)]

min_ratio_in_hex = st.slider("Minimum ratio to keep", min_value=0.0, max_value=1.0, value=0.0, step=0.05)

view_state = pdk.ViewState(
    latitude = 39.8283,
    longitude = -98.5795,
    zoom = 3  # This gives a good view of the continental US
)

hex_df = fused.run(
    "UDF_Hex5_visualize_CDL_crop", # Using a public UDF to get data from
    vals=[selected_crop_id],
    year=2024, # Only 2024 is supported for now
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
