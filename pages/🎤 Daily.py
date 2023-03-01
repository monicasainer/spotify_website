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

# Get the sheet as dataframe
def get_the_mean(option,df):
    if df=="morning":
        morning_data_df = load_the_spreadsheet('morning_data')
        mean_morning_data = morning_data_df[option].mean()
        return mean_morning_data
    if df=="evening":
        evening_data_df = load_the_spreadsheet('evening_data')
        mean_evening_data = evening_data_df[option].mean()
        return mean_evening_data
    if df=="night":
        night_data_df = load_the_spreadsheet('night_data')
        mean_night_data = night_data_df[option].mean()
        return mean_night_data

# Loading the data
time_listening_df = load_the_spreadsheet('time_listening')
time_listening_df['endTime']=time_listening_df['endTime'].apply(pd.to_datetime)
count_listening_df = load_the_spreadsheet('count_listening')

adj_count_listening = {'time': [x for (x) in count_listening_df['time']]*3,\
    'typeObject':['Total','Total','Total','Track','Track','Track','Podcast','Podcast','Podcast'],\
        "minutes_listened":[t for t in count_listening_df['Total']]+[n for n in count_listening_df['Tracks']]+[s for s in count_listening_df['Podcast']]}
adj_count_listening_df = pd.DataFrame.from_dict(adj_count_listening)
morning_data_df = load_the_spreadsheet('morning_data')
evening_data_df = load_the_spreadsheet('evening_data')
night_data_df = load_the_spreadsheet('night_data')


st.set_page_config(page_title="Daily Data",
                   page_icon="📈",
                   layout="wide")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.markdown("# Daily Data")
st.sidebar.header("Daily Data")


col1,col2=st.columns(2)

with col1:
    st.subheader("Minutes listened each timeframe")

    tab1, tab2, tab3 = st.tabs(["Tracks and Podcasts", "Tracks","Podcasts"])
    with tab1:
        with st.expander("See explanation"):
            st.write("""The chart below shows how many minutes have been listened per timeframe daily.
                The legend means:""")
            st.write("""*08:00:00* ➡️ From 00:00 to 08:00""")
            st.write("""*16:00:00* ➡️ From 08:00 to 16:00""")
            st.write("""*00:00:00* ➡️ From 16:00 to 00:00""")
        fig_1=px.scatter(time_listening_df[['endTime','Total']],x=time_listening_df.endTime.dt.date,y="Total",color=time_listening_df.endTime.dt.time)
        st.plotly_chart(fig_1, theme=None, use_container_width=True)
    with tab2:
        with st.expander("See explanation"):
            st.write("""The chart below shows how many minutes of tracks have been listened per timeframe daily.
                The legend means:""")
            st.write("""*08:00:00* ➡️ From 00:00 to 08:00""")
            st.write("""*16:00:00* ➡️ From 08:00 to 16:00""")
            st.write("""*00:00:00* ➡️ From 16:00 to 00:00""")
        fig_2=px.scatter(time_listening_df[['endTime','Tracks']],x=time_listening_df.endTime.dt.date,y="Tracks",color=time_listening_df.endTime.dt.time)
        st.plotly_chart(fig_2, theme=None, use_container_width=True)
    with tab3:
        with st.expander("See explanation"):
            st.write("""The chart below shows how many minutes of podcasts have been listened per timeframe daily.
                The legend means:""")
            st.write("""*08:00:00* ➡️ From 00:00 to 08:00""")
            st.write("""*16:00:00* ➡️ From 08:00 to 16:00""")
            st.write("""*00:00:00* ➡️ From 16:00 to 00:00""")
        fig_3=px.scatter(time_listening_df[['endTime','Podcast']],x=time_listening_df.endTime.dt.date,y="Podcast",color=time_listening_df.endTime.dt.time)
        st.plotly_chart(fig_3, theme=None, use_container_width=True)

with col2:
    st.subheader("Minutes listened each timeframe by type")
    timeframes = adj_count_listening_df['time']
    with st.expander("See explanation"):
        st.write("""The chart below shows how many minutes have been listened per timeframe, based on the audio type.
                    The legend means:""")
        st.write("""*08:00:00* ➡️ From 00:00 to 08:00""")
        st.write("""*16:00:00* ➡️ From 08:00 to 16:00""")
        st.write("""*00:00:00* ➡️ From 16:00 to 00:00""")


    fig = go.Figure(data=[
        go.Bar(name='Total', x=timeframes, y=adj_count_listening_df['minutes_listened'][adj_count_listening_df['typeObject']=='Total']),
        go.Bar(name='Track', x=timeframes, y=adj_count_listening_df['minutes_listened'][adj_count_listening_df['typeObject']=='Track']),
        go.Bar(name='Podcast', x=timeframes, y=adj_count_listening_df['minutes_listened'][adj_count_listening_df['typeObject']=='Podcast'])
    ])
    # Change the bar mode
    fig.update_layout(barmode='group')
    fig.update_layout(title_text='Minutes listened (Total)')

    st.plotly_chart(fig,theme=None, use_container_width=True)


st.subheader("Check how track features change during the day")
option = st.multiselect(
    'What feature are you interested in?',
    ['danceability','energy','key','loudness','mode','speechiness','acousticness',\
        'instrumentalness','liveness','valence','tempo','duration_ms','time_signature'],"danceability")

col1, col2, col3=st.columns(3)
with col1:
    with st.spinner(f'Retrieving {option}...'):
            time.sleep(2)
            st.metric(label=f"Morning - Average  ", \
                value=get_the_mean(option,"morning").round(2))

with col2:
    # if option!="artistName":
    with st.spinner(f'Retrieving {option}...'):
        time.sleep(2)
        st.metric(label=f"Evening - Average ", \
            value=get_the_mean(option,"evening").round(2))

with col3:
    # if option!="artistName":
    with st.spinner(f'Retrieving {option}...'):
        time.sleep(2)
        st.metric(label=f"Night - Average", \
            value=get_the_mean(option,"night").round(2))
