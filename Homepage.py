import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from  gspread_pandas import Spread, Client
import ssl
import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from PIL import Image


current_dir = Path(__file__).parent if "__file__"in locals() else Path.cwd()

qr_code = current_dir / "assets" / "qr_code.JPG"
spotify = current_dir / "assets" / "spotify.jpg"
qr_code = Image.open(qr_code)
spotify = Image.open(spotify)

st.set_page_config(
    page_title="Spotify Dashboard",
    page_icon="🎹",
    layout="wide"
)


# ## Page configuration

st.header('🎧 Spotify Dashboard - One year of audio streaming')

col1,col2=st.columns(2,gap="small")

with col1:
    st.write("")
    st.write("")
    st.image(spotify)
    st.write("")
    st.write("")
with col2:
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.markdown("""
                The dashboard analyses my Spotify history since February 2022 to February 2023.

                It contains aggregated data for different frequencies : Daily, Weekly, Monthly and Yearly.

                Each section contains charts with a brief explanation and conclusions.
                """)


st.write("")
st.write("")
st.write("")

st.markdown(
    """
    #### Do you want to explore?

    **👈 Select an option from the sidebar**
""")
st.write(" ")
st.write(" ")
st.write(" ")
st.write("--------------------------------------------------------------------------------")
st.markdown(""" #### About me:""")
col1,col2,col3=st.columns(3)

with col1:
    st.write(""" [Github](https://github.com/monicasainer)""")
with col2:
    st.write(""" [LinkedIn](https://www.linkedin.com/in/msainerb/)""")
    st.write(" ")
    st.write(" ")
    st.image(qr_code)
with col3:
    st.write("""Send your feedback and/or ask me a question:""")
    st.write("📧 monicasainerboto@gmail.com")
