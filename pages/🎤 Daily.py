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

st.write("")
st.write("")
st.write("--------------------------------------------------------------------------------")
st.write("")
st.write("")


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

st.write("")
st.write("")
with st.expander("**Conclusions**"):
    st.write("""
            -I am a morning bird 🐓:

                The timeframe of the day where I listened to Spotify the most is between 00:00h and 08:00h.

            -I listened to what others have to say 👂:

                Regardless of the timeframe, the total minutes listened to podcasts is greater than minutes of
                music played.

            -My consumption increased from Frebuary to November potencially 📈:

                Looking at the positive slope of the blue and green points in the three charts,
                it seems I increased the number of minutes on Spotify in the morning (00:00h-08:00h)
                and in the evening (16:00h-00:00h) during these months.
                However, we need to check the aggregated data in the section `Monthly` to confirm this fact.
             """)
st.write("")
st.write("")
st.write("")
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

st.write("")

with st.expander("**Features information**"):
    st.write("""

            -Danceability:

                Danceability describes how suitable a track is for dancing based on a combination of musical
                elements including tempo, rhythm stability, beat strength, and overall regularity.
                A value of 0.0 is least danceable and 1.0 is most danceable.

            -Acousticness:

                A measure from 0.0 to 1.0 of whether the track is acoustic.

            -Energy:

                Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity.
                Typically, energetic tracks feel fast, loud, and noisy.

            -Instrumentalness:

                Predicts whether a track contains no vocals. The closer the instrumentalness value is to 1.0,
                the greater likelihood the track contains no vocal content.

            -Liveness:

                Detects the presence of an audience in the recording.
                Higher liveness values represent an increased probability that the track was performed live.

            -Loudness:

                The overall loudness of a track in decibels (dB).
                Loudness values are averaged across the entire track. Values typical range between -60 and 0 db.

            -Speechiness:

                Speechiness detects the presence of spoken words in a track.
                The more exclusively speech-like the recording (e.g. talk show, audio book, poetry),
                the closer to 1.0 the attribute value.

            -Tempo:

                The overall estimated tempo of a track in beats per minute (BPM).
                In musical terminology, tempo is the speed or pace of a given piece and derives directly
                from the average beat duration.

            -Valence:

                A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track.
                Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric),
                while tracks with low valence sound more negative (e.g. sad, depressed, angry).

            """)


st.subheader("Check how tracks features are correlated with each other")

tab_1, tab_2, tab_3 = st.tabs(["Morning", "Evening","Night"])
with tab_1:
    with st.expander("See explanation"):
        st.write("""The chart below shows the correlation between features of the songs I played from 00:00h to 08:00h.""")
    morning_data_df = load_the_spreadsheet('morning_data')[['danceability','energy','key','loudness','mode','speechiness','acousticness',\
        'instrumentalness','liveness','valence','tempo','duration_ms','time_signature']]
    morning_data_df_corr = morning_data_df.corr()
    fig_1=go.Figure(data=go.Heatmap(
        z = morning_data_df_corr,
        x=morning_data_df_corr.columns.values,
        y=morning_data_df_corr.columns.values))
    st.plotly_chart(fig_1, theme=None, use_container_width=True)
with tab_2:
    with st.expander("See explanation"):
        st.write("""The chart below shows the correlation between features of the songs I played from 08:00h to 16:00h.""")
    evening_data_df = load_the_spreadsheet('evening_data')[['danceability','energy','key','loudness','mode','speechiness','acousticness',\
    'instrumentalness','liveness','valence','tempo','duration_ms','time_signature']]
    evening_data_df_corr = evening_data_df.corr()
    fig_2=go.Figure(data=go.Heatmap(
        z = evening_data_df_corr,
        x=evening_data_df_corr.columns.values,
        y=evening_data_df_corr.columns.values))
    st.plotly_chart(fig_2, theme=None, use_container_width=True)
with tab_3:
    with st.expander("See explanation"):
        st.write("""The chart below shows the correlation between features of the songs I played from 16:00h to 00:00h.""")
    night_data_df = load_the_spreadsheet('night_data')[['danceability','energy','key','loudness','mode','speechiness','acousticness',\
            'instrumentalness','liveness','valence','tempo','duration_ms','time_signature']]
    night_data_df_corr = night_data_df.corr()
    fig_3=go.Figure(data=go.Heatmap(
        z = night_data_df_corr,
        x=night_data_df_corr.columns.values,
        y=night_data_df_corr.columns.values))
    st.plotly_chart(fig_3, theme=None, use_container_width=True)




with st.expander("**Conclusions**"):
    st.write("""
            -I start and finish the day with energy ⚡️:

                The energy level of the songs I listened to during the morning and night are 2 pp
                higher than during the day.

            -I need more instrumental background to focus 🧘‍♀️ :

                During my day I tended to listen to more instrumental music (11%) than during the morning (6%)
                or night (8%).

            -Correlation between features :

                Even though the correlations vary slighly from one timeframe to another, there are common
                patterns:
                    To analyse them, let's divide some of the features in two groups:

                        ▫️ Group 1: Loudness, energy, valence and danceability.
                        ◾️ Group 2: Instrumentalness, acousticness.

                    While the correlations between variables of group 1 and variables of group 2
                    are negative and in some cases strong (e.g:Loudness vs Instrumentalness), the
                    correlation between variables of the same group are positive (e.g: Loudness vs Energy).
             """)
