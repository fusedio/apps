import streamlit as st
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

st.title("Color Scheme Selector for Image Processing")

# Define some cool color schemes
color_schemes = {
    "Pink": ("black", "pink"),
    "Sepia": ("black", "#704214"),
    "Cyan": ("black", "cyan"),
    "Yellow": ("black", "yellow"),
    "Purple": ("black", "purple")
}

# Capture webcam input
img_file_buffer = st.camera_input("Take a picture")

if img_file_buffer is not None:
    # Load the image
    image = Image.open(img_file_buffer)
    
    # Convert the image to grayscale (black and white)
    bw_image = image.convert("L")
    selected_scheme = st.selectbox("Choose a color scheme", list(color_schemes.keys()))

    # Get the selected color scheme
    black, white = color_schemes[selected_scheme]
    
    # Apply the selected color scheme
    colored_image = ImageOps.colorize(bw_image, black=black, white=white)
    
    # Add sliders for brightness, contrast, sharpness, and color
    brightness = st.slider("Brightness", 0.5, 3.0, 1.0)
    contrast = st.slider("Contrast", 0.5, 3.0, 1.0)
    sharpness = st.slider("Sharpness", 0.5, 3.0, 1.0)
    color = st.slider("Color", 0.0, 3.0, 1.0)
    
    # Apply enhancements
    enhancer = ImageEnhance.Brightness(colored_image)
    colored_image = enhancer.enhance(brightness)
    
    enhancer = ImageEnhance.Contrast(colored_image)
    colored_image = enhancer.enhance(contrast)
    
    enhancer = ImageEnhance.Sharpness(colored_image)
    colored_image = enhancer.enhance(sharpness)
    
    enhancer = ImageEnhance.Color(colored_image)
    colored_image = enhancer.enhance(color)
    
    # Add a checkbox for edge detection
    if st.checkbox("Apply Edge Detection"):
        colored_image = colored_image.filter(ImageFilter.FIND_EDGES)
    
    # Add a selectbox for other filters
    filter_options = ["None", "Blur", "Contour", "Detail", "Emboss", "Sharpen", "Smooth"]
    selected_filter = st.selectbox("Apply Filter", filter_options)
    
    # Apply the selected filter
    if selected_filter == "Blur":
        colored_image = colored_image.filter(ImageFilter.BLUR)
    elif selected_filter == "Contour":
        colored_image = colored_image.filter(ImageFilter.CONTOUR)
    elif selected_filter == "Detail":
        colored_image = colored_image.filter(ImageFilter.DETAIL)
    elif selected_filter == "Emboss":
        colored_image = colored_image.filter(ImageFilter.EMBOSS)
    elif selected_filter == "Sharpen":
        colored_image = colored_image.filter(ImageFilter.SHARPEN)
    elif selected_filter == "Smooth":
        colored_image = colored_image.filter(ImageFilter.SMOOTH)
    
    # Display the processed image
    st.image(colored_image, caption=f"{selected_scheme} Image", use_column_width=True)
