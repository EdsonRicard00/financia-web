import sqlite3
import csv
import os

def importar_ativos_do_csv():
    caminho_csv = 'ativos.csv'
    
    # Verifica se o arquivo CSV existe antes de continuar
    if not os.path.exists(caminho_csv):
        print("❌ Erro: Arquivo 'ativos.csv' não encontrado. Crie o arquivo primeiro.")
        return

    # Conecta ao banco de dados que já criamos
    conn = sqlite3.connect('financas.db')
    cursor = conn.cursor()

    print("Iniciando importação de ativos...")
    ativos_inseridos = 0

    # Abre o arquivo CSV no modo leitura (com encoding utf-8 para ler os emojis)
    with open(caminho_csv, mode='r', encoding='utf-8') as arquivo:
        leitor_csv = csv.DictReader(arquivo) # Lê a primeira linha como cabeçalho
        
        for linha in leitor_csv:
            # 1. Busca o ID do tipo do ativo (Ação, Criptomoeda, etc)
            cursor.execute("SELECT id FROM asset_types WHERE name = ?", (linha['type'],))
            resultado_tipo = cursor.fetchone()
            
            # Se o tipo existir no banco, pega o ID. Se não, define como None (nulo)
            type_id = resultado_tipo[0] if resultado_tipo else None
            
            # 2. Insere o ativo na tabela (usamos IGNORE para não dar erro se o ativo já existir)
            cursor.execute('''
                INSERT OR IGNORE INTO assets 
                (ticker, name, display_name, country, exchange, currency, type_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                linha['ticker'], 
                linha['name'], 
                linha['display'], 
                linha['country'], 
                linha['exchange'], 
                linha['currency'], 
                type_id
            ))
            
            # Apenas soma se uma nova linha foi realmente inserida
            if cursor.rowcount > 0:
                ativos_inseridos += 1

    conn.commit()
    conn.close()
    print(f"✅ Importação concluída! {ativos_inseridos} novos ativos foram adicionados ao banco de dados.")

if __name__ == "__main__":
    importar_ativos_do_csv()