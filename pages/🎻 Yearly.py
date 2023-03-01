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
historical_data_dates_types_df = load_the_spreadsheet('historical_dates_types')
historical_data_dates_track_types_df = load_the_spreadsheet('historical_dates_types_grouped')
historical_data_dates_df = load_the_spreadsheet('historical_dates')
number_of_artists_yearly = historical_data_df['artistName'].nunique()
number_of_tracks_yearly = historical_data_df['trackName'].nunique()

st.set_page_config(page_title="Yearly Data", page_icon="📈")

with open('style.css') as r:
    st.markdown(f'<style>{r.read()}</style>', unsafe_allow_html=True)


st.markdown("# Yearly Data")
st.sidebar.header("Plotting Demo")

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




# historical_data_dates_types_df['date']=pd.to_datetime(historical_data_dates_types_df['date'])
# historical_data_dates_df['date']==pd.to_datetime(historical_data_dates_types_df['date'])

def interactive_plot(df1,df2):
    plot=go.Figure()
    plot.add_trace(go.Scatter(x=df1['date'],y=df1['totalTime'],name ='Total', line={'color':'skyblue', 'width':2}))
    plot.add_trace(go.Scatter(x=df2['date'],y=df2[df2['typeObject']=='Track']['listeningTracks'],name ='Track', line={'color':'red', 'width':2}))
    plot.add_trace(go.Scatter(x=df2['date'],y=df2[df2['typeObject']=='Podcast']['listeningTracks'],name ='Podcast', line={'color':'white', 'width':2}))
    plot.update_xaxes(
            rangeslider_visible=False,
            rangeselector={
                'buttons':list([
                    {'count':1, 'label':"1m", 'step':"month", 'stepmode':"backward"},
                    {'count':6, 'label':"6m", 'step':"month", 'stepmode':"backward"},
                    {'count':1, 'label':"1y", 'step':"year", 'stepmode':"backward"},
                    {'step':"all"}
                ])
            },
            rangeselector_font_color='#faf8f7',
            showgrid=False
            )
    plot.update_layout(legend={'orientation': "h", 'yanchor':"bottom",
                                    'y':-0.2,'xanchor':"left", 'x':0,'title':None},
                        xaxis_title= None,
                        yaxis_title= None,
                        plot_bgcolor = 'rgba(0, 0, 0, 0)',
                        paper_bgcolor = 'rgba(0, 0, 0, 0)',
                        margin ={'t':50,'l':50,'b':50,'r':0.1},
                        autosize=False,
                        width=1000,
                        height=600
                            )
    plot.update_yaxes(exponentformat='none',
                        gridwidth=1,
                        gridcolor='#808080')
    return plot
plot = interactive_plot(historical_data_dates_df,historical_data_dates_track_types_df)
st.plotly_chart(plot, x='Time spend',y='time')
