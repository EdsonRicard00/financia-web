import pandas as pd
import re

# 1. Simulação do Web Scraping (Dados Brutos extraídos do HTML)
# Na prática, o BeautifulSoup alimentaria esta lista extraindo as <div> e <span> do site
dados_extraidos = [
    {"bairro": "Saúde", "preco_texto": "R$ 3.500 /mês", "area_texto": "65 m²", "quartos": 2},
    {"bairro": "Saúde", "preco_texto": "R$ 4.100 /mês", "area_texto": "80 m²", "quartos": 3},
    {"bairro": "Vila Mariana", "preco_texto": "R$ 5.200 /mês", "area_texto": "70 m²", "quartos": 2},
    {"bairro": "Vila Mariana", "preco_texto": "R$ 6.000 /mês", "area_texto": "90 m²", "quartos": 3},
    {"bairro": "Planalto Paulista", "preco_texto": "R$ 4.800 /mês", "area_texto": "85 m²", "quartos": 3},
    {"bairro": "Planalto Paulista", "preco_texto": "R$ 3.100 /mês", "area_texto": "50 m²", "quartos": 1}
]

# 2. Transformando em um DataFrame (A mágica do Pandas)
df = pd.DataFrame(dados_extraidos)

# 3. Tratamento de Dados (Limpeza)
# Expressões regulares (Regex) para extrair apenas os números
df['preco_aluguel'] = df['preco_texto'].apply(lambda x: float(re.sub(r'[^\d]', '', x)))
df['area_m2'] = df['area_texto'].apply(lambda x: float(re.sub(r'[^\d]', '', x)))

# 4. Análise e Criação de Métricas (Métrica de Investimento)
df['preco_por_m2'] = round(df['preco_aluguel'] / df['area_m2'], 2)

# Exibe no terminal para você validar
print("Dados Limpos e Processados:")
print(df[['bairro', 'preco_aluguel', 'area_m2', 'preco_por_m2']])

# 5. Salva para o nosso Dashboard ler
df.to_csv("dataset_imoveis_sp.csv", index=False)
print("\nArquivo 'dataset_imoveis_sp.csv' gerado com sucesso!")