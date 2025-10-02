import streamlit as st

st.set_page_config(page_title='Home', page_icon='img/logo.png', layout='wide')

st.sidebar.image('img/logo.png', width=120)
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest delivery in town')
st.sidebar.markdown('---')

st.markdown('# Curry Company - Growth Dashboard')
st.markdown(
    """
    O Growth Dashboard foi construído para acompanhar as métricas de crescimento da empresa, entregadores e restaurantes

    ### Como utilizar este dashboard?
    - Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização
    - Entregadores:
        - Acompanhamento dos indicadores semanais de crescimento
    - Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes
    """
)