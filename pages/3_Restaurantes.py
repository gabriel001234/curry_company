# =======================================
# Imports
# =======================================
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from haversine import haversine
from utils.data_manipulation import load_data, clean_data, chart

# =======================================
# Configurações da página
# =======================================
st.set_page_config(layout="wide", page_title='Visão Restaurantes', page_icon='img/logo.png')

# =======================================
# Funções
# =======================================
def avg_std_time_festival(df, festival, col):
    """ Esta função tem a responsabilidade de retornar as métricas de média e desvio padrão do tempo de entrega com e sem festivais.

        Input: 
        - df (DataFrame): DataFrame com os dados das entregas
        - festival (str): Flag que indica se está ocorrendo o festival
        ('Yes' para presença do festival, 'No' para a ausência do festival)
        - col (str): String que indica qual métrica deve ser retornada
        ('time_mean' para média, 'time_std' para desvio padrão)
        Output: DataFrame
    """    
    df_festival = df.loc[:, ['Festival', 'Time_taken(min)']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
    df_festival.columns = ['Festival', 'time_mean', 'time_std']
    
    try:
        value = np.round(df_festival.loc[df_festival['Festival'] == festival, col].reset_index(drop=True)[0], 2)

    except:
        value = 'nan'

    return value

# =======================================
# Extração
# =======================================
path = 'datasets/train.csv'
df = load_data(path)

# =======================================
# Limpeza
# =======================================
df1 = clean_data(df)

# Criando nova coluna 'distance'

df1['distance'] = df1.loc[:, ['Restaurant_latitude', 
                              'Restaurant_longitude', 
                              'Delivery_location_latitude', 
                              'Delivery_location_longitude']].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), 
                                                                                        axis=1)



# =======================================
# Barra Lateral
# =======================================
st.markdown('# Marketplace - Visão Restaurantes')
st.sidebar.image('img/logo.png', width=120)
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest delivery in town')
st.sidebar.markdown('---')

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual valor?', value=df1['Order_Date'].max().to_pydatetime(), 
                                                   min_value=df1['Order_Date'].min().to_pydatetime(), 
                                                   max_value=df1['Order_Date'].max().to_pydatetime(),
                                                   format='DD-MM-YYYY')
st.sidebar.markdown('---')

traffic_options = st.sidebar.multiselect('Quais as condições de trânsito?', 
                                 options=df1['Road_traffic_density'].unique(), 
                                 default=df1['Road_traffic_density'].unique(),
                                 placeholder='Escolha as densidades')

st.sidebar.markdown('---')
st.sidebar.markdown('### Made by Gabriel Paneque Didi')

# Uso dos filtros
df1 = df1.loc[(df1['Order_Date'] < date_slider) & (df1['Road_traffic_density'].isin(traffic_options)), :]

# =======================================
# Layout
# =======================================

st.markdown('#### Métricas gerais')

with st.container():
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric(label='Entregadores únicos', value=df1['Delivery_person_ID'].nunique())

    with col2:
        st.metric(label='Distância média (km)', value=np.round(float(df1['distance'].mean()), 2))

    with col3:
        st.metric(label='Tempo médio c/ Festival', value=avg_std_time_festival(df1, 'Yes', 'time_mean'))
    
    with col4:
        st.metric(label='Desvio padrão c/ Festival', value=avg_std_time_festival(df1, 'Yes', 'time_std'))

    with col5:
        st.metric(label='Tempo médio s/ Festival', value=avg_std_time_festival(df1, 'No', 'time_mean'))

    with col6:
        st.metric(label='Desvio padrão s/ Festival', value=avg_std_time_festival(df1, 'No', 'time_std'))

with st.container():
    st.markdown('---')

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('#### Distribuição do tempo por cidade')

        df_mean_std_time_by_city = df1.loc[:, ['Time_taken(min)', 'City']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
        df_mean_std_time_by_city.columns = ['City', 'time_mean', 'time_std']

        fig_mean_std_time = go.Figure()
        fig_mean_std_time.add_trace(go.Bar(x=df_mean_std_time_by_city['City'], 
                             y=df_mean_std_time_by_city['time_mean'], 
                             error_y={'type': 'data',
                                      'array': df_mean_std_time_by_city['time_std']}))
        st.plotly_chart(fig_mean_std_time)
    
    with col2:
        st.markdown('#### Tempo médio por tipo de entrega')
        
        df_mean_std_time_by_city_and_order_type = df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
        df_mean_std_time_by_city_and_order_type.columns = ['City', 'Type_of_order', 'time_mean', 'time_std']
        st.dataframe(df_mean_std_time_by_city_and_order_type)

with st.container():
    st.markdown('---')
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('#### Distrbuição da distância média por cidade')
        
        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig_avg_distance = go.Figure(data=[go.Pie(values=avg_distance['distance'], labels=avg_distance['City'], pull=[0, 0.1, 0])])
        st.plotly_chart(fig_avg_distance)
    
    with col2:
        try:
            st.markdown('#### Tempo médio por cidade e tipo de tráfego')

            if len(df1) == 0:
                raise ValueError('DataFrame vazio') 
            
            df_mean_std_time_by_city_and_traffic_density = df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
            df_mean_std_time_by_city_and_traffic_density.columns = ['City', 'Road_traffic_density', 'time_mean', 'time_std']

            fig_sunburst = chart(df_mean_std_time_by_city_and_traffic_density, 
                                 ['City', 'Road_traffic_density', 'time_mean'], 
                                 color='time_std', 
                                 cc_scale='RdBu_r', 
                                 cc_midpoint=np.average(df_mean_std_time_by_city_and_traffic_density['time_std']),
                                 type='sb')
            st.plotly_chart(fig_sunburst)

        except:
            st.markdown('Erro! Tente atualizar os filtros!')