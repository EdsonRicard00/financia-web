from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Literal

import uvicorn
import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logger = logging.getLogger("financia.api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

app = FastAPI(
    title="financIA API",
    version="2.0.0",
    description="API de mercado com dados em tempo real para dashboard glassmorphism.",
)

# Segurança flexível para dev/prod.
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


ASSET_DB = {
    "🇺🇸 NVIDIA (NVDA)": "NVDA",
    "🇺🇸 Apple (AAPL)": "AAPL",
    "🇺🇸 Microsoft (MSFT)": "MSFT",
    "🇺🇸 Amazon (AMZN)": "AMZN",
    "🇺🇸 Google (GOOGL)": "GOOGL",
    "🇺🇸 Meta (META)": "META",
    "🇺🇸 Tesla (TSLA)": "TSLA",
    "🇧🇷 Petrobras PN (PETR4)": "PETR4.SA",
    "🇧🇷 Vale (VALE3)": "VALE3.SA",
    "🇧🇷 Itaú (ITUB4)": "ITUB4.SA",
    "🇧🇷 Banco do Brasil (BBAS3)": "BBAS3.SA",
    "🇧🇷 Weg (WEGE3)": "WEGE3.SA",
    "🇧🇷 Magalu (MGLU3)": "MGLU3.SA",
    "₿ Bitcoin (USD)": "BTC-USD",
    "₿ Ethereum (USD)": "ETH-USD",
    "💵 Dólar (BRL)": "BRL=X",
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
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": "financIA API"}


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


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
