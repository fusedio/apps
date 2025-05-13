import streamlit as st
import random
st.title("Your Name in Landsat Images")
st.markdown("""Rebuild of [NASA Webapp](https://landsat.gsfc.nasa.gov/apps/YourNameInLandsat-main/index.html) using Fused App.""")
name = st.text_input("Enter your name:", value='FUSED')
 
if name.replace(" ", "").isalpha():
    # Create a row with the number of columns equal to the length of the name  
    columns = st.columns(len(name))
    for idx, l in enumerate(name.lower()):
        if l==' ':
            continue
        url = f"https://landsat.gsfc.nasa.gov/apps/YourNameInLandsat-main/public/images/{l}_{random.randint(0, 1)}.jpg"
        # Place the image in the respective column
        columns[idx].image(url, use_container_width=True)
else:
    st.info("Please enter only alphabetic characters and spaces.")