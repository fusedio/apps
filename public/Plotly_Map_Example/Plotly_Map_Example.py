import streamlit as st
st.set_page_config(layout="wide") 
st.markdown('### Plotly Map Example')

import micropip
await micropip.install('streamlit_folium')
await micropip.install('plotly')
import plotly.graph_objects as go

class WorldMap:
    """This class provides a method for plotting a choropleth map of the world."""

    def __init__(self, locations, z, text=None, colorbar_title=None):
        self.locations = locations
        self.z = z
        self.text = text
        self.colorbar_title = colorbar_title
        self.fig = self.plot()
        self.update_layout()

    def plot(self, **kwargs):
        fig_world = go.Figure(
            data=go.Choropleth(
                locations=self.locations,
                z=self.z,
                text=self.text,
                colorscale='Solar',
                autocolorscale=False,
                marker_line_color='darkgray',
                marker_line_width=1,
                colorbar_title=self.colorbar_title,
                **kwargs
            )
        )
        return fig_world

    def update_layout(self, lon=None, lat=None, projection_type="orthographic", **kwargs):
        self.fig.update_layout(
            geo=dict(
                showframe=True,
                showcoastlines=False,
                projection=go.layout.geo.Projection(
                    type=projection_type,
                    scale=1
                ),
                projection_rotation=dict(lon=lon if lon is not None else 0, lat=lat if lat is not None else 0),
            ),
            height=400,
            margin={"r": 10, "t": 0, "l": 10, "b": 50}
        )
        self.fig.data[0].colorbar.x = 0.

# Example data - replace with your actual data
world_map = WorldMap(
    locations=['USA', 'CAN', 'MEX'],
    z=[10, 20, 30],
    text=['USA', 'Canada', 'Mexico'],
    colorbar_title="Total Cup Points"
)

projection_type = st.radio("Map Projection Type", ["orthographic", "stereographic", "natural earth"])
lon_lat_dict = {'lat': 43, 'lon': -73}
world_map.update_layout(projection_type=projection_type, **lon_lat_dict)

st.plotly_chart(world_map.fig, use_container_width=True)
