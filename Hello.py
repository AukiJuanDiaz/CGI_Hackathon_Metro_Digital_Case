import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to the CustomerAgent Evaluation Tool! 👋")

st.subheader("METRO meets IONOS Cloud Solutions")
st.write("This tool allows you to evaluate the performance of the METRO chatbot based on various performamce metrics.")   
st.text("We are happy to present our evaluation model in collaboration with IONOS Cloud Services.")

from PIL import Image

metro_img = Image.open('docs/images/digital_metro_logo.png')
ionos_img = Image.open('docs/images/IONOS_logo_2.png')

col1, col2 = st.columns(2)
with col1:
    st.image(metro_img, width=300)
with col2:
    st.image(ionos_img, width=300)

st.sidebar.success("Select a page in the side menu above.")

