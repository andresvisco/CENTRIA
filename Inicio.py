from PIL import Image
import streamlit as st
image = Image.open('logo.png')

container = st.container()
col1,col2,col3 = st.columns(3)
with container:
    col2.image(image, use_column_width=False)
