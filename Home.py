import streamlit as st

img_path = 'img/logo.png'

st.set_page_config(page_title='Home', page_icon=img_path)

# ---------------------------------------------
# Barra Lateral
# ---------------------------------------------
st.sidebar.image('img/logo.png', width=120)
st.sidebar.write('# Curry Company')
st.sidebar.write('## Fastest delivery in town')
st.sidebar.write('---')
st.sidebar.write('### Created by Gabriel Paneque Didi')

# ---------------------------------------------
# Layout no Streamlit
# ---------------------------------------------

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento
        - Visão Tática: Indicadores semanais de crescimento
        - Visão Geográfica: Insights de geolocalização
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for help
    - Time de Data Science no Discord

""")