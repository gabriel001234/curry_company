# Imports
from datetime import datetime

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

def top_delivery_person_ids(df1, ascending):
    """ Esta função tem a responsabilidade de retornar um dataframe com os 10 entregadores mais rápidos ou mais lentos por cidade baseado na flag 'ascending'

        Input: df1 (DataFrame), ascending (bool)
        Output: DataFrame
    """
    
    df_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Delivery_person_ID']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['City', 'Time_taken(min)'], ascending=ascending).reset_index()

    df_urban = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
    df_metropolitian = df_aux.loc[df_aux['City'] == 'Metropolitian'].head(10)
    df_semi_urban = df_aux.loc[df_aux['City'] == 'Semi-Urban'].head(10)
    
    df_top_10 = pd.concat([df_metropolitian, df_urban, df_semi_urban]).reset_index(drop=True)

    return df_top_10

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

# Limpando dos dados
df1 = clean_dataset(df)

# ---------------------------------------------
# Barra Lateral
# ---------------------------------------------
st.write('# Marketplace - Visão Entregadores')

st.sidebar.image('img/logo.png', width=120)
st.sidebar.write('# Curry Company')
st.sidebar.write('## Fastest delivery in town')
st.sidebar.write('---')

data_slider = st.sidebar.slider('Até qual valor?', value=datetime(2022, 3, 10), min_value=datetime(2022, 2, 11), max_value=datetime(2022, 4, 13), format='DD-MM-YYYY')

traffic_types = df1['Road_traffic_density'].unique().tolist()
traffic_options = st.sidebar.multiselect('Quais as condições do trânsito?', traffic_types, default=traffic_types)

# Filtro nos dados
df1 = df1.loc[(df1['Order_Date'] < data_slider) & (df1['Road_traffic_density'].isin(traffic_options)), :]

st.sidebar.write('---')
st.sidebar.write('### Created by Gabriel Paneque Didi')

# ---------------------------------------------
# Layout no Streamlit
# ---------------------------------------------

# Visão Gerencial
st.header('Visão Gerencial')
st.write('---')

with st.container():
    st.write('### Métricas gerais')

    col1, col2, col3, col4 = st.columns(4, gap='large')
    
    with col1:
        st.metric('Maior Idade', df1.loc[:, 'Delivery_person_Age'].max())
    with col2:
        st.metric('Menor Idade', df1.loc[:, 'Delivery_person_Age'].min())
    with col3:
        st.metric('Melhor condição (veículo)', df1.loc[:, 'Vehicle_condition'].max())
    with col4:
        st.metric('Pior condição (veículo)', df1.loc[:, 'Vehicle_condition'].min())
        
st.write('---')

with st.container():
    st.write('### Avaliações')

    col1, col2 = st.columns(2)

    with col1:
        st.write('#### Média das avaliações por entregador')
        st.dataframe(df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']].groupby('Delivery_person_ID').mean().reset_index())
        
    with col2:
        st.write('#### Média e desvio-padrão das avaliações por tipo de tráfego')
        
        df_avg_std_ratings_by_traffic = df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg(['mean', 'std']).reset_index()
        df_avg_std_ratings_by_traffic.columns = ['Road_traffic_density', 'delivery_mean', 'delivery_std']
        st.dataframe(df_avg_std_ratings_by_traffic)
        
        st.write('#### Média e desvio-padrão das avaliações por tipo de clima')
        
        df_avg_std_ratings_by_weather = df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg(['mean', 'std']).reset_index()
        df_avg_std_ratings_by_weather.columns = ['Weatherconditions', 'delivery_mean', 'delivery_std']
        st.dataframe(df_avg_std_ratings_by_weather)

st.write('---')

with st.container():
    st.write('### Velocidade de entrega')

    col1, col2 = st.columns(2)

    with col1:
        st.write('#### Top 10 entregadores mais rápidos por cidade')
        st.dataframe(top_delivery_person_ids(df1, True))
    
    with col2:
        st.write('#### Top 10 entregadores mais lentos por cidade')
        st.dataframe(top_delivery_person_ids(df1, False))
        
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