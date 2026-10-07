import streamlit as st
import pandas as pd

from datetime import datetime

# TÍTULO

st.write('# Mercado Preço Bom')

# LEITURA DO ESTOQUE


produtos = pd.read_csv('mercado.csv')


# Aviso de Estoque baixo !!
estoque_baixo = produtos [produtos['estoque']<= 5]
if  not estoque_baixo.empty:
    st.warning('Existem produtos com estoque baixo!')
    st.dataframe(estoque_baixo)

# botoes ==
if 'mostrar_estoque' not in st.session_state:
    st.session_state['mostrar_estoque'] = False

if 'mostrar_historico' not in st.session_state:
    st.session_state['mostrar_historico'] = False


if st.button('Acessar estoque'):
    st.session_state['mostrar_estoque'] = not st.session_state['mostrar_estoque']

if st.button('Acessar Historico De Vendas'):
    st.session_state['mostrar_historico'] = not st.session_state['mostrar_historico']


if st.session_state['mostrar_estoque']:
    st.write('## Estoque Atual')
    st.dataframe(produtos)


      
# carrinho 

if 'carrinho' not in st.session_state: 
    st.session_state['carrinho'] = []
 

# LEITURA DO HISTÓRICO DE VENDAS


try:
    vendas = pd.read_csv('vendas.csv')

except FileNotFoundError:
    vendas = pd.DataFrame(columns=[
        'produto',
        'categoria',
        'quantidade',
        'valor',
        'forma_pagamento',
        'data'
    ])

if 'data' not in vendas.columns:
    vendas['data'] = ''



# SISTEMA DE VENDAS

produto_escolhido = st.sidebar.selectbox(
    'Produto',
    produtos['produto'].unique()
)

categoria = st.sidebar.selectbox(
    'Categoria',
    produtos['categoria'].unique()
)
quantidade = st.sidebar.number_input(
    'Quantidade',
    min_value=0
)

preco_produto = produtos.loc[
    produtos['produto'] == produto_escolhido,
    'preco'
].iloc[0]


#total preco

st.sidebar.write(f'preço total: R$ {preco_produto:.2f}')

# calculo do produtos (preco x quantidade)
valor_total = preco_produto * quantidade

st.sidebar.write(f'Total: R$ { valor_total :.2f}')

# forma de pagamento

formas_pagamento = st.sidebar.selectbox(
    'Formas de pagamento',
    ['Dinheiro', 'Credito', 'Pix', 'Debito']
)

# carrinho botao:

adicionar = st.sidebar.button ('Adicionar ao carrinho')

if adicionar :
    item = {'produto' : produto_escolhido,
    'quantidade' : quantidade,
    'preço' : preco_produto,
    'total':  valor_total,
    }
    st.session_state['carrinho'].append(item)

# tela carrinho

st.write('## Carrinho')

if st.session_state['carrinho']:
    st.dataframe(st.session_state['carrinho'])
else:
    st.info('Carrinho vazio')

total_carrinho = sum(
    item['total']
    for item in st.session_state['carrinho']
)

st.sidebar.write('## Total Carrinho')
st.sidebar.write(f'R$ {total_carrinho:.2f}')


# REGISTRAR VENDA

botao = st.sidebar.button('Registrar venda')

if botao:

    # Verificar estoque de todos os produtos
    estoque_ok = True

    for item in st.session_state['carrinho']:

        estoque_atual = produtos.loc[
            produtos['produto'] == item['produto'],
            'estoque'
        ].iloc[0]

        if item['quantidade'] > estoque_atual:
            st.error(
                f"Estoque insuficiente para {item['produto']}!"
            )
            estoque_ok = False

# Só registra se todos tiverem estoque
    if estoque_ok:

        for item in st.session_state['carrinho']:

            # Abater estoque
            produtos.loc[
                produtos['produto'] == item['produto'],
                'estoque'
            ] -= item['quantidade']

            # Criar venda
            nova_venda = {
                'produto': item['produto'],
                'categoria': categoria,
                'quantidade': item['quantidade'],
                'valor': item['total'],
                'forma_pagamento': formas_pagamento,
                'data' : datetime.now().strftime('%d/%m/%y') 
                }
            

            vendas = pd.concat(
                [vendas, pd.DataFrame([nova_venda])],
                ignore_index=True
            )

        # Salvar
        vendas.to_csv('vendas.csv', index=False)
        produtos.to_csv('mercado.csv', index=False)

        # Limpar carrinho
        st.session_state['carrinho'] = []

        st.success('Venda registrada!')

# HISTÓRICO DE VENDAS 


data_hoje = datetime.now().strftime('%d/%m/%y')

if st.session_state['mostrar_historico']:
    st.write('## Histórico de Vendas')

    if vendas.empty:
        st.info('Nenhuma venda registrada ainda.')
    else:
        st.dataframe(vendas)



# RESUMO DO DIA


vendas_hoje = vendas[vendas['data'] == data_hoje]

# Produtos mais vendidos
st.write('## Produtos mais vendidos')

mais_vendidos = (
    vendas_hoje.groupby('produto')['quantidade']
    .sum()
    .sort_values(ascending=False)
    .head(5)
)

ranking = mais_vendidos.reset_index()

ranking = ranking.merge(
    produtos[['produto', 'estoque']],
    on='produto',
    how='left'
)

ranking = ranking.rename(columns={
    'quantidade': 'Vendidos hoje',
    'estoque': 'Estoque atual'
})

st.dataframe(ranking)

st.write('## Status do estoque')

for _, item in ranking.iterrows():

    if item['Estoque atual'] <= 2:
        st.error(
            f"🔴 {item['produto']}: REPOSIÇÃO URGENTE! "
            f"Vendeu {item['Vendidos hoje']} hoje "
            f"e restam {item['Estoque atual']} unidades."
        )

    elif item['Estoque atual'] <= 5:
        st.warning(
            f"🟡 {item['produto']}: ATENÇÃO! "
            f"Vendeu {item['Vendidos hoje']} hoje "
            f"e restam {item['Estoque atual']} unidades."
        )

    else:
        st.success(
            f"🟢 {item['produto']}: Estoque saudável. "
            f"Vendeu {item['Vendidos hoje']} hoje "
            f"e restam {item['Estoque atual']} unidades."
        )

# Métricas
faturamento = vendas_hoje['valor'].sum()
quantidade_vendas = len(vendas_hoje)
item_vendidos = vendas_hoje['quantidade'].sum()

if quantidade_vendas > 0:
    ticket_medio = faturamento / quantidade_vendas
else:
    ticket_medio = 0


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric('Itens vendidos', int(item_vendidos))

with col2:
    st.metric('Ticket médio', f'R$ {ticket_medio:.2f}')

with col3:
    st.metric('Faturamento', f'R$ {faturamento:.2f}')

with col4:
    st.metric('Vendas realizadas', quantidade_vendas)
                     
# carregamento local

# streamlit run Mercado.py

