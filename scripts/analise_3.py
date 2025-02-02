import pandas as pd

transacoes = pd.read_csv('./banvic_data/transacoes.csv')
dim_date = pd.read_csv('./banvic_data/dim_dates.csv')
dados_totais = pd.read_csv('./banvic_data/dados_totais.csv')


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


