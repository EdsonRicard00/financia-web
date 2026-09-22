const API_URL = "http://127.0.0.1:8000";

window.onload = async function () {
    await loadAssets();
    await loadTopBar();
    setInterval(loadTopBar, 45000);
};

async function fetchJson(url) {
    const response = await fetch(url);
    if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        const detail = payload.detail || "Falha na comunicação com a API.";
        throw new Error(detail);
    }
    return response.json();
}

async function loadAssets() {
    const select = document.getElementById("asset-select");
    try {
        const ativos = await fetchJson(`${API_URL}/lista-ativos`);
        select.innerHTML = "";

        ativos.forEach((ativo) => {
            const opt = document.createElement("option");
            opt.value = ativo;
            opt.text = ativo;
            select.appendChild(opt);
        });

        select.value = "🇺🇸 NVIDIA (NVDA)";
        updateDashboard();
    } catch (error) {
        console.error(error);
        select.innerHTML = '<option>Erro ao carregar ativos</option>';
        alert(`Não foi possível carregar os ativos: ${error.message}`);
    }
}

async function loadTopBar() {
    const container = document.getElementById("top-ticker-bar");
    try {
        const data = await fetchJson(`${API_URL}/resumo-mercado`);
        if (!Array.isArray(data) || data.length === 0) {
            throw new Error("Sem dados no momento.");
        }

        container.innerHTML = "";
        data.forEach((item) => {
            const div = document.createElement("div");
            div.className = "t-item";
            const icon = item.cor === "pos" ? "▲" : "▼";
            div.innerHTML = `<span style="color:#aaa">${item.nome}</span><span class="t-val">${item.valor}</span><span class="${item.cor}">${icon} ${item.var}</span>`;
            div.style.marginRight = "30px";
            container.appendChild(div);
        });
    } catch (error) {
        container.innerHTML = '<span style="color:#666; padding:10px;">Mercado offline (reconectando...)</span>';
    }
}

async function updateDashboard() {
    const ativo = document.getElementById("asset-select").value;
    const periodo = document.getElementById("period-select").value;
    const btn = document.querySelector(".btn-analyze");

    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
    btn.disabled = true;

    try {
        const payload = `${encodeURIComponent(ativo)}/${encodeURIComponent(periodo)}`;
        const data = await fetchJson(`${API_URL}/analise-completa/${payload}`);

        document.getElementById("display-price").innerText = `R$ ${data.preco}`;

        const varElem = document.getElementById("display-var");
        const isNegative = data.variacao.includes("-");
        varElem.innerHTML = isNegative ? `▼ ${data.variacao}` : `▲ ${data.variacao}`;
        varElem.className = isNegative ? "lp-tag text-red" : "lp-tag text-green";

        const verdict = document.getElementById("ai-verdict");
        verdict.innerText = data.recomendacao;
        verdict.style.color = data.cor_sentimento;
        verdict.style.opacity = "1";

        const confidenceBar = document.getElementById("confidence-bar");
        confidenceBar.style.width = "0%";
        setTimeout(() => {
            confidenceBar.style.width = `${data.confianca}%`;
            confidenceBar.style.background = data.cor_sentimento;
        }, 100);

        renderCharts(data, isNegative);
    } catch (error) {
        console.error(error);
        alert(`Não foi possível analisar esse ativo: ${error.message}`);
    } finally {
        btn.innerHTML = '<i class="fas fa-microchip"></i> PROCESSAR DADOS';
        btn.disabled = false;
    }
}

function renderCharts(data, isNegative) {
    const commonLayout = {
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { color: "#ccc", family: "Poppins" },
        xaxis: { showgrid: false },
        yaxis: { gridcolor: "rgba(255,255,255,0.05)" },
        margin: { t: 10, l: 40, r: 10, b: 30 },
        showlegend: false,
        height: 250,
    };

    Plotly.newPlot(
        "chart-price",
        [{ x: data.datas, y: data.precos, type: "scatter", mode: "lines", line: { color: "#47dbff", width: 2.5 }, fill: "tozeroy" }],
        commonLayout,
        { displayModeBar: false, responsive: true },
    );

    Plotly.newPlot(
        "chart-volume",
        [{ x: data.datas, y: data.volumes, type: "bar", marker: { color: "#9f7cff" } }],
        commonLayout,
        { displayModeBar: false, responsive: true },
    );

    const startPrice = data.precos[0];
    const pctChange = data.precos.map((p) => ((p - startPrice) / startPrice) * 100);
    const layoutPct = { ...commonLayout, yaxis: { ...commonLayout.yaxis, ticksuffix: "%" } };

    Plotly.newPlot(
        "chart-percent",
        [{ x: data.datas, y: pctChange, type: "scatter", mode: "lines", line: { color: isNegative ? "#ff5f84" : "#00e5a8", width: 2.5 } }],
        layoutPct,
        { displayModeBar: false, responsive: true },
    );
}
