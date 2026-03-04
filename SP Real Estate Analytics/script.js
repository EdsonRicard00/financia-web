document.addEventListener('DOMContentLoaded', () => {
    const btnComprar = document.getElementById('btn-comprar');
    const statusMessage = document.getElementById('status-message');

    btnComprar.addEventListener('click', async () => {
        // Feedback visual imediato (UX)
        const textoOriginal = btnComprar.innerText;
        btnComprar.innerText = 'Processando...';
        btnComprar.style.opacity = '0.8';
        btnComprar.disabled = true;

        try {
            // Simulando uma requisição para o backend Python (API)
            const response = await fetch('http://127.0.0.1:5000/api/checkout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ produto_id: 1, valor: 1299.00 })
            });

            const data = await response.json();

            if(response.ok) {
                statusMessage.innerText = data.mensagem;
                statusMessage.style.opacity = '1';
                btnComprar.innerText = 'Redirecionando...';
            }
        } catch (error) {
            statusMessage.innerText = "Erro ao conectar. Tente novamente.";
            statusMessage.style.color = "#f87171";
            statusMessage.style.opacity = '1';
            btnComprar.innerText = textoOriginal;
            btnComprar.disabled = false;
        }
    });
});