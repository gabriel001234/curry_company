# Imports
from datetime import datetime
from plotly   import graph_objects as go

import haversine      as hs
import numpy          as np
import pandas         as pd
import plotly.express as px
import streamlit      as st

# ---------------------------------------------
# Funções
# ---------------------------------------------
def clean_dataset(df):
    """ Esta função tem a responsabilidade de limpar o dataframe
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo de dados das colunas
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção da variável numérica)

        Input: df (DataFrame)
        Output: DataFrame
    """
    
    # convertendo a coluna Age de texto para numero
    condition = (df['Delivery_person_Age'] != 'NaN ') & (df['Weatherconditions'] != 'NaN ') & (df['multiple_deliveries'] != 'NaN ') & (df['Road_traffic_density'] != 'NaN ') & (df['City'] != 'NaN ') & (df['Type_of_vehicle'] != 'NaN ') & (df['Type_of_order'] != 'NaN ') & (df['Festival'] != 'NaN ')
    df1 = df.loc[condition, :].copy()    
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    # convertendo a coluna Ratings de texto para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    # convertendo a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')
    
    # convertendo a coluna multiple_deliveries de texto para numero
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    # removendo os espacos dentro de strings/texto/object
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.replace('(min) ', '', regex=False).astype(int)
    
    df1 = df1.reset_index(drop=True)

    return df1

def distance(df1):
    """ Esta função tem a responsabilidade de criar a coluna 'distance' no DataFrame com os dados das entregas

        Input: df1 (DataFrame)
        Output: Series
    """    
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

    df1['distance'] = df1.loc[:, cols].apply(lambda row: hs.haversine((row['Restaurant_latitude'], row['Restaurant_longitude']), (row['Delivery_location_latitude'], row['Delivery_location_longitude'])), axis=1)

    return df1['distance']

def avg_std_time_festival(df1, festival, col):
    """ Esta função tem a responsabilidade de calcular a média e o desvio-padrão do tempo no Festival, baseado nas flags 'Festivak' ('Yes' ou 'No') e na coluna desejada ('time_mean' ou 'time_std')

        Input: df1 (DataFrame), festival (str), col (str)
        Output: str ou float
    """        
    value = 'nan'
    
    df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg(['mean', 'std']).reset_index()
    df_aux.columns = ['Festival', 'time_mean', 'time_std']

    if len(df_aux) != 0:
        value = np.round(df_aux.loc[df_aux['Festival'] == festival, col], 2)
    
    return value

def bar_mean_std_time_per_city(df1):
    """ Esta função tem a responsabilidade de gerar um gráfico de barras que mostra a média e o desvio-padrão do tempo de entrega por cidade

        Input: df1 (DataFrame)
        Output: Figure (gráfico de barras do Plotly)
    """         
    df_mean_std_time_taken_by_city = df1.loc[:, ['Time_taken(min)', 'City']].groupby('City').agg(['mean', 'std']).reset_index()
    df_mean_std_time_taken_by_city.columns = ['City', 'time_mean', 'time_std']
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Avg Time by City', x=df_mean_std_time_taken_by_city['City'], y=df_mean_std_time_taken_by_city['time_mean'], error_y={'type': 'data', 'array': df_mean_std_time_taken_by_city['time_std']}))    
    
    return fig

def sb_time_per_city_and_traffic(df1):
    """ Esta função tem a responsabilidade de gerar um gráfico Sunburst que mostra a distribuição do tempo de entrega por cidade e tipo de tráfego

        Input: df1 (DataFrame)
        Output: Figure (gráfico Sunburst do Plotly)
    """         
    df_mean_std_time_taken_by_city_traffic = df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg(['mean', 'std']).reset_index()
    df_mean_std_time_taken_by_city_traffic.columns = ['City', 'Road_traffic_density', 'time_mean', 'time_std']
        
    fig = px.sunburst(df_mean_std_time_taken_by_city_traffic, path=['City', 'Road_traffic_density'], values='time_mean', color='time_std', color_continuous_scale='RdBu_r', color_continuous_midpoint=np.average(df_mean_std_time_taken_by_city_traffic['time_std']))

    return fig

@st.cache_data
def load_data(path):
    """ Esta função tem a responsabilidade de fazer a carga de dados e salvar em um dataframe

        Input: path (str)
        Output: DataFrame
    """
    
    df = pd.read_csv(path)
    return df

# --------------------------------------------- Início da estrutura lógica do código ---------------------------------------------

# Definindo configuração de página
st.set_page_config(page_icon='img/logo.png', layout='wide')

# Carregando dados
df = load_data('datasets/train.csv')

# Limpando os dados
df1 = clean_dataset(df)

# ---------------------------------------------
# Barra Lateral
# ---------------------------------------------=
st.write('# Marketplace - Visão Restaurantes')

st.sidebar.image('img/logo.png', width=120)
st.sidebar.write('# Curry Company')
st.sidebar.write('## Fastest delivery in town')
st.sidebar.write('---')

data_slider = st.sidebar.slider('Até qual valor?', value=datetime(2022, 3, 10), min_value=datetime(2022, 2, 11), max_value=datetime(2022, 4, 13), format='DD-MM-YYYY')

traffic_types = df1['Road_traffic_density'].unique().tolist()
traffic_options = st.sidebar.multiselect('Quais as condições do trânsito?', traffic_types, default=traffic_types)

st.sidebar.write('---')
st.sidebar.write('### Created by Gabriel Paneque Didi')

# Filtro nos dados
df1 = df1.loc[(df1['Order_Date'] < data_slider) & (df1['Road_traffic_density'].isin(traffic_options)), :]

# ---------------------------------------------
# Layout no Streamlit
# ---------------------------------------------
st.header('Visão Gerencial')
st.write('---')

with st.container():
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric(label='Entregadores únicos', value=df1["Delivery_person_ID"].nunique())

    with col2:
        st.metric('Distância média', np.round(distance(df1).mean(), 2))

    with col3:
        st.metric('Tempo médio de entrega c/ Festival', avg_std_time_festival(df1, 'Yes', 'time_mean'))

    with col4:
        st.metric('Desvio-padrão de entrega c/ Festival', avg_std_time_festival(df1, 'Yes', 'time_std'))

    with col5:
        st.metric('Tempo médio de entrega s/ Festival', avg_std_time_festival(df1, 'No', 'time_mean'))

    with col6:
        st.metric('Desvio-padrão de entrega s/ Festival', avg_std_time_festival(df1, 'No', 'time_std'))

st.write('---')

with st.container():
    st.write('### Distância média por cidade')
    
    if len(df1) == 0:
        st.write('Escolha alguns filtros!')
    else:
        avg_distance = df1.loc[:, ['distance', 'City']].groupby('City').mean().reset_index()
        
        fig = go.Figure(data=go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0]))
        st.plotly_chart(fig, use_container_width=True)

st.write('---')

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.write('### Tempo médio de entrega por cidade')
        
        st.plotly_chart(bar_mean_std_time_per_city(df1), use_container_width=True)

    with col2:
        st.write('### Tempo médio e o desvio padrão de entrega por cidade e tipo de pedido')
        
        df_mean_std_time_taken_by_city_order = df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg(['mean', 'std']).reset_index()
        df_mean_std_time_taken_by_city_order.columns = ['City', 'Type_of_order', 'time_mean', 'time_std']
        
        st.dataframe(df_mean_std_time_taken_by_city_order)

st.write('---')

with st.container():
    st.write('### Tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego')
    
    if len(df1) == 0:
        st.write('Escolha alguns filtros!')
    else:       
        st.plotly_chart(sb_time_per_city_and_traffic(df1), use_container_width=True)
    
# ---------------------------------------------
# Alterando texto padrão do multiselect
# ---------------------------------------------
multi_css="""
<style>
.stMultiSelect div div div div div:nth-of-type(2) {visibility: hidden;}
.stMultiSelect div div div div div:nth-of-type(2)::before {visibility: visible; content: 'Escolha uma opção';}
</style>
"""
st.markdown(multi_css, unsafe_allow_html=True)