from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

import uvicorn
import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

logger = logging.getLogger("financia.api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

app = FastAPI(
    title="financIA API",
    version="2.0.0",
    description="API de mercado com dados em tempo real para dashboard glassmorphism.",
)

BASE_DIR = Path(__file__).resolve().parent

# Segurança flexível para dev/prod.
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


ASSET_CATALOG = {
    "🇺🇸 Ações EUA": [
        ("NVIDIA", "NVDA"), ("Apple", "AAPL"), ("Microsoft", "MSFT"), ("Amazon", "AMZN"), ("Google", "GOOGL"),
        ("Meta", "META"), ("Tesla", "TSLA"), ("Berkshire Hathaway", "BRK-B"), ("JPMorgan", "JPM"), ("Visa", "V"),
        ("Mastercard", "MA"), ("Eli Lilly", "LLY"), ("Broadcom", "AVGO"), ("ExxonMobil", "XOM"), ("UnitedHealth", "UNH"),
        ("Johnson & Johnson", "JNJ"), ("Procter & Gamble", "PG"), ("Home Depot", "HD"), ("Costco", "COST"), ("Walmart", "WMT"),
        ("AbbVie", "ABBV"), ("Coca-Cola", "KO"), ("PepsiCo", "PEP"), ("McDonald's", "MCD"), ("Netflix", "NFLX"),
        ("Adobe", "ADBE"), ("Salesforce", "CRM"), ("Oracle", "ORCL"), ("Cisco", "CSCO"), ("Intel", "INTC"),
        ("AMD", "AMD"), ("Qualcomm", "QCOM"), ("Texas Instruments", "TXN"), ("Applied Materials", "AMAT"), ("Micron", "MU"),
        ("IBM", "IBM"), ("Accenture", "ACN"), ("Palantir", "PLTR"), ("Uber", "UBER"), ("Airbnb", "ABNB"),
        ("Boeing", "BA"), ("Caterpillar", "CAT"), ("GE Aerospace", "GE"), ("Lockheed Martin", "LMT"), ("Raytheon", "RTX"),
        ("Honeywell", "HON"), ("3M", "MMM"), ("Union Pacific", "UNP"), ("Deere", "DE"), ("American Express", "AXP"),
        ("Goldman Sachs", "GS"), ("Morgan Stanley", "MS"), ("Bank of America", "BAC"), ("Wells Fargo", "WFC"), ("Citigroup", "C"),
        ("BlackRock", "BLK"), ("Charles Schwab", "SCHW"), ("S&P Global", "SPGI"), ("Moody's", "MCO"), ("PayPal", "PYPL"),
        ("Block", "SQ"), ("Shopify", "SHOP"), ("Snowflake", "SNOW"), ("CrowdStrike", "CRWD"), ("Palo Alto Networks", "PANW"),
        ("ServiceNow", "NOW"), ("Datadog", "DDOG"), ("Intuit", "INTU"), ("Booking", "BKNG"), ("American Tower", "AMT"),
        ("Prologis", "PLD"), ("Realty Income", "O"), ("Simon Property", "SPG"), ("NextEra Energy", "NEE"), ("Duke Energy", "DUK"),
        ("Southern Company", "SO"), ("Dominion Energy", "D"), ("Chevron", "CVX"), ("ConocoPhillips", "COP"), ("Occidental", "OXY"),
        ("Marathon Petroleum", "MPC"), ("Valero", "VLO"), ("Pfizer", "PFE"), ("Merck", "MRK"), ("Bristol Myers Squibb", "BMY"),
        ("Amgen", "AMGN"), ("Gilead", "GILD"), ("Moderna", "MRNA"), ("Starbucks", "SBUX"), ("Nike", "NKE"),
        ("Target", "TGT"), ("Lowe's", "LOW"), ("T-Mobile", "TMUS"), ("AT&T", "T"), ("Verizon", "VZ"),
        ("Disney", "DIS"), ("Comcast", "CMCSA"), ("Robinhood", "HOOD"), ("Coinbase", "COIN"), ("Roblox", "RBLX"),
    ],
    "🇧🇷 Ações Brasil": [
        ("Petrobras PN", "PETR4.SA"), ("Petrobras ON", "PETR3.SA"), ("Vale", "VALE3.SA"), ("Itaú", "ITUB4.SA"), ("Bradesco PN", "BBDC4.SA"),
        ("Bradesco ON", "BBDC3.SA"), ("Banco do Brasil", "BBAS3.SA"), ("Santander", "SANB11.SA"), ("Itaúsa", "ITSA4.SA"), ("BTG Pactual", "BPAC11.SA"),
        ("B3", "B3SA3.SA"), ("Weg", "WEGE3.SA"), ("Embraer", "EMBR3.SA"), ("JBS", "JBSS3.SA"), ("Suzano", "SUZB3.SA"),
        ("Klabin", "KLBN11.SA"), ("Gerdau", "GGBR4.SA"), ("CSN", "CSNA3.SA"), ("Usiminas", "USIM5.SA"), ("CSN Mineração", "CMIN3.SA"),
        ("Localiza", "RENT3.SA"), ("Movida", "MOVI3.SA"), ("CCR", "CCRO3.SA"), ("Ecorodovias", "ECOR3.SA"), ("Rumo", "RAIL3.SA"),
        ("Gol", "GOLL4.SA"), ("Azul", "AZUL4.SA"), ("Magazine Luiza", "MGLU3.SA"), ("Lojas Renner", "LREN3.SA"), ("Natura", "NTCO3.SA"),
        ("Raia Drogasil", "RADL3.SA"), ("Pão de Açúcar", "PCAR3.SA"), ("Assaí", "ASAI3.SA"), ("Carrefour Brasil", "CRFB3.SA"), ("Grupo Mateus", "GMAT3.SA"),
        ("Ambev", "ABEV3.SA"), ("BRF", "BRFS3.SA"), ("Marfrig", "MRFG3.SA"), ("SLC Agrícola", "SLCE3.SA"), ("São Martinho", "SMTO3.SA"),
        ("Cosan", "CSAN3.SA"), ("Raízen", "RAIZ4.SA"), ("Ultrapar", "UGPA3.SA"), ("Vibra", "VBBR3.SA"), ("Prio", "PRIO3.SA"),
        ("PetroRio antiga", "PRIO3.SA"), ("3R Petroleum", "RRRP3.SA"), ("PetroRecôncavo", "RECV3.SA"), ("Eneva", "ENEV3.SA"), ("Auren", "AURE3.SA"),
        ("CPFL Energia", "CPFE3.SA"), ("Eletrobras ON", "ELET3.SA"), ("Eletrobras PNB", "ELET6.SA"), ("Engie Brasil", "EGIE3.SA"), ("Taesa", "TAEE11.SA"),
        ("Cemig", "CMIG4.SA"), ("Copel", "CPLE6.SA"), ("Sanepar", "SAPR4.SA"), ("Sabesp", "SBSP3.SA"), ("Aegea", "AEGE3.SA"),
        ("Vivo", "VIVT3.SA"), ("TIM", "TIMS3.SA"), ("Oi", "OIBR3.SA"), ("Totvs", "TOTS3.SA"), ("LWSA", "LWSA3.SA"),
        ("Intelbras", "INTB3.SA"), ("Positivo", "POSI3.SA"), ("Multilaser", "MLAS3.SA"), ("Banco Inter", "INBR32.SA"), ("Nubank BDR", "ROXO34.SA"),
        ("XP Inc BDR", "XPBR31.SA"), ("Méliuz", "CASH3.SA"), ("Cielo", "CIEL3.SA"), ("Stone BDR", "STOC31.SA"), ("PagSeguro BDR", "PAGS34.SA"),
        ("Cyrela", "CYRE3.SA"), ("MRV", "MRVE3.SA"), ("Eztec", "EZTC3.SA"), ("Direcional", "DIRR3.SA"), ("Even", "EVEN3.SA"),
        ("BR Malls", "BRML3.SA"), ("Iguatemi", "IGTI11.SA"), ("Multiplan", "MULT3.SA"), ("Aliansce Sonae", "ALSO3.SA"), ("São Carlos", "SCAR3.SA"),
    ],
    "🌍 ETFs e Índices": [
        ("S&P 500 ETF", "SPY"), ("Nasdaq 100 ETF", "QQQ"), ("Dow Jones ETF", "DIA"), ("Russell 2000 ETF", "IWM"), ("Total US Market", "VTI"),
        ("MSCI World", "URTH"), ("Mercados Emergentes", "EEM"), ("China Large Cap", "FXI"), ("Europa", "VGK"), ("Japão", "EWJ"),
        ("Índia", "INDA"), ("Brasil ETF", "EWZ"), ("Small Caps EUA", "IJR"), ("Semicondutores", "SOXX"), ("Nuvem", "CLOU"),
        ("Inteligência Artificial", "BOTZ"), ("Cibersegurança", "CIBR"), ("Energia Limpa", "ICLN"), ("Petróleo", "USO"), ("Ouro", "GLD"),
        ("Prata", "SLV"), ("Real Estate", "VNQ"), ("Dividendos", "VYM"), ("Bonds 20+ anos", "TLT"), ("Volatilidade", "VIXY"),
    ],
    "₿ Cripto": [
        ("Bitcoin (USD)", "BTC-USD"), ("Ethereum (USD)", "ETH-USD"), ("Solana (USD)", "SOL-USD"), ("BNB (USD)", "BNB-USD"), ("XRP (USD)", "XRP-USD"),
        ("Cardano (USD)", "ADA-USD"), ("Dogecoin (USD)", "DOGE-USD"), ("TRON (USD)", "TRX-USD"), ("Avalanche (USD)", "AVAX-USD"), ("Chainlink (USD)", "LINK-USD"),
        ("Polkadot (USD)", "DOT-USD"), ("Litecoin (USD)", "LTC-USD"), ("Bitcoin Cash (USD)", "BCH-USD"), ("Shiba Inu (USD)", "SHIB-USD"), ("Uniswap (USD)", "UNI-USD"),
    ],
    "💱 Câmbio": [
        ("Dólar (BRL)", "BRL=X"), ("Euro (USD)", "EURUSD=X"), ("Libra (USD)", "GBPUSD=X"), ("Iene (USD)", "JPY=X"), ("Franco Suíço (USD)", "CHF=X"),
    ],
}

ASSET_DB = {
    f"{category.split()[0]} {name} ({ticker.replace('.SA', '')})": ticker
    for category, assets in ASSET_CATALOG.items()
    for name, ticker in assets
}


PERIOD_MAP = {
    "1 Mês": "1mo",
    "6 Meses": "6mo",
    "1 Ano": "1y",
    "5 Anos": "5y",
    "max": "max",
}


class MarketSummaryItem(BaseModel):
    nome: str
    valor: str
    var: str
    cor: Literal["pos", "neg"]


class FullAnalysisResponse(BaseModel):
    preco: str
    variacao: str
    recomendacao: str
    cor_sentimento: str
    confianca: int = Field(ge=40, le=98)
    datas: list[str]
    precos: list[float]
    volumes: list[int]


@lru_cache(maxsize=1)
def sorted_assets() -> list[str]:
    return sorted(ASSET_DB.keys(), key=lambda x: x.lower())


def _sentimento_from_variacao(var_pct: float) -> tuple[str, str, int]:
    if var_pct > 15:
        return "COMPRA FORTE 🚀", "#00E5A8", 94
    if var_pct < -5:
        return "CAUTELA 🔻", "#FF4D6D", 61
    return "NEUTRO ⚖️", "#8FA8FF", 78


@app.get("/")
def ler_index() -> FileResponse:
    return FileResponse(BASE_DIR / "index.html")


@app.get("/lista-ativos", response_model=list[str])
def listar_ativos() -> list[str]:
    return sorted_assets()


@app.get("/resumo-mercado", response_model=list[MarketSummaryItem])
def resumo_mercado() -> list[MarketSummaryItem]:
    indices = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "BITCOIN": "BTC-USD",
        "DÓLAR": "BRL=X",
    }
    try:
        dados = yf.download(list(indices.values()), period="5d", progress=False)["Close"]
    except Exception:
        logger.exception("Falha ao baixar resumo de mercado")
        return []

    if dados.empty:
        return []

    resultado: list[MarketSummaryItem] = []
    for nome, ticker in indices.items():
        if ticker not in dados:
            continue
        series = dados[ticker].dropna()
        if len(series) < 2:
            continue

        atual = float(series.iloc[-1])
        anterior = float(series.iloc[-2])
        variacao = ((atual - anterior) / anterior) * 100

        resultado.append(
            MarketSummaryItem(
                nome=nome,
                valor=f"{atual:,.2f}",
                var=f"{variacao:+.2f}%",
                cor="pos" if variacao >= 0 else "neg",
            )
        )

    return resultado


@app.get("/analise-completa/{nome_ativo}/{periodo}", response_model=FullAnalysisResponse)
def analise_completa(nome_ativo: str, periodo: str) -> FullAnalysisResponse:
    ticker = ASSET_DB.get(nome_ativo)
    if not ticker:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")

    periodo_resolvido = PERIOD_MAP.get(periodo)
    if not periodo_resolvido:
        raise HTTPException(status_code=400, detail="Período inválido")

    try:
        hist = yf.Ticker(ticker).history(period=periodo_resolvido)
    except Exception as exc:
        logger.exception("Falha ao consultar histórico")
        raise HTTPException(status_code=502, detail="Falha ao consultar provedor de mercado") from exc

    if hist.empty:
        raise HTTPException(status_code=404, detail="Sem dados disponíveis")

    closes = hist["Close"].dropna()
    if len(closes) < 2:
        raise HTTPException(status_code=404, detail="Dados insuficientes para análise")

    preco_atual = float(closes.iloc[-1])
    variacao_pct = ((preco_atual - float(closes.iloc[0])) / float(closes.iloc[0])) * 100
    sentimento, cor, confianca = _sentimento_from_variacao(variacao_pct)

    return FullAnalysisResponse(
        preco=f"{preco_atual:.2f}",
        variacao=f"{variacao_pct:+.2f}%",
        recomendacao=sentimento,
        cor_sentimento=cor,
        confianca=confianca,
        datas=closes.index.strftime("%Y-%m-%d").tolist(),
        precos=[float(v) for v in closes.tolist()],
        volumes=[int(v) for v in hist["Volume"].fillna(0).astype(int).tolist()],
    )


app.mount("/", StaticFiles(directory=BASE_DIR, html=True), name="static")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
