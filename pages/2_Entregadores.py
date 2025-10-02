# =======================================
# Imports
# =======================================
import pandas as pd
import streamlit as st
from utils.data_manipulation import load_data, clean_data

# =======================================
# Configurações da página
# =======================================
st.set_page_config(layout="wide", page_title='Visão Entregadores', page_icon='img/logo.png')

# =======================================
# Funções
# =======================================
def top_deliveries(df, ascending):
    """ Esta função tem a responsabilidade de retornar os 10 entregadores mais rápidos (ou mais lentos) por cidade

        Input: 
        - df (DataFrame): DataFrame com os dados de entregas
        - ascending (bool): Flag que indica se vai retornar os entregadores mais rápidos ou mais lentos 
        (True para os mais rápidos, False para os mais lentos)
        Output: DataFrame
    """
    cities = df['City'].unique()

    df_times = df.loc[:, ['Time_taken(min)', 'City', 'Delivery_person_ID']].groupby(['City', 'Delivery_person_ID']).mean().reset_index()

    df_top = pd.DataFrame()

    for city in cities:
        df_aux = df_times.loc[df_times['City'] == city, :].sort_values(by='Time_taken(min)', ascending=ascending).head(10)

        df_top = pd.concat([df_top, df_aux]).reset_index(drop=True)

    return df_top


# =======================================
# Extração
# =======================================
path = 'datasets/train.csv'
df = load_data(path)

# =======================================
# Limpeza
# =======================================
df1 = clean_data(df)

# =======================================
# Barra Lateral
# =======================================
st.markdown('# Marketplace - Visão Entregadores')
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

with st.container():
    st.markdown('#### Métricas gerais')
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Maior idade dos entregadores
        st.metric(label='Maior idade', value=df1.loc[:, 'Delivery_person_Age'].max())
    with col2:
        # Menor idade dos entregadores
        st.metric(label='Menor idade', value=df1.loc[:, 'Delivery_person_Age'].min())
    with col3:
        # Melhor condição dos veículos
        st.metric(label='Melhor condição', value=df1.loc[:, 'Vehicle_condition'].max())     
    with col4:
        # Pior condição dos veículos
        st.metric(label='Pior condição', value=df1.loc[:, 'Vehicle_condition'].min())  

st.markdown('---')

with st.container():
    # Avaliação média por entregador
    st.markdown('#### Avaliação média por entregador')  

    ratings_by_person = df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
    st.dataframe(ratings_by_person)     

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        # Avaliação média e o desvio padrão por tipo de tráfego
        st.markdown('#### Avaliação média por tráfego') 
        mean_std_by_traffic_density = df1.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']].groupby('Road_traffic_density') \
                                                                                    .agg({'Delivery_person_Ratings': ['mean', 'std']}).reset_index()
        mean_std_by_traffic_density.columns = ['Road_traffic_density', 'ratings_mean', 'ratings_std']
        st.dataframe(mean_std_by_traffic_density)  
    with col2:
        # Avaliação média e o desvio padrão por clima
        st.markdown('#### Avaliação média por clima')             
        mean_std_by_weather = df1.loc[:, ['Weatherconditions', 'Delivery_person_Ratings']].groupby('Weatherconditions') \
                                                                                        .agg({'Delivery_person_Ratings': ['mean', 'std']}).reset_index()
        mean_std_by_weather.columns = ['Weatherconditions', 'ratings_mean', 'ratings_std']
        st.dataframe(mean_std_by_weather)

st.markdown('---')

with st.container():

    col1, col2 = st.columns(2)

    with col1:
        # Top 10 entregadores mais rápidos por cidade
        st.markdown('#### Top 10 entregadores mais rápidos por cidade')
        st.dataframe(top_deliveries(df1, True))

    with col2:
        # Top 10 entregadores mais lentos por cidade
        st.markdown('#### Top 10 entregadores mais lentos por cidade')
        st.dataframe(top_deliveries(df1, False))