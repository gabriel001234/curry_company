import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data(path):
    """Esta função tem o objetivo de carregar os dados e armazená-los em um dataframe.

        Input: path (str)
        Output: DataFrame
    """
    df = pd.read_csv(path)
    return df

def clean_data(df):
    """ Esta função tem a responsabilidade de limpar o dataframe

        Limpezas realizadas:
        1. Remoção dos dados NaN
        2. Mudança do tipo de dados das colunas
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção da variável numérica)

        Input: df (DataFrame)
        Output: DataFrame
    """
    # Cópia do df informado
    df1 = df.copy()

    # Removendo dados nulos
    linhas_selecionadas = (df['Delivery_person_Age'] != 'NaN ') & (df['multiple_deliveries'] != 'NaN ') & (df['Road_traffic_density'] != 'NaN ') & (df['City'] != 'NaN ') & (df['Festival'] != 'NaN ')
    df1 = df.loc[linhas_selecionadas, :].copy().reset_index()

    # Converter 'Delivery_person_Age' e 'multiple_deliveries' para int
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # Converter 'Delivery_person_Ratings' para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # Converter 'Order_Date' para datetime
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # Remover caracteres desnecessários
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Time_taken(min)'] = df1.loc[:, 'Time_taken(min)'].str.replace('(min) ', '', regex=False).astype(int)

    # Criando nova coluna 'week_of_year'
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')

    return df1

def chart(df, cols, labels=None, size=None, color=None, cc_scale=None, cc_midpoint=None, type='bar'):
    """ Esta função tem o objetivo de criar gráficos simples do Plotly. Não inclui gráficos do módulo graph_objects.

        Tipos de gráficos:
        1. Gráfico de barras (bar)
        2. Gráfico de pizza (pie)
        3. Gráfico de dispersão (scatter)
        4. Gráfico de linha (line)
        5. Gráfico sunburst

        Input: 
        - df (DataFrame): DataFrame com os dados
        - cols (list): Lista de strings com nomes de colunas a serem utilizadas. 
        No caso de pie, a estrutura é [names, values]; no caso de sb, a estutura é [path1, path2, values]  
        - labels (dict): Dicionário com labels para os eixos dos gráficos 
        - size (str): Define a coluna para tamanho em gráficos suportados 
        - color (str): Define a coluna para cor em gráficos suportados 
        - cc_scale (str): Define o tipo de escala contínua de cores em gráficos suportados
        - cc_midpoint(str): Define o ponto do meio para cores contínuas em gráficos suportados
        - type (str): Define o tipo. Tipos suportados: 'bar', 'pie', 'scatter', 'line', e 'sb'
        Output: Figure
    """
    if type == 'bar':
        fig = px.bar(df, x=cols[0], y=cols[1], labels=labels)
    elif type == 'pie':
        fig = px.pie(df, names=cols[0], values=cols[1], labels=labels)
    elif type == 'scatter':
        fig = px.scatter(df, x=cols[0], y=cols[1], size=size, color=color, labels=labels)
    elif type == 'line':
        fig = px.line(df, x=cols[0], y=cols[1], labels=labels)
    elif type == 'sb':
        fig = px.sunburst(df, path=cols[0:2], values=cols[2], color=color, color_continuous_scale=cc_scale, color_continuous_midpoint=cc_midpoint)        
    return fig