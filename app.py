import os
import sqlite3
import time
from flask import Flask, jsonify, render_template

# Permite importar a biblioteca serial apenas se disponível
try:
    import serial
except ImportError:
    serial = None

# Configura o Flask para procurar os templates na raiz do projeto
app = Flask(__name__, template_folder='.')

# --- CONFIGURAÇÃO DA COMUNICAÇÃO SERIAL (ARDUINO) ---
# Tenta conectar à porta Serial do Arduino (Modo Local).
# Se estiver no Render (Nuvem) ou se o Arduino não estiver conectado, ignora o erro.
arduino = None
if serial:
    try:
        arduino = serial.Serial('COM3', 9600, timeout=1)  # Ajuste a porta COM se necessário no seu PC
        print("✅ Arduino conectado com sucesso na porta COM3!")
    except Exception as e:
        print("⚠️ Aviso: Arduino não encontrado. Modo simulação/nuvem ativo.")
else:
    print("⚠️ Biblioteca pyserial não instalada. Modo simulação/nuvem ativo.")


# --- CONFIGURAÇÃO DO BANCO DE DADOS (SQLite) ---
DB_NAME = "portao.db"

def init_db():
    """Cria a tabela de acionamentos se ela não existir."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS acionamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acao VARCHAR(20) NOT NULL,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print("✅ Banco de dados SQLite inicializado com sucesso.")

# Inicializa o banco ao rodar o app
init_db()

def registrar_acionamento(acao):
    """Grava o comando no banco de dados e retorna o total acumulado."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO acionamentos (acao) VALUES (?)", (acao,))
    conn.commit()
    
    # Recupera o total atualizado
    cursor.execute("SELECT COUNT(*) FROM acionamentos")
    total = cursor.fetchone()[0]
    conn.close()
    print(f"📡 Comando recebido e gravado: {acao.upper()}. Total no BD: {total}")
    return total


# --- ROTAS DA APLICAÇÃO WEB ---

@app.route("/")
def index():
    """Serve o frontend (index.html na raiz do projeto)."""
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def status():
    """Retorna o total de acionamentos para o frontend atualizar o contador."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM acionamentos")
        total = cursor.fetchone()[0]
        conn.close()
        return jsonify({"total_acionamentos": total})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route("/api/portao/<acao>", methods=["POST"])
def controlar_portao(acao):
    """Processa os comandos recebidos do controle remoto no frontend."""
    if acao not in ["abrir", "fechar"]:
        return jsonify({"status": "erro", "mensagem": "Ação inválida"}), 400

    # 1. Envia comando para a Serial do Arduino (se conectado no PC)
    if arduino:
        try:
            comando_char = b'A' if acao == "abrir" else b'F'
            arduino.write(comando_char)
            print(f"🔌 Sinal Serial enviado ao Arduino: {comando_char.decode('utf-8')}")
        except Exception as e:
            print(f"⚠️ Erro ao enviar comando serial ao Arduino: {e}")

    # 2. Grava a ação no banco de dados SQLite
    try:
        total_atualizado = registrar_acionamento(acao)
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": f"Erro no banco de dados: {e}"}), 500

    # 3. Retorna sucesso para o frontend
    return jsonify({
        "status": "sucesso",
        "acao": acao,
        "total_acionamentos": total_atualizado,
        "mensagem": f"O portão começou a {acao}."
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)