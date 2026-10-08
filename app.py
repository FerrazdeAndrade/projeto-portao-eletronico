import os
import sqlite3
import time
from flask import Flask, jsonify, render_template
from flask_cors import CORS  # Permite requisições do Live Server (porta 5500)
import serial

app = Flask(__name__)
CORS(app)  # Libera o acesso para o Go Live (porta 5500)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "portao.db")

PORTA_SERIAL = "COM3"
BAUD_RATE = 9600

try:
  arduino = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
  time.sleep(2)
  print(f"Conectado ao Arduino na porta {PORTA_SERIAL}")
except Exception as e:
  arduino = None
  print(f"Arduino não conectado: modo simulação ativo.")


def init_db():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS acionamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acao TEXT NOT NULL,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
  conn.commit()
  conn.close()


init_db()


def registrar_acionamento(acao):
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("INSERT INTO acionamentos (acao) VALUES (?)", (acao,))
  conn.commit()

  cursor.execute("SELECT COUNT(*) FROM acionamentos")
  total = cursor.fetchone()[0]
  conn.close()
  return total


def get_total_acionamentos():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("SELECT COUNT(*) FROM acionamentos")
  resultado = cursor.fetchone()
  conn.close()
  return resultado[0] if resultado else 0


@app.route("/")
def index():
  return render_template("index.html")


@app.route("/api/status", methods=["GET"])
def status():
  total = get_total_acionamentos()
  return jsonify({"total_acionamentos": total})


@app.route("/api/portao/<acao>", methods=["POST"])
def controlar_portao(acao):
  if acao not in ["abrir", "fechar"]:
    return jsonify({"status": "erro", "mensagem": "Ação inválida"}), 400

  if arduino and arduino.is_open:
    try:
      comando = "A" if acao == "abrir" else "F"
      arduino.write(comando.encode())
    except Exception as e:
      print(f"Erro no Arduino: {e}")

  total = registrar_acionamento(acao)
  return jsonify({
      "status": "sucesso",
      "acao": acao,
      "total_acionamentos": total,
  })


if __name__ == "__main__":
  app.run(debug=True, port=5000)