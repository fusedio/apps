import streamlit as st
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import urllib.request
from io import BytesIO

st.title("Simple Image Processing")

# Define some cool color schemes
color_schemes = {
    "Pink": ("black", "pink"),
    "Sepia": ("black", "#704214"),
    "Cyan": ("black", "cyan"),
    "Yellow": ("black", "yellow"),
    "Purple": ("black", "purple")
}

# Setup for default image
default_image_url = "https://fused-magic.s3.us-west-2.amazonaws.com/docs_assets/github_app_repo/Fused_team.png"

# Image upload with drag & drop
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], accept_multiple_files=False)

# Load image
if uploaded_file is not None:
    # User uploaded an image
    image = Image.open(uploaded_file)
else:
    # Use default image
    try:
        response = urllib.request.urlopen(default_image_url)
        image = Image.open(BytesIO(response.read()))
        st.info("Using default image. Upload your own to get started!")
    except:
        st.error("Failed to load default image. Please upload an image.")
        image = None

# Process the image
if image is not None:
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
    st.image(colored_image, caption=f"{selected_scheme} Image", use_container_width=True)