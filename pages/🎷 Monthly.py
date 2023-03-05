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
minutes_per_month_df = load_the_spreadsheet('minutes_per_month')
minutes_per_month_wth_type_df = load_the_spreadsheet('minutes_month_wth_type')

st.set_page_config(page_title="Monthly Data",
                   page_icon="📈",
                   layout="wide")

st.markdown("# Monthly Data")
st.sidebar.header("Monthly Data")
st.write("")
st.write("")
st.write("--------------------------------------------------------------------------------")
st.write("")
st.write("")

col1,col2 = st.columns(2)

with col1:
    fig = px.bar_polar(minutes_per_month_wth_type_df,r="minutes_per_month",theta="month",
    color_discrete_sequence=px.colors.qualitative.Pastel1)
    background_color = "white"

    fig.update_layout(
        polar = dict(
            bgcolor = background_color,
            radialaxis = dict(showticklabels=True, ticks=''),
        ),
        title = "Total minutes per month"
    )
    st.plotly_chart(fig,theme=None, use_container_width=True)
    with st.expander("See explanation"):
        st.write("""This is a polar chart.""")
        st.write("""The length of the radial shows how many minutes of audio I played per month.""")

with col2:

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=minutes_per_month_df['month'].unique(),
        x=minutes_per_month_df['minutes_per_month'][minutes_per_month_df['typeObject']=="Podcast"],
        name='Podcast',
        orientation='h',
        marker=dict(
            color='rgba(256, 78, 139, 0.6)',
            line=dict(color='rgba(256, 78, 139, 1.0)', width=3)
        )
    ))
    fig.add_trace(go.Bar(
        y=minutes_per_month_df['month'].unique(),
        x=minutes_per_month_df['minutes_per_month'][minutes_per_month_df['typeObject']=="Track"],
        name='Track',
        orientation='h',
        marker=dict(
            color='rgba(158, 71, 80, 0.6)',
            line=dict(color='rgba(158, 71, 80, 1.0)', width=3)
        )
    ))
    fig.update_layout(barmode='stack',title_text='Minutes listened by audio type')
    st.plotly_chart(fig,theme=None, use_container_width=True)
    with st.expander("See explanation"):
            st.write("""The length of each bar represents how many minutes have been played each month.""")
            st.write("""The color indicates which proportion corresponds to each type of audio.""")


with st.expander("**Conclusions**"):
    st.write("""
            -Spotify in Summer ☀️ :

                The listenings during July and August increased drastically compared to months as January.
                There is not a special driver since both, minutes of pocasts listened and minutes of tracks grow.

            -Tracks vs Podcasts 🥊 :

                Although from a general perspective I listened to Podcasts for more minutes (yearly analysis),
                during the first six months (January, February, March, April, June, and July)
                I prefered songs.

             """)
