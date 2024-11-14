import pandas as pd

file_path = 'planilha.xlsx' 
data = pd.read_excel(file_path)

data['Data coleta'] = pd.to_datetime(data['Data coleta'], errors='coerce')
data['Data entrega'] = pd.to_datetime(data['Data entrega'], errors='coerce')

estado_para_sigla = {
    'Acre': 'AC', 'Alagoas': 'AL', 'Amapá': 'AP', 'Amazonas': 'AM', 'Bahia': 'BA', 'Ceará': 'CE',
    'Distrito Federal': 'DF', 'Espírito Santo': 'ES', 'Goiás': 'GO', 'Maranhão': 'MA', 'Mato Grosso': 'MT',
    'Mato Grosso do Sul': 'MS', 'Minas Gerais': 'MG', 'Pará': 'PA', 'Paraíba': 'PB', 'Paraná': 'PR',
    'Pernambuco': 'PE', 'Piauí': 'PI', 'Rio de Janeiro': 'RJ', 'Rio Grande do Norte': 'RN', 'Rio Grande do Sul': 'RS',
    'Rondônia': 'RO', 'Roraima': 'RR', 'Santa Catarina': 'SC', 'São Paulo': 'SP', 'Sergipe': 'SE', 'Tocantins': 'TO'
}

data['Estado'] = data['Estado'].replace(estado_para_sigla)

data['Dias para entrega'] = data.apply(lambda row: max((row['Data entrega'] - row['Data coleta']).days, 0)
                                       if pd.notnull(row['Data entrega']) and row['Data entrega'] >= row['Data coleta'] 
                                       else 0, axis=1)

data['Erro de entrega'] = data.apply(lambda row: 'extraviado' in str(row['Data entrega']).lower() or 
                                     (pd.notnull(row['Data entrega']) and row['Data entrega'] < row['Data coleta']),
                                     axis=1)

data_valida = data[data['Erro de entrega'] == False]

sla_por_estado = {
    'AC': 7, 'AL': 6, 'AP': 6, 'AM': 6, 'BA': 6, 'CE': 5, 'DF': 4, 'ES': 5, 'GO': 5, 'MA': 5,
    'MG': 5, 'MS': 5, 'MT': 5, 'PA': 6, 'PB': 7, 'PE': 5, 'PI': 7, 'PR': 4, 'RJ': 4, 'RN': 5,
    'RO': 7, 'RR': 7, 'RS': 5, 'SC': 5, 'SE': 6, 'SP': 4, 'TO': 6
}

cidades_por_estado = data_valida.groupby('Estado')['Cidade'].count()

dias_entrega_por_estado = data_valida.groupby('Estado')['Dias para entrega'].sum()

print("\nMédia de dias de entrega por estado (comparação com o SLA):")
for estado in sla_por_estado:
    if cidades_por_estado.get(estado, 0) > 0:
        media_dias = dias_entrega_por_estado.get(estado, 0) / cidades_por_estado.get(estado, 1)
        status_sla = "Atendeu ao SLA" if media_dias <= sla_por_estado[estado] else "Não atendeu ao SLA"
        print(f"{estado}: Média = {media_dias:.2f} dias, SLA = {sla_por_estado[estado]} dias -> {status_sla}")
    else:
        print(f"{estado}: Não houve entregas válidas registradas")

erros = data[data['Erro de entrega'] == True][['ID do pedido', 'Data coleta', 'Data entrega']]
print("\nPedidos com erro (extraviado ou entrega antes da coleta):")
print(erros)
