# Imports
from streamlit_folium import st_folium
from datetime         import datetime

import folium
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

def orders_by_day(df1):
    """ Esta função tem a responsabilidade de gerar um gráfico de barras que mostra o número de pedidos por dia

        Input: df1 (DataFrame)
        Output: Figure (gráfico de barras do Plotly)
    """    
    
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y='ID')

    return fig

def orders_by_traffic_density(df1):
    """ Esta função tem a responsabilidade de gerar um gráfico de pizza que mostra a distribuição de pedidos por densidade de tráfego

        Input: df1 (DataFrame)
        Output: Figure (gráfico de pizza do Plotly)
    """      
    
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    fig = px.pie(df_aux, values='ID', names='Road_traffic_density')

    return fig

def orders_by_city_traffic_density(df1):
    """ Esta função tem a responsabilidade de gerar um gráfico de bolhas que mostra o volume de pedidos por cidade e densidade de tráfego

        Input: df1 (DataFrame)
        Output: Figure (gráfico de bolhas do Plotly)
    """ 
    
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')    

    return fig

def orders_by_week(df1):
    """ Esta função tem a responsabilidade de gerar um gráfico de linha que mostra o volume de pedidos por semana

        Input: df1 (DataFrame)
        Output: Figure (gráfico de linha do Plotly)
    """ 
    
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()     
    fig = px.line(df_aux, x='week_of_year', y='ID')

    return fig

def order_share_by_week(df1):
    """ Esta função tem a responsabilidade de gerar um gráfico de linha que mostra o volume de pedidos por entregador a cada semana

        Input: df1 (DataFrame)
        Output: Figure (gráfico de linha do Plotly)
    """ 
    
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux3 = pd.merge(df_aux, df_aux2, how='inner', on='week_of_year')
    df_aux3['orders_by_week'] = df_aux3['ID'] / df_aux3['Delivery_person_ID']
    fig = px.line(df_aux3, x='week_of_year', y='orders_by_week')

    return fig

def create_map(df1):
    """ Esta função tem a responsabilidade de gerar um mapa com a localização central de cada cidade por tipo de tráfego

        Input: df1 (DataFrame)
        Output: None
    """ 
        
    df_aux = df1.loc[:, ['Delivery_location_latitude', 'Delivery_location_longitude', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    
    map = folium.Map([df_aux['Delivery_location_latitude'].median(), df_aux['Delivery_location_longitude'].median()], zoom_start=10, control_scale=True)
    
    for index, row in df_aux.iterrows():
      folium.Marker([row['Delivery_location_latitude'], row['Delivery_location_longitude']], popup=f'City: {row["City"]}; Road Traffic Density: {row["Road_traffic_density"]}').add_to(map)    

    st_folium(map, returned_objects=[])
    
    return None

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
# ---------------------------------------------
st.write('# Marketplace - Visão Empresa')

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

# Visão Gerencial
with tab1:   
    with st.container():
        st.header('Pedidos por dia')
        st.plotly_chart(orders_by_day(df1), use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.header('Pedidos por densidade de tráfego')
            st.plotly_chart(orders_by_traffic_density(df1), use_container_width=True)
        
        with col2:
            st.header('Volume de pedidos por cidade e tipo de tráfego')
            st.plotly_chart(orders_by_city_traffic_density(df1), use_container_width=True)

# Visão Tática
with tab2:
    with st.container():
        
        st.header('Quantidade de pedidos por semana')
        st.plotly_chart(orders_by_week(df1), use_container_width=True)

    with st.container():

        st.header('A quantidade de pedidos por entregador por semana')
        st.plotly_chart(order_share_by_week(df1), use_container_width=True)

# Visão Geográfica
with tab3:
    st.header('A localização central de cada cidade por tipo de tráfego')

    if len(df1) == 0:
        st.write('Escolha alguns filtros!')
        
    else:               
        create_map(df1)
        
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
