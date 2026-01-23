const API_URL = "http://127.0.0.1:8000";

window.onload = async function() {
    console.log("Iniciando Frontend...");
    await loadAssets();
    await loadTopBar();
};

async function loadAssets() {
    const select = document.getElementById('asset-select');
    try {
        const res = await fetch(`${API_URL}/lista-ativos`);
        if (!res.ok) throw new Error("Falha na conexão");
        const ativos = await res.json();
        
        select.innerHTML = ''; 
        ativos.forEach(ativo => {
            let opt = document.createElement('option');
            opt.value = ativo;
            opt.text = ativo;
            select.appendChild(opt);
        });
        
        // Seleciona um ativo padrão e carrega
        select.value = "🇺🇸 NVIDIA (NVDA)"; 
        updateDashboard(); 
    } catch(e) {
        console.error(e);
        select.innerHTML = '<option>ERRO: Reinicie o Python (Play)</option>';
        alert("O site não conseguiu falar com o Python. Verifique se o terminal preto está rodando.");
    }
}

async function loadTopBar() {
    const container = document.getElementById('top-ticker-bar');
    try {
        const res = await fetch(`${API_URL}/resumo-mercado`);
        const data = await res.json();
        if(data.length === 0) throw new Error("Vazio");
        
        container.innerHTML = '';
        data.forEach(item => {
            const div = document.createElement('div');
            div.className = 't-item';
            const colorClass = item.cor === 'pos' ? 'pos' : 'neg';
            const icon = item.cor === 'pos' ? '▲' : '▼';
            div.innerHTML = `<span style="color:#aaa">${item.nome}</span><span class="t-val">${item.valor}</span><span class="${colorClass}">${icon} ${item.var}</span>`;
            div.style.marginRight = "30px";
            container.appendChild(div);
        });
    } catch(e) { 
        container.innerHTML = '<span style="color:#666; padding:10px;">Mercado Offline (Tentando reconectar...)</span>';
    }
}

async function updateDashboard() {
    const ativo = document.getElementById('asset-select').value;
    const periodo = document.getElementById('period-select').value;
    const btn = document.querySelector('.btn-analyze');
    
    // UI de Carregamento
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Baixando Dados...';
    document.getElementById('ai-verdict').style.opacity = "0.3";
    
    try {
        const res = await fetch(`${API_URL}/analise-completa/${ativo}/${periodo}`);
        const data = await res.json();
        
        if(data.erro) { alert("Erro no Python: " + data.erro); return; }
        
        // 1. Atualiza Preço e Variação
        document.getElementById('display-price').innerText = `R$ ${data.preco}`;
        const varElem = document.getElementById('display-var');
        varElem.innerHTML = data.variacao.includes('-') ? `▼ ${data.variacao}` : `▲ ${data.variacao}`;
        varElem.className = data.variacao.includes('-') ? 'lp-tag text-red' : 'lp-tag text-green';

        // 2. Atualiza IA
        const verdict = document.getElementById('ai-verdict');
        verdict.innerText = data.recomendacao;
        verdict.style.opacity = "1";
        verdict.style.color = data.cor_sentimento;

        // --- 3. DESENHA OS 3 GRÁFICOS ---
        const commonLayout = {
            paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ccc', family: 'Poppins' },
            xaxis: { showgrid: false }, yaxis: { gridcolor: 'rgba(255,255,255,0.05)' },
            margin: { t: 10, l: 40, r: 10, b: 30 }, showlegend: false,
            height: 250 // Altura fixa para cada gráfico
        };

        // Gráfico 1: Preço
        Plotly.newPlot('chart-price', [{
            x: data.datas, y: data.precos, type: 'scatter', mode: 'lines',
            line: { color: '#00f2ff', width: 2 }, fill: 'tozeroy'
        }], commonLayout, {displayModeBar: false, responsive: true});

        // Gráfico 2: Volume
        Plotly.newPlot('chart-volume', [{
            x: data.datas, y: data.volumes, type: 'bar', marker: { color: '#7000ff' }
        }], commonLayout, {displayModeBar: false, responsive: true});

        // Gráfico 3: Rentabilidade (%)
        const startPrice = data.precos[0];
        const pctChange = data.precos.map(p => ((p - startPrice) / startPrice) * 100);
        
        const layoutPct = JSON.parse(JSON.stringify(commonLayout));
        layoutPct.yaxis.ticksuffix = "%";
        
        Plotly.newPlot('chart-percent', [{
            x: data.datas, y: pctChange, type: 'scatter', mode: 'lines',
            line: { color: data.variacao.includes('-') ? '#ff0055' : '#00ff88', width: 2 }
        }], layoutPct, {displayModeBar: false, responsive: true});

        // Barra de Confiança
        const bar = document.getElementById('confidence-bar');
        bar.style.width = "0%";
        setTimeout(() => { bar.style.width = "94%"; bar.style.background = data.cor_sentimento; }, 100);

    } catch(e) {
        console.error(e);
        alert("Erro ao desenhar gráficos. Verifique o console.");
    } finally {
        btn.innerHTML = '<i class="fas fa-microchip"></i> PROCESSAR DADOS';
    }
}