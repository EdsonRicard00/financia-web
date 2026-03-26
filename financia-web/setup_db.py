import sqlite3

def criar_banco_de_dados():
    conn = sqlite3.connect('financas.db')
    cursor = conn.cursor()

    # Cria a Tabela de Tipos de Ativos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS asset_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')

    # Cria a Tabela de Ativos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        display_name TEXT NOT NULL,
        country TEXT,
        exchange TEXT,
        currency TEXT,
        type_id INTEGER,
        FOREIGN KEY (type_id) REFERENCES asset_types (id)
    )
    ''')

    # Insere as categorias básicas
    tipos = [('Ação',), ('Criptomoeda',), ('Moeda Fiduciária',), ('ETF',)]
    cursor.executemany('INSERT OR IGNORE INTO asset_types (name) VALUES (?)', tipos)
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados e tabelas criados com sucesso!")

if __name__ == "__main__":
    criar_banco_de_dados()