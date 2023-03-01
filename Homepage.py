import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from  gspread_pandas import Spread, Client
import ssl
import datetime
import time
import plotly.express as px
import plotly.graph_objects as go



st.set_page_config(
    page_title="Spotify Dashboard",
    page_icon="🎹",
    layout="wide"
)


# ## Page configuration

st.header('Spotify Dashboard - One year of audio streaming')

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    This is a dashboard that analyses my Spotify data for the last year.

    **👈 Select an option from the sidebar**

    ### Want to learn more?
    - Check out my [Github](https://github.com/monicasainer)

    - Ask me a question on [LinkedIn](www.linkedin.com/in/msainerb)
""")
