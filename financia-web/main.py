from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import uvicorn

app = FastAPI()

# CONFIGURAÇÃO DE SEGURANÇA (Liberando conexão do navegador)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Aceita qualquer origem (Live Server, Arquivo, etc)
    allow_credentials=True,
    allow_methods=["*"], # Aceita GET, POST, OPTIONS
    allow_headers=["*"],
)

# --- BANCO DE DADOS ---
ASSET_DB = {
    "🇺🇸 NVIDIA (NVDA)": "NVDA", "🇺🇸 Apple (AAPL)": "AAPL", "🇺🇸 Microsoft (MSFT)": "MSFT",
    "🇺🇸 Amazon (AMZN)": "AMZN", "🇺🇸 Google (GOOGL)": "GOOGL", "🇺🇸 Meta (META)": "META",
    "🇺🇸 Tesla (TSLA)": "TSLA", 
    "🇧🇷 Petrobras PN (PETR4)": "PETR4.SA", "🇧🇷 Vale (VALE3)": "VALE3.SA", 
    "🇧🇷 Itaú (ITUB4)": "ITUB4.SA", "🇧🇷 Banco do Brasil (BBAS3)": "BBAS3.SA",
    "🇧🇷 Weg (WEGE3)": "WEGE3.SA", "🇧🇷 Magalu (MGLU3)": "MGLU3.SA",
    "₿ Bitcoin (USD)": "BTC-USD", "₿ Ethereum (USD)": "ETH-USD", 
    "💵 Dólar (BRL)": "BRL=X"
}

@app.get("/lista-ativos")
def listar_ativos():
    return list(ASSET_DB.keys())

@app.get("/resumo-mercado")
def resumo_mercado():
    indices = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "BITCOIN": "BTC-USD", "DÓLAR": "BRL=X"}
    resultado = []
    try:
        # Tenta baixar dados. Se falhar, retorna lista vazia para não travar o site
        dados = yf.download(list(indices.values()), period="5d", progress=False)['Close']
        if dados.empty: return []
        
        for nome, ticker in indices.items():
            try:
                series = dados[ticker].dropna()
                if len(series) < 2: continue
                atual = series.iloc[-1]
                anterior = series.iloc[-2]
                var = ((atual - anterior) / anterior) * 100
                resultado.append({
                    "nome": nome, "valor": f"{atual:,.2f}", 
                    "var": f"{var:+.2f}%", "cor": "pos" if var >= 0 else "neg"
                })
            except: pass
    except: pass
    return resultado

@app.get("/analise-completa/{nome_ativo}/{periodo}")
def analise_completa(nome_ativo: str, periodo: str):
    ticker = ASSET_DB.get(nome_ativo)
    if not ticker: return {"erro": "Ativo não encontrado"}

    try:
        # Mapa de períodos (Com MAX para 40 anos)
        p_map = {
            "1 Mês": "1mo", "6 Meses": "6mo", 
            "1 Ano": "1y", "5 Anos": "5y", "max": "max"
        }
        
        stock = yf.Ticker(ticker)
        hist = stock.history(period=p_map.get(periodo, "1mo"))
        
        if hist.empty: return {"erro": "Sem dados disponíveis"}

        # Cálculos
        preco_atual = hist['Close'].iloc[-1]
        var_pct = ((preco_atual - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
        
        # Preparando dados para os 3 Gráficos
        datas = hist.index.strftime('%Y-%m-%d').tolist()
        precos = hist['Close'].tolist()
        volumes = hist['Volume'].tolist()

        sentimento = "COMPRA FORTE 🚀" if var_pct > 15 else "CAUTELA 🔻" if var_pct < -5 else "NEUTRO ⚖️"
        cor = "#00ff88" if var_pct >= 0 else "#ff0055"

        return {
            "preco": f"{preco_atual:.2f}",
            "variacao": f"{var_pct:+.2f}%",
            "recomendacao": sentimento,
            "cor_sentimento": cor,
            "datas": datas,
            "precos": precos,
            "volumes": volumes
        }

    except Exception as e: return {"erro": str(e)}

# Bloco para rodar com o botão Play do VS Code
if __name__ == "__main__":
    print("Iniciando Servidor na porta 8000...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)