import pandas as pd
import requests

# script para pegar a API dos dados governamentais de IPCA, PIB e desemprego para calcular a correlação com as transacoes do banco

codigo_ipca = 433

def dados_bcb(codigo, nome):
    url = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json'

    r = requests.get(url)

    if r.status_code == 200:
        dados = pd.DataFrame(r.json())

        dados['data'] = pd.to_datetime(dados['data'], format='%d/%m/%Y')
        dados['valor'] = pd.to_numeric(dados['valor'])
        dados = dados.rename(columns={'valor': nome})
        return dados
    else:
        print("Erro ao acessar API!! Código de status:", r.status_code)

dados_ipca = dados_bcb(433, 'IPCA')
dados_pib = dados_bcb(4380, 'PIB')
dados_desemprego = dados_bcb(24369, 'Desemprego')

dados_totais = pd.merge(dados_ipca, dados_pib, on='data', how='outer')
dados_totais = pd.merge(dados_totais, dados_desemprego, on='data', how='outer')

dados_totais = dados_totais[(dados_totais['data'] >= '2010-01-01') & (dados_totais['data'] <= '2023-12-31')]

dados_totais.to_csv('dados_totais.csv', index=False)

print("Dados salvos com sucesso em 'dados_totais.csv'.")
print(dados_totais)

