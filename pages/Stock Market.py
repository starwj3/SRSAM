import random
from sqlalchemy import create_engine
import requests as rq
from io import BytesIO
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import altair as alt

def high_price(n):
    n+=1
    engine = create_engine('mysql+pymysql://root:990108wj@127.0.0.1:3306/stock')
    query="select distinct 일자 from price"
    a=pd.read_sql(query,con=engine)
    a=a.sort_values("일자")
    query=f"select * from price where 일자='{a.iloc[-1]['일자']}' and 등락률 > 0"
    df_recent=pd.read_sql(query,con=engine)
    
    name=df_recent["종목명"]
    name=[i for i in name if "스팩" not in i ]
    query=f"select * from price where 일자>\'{a['일자'].iloc[-n]}\' and 등락률 > 0"
    df_data=pd.read_sql(query,con=engine)
    
    df_new_high=pd.DataFrame()
    num=0
    length_name=len(name)
    progress_bar = st.progress(0)
    for i in name:
        progress_bar.progress((num/len(name)))
        num+=1
        recent_price=df_data[df_data["종목명"]==i].sort_values("일자").iloc[[-1]]
        recent_price["조회기간 등락"]=(((df_data[df_data["종목명"]==i].sort_values("일자")["종가"].iloc[-1]/df_data[df_data["종목명"]==i].sort_values("일자")["종가"].iloc[0])-1)*100).round(2)
        if df_data[df_data["종목명"]==i].sort_values("일자")["종가"].iloc[-1] == df_data[df_data["종목명"]==i]['종가'].max():
            df_new_high=pd.concat([df_new_high,recent_price])
    
    df_new_high=df_new_high.reset_index(drop=True)
    df_new_high["일자"]=df_new_high["일자"].apply(lambda x: x.strftime("%Y-%m-%d"))
    return df_new_high

def stock_chart(start,end,name):
    engine = create_engine('mysql+pymysql://root:990108wj@127.0.0.1:3306/stock')
    query=f"select * from price where 종목명='{name}' and 일자>='{start}' and 일자<= '{end}' "
    df=pd.read_sql(query,con=engine)
    return df
def stock_volume(name,date):
        date=date.strftime("%Y-%m-%d")
        engine = create_engine('mysql+pymysql://root:990108wj@127.0.0.1:3306/stock')
        query=f"select * from volume where 종목명='{name}' and 일자='{date}'"
        df=pd.read_sql(query,con=engine)
        df = df[~df['종목명'].str.contains('스팩')]
        df["시총 대비 거래대금%"]=(df["거래대금"]/df["시가총액"])*100
        df=df[["종목명","일자","종가","고가","저가","등락률","거래대금","거래량","시총 대비 거래대금%"]]
        df=df.set_index("일자", drop=True)
        return df 
    
def stock_volume_all(date):
        date=date.strftime("%Y-%m-%d")
        engine = create_engine('mysql+pymysql://root:990108wj@127.0.0.1:3306/stock')
        query=f"select * from volume where 일자='{date}'"
        df=pd.read_sql(query,con=engine)
        df = df[~df['종목명'].str.contains('스팩')]
        df["시총 대비 거래대금%"]=(df["거래대금"]/df["시가총액"])*100
        df=df[["종목명","일자","종가","고가","저가","등락률","거래대금","거래량","시총 대비 거래대금%"]]
        df=df.set_index("일자", drop=True)
        return df 
    
    

st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "## Made by SRS 32기 이우제"
    }
)


# 상단에 탭 위치

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(['관심종목','투자경고지정','연기금 순매수',"개별종목 차트 조회","종목비교","신고가", "거래량/거래대금"])	

with tab4:
    engine = create_engine('mysql+pymysql://root:990108wj@127.0.0.1:3306/stock')
    query="select distinct 일자 from price"
    d=pd.read_sql(query,con=engine)
    
    engine = create_engine('mysql+pymysql://root:990108wj@127.0.0.1:3306/stock')
    query="select distinct 종목명 from price"
    n=pd.read_sql(query,con=engine)
    st.header("개별종목차트")
    col1,col2, col3= st.columns([1,1,2])
    with col1 :
        select_start=st.selectbox("시작날짜",d)
    with col2 :
      select_end=st.selectbox("종료날짜",d, index=len(d)-1)
      
    col1,col2= st.columns([1,3])
    with col1 :
        select_name=st.selectbox("주가 조회 종목명",n)
    col1,col2= st.columns([1,1])
    with col1 :
        price=stock_chart(select_start,select_end, select_name)
        price=price.set_index("일자",drop=True)
        st.line_chart(price["종가"])
    with col2 :
        st.dataframe(price[["종목명","종목코드","시장구분","종가"]], width=2000, height=300)
    
with tab5:
    st.header("종목비교")
    data_load_state = st.text('Loading data...')
    engine = create_engine('mysql+pymysql://root:990108wj@127.0.0.1:3306/stock')
    query="select distinct 일자 from price"
    d=pd.read_sql(query,con=engine)
    
    engine = create_engine('mysql+pymysql://root:990108wj@127.0.0.1:3306/stock')
    query="select distinct 종목명 from price"
    n=pd.read_sql(query,con=engine)
    data_load_state.text("")
    col1,col2, col3= st.columns([1,1,2])
    with col1 :
        select_start=st.selectbox("시작",d)
    with col2 :
      select_end=st.selectbox("종료",d, index=len(d)-1)
      
    col1,col2, col3= st.columns([1,1,2])
    with col1 :
        select_name1=st.selectbox("주가 조회 종목명_1",n,index=100)
      
    with col2 :
        select_name2=st.selectbox("주가 조회 종목명_2",n, index=120)
    col1,col2= st.columns([1,1])
    with col1 :
        price1=stock_chart(select_start,select_end, select_name1)
        price1=price1.set_index("일자",drop=True)
        price2=stock_chart(select_start,select_end, select_name2)
        price2=price2.set_index("일자",drop=True)
        price_compair=pd.DataFrame({select_name1:price1['종가'],select_name2:price2['종가']})
        normalization_df = (price_compair - price_compair.mean())/price_compair.std()
        st.line_chart(normalization_df)
        
    with col2 :
        st.dataframe(price_compair, width=2000, height=300)    
      
with tab6:
    st.header("신고가 Monitoring")
    col1, col2=st.columns([1,3])
    with col1:
        select_period=st.selectbox("신고가 조회기간(영업일)",[3,5,10,20,30,50,60,90,120], index=3)
    col1, col2=st.columns([1,3])
    with col1:
        data_load_state = st.text('Loading data...')
        df=high_price(select_period)
        data_load_state.text("")
    st.dataframe(df, width=1200)

with tab7:
    st.header("일자별 거래량/거래대금")
    col1,col2, col3= st.columns([1,1,2])
    query_v="select distinct 일자 from volume"
    d_v=pd.read_sql(query_v,con=engine)
    n_v=n["종목명"].to_list().insert(0,"전체")
    with col1 :
        select_date_volume=st.selectbox("거래량 조회일",d_v, index=len(d_v)-1)
      
    col1,col2= st.columns([1,3])
    with col1 :
        df_volume=stock_volume_all(select_date_volume)
    st.dataframe(df_volume, width=1200)
            



