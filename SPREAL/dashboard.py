import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuração da Página
st.set_page_config(page_title="SP Real Estate Analytics", layout="wide")
st.title("🏢 SP Real Estate Analytics")
st.subheader("Análise de Custo-Benefício: Saúde e Região")

# 1. Carregando os dados limpos
@st.cache_data
def carregar_dados():
    return pd.read_csv("dataset_imoveis_sp.csv")

df = carregar_dados()

# 2. Menu Lateral para Filtros (Interatividade)
bairros_disponiveis = df['bairro'].unique()
bairros_selecionados = st.sidebar.multiselect(
    "Selecione os Bairros para comparar:", 
    bairros_disponiveis, 
    default=bairros_disponiveis
)

# Filtra o DataFrame com base na seleção
df_filtrado = df[df['bairro'].isin(bairros_selecionados)]

# 3. Métricas de Resumo (Cards)
st.write("### Indicadores Principais")
col1, col2, col3 = st.columns(3)

if not df_filtrado.empty:
    media_m2 = df_filtrado['preco_por_m2'].mean()
    bairro_mais_barato = df_filtrado.groupby('bairro')['preco_por_m2'].mean().idxmin()
    
    col1.metric("Média de Preço por m²", f"R$ {media_m2:.2f}")
    col2.metric("Bairro com Melhor Custo/m²", bairro_mais_barato)
    col3.metric("Imóveis Analisados", len(df_filtrado))

    # 4. Visualização Gráfica (Matplotlib)
    st.write("### Comparativo de Preço Médio por m²")
    
    # Agrupando os dados para o gráfico
    grafico_dados = df_filtrado.groupby('bairro')['preco_por_m2'].mean().sort_values()
    
    fig, ax = plt.subplots(figsize=(10, 4))
    grafico_dados.plot(kind='barh', color=['#4f46e5', '#0ea5e9', '#d4af37'], ax=ax)
    ax.set_xlabel("Preço Médio (R$ / m²)")
    ax.set_ylabel("Bairro")
    
    st.pyplot(fig)
    
    # 5. Tabela de Dados Brutos
    st.write("### Base de Dados")
    st.dataframe(df_filtrado[['bairro', 'preco_aluguel', 'area_m2', 'quartos', 'preco_por_m2']])
else:
    st.warning("Selecione pelo menos um bairro no menu lateral.")
    