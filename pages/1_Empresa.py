# =======================================
# Imports
# =======================================
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from utils.data_manipulation import load_data, clean_data, chart

# =======================================
# Configurações da página
# =======================================
st.set_page_config(layout="wide", page_title='Visão Empresa', page_icon='img/logo.png')

# =======================================
# Funções
# =======================================
def draw_map(df_map, cols, popup_cols):
    """ Esta função tem o objetivo de criar um mapa que mostra a localização central dos restaurantes por tipo de cidade.

        Input: 
            - df_map (DataFrame), 
            - cols (list) -> Lista de strings com nomes de colunas que retornam latiude e longitude
            - popup_cols (list) -> Lista de strings com nomes de colunas a serem incluídas no popup

        Output: Map
    """    
    map = folium.Map(location=(df_map[cols[0]].mean(), 
                               df_map[cols[1]].mean()), 
                               zoom_control=True, control_scale=True, 
                               zoom_start=6)

    for _, row in df_map.iterrows():
        folium.Marker(location=(row[cols[0]], 
                                row[cols[1]]), 
                                popup=row[popup_cols], 
                                icon=folium.Icon(color='red')).add_to(map)   

    return map

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
st.markdown('# Marketplace - Visão Empresa')
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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Quantidade de pedidos por dia
        st.markdown('#### Quantidade de pedidos por dia')

        orders_by_date = df1.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()

        fig_orders_by_date = chart(orders_by_date, ['Order_Date', 'ID'], {'ID': 'Num. pedidos', 'Order_Date': 'Data'})
        st.plotly_chart(fig_orders_by_date)

    with st.container():
        col1, col2 = st.columns(2)

    with col1:
        # Quantidade de pedidos por densidade de tráfego
        st.markdown('#### Quantidade de pedidos por densidade de tráfego')   

        orders_by_traffic_density = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()

        fig_orders_by_traffic_density = chart(orders_by_traffic_density, ['Road_traffic_density', 'ID'], type='pie')
        st.plotly_chart(fig_orders_by_traffic_density)

    with col2:
        # Comparação do volume de pedidos por cidade e tipo de tráfego
        st.markdown('#### Comparação do volume de pedidos por cidade e tipo de tráfego')
        
        orders_by_city_and_traffic = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
        
        fig_orders_by_city_and_traffic = chart(orders_by_city_and_traffic, 
                                               ['City', 'Road_traffic_density'], 
                                               size='ID', color='City', 
                                               labels={'City': 'Tipo de cidade', 'Road_traffic_density': 'Densidade de tráfego'},
                                               type='scatter')
        st.plotly_chart(fig_orders_by_city_and_traffic)

with tab2:
    with st.container():
        # Quantidade de pedidos por semana
        st.markdown('#### Quantidade de pedidos por semana')    

        orders_by_week = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()

        fig_orders_by_week = chart(orders_by_week, 
                                   ['week_of_year', 'ID'], 
                                   labels={'ID': 'Num. pedidos', 'week_of_year': 'Semana'}, 
                                   type='line')
        st.plotly_chart(fig_orders_by_week)

    with st.container():
        # Quantidade de pedidos por entregador por semana
        st.markdown('#### Quantidade de pedidos por entregador por semana') 
        people_by_week = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

        orders_by_person = pd.merge(orders_by_week, people_by_week, how='inner', on='week_of_year')
        orders_by_person['orders_by_person'] = orders_by_person['ID'] / orders_by_person['Delivery_person_ID']

        fig_orders_by_person = chart(orders_by_person, 
                                    ['week_of_year', 'orders_by_person'],
                                    labels={'week_of_year': 'Semana', 'orders_by_person': 'Pedidos por entregador'},
                                    type='line')

        st.plotly_chart(fig_orders_by_person)

with tab3:
    # A localização central de cada cidade por tipo de tráfego
    df_map = df1.loc[:, ['Delivery_location_latitude', 'Delivery_location_longitude', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    try:
        map = draw_map(df_map, ['Delivery_location_latitude', 'Delivery_location_longitude'], ['City', 'Road_traffic_density'])

        with st.container():
            st.markdown('#### A localização central de cada cidade por tipo de tráfego')
            st_folium(map, returned_objects=[], use_container_width=True)
    except:
        st.markdown('Erro! Tente atualizar os filtros!')