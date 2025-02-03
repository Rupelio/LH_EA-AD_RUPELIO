import pandas as pd
from datetime import date

transacoes = pd.read_csv('./banvic_data/transacoes.csv')
dim_date = pd.read_csv('./banvic_data/dim_dates.csv')
dados_totais = pd.read_csv('./banvic_data/dados_totais.csv')
propostas_credito = pd.read_csv('./banvic_data/propostas_credito.csv')
contas = pd.read_csv('./banvic_data/contas.csv')
clientes = pd.read_csv('./banvic_data/clientes.csv')

def converter_para_date(valor):
    try:
        return pd.to_datetime(valor, errors='coerce').date()
    except:
        return None

dim_date['data'] = dim_date['data'].apply(converter_para_date)
transacoes['data_transacao'] = transacoes['data_transacao'].str.replace(' UTC', '', regex=True).apply(converter_para_date)
dados_totais['data'] = dados_totais['data'].apply(converter_para_date)

transacoes_completo = pd.merge(transacoes, dim_date, left_on='data_transacao', right_on='data', how='left')

media_trimestre = transacoes_completo.groupby('trimestre').size().reset_index(name='transacoes_total')

valor_trimestre = transacoes_completo.groupby('trimestre')['valor_transacao'].sum().reset_index(name='volume_total')

transacoes_r = transacoes_completo.groupby('tem_R')['valor_transacao'].sum().reset_index()

transacoes_r.columns = ['tem_R', 'volume_total']

volume_r = transacoes_r[transacoes_r['tem_R'] == True]['volume_total'].values[0]
volume_nao_r = transacoes_r[transacoes_r['tem_R'] == False]['volume_total'].values[0]

mes_mais_transacoes = transacoes_completo.groupby('nome_mes')['valor_transacao'].sum().reset_index().sort_values(by='valor_transacao', ascending=False)

transacoes_totais = pd.merge(transacoes, dados_totais, left_on='data_transacao', right_on='data', how='left')

correlacao_ipca = transacoes_totais['valor_transacao'].corr(transacoes_totais['IPCA'])
correlacao_pib = transacoes_totais['valor_transacao'].corr(transacoes_totais['PIB'])
correlacao_desemprego = transacoes_totais['valor_transacao'].corr(transacoes_totais['Desemprego'])

correlacoes = pd.DataFrame({
    'Indicador': ['IPCA', 'PIB', 'Desemprego'],
    'Correlação com Transações': [correlacao_ipca, correlacao_pib, correlacao_desemprego]
})

taxa_aprovacao = propostas_credito.groupby('status_proposta')['cod_proposta'].count().reset_index()
taxa_aprovacao['percentual'] = (taxa_aprovacao['cod_proposta'] / taxa_aprovacao['cod_proposta'].sum()) * 100

transacoes_agencias = pd.merge(transacoes, contas, on='num_conta', how='left')

# agencia que mais movimentou por ordem de maior pro menor
volume_agencia = transacoes_agencias.groupby('cod_agencia')['valor_transacao'].sum().reset_index().sort_values(by='valor_transacao', ascending=False)

clientes['data_nascimento'] = pd.to_datetime(clientes['data_nascimento'])


def idade_clientes(nascimento):
    hoje = date.today()
    idade = hoje.year - nascimento.year

    if(hoje.month, hoje.day) < (nascimento.month, nascimento.day):
        idade -= 1
    return idade


clientes['idade'] = clientes['data_nascimento'].apply(idade_clientes)

clientes['faixa_etaria'] = pd.cut(clientes['idade'], bins=[17, 30, 40, 50, 60, 100], labels=['18-30', '31-40', '41-50', '51-60', '60+'])

transacoes_contas = pd.merge(transacoes, contas[['num_conta', 'cod_cliente']], on='num_conta', how='left')
transacoes_clientes = pd.merge(transacoes_contas, clientes[['cod_cliente', 'faixa_etaria']], on='cod_cliente', how='left')

transacoes_faixa_etaria = transacoes_clientes.groupby('faixa_etaria')['valor_transacao'].sum().reset_index()

propostas_aprovadas = propostas_credito[propostas_credito['status_proposta'] == 'Aprovada']

propostas_aprovadas['lucro_presumido'] = propostas_aprovadas['valor_financiamento'] * propostas_aprovadas['taxa_juros_mensal'] * propostas_aprovadas['quantidade_parcelas']

lucro_total = propostas_aprovadas['lucro_presumido'].sum()
valor_emprestado = propostas_aprovadas['valor_financiamento'].sum()
if lucro_total > 0:
    margem = (lucro_total - valor_emprestado) / lucro_total
else:
    margem = 0

ticket_medio = propostas_aprovadas['valor_financiamento'].mean()

propostas_df = pd.DataFrame({
    'Métrica': ['Lucro Presumido', 'Margem Bruta', "Ticket Médio"],
    'Valor': [lucro_total, margem, ticket_medio]
})
