import psycopg2

# Configurações de conexão com o seu PostgreSQL (PgAdmin)
DB_CONFIG = {
    "dbname": "db_portao",
    "user": "postgres",
    "password": "Ead@0219702812",
    "host": "localhost",
    "port": "5432"  # Altere para 5433 caso sua instância utilize essa porta
}

def visualizar_dados():
    try:
        # Conectando ao banco de dados
        conexao = psycopg2.connect(**DB_CONFIG)
        cursor = conexao.cursor()

        print("✅ Conexão com o PostgreSQL estabelecida com sucesso!\n")

        # Consultando os dados armazenados na tabela 'acionamentos'
        cursor.execute("SELECT id, tipo, texto, data_hora FROM acionamentos ORDER BY id DESC;")
        registros = cursor.fetchall()

        if not registros:
            print("📭 Nenhum acionamento encontrado no banco de dados.")
        else:
            print(f"📊 Total de registros encontrados: {len(registros)}\n")
            print(f"{'ID':<5} | {'TIPO':<10} | {'DESCRIÇÃO':<15} | {'DATA E HORA'}")
            print("-" * 55)
            
            for reg in registros:
                print(f"{reg[0]:<5} | {reg[1]:<10} | {reg[2]:<15} | {reg[3]}")

    except Exception as erro:
        print(f"❌ Erro ao conectar ou consultar o banco de dados: {erro}")
    
    finally:
        # Garante o fechamento da conexão
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conexao' in locals() and conexao:
            conexao.close()
            print("\n🔒 Conexão encerrada.")

if __name__ == "__main__":
    visualizar_dados()