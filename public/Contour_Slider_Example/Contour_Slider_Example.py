import streamlit as st
st.markdown('### Contour Slider Example')

import streamlit.components.v1 as components
import fused
@fused.udf
def udf(x0:int=4,y0:int=6,z0:int=4, pivot: int=500): 
    import pandas as pd
    import h3
    df = fused.run('UDF_DEM_Tile_Hexify', x=x0,y=y0,z=z0)
    df['lat'] = df['hex'].map(lambda x:h3.api.basic_int.cell_to_latlng(x)[0])
    df['lng'] = df['hex'].map(lambda x:h3.api.basic_int.cell_to_latlng(x)[1])
    df=df[['lat','lng','metric']]
    return df
df = fused.run(udf)
template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Plot</title>
    <style> 
        body {
            background-color: #121212;  /* Dark background */
            color: white;  /* White text */
            font-family: Arial, sans-serif;
            padding: 20px;
        }
        select, input[type="range"] {
            margin: 10px 0;
            padding: 10px;
            background-color: #333;
            color: white;
            border: 1px solid #555;
            width: 100%; /* Make the slider span full width */
        }
        label {
            margin-left: 10px;
        }
        #controls {
            width: 100%;
            max-width: 600px; /* Optional: limit width of controls */
        }
    </style>
</head>
<body>
    <div id="controls">
        <label for="colorScheme">Choose color scheme:</label>
        <select id="colorScheme">
            <option value="rdbu">Red-Blue (rdbu)</option>
            <option value="viridis">Viridis</option>
            <option value="magma">Magma</option>
            <option value="cividis">Cividis</option>
        </select>

        <label for="blurSlider">Blur Value:</label>
        <input type="range" id="blurSlider" min="0" max="10" value="5" step="0.1">
        <span id="blurValue">5</span>
    </div>

    <div id="myplot"></div>

    <script type="module">
        import * as Plot from "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6/+esm";

        // Initial plot
        const plotContainer = document.querySelector("#myplot");

        const createPlot = (colorScheme, blurValue) => {
            const plot = Plot.contour({{data}}, {x: "lng", y: "lat", fill: "metric", blur: blurValue})
                .plot({color: {type: "diverging", scheme: colorScheme, pivot: "500"}});
            plotContainer.innerHTML = ''; // Clear previous plot
            plotContainer.append(plot);
        };

        // Set initial plot
        createPlot('rdbu', 5);

        // Dropdown color change handler
        document.querySelector("#colorScheme").addEventListener("change", (event) => {
            const colorScheme = event.target.value;
            const blurValue = document.querySelector("#blurSlider").value;
            createPlot(colorScheme, blurValue);
        });

        // Slider blur change handler
        document.querySelector("#blurSlider").addEventListener("input", (event) => {
            const blurValue = event.target.value;
            document.querySelector("#blurValue").textContent = blurValue; // Display current blur value
            const colorScheme = document.querySelector("#colorScheme").value;
            createPlot(colorScheme, blurValue);
        });
    </script>
</body>
</html>
""" 
html_str = fused.utils.common.html_params(template,data=df.to_json(orient='records'))

# st.html(html_str) #not working
components.html(html_str, height=1300, scrolling=True) 
