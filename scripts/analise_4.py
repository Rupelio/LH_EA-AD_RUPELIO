import pandas as pd

transacoes = pd.read_csv('./banvic_data/transacoes.csv')

transacoes['data_transacao'] = pd.to_datetime(transacoes['data_transacao'], format='mixed')


