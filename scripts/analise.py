import pandas as pd
from datetime import date

# le os csv
transacoes = pd.read_csv('./banvic_data/transacoes.csv')
dim_date = pd.read_csv('./banvic_data/dim_dates.csv')
dados_totais = pd.read_csv('./banvic_data/dados_totais.csv')
propostas_credito = pd.read_csv('./banvic_data/propostas_credito.csv')
contas = pd.read_csv('./banvic_data/contas.csv')
clientes = pd.read_csv('./banvic_data/clientes.csv')

# corrigir datas de maneira correta para que nenhuma tenha NaN
def converter_para_date(valor):
    try:
        return pd.to_datetime(valor, errors='coerce').date()
    except:
        return None

# aplicando a conversão de csv para datetime
dim_date['data'] = dim_date['data'].apply(converter_para_date)
transacoes['data_transacao'] = transacoes['data_transacao'].str.replace(' UTC', '', regex=True).apply(converter_para_date)
dados_totais['data'] = dados_totais['data'].apply(converter_para_date)

# juntando os csv's transacoes e dim date
transacoes_completo = pd.merge(transacoes, dim_date, left_on='data_transacao', right_on='data', how='left')

# pegando a media trimestral de transacoes = valores em quantidade
media_trimestre = transacoes_completo.groupby('trimestre').size().reset_index(name='transacoes_total')

# pegando o valor trimestral de transacoes = valores em dinheiro
valor_trimestre = transacoes_completo.groupby('trimestre')['valor_transacao'].sum().reset_index(name='volume_total')

# transacoes em meses com a letra r
transacoes_r = transacoes_completo.groupby('tem_R')['valor_transacao'].sum().reset_index()

# criando colunas das transacoes
transacoes_r.columns = ['tem_R', 'volume_total']

# deixando separado as transacoes dos meses com e sem r
volume_r = transacoes_r[transacoes_r['tem_R'] == True]['volume_total'].values[0]
volume_nao_r = transacoes_r[transacoes_r['tem_R'] == False]['volume_total'].values[0]

# vendo qual mes teve mais transacoes
mes_mais_transacoes = transacoes_completo.groupby('nome_mes')['valor_transacao'].sum().reset_index().sort_values(by='valor_transacao', ascending=False)

# juntando o csv de transacoes com os dados de IPCA, PIB e desemprego
transacoes_totais = pd.merge(transacoes, dados_totais, left_on='data_transacao', right_on='data', how='left')

# calculando a correlacao de cada dado com as transacoes
correlacao_ipca = transacoes_totais['valor_transacao'].corr(transacoes_totais['IPCA'])
correlacao_pib = transacoes_totais['valor_transacao'].corr(transacoes_totais['PIB'])
correlacao_desemprego = transacoes_totais['valor_transacao'].corr(transacoes_totais['Desemprego'])

# transformando em um dataframe para exportar para xlsx
correlacoes = pd.DataFrame({
    'Indicador': ['IPCA', 'PIB', 'Desemprego'],
    'Correlação com Transações': [correlacao_ipca, correlacao_pib, correlacao_desemprego]
})

# vendo a taxa de cada status das propostas de credito
taxa_aprovacao = propostas_credito.groupby('status_proposta')['cod_proposta'].count().reset_index()
# transformando a taxa em porcentagem
taxa_aprovacao['percentual'] = (taxa_aprovacao['cod_proposta'] / taxa_aprovacao['cod_proposta'].sum()) * 100

# jutando os csv para ver qual agencia teve mais transacoes
transacoes_agencias = pd.merge(transacoes, contas, on='num_conta', how='left')

# agencia que mais movimentou por ordem de maior pro menor
volume_agencia = transacoes_agencias.groupby('cod_agencia')['valor_transacao'].sum().reset_index().sort_values(by='valor_transacao', ascending=False)

# transformando a data de nascimento em datetime
clientes['data_nascimento'] = pd.to_datetime(clientes['data_nascimento'])

# funcao para calcular a idade do cliente
def idade_clientes(nascimento):
    hoje = date.today()
    idade = hoje.year - nascimento.year

    if(hoje.month, hoje.day) < (nascimento.month, nascimento.day):
        idade -= 1
    return idade

# tranformando em idade
clientes['idade'] = clientes['data_nascimento'].apply(idade_clientes)

# separando por faixa etaria
clientes['faixa_etaria'] = pd.cut(clientes['idade'], bins=[17, 30, 40, 50, 60, 100], labels=['18-30', '31-40', '41-50', '51-60', '60+'])

# juntando csv's para chegar em transacoes por faixa etaria, aqui tive que pegar transacoes e contas para pegar o num_conta e cod_cliente
# depois juntei com clientes para juntar o cod_cliente e faixa etaria, pois transacoes não tem dados do codigo do cliente
transacoes_contas = pd.merge(transacoes, contas[['num_conta', 'cod_cliente']], on='num_conta', how='left')
transacoes_clientes = pd.merge(transacoes_contas, clientes[['cod_cliente', 'faixa_etaria']], on='cod_cliente', how='left')

# pega o dado das transacoes por faixa etaria
transacoes_faixa_etaria = transacoes_clientes.groupby('faixa_etaria')['valor_transacao'].sum().reset_index()

# verifica quais propostas aprovadas foram aprovadas
propostas_aprovadas = propostas_credito[propostas_credito['status_proposta'] == 'Aprovada']

# calcula o lucro presumido das propostas aprovadas
propostas_aprovadas['lucro_presumido'] = propostas_aprovadas['valor_financiamento'] * propostas_aprovadas['taxa_juros_mensal'] * propostas_aprovadas['quantidade_parcelas']

# pega o lucro presumido e soma
lucro_total = propostas_aprovadas['lucro_presumido'].sum()
# pega o valor financiado e soma
valor_emprestado = propostas_aprovadas['valor_financiamento'].sum()
# funcao para calcular a margem bruta
if lucro_total > 0:
    margem = (lucro_total - valor_emprestado) / lucro_total
else:
    margem = 0
# calcula o ticket medio do usuario a partir das propostras aprovadas e valor financiado
ticket_medio = propostas_aprovadas['valor_financiamento'].mean()

# transforma em dataframe para exportar para xlsxS
propostas_df = pd.DataFrame({
    'Métrica': ['Lucro Presumido', 'Margem Bruta', "Ticket Médio"],
    'Valor': [lucro_total, margem, ticket_medio]
})
