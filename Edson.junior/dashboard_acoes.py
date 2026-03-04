import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config(page_title="Dashboard Bolsa Brasil 2025", layout="wide")

st.title("📈 Análise de Performance: Top 10 Ações Brasileiras (5 Anos)")
st.markdown("""
**Analista:** Gemini Data Expert | **Fonte de Dados:** Yahoo Finance  
Este dashboard compara a rentabilidade das principais Blue Chips da B3 contra benchmarks de mercado.
""")

# ================= SIDEBAR =================
st.sidebar.header("Parâmetros do Investidor")

tickers_list = [
    'VALE3.SA', 'PETR4.SA', 'ITUB4.SA', 'BBDC4.SA', 'BBAS3.SA',
    'ABEV3.SA', 'WEGE3.SA', 'ELET3.SA', 'RENT3.SA', 'SUZB3.SA'
]

selected_tickers = st.sidebar.multiselect(
    "Selecione as Ações para Comparar:",
    options=tickers_list,
    default=['VALE3.SA', 'PETR4.SA', 'WEGE3.SA', 'ITUB4.SA']
)

investimento_inicial = st.sidebar.number_input(
    "Valor a Investir (Simulação R$):",
    min_value=1000.0,
    value=10000.0,
    step=1000.0
)

# ================= FUNÇÃO DE DADOS =================
@st.cache_data
def get_data(tickers, start_date, end_date):
    all_tickers = list(tickers) + ['^BVSP']

    data = yf.download(all_tickers, start=start_date, end=end_date, auto_adjust=False, threads=True)

    if data.empty:
        st.error("⚠️ Não foi possível baixar os dados. Verifique sua conexão.")
        return pd.DataFrame()

    if isinstance(data.columns, pd.MultiIndex):
        if 'Adj Close' in data.columns.get_level_values(0):
            data = data.xs('Adj Close', axis=1, level=0, drop_level=True)
        elif 'Close' in data.columns.get_level_values(0):
            st.warning("⚠️ 'Adj Close' não encontrado. Usando 'Close' padrão.")
            data = data.xs('Close', axis=1, level=0, drop_level=True)
    else:
        if 'Adj Close' in data.columns:
            data = data['Adj Close']
        elif 'Close' in data.columns:
            st.warning("⚠️ 'Adj Close' não encontrado. Usando 'Close' padrão.")
            data = data['Close']

    if isinstance(data, pd.Series):
        data = data.to_frame()

    data = data.ffill().bfill()
    return data

# ================= PERÍODO =================
end_date = datetime.now()
start_date = end_date - timedelta(days=5 * 365)

# ================= PROCESSAMENTO =================
if selected_tickers:
    with st.spinner('Baixando dados de mercado...'):
        df = get_data(tuple(selected_tickers), start_date, end_date)

    if df.empty:
        st.error("Erro ao baixar dados do Yahoo Finance.")
        st.stop()

    df_normalized = (df / df.iloc[0]) * investimento_inicial

    # ================= CDI e POUPANÇA SIMULADOS =================
    cdi_rate_daily = (1 + 0.105) ** (1/252) - 1
    poupanca_rate_daily = (1 + 0.06) ** (1/252) - 1

    dias = range(len(df_normalized))

    df_normalized['CDI (Simulado)'] = investimento_inicial * (1 + cdi_rate_daily) ** pd.Series(dias, index=df_normalized.index)
    df_normalized['Poupança (Simulado)'] = investimento_inicial * (1 + poupanca_rate_daily) ** pd.Series(dias, index=df_normalized.index)

    if '^BVSP' in df_normalized.columns:
        df_normalized = df_normalized.rename(columns={'^BVSP': 'IBOVESPA'})

    # ================= GRÁFICO DE LINHA =================
    st.subheader(f"Evolução Patrimonial: R$ {investimento_inicial:,.2f} aplicados há 5 anos")

    fig = px.line(
        df_normalized,
        labels={'value': 'Valor (R$)', 'variable': 'Ativo'},
        title="Comparativo de Rentabilidade"
    )

    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # ================= RESULTADO FINAL =================
    st.subheader("Resultado Final (Hoje)")
    last_values = df_normalized.iloc[-1].sort_values(ascending=False)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.write("### Ranking de Retorno")
        for asset, value in last_values.items():
            delta = ((value - investimento_inicial) / investimento_inicial) * 100
            st.metric(asset, f"R$ {value:,.2f}", f"{delta:.2f}%")

    with col2:
        fig_bar = px.bar(
            x=last_values.values,
            y=last_values.index,
            orientation='h',
            labels={'x': 'Valor (R$)', 'y': 'Ativo'},
            title="Valor Final Acumulado"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ================= TABELA MENSAL =================
    st.subheader("Histórico de Performance Mensal (Amostra)")
    df_monthly = df.resample('ME').last().pct_change() * 100
    st.dataframe(df_monthly.tail(12).style.format("{:.2f}%").background_gradient(cmap='RdYlGn'))

else:
    st.warning("Selecione ao menos uma ação no menu lateral.")

# ================= RODAPÉ =================
st.markdown("---")
st.markdown("""
**Nota do Especialista:**
1. Usa `Adj Close`, que já considera dividendos.
2. CDI e Poupança são simulados por juros compostos médios.
3. Para valores oficiais, é necessário API do Banco Central.
""")
