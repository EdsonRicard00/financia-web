from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
# Permite que o frontend (HTML/JS) converse com este backend
CORS(app) 

@app.route('/api/checkout', methods=['POST'])
def checkout():
    # Recebe os dados do clique no botão comprar
    dados_compra = request.json
    
    produto_id = dados_compra.get('produto_id')
    valor = dados_compra.get('valor')
    
    # Aqui entraria a lógica de integração com MercadoPago, Stripe, etc.
    print(f"Iniciando checkout do produto {produto_id} no valor de R${valor}")
    
    # Simulando um pequeno delay de processamento
    time.sleep(1)
    
    # Retorna sucesso para o JavaScript
    return jsonify({
        "status": "sucesso",
        "mensagem": "Excelente escolha! Redirecionando para o pagamento seguro...",
        "redirect_url": "/pagamento"
    }), 200

if __name__ == '__main__':
    # Roda o servidor na porta 5000
    app.run(debug=True, port=5000)