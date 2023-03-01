import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from  gspread_pandas import Spread, Client
import ssl
import datetime
import time
import plotly.express as px
import plotly.graph_objects as go


ssl.create_default_https_context = ssl._create_unverified_context

scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope)

clients = Client(scope=scope,creds=credentials)

spreadsheet_name = "Spotify_database"
spread = Spread(spreadsheet_name,client=clients)

sh = clients.open(spreadsheet_name)
worksheet_list =sh.worksheets()


# Functions
@st.cache_resource()
# Get our worksheet names
def worksheet_names():
    sheet_names = []
    for sheet in worksheet_list:
        sheet_names.append(sheet.title)
    return sheet_names

# Get the sheet as dataframe
def load_the_spreadsheet(spreadsheetname):
    worksheet = sh.worksheet(spreadsheetname)
    df = pd.DataFrame(worksheet.get_all_records())
    return df

# Loading the data
music_per_week_df  = load_the_spreadsheet('music_week')[['totalTime','nrArtists']]
music_per_week_df["week"] = [str(x) for x in range(1, 53)]

st.set_page_config(page_title="Weekly Data",
                   page_icon="📈",
                   layout="wide")

st.markdown("# Weekly Data")
st.sidebar.header("Weekly Data")

with st.expander("See explanation"):
        st.write("""This is a polar chart.""")
        st.write("""The length of the radial shows how many minutes of audio I played per week,
                 while the color specifies how many artists I listened to.""")


fig = px.bar_polar(music_per_week_df,
r='totalTime',
theta='week',
log_r=True,
color="nrArtists",
barmode="group",
category_orders={"week": [str(x) for x in range(1, 53)]},
color_discrete_sequence=px.colors.qualitative.Pastel2,
labels={"nrArtists": "Number artists"})
fig.update_polars(angularaxis_autotypenumbers="strict")
fig.update_layout(title = 'Number of artists per week')
st.plotly_chart(fig,theme=None, use_container_width=False)
