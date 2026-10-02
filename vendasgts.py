# importacao de sistemas usandos
import streamlit as st
import pandas as pd
import plotly.express as px

# base de vendas tabela de vendas
tabela_vendas = pd.read_csv('vendas.csv')

# titulo do sistema de vendas ( nome )
st.write('# Sistema de vendas de eletronicos')

# cadastro de vendas
st.sidebar.write('## Cadastrar vendas')


data = st.sidebar.date_input ('Data da vendas')

vendedor = st.sidebar.selectbox ('vendedor', [ 'joao', 'maria', 'jose'])

produto = st.sidebar.selectbox ('produto', ["celular", "nooteebook", "fone "])

quantidade = st.sidebar.number_input('quantidade', step=1)

valor = st.sidebar.number_input('valor', step=0.01)

botao_cadastrar = st.sidebar.button('cadastrar venda')

#logica de cadrastro de vendas
if botao_cadastrar: # fucao de cadastro de vendas
    
    tabela_vendas.to_csv('vendas.csv', index=False) # salva a tabela de vendas no arguivo csv ( base de dados )

    if valor <= 0: # bloqueio de cadastro de vendas com valor menor ou igual a 0
        st.error('O valor da venda deve ser maior que 0')
    else:
        nova_venda = [str(data), vendedor, produto, quantidade, valor] # nova venda cadastrada

        ultima_linha = len(tabela_vendas) # 122 LINHAS
        tabela_vendas.loc[ultima_linha] = nova_venda
    print(nova_venda)
    st.success('venda cadastrada com sucesso') 

# sessao de cadastro de vendas 
st.write('## vendas cadastradas')
st.dataframe(tabela_vendas)


# sessao de Dashboard
st.write('## Dashboard de Vendas')
# card / metricas -. total de vendas
faturamento = tabela_vendas['valor'].sum()
st.metric('Faturamento Total',f' R$ {faturamento}')

# grafico de barras
grafico_barra = px.bar(tabela_vendas, x='vendedor', y='valor', color='produto', text='quantidade')
st.plotly_chart(grafico_barra)

# grafico de pizza 
grafico_pizza =px.pie(tabela_vendas, 'produto', values='valor',hole=0.2)
st.plotly_chart(grafico_pizza)

