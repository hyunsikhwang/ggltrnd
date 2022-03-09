import pandas as pd
from pytrends.request import TrendReq
from datetime import datetime
from pytz import timezone, utc
from pytrends import dailydata
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Google Trend for 2022년 제20대 대한민국 대선",
    page_icon=":shark:",
    layout="wide",
    initial_sidebar_state="expanded"
    )

st.title("Google Trend for 2022년 제20대 대한민국 대선")

pytrend = TrendReq()


KST = timezone('Asia/Seoul')
now = datetime.utcnow()

SeoulTime = utc.localize(now).astimezone(KST)
curDay = SeoulTime.day
curMonth = SeoulTime.month
curYear = SeoulTime.year
curHour = SeoulTime.hour

kw_list_default = ['이재명', '윤석열', '안철수', '허경영', '심상정', '홍준표', '김건희']
kw_list = st.multiselect('대선 후보 선택', options=kw_list_default, default=['이재명', '윤석열', '안철수', '김건희'])

pytrend.build_payload(kw_list=kw_list, cat=0, timeframe='today 5-y', geo='', gprop='')

#df = pytrend.interest_over_time().reset_index()

@st.cache
def init():
    df = pytrend.get_historical_interest(kw_list, year_start=2021, month_start=1, day_start=1, hour_start=0, year_end=curYear, month_end=curMonth, day_end=curDay, hour_end=curHour, cat=0, geo='', gprop='', sleep=0).reset_index()

    return df

df_org = init()
df = df_org.copy()

df['date'] = df['date'].dt.strftime('%Y%m%d')
df['date']= pd.to_datetime(df['date'])
df = df.groupby(['date']).sum().reset_index()


df1 = df.copy()

MA = 15
kw_list_MA = []

for name in kw_list:
    df1[f'{name}_MA'] = df1[f'{name}'].rolling(MA).mean()
    kw_list_MA.append(f'{name}_MA')
df1 = df1.melt(id_vars='date', value_vars=kw_list_MA, var_name='이름', value_name='value')

fig = px.line(df1, x='date', y='value', color='이름')
fig.update_xaxes(dtick=86400000.0*7*2, showspikes=True, spikecolor="green", spikesnap="cursor", spikemode="across")
fig.update_yaxes(showspikes=True, spikecolor="orange", spikethickness=2)
fig.update_layout(xaxis_tickformat = '%d %B (%a)<br>%Y', spikedistance=1000, hoverdistance=100)

st.plotly_chart(fig, use_container_width=True)

