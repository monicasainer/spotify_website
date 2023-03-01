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
historical_data_df = load_the_spreadsheet('historical_data')
classification_df = load_the_spreadsheet('classification')
number_of_artists_yearly = historical_data_df['artistName'].nunique()
number_of_tracks_yearly = historical_data_df['trackName'].nunique()

st.set_page_config(page_title="Yearly Data", page_icon="📈")

with open('style.css') as r:
    st.markdown(f'<style>{r.read()}</style>', unsafe_allow_html=True)


st.markdown("# Yearly Data")
st.sidebar.header("Plotting Demo")

col1,col2 = st.columns(2)

with col1:
    with st.spinner('Retrieving number of artists...'):
        time.sleep(3)
        st.metric(label="Total number of artist listened", \
            value=number_of_artists_yearly)
with col2:
    with st.spinner('Retrieving number of audios...'):
        time.sleep(3)
        st.metric(label="Total number of tracks and podcasts listened", \
            value=number_of_tracks_yearly)

total_classification_df = {'typeObject':["total"],'total_minutes_played':[classification_df['total_minutes_played'].sum()]}
total_classification_df = pd.DataFrame.from_dict(total_classification_df)
classification_df_def= pd.concat([classification_df,total_classification_df],axis=0)



colors = ['lightslategray',] * 5
colors[2] = 'crimson'

fig = go.Figure(data=[go.Bar(
    x=classification_df_def['typeObject'],
    y=classification_df_def['total_minutes_played'],
    marker_color=colors # marker color can be a single color value or an iterable
)])
fig.update_layout(title_text='Minutes listened (Total)')

st.plotly_chart(fig,theme=None, use_container_width=True)
