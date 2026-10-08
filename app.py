import os
import sqlite3
import time
from flask import Flask, jsonify, render_template
# import serial  # Serial removido temporariamente para focar no frontend puramente.

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS (SQLite) ---
# Define o nome do arquivo do banco de dados na mesma pasta do app.py
DB_NAME = "portao.db"

def init_db():
    # Cria a tabela de acionamentos se ela não existir
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

# Função para gravar uma ação no banco
def registrar_acionamento(acao):
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
    # Serve o frontend (templates/index.html)
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def status():
    # Retorna o total de acionamentos para o frontend atualizar o contador
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM acionamentos")
    total = cursor.fetchone()[0]
    conn.close()
    return jsonify({"total_acionamentos": total})

@app.route("/api/portao/<acao>", methods=["POST"])
def controlar_portao(acao):
    # Processa os comandos recebidos do controle remoto no frontend
    if acao not in ["abrir", "fechar"]:
        return jsonify({"status": "erro", "mensagem": "Ação inválida"}), 400

    # Grava a ação no banco de dados SQLite
    try:
        total_atualizado = registrar_acionamento(acao)
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": f"Erro no banco de dados: {e}"})

    # Retorna sucesso IMEDIATAMENTE para o frontend começar a animação
    return jsonify({
        "status": "sucesso",
        "acao": acao,
        "total_acionamentos": total_atualizado,
        "mensagem": f"O portão começou a {acao} (simulação)."
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)