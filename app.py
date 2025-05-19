from flask import Flask, render_template, jsonify
from monitor import get_status_data
import threading
import time
import traceback

app = Flask(__name__)

# Atualiza dados em background
def update_data_loop():
    while True:
        try:
            get_status_data()
        except Exception as e:
            print("[ERRO NA ATUALIZAÇÃO DE DADOS]")
            traceback.print_exc()
        time.sleep(5)  # intervalo de 5 segundos

# Inicia thread em segundo plano
threading.Thread(target=update_data_loop, daemon=True).start()

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        print("[ERRO AO CARREGAR TELA INICIAL]")
        traceback.print_exc()
        return "<h1>Erro interno no servidor</h1>", 500

@app.route('/data')
def data():
    try:
        data = get_status_data()
        return jsonify(data)
    except Exception as e:
        print("[ERRO AO OBTER DADOS]")
        traceback.print_exc()
        return jsonify({
            "timestamps": [],
            "data": {},
            "status_colors": {},
            "alerts": ["Erro ao obter dados do monitoramento"]
        }), 500

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        print("[ERRO AO INICIAR SERVIDOR FLASK]")
        traceback.print_exc()
