import pandas as pd
from datetime import date

transacoes = pd.read_csv('./banvic_data/transacoes.csv')
contas = pd.read_csv('./banvic_data/contas.csv')
clientes = pd.read_csv('./banvic_data/clientes.csv')

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

clientes['faixa_etaria'] = pd.cut(clientes['idade'], bins=[18, 30, 40, 50, 60, 100], labels=['18-30', '31-40', '41-50', '51-60', '60+'])

transacoes_contas = pd.merge(transacoes, contas[['num_conta', 'cod_cliente']], on='num_conta', how='left')
transacoes_clientes = pd.merge(transacoes_contas, clientes[['cod_cliente', 'faixa_etaria']], on='cod_cliente', how='left')

transferencia_faixa_etaria = transacoes_clientes.groupby('faixa_etaria')['valor_transacao'].sum().reset_index()
