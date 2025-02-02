import pandas as pd

propostas_credito = pd.read_csv('./banvic_data/propostas_credito.csv')

taxa_aprovacao = propostas_credito.groupby('status_proposta')['cod_proposta'].count().reset_index()
taxa_aprovacao['percentual'] = (taxa_aprovacao['cod_proposta'] / taxa_aprovacao['cod_proposta'].sum()) * 100
