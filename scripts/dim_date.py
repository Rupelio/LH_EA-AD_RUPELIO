import pandas as pd

start = '2010-01-01'
end = '2023-12-31'

dim_dates = pd.DataFrame(pd.date_range(start=start, end=end, freq='D'), columns=['data'])

# Adicionar atributos derivados
dim_dates['ano'] = dim_dates['data'].dt.year
dim_dates['mes'] = dim_dates['data'].dt.month
dim_dates['dia'] = dim_dates['data'].dt.day
dim_dates['trimestre'] = dim_dates['data'].dt.quarter
dim_dates['dia_semana'] = dim_dates['data'].dt.weekday
dim_dates['nome_mes'] = dim_dates['data'].dt.month_name()
dim_dates['nome_dia_semana'] = dim_dates['data'].dt.day_name()

dim_dates['tem_R'] = dim_dates['nome_mes'].str.contains('r', case=False)

dim_dates.to_csv('dim_dates.csv', index=False)
