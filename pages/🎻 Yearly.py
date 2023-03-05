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
historical_data_dates_track_types_df = load_the_spreadsheet('historical_dates_types_grouped')
historical_data_dates_df = load_the_spreadsheet('historical_dates')
number_of_artists_yearly = historical_data_df['artistName'].nunique()
number_of_tracks_yearly = historical_data_df['trackName'].nunique()
minutes_per_weekday_total = historical_data_dates_df.groupby(['weekday'],as_index=False).agg(minutes_played=('minutesPlayed','sum'))
weekdays= {0:'Monday',1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday',5:'Saturday',6:'Sunday'}
minutes_per_weekday_total['weekday']=minutes_per_weekday_total['weekday'].map(weekdays)
minutes_per_weekday_type = historical_data_dates_track_types_df.groupby(['typeObject','weekday'],as_index=False).agg(minutes_played=('listeningTracks','sum'))




st.set_page_config(page_title="Yearly Data", page_icon="📈")

with open('style.css') as r:
    st.markdown(f'<style>{r.read()}</style>', unsafe_allow_html=True)


st.markdown("# Yearly Data")
st.sidebar.header("Plotting Demo")
st.write("")
st.write("")
st.write("--------------------------------------------------------------------------------")
st.write("")
st.write("")

col1,col2= st.columns(2)

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




fig = go.Figure(data=[
    go.Bar(name='Total', x=minutes_per_weekday_total['weekday'], y=minutes_per_weekday_total['minutes_played'],marker=dict(
            color='rgba(89, 84, 84, 0.6)'
        )),
    go.Bar(name='Tracks', x=minutes_per_weekday_total['weekday'], y=minutes_per_weekday_type[minutes_per_weekday_type['typeObject']=='Track']['minutes_played'],marker=dict(
            color='crimson'
        )),
    go.Bar(name='Podcasts', x=minutes_per_weekday_total['weekday'], y=minutes_per_weekday_type[minutes_per_weekday_type['typeObject']=='Podcast']['minutes_played'],marker=dict(
            color='rgba(3, 3, 3, 0.6)'))])
fig.update_layout(title_text='Minutes listened per weekday')
st.plotly_chart(fig,theme=None, use_container_width=True)


with st.expander("**Conclusions**"):
    st.write("""

            -Tracks vs Podcasts 🥊 :

                From a general perspective I listened to Podcasts for more minutes than to
                songs (53,53% vs 46,47%).

            -Week trend 📅 :

                The Spotify use diminished over the week. It is on Fridays where the general
                level almost reaches Monday's driven by songs.

                Saturday is the day where I listened to more music, while Sundays are for
                podcasts mainly .

             """)
