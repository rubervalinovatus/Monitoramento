from flask import Flask, render_template, jsonify
from monitor import get_status_data
import threading
import time
import traceback

app = Flask(__name__)

# Flag para evitar múltiplas threads
data_thread_started = False

# Atualiza dados em background
def update_data_loop():
    while True:
        try:
            get_status_data()
        except Exception as e:
            print("[ERRO NA ATUALIZAÇÃO DE DADOS]")
            traceback.print_exc()
        time.sleep(5)  # intervalo de 5 segundos


#@app.before_first_request
#def start_background_thread():
  #  global data_thread_started
   # if not data_thread_started:
    #    print("[INFO] Iniciando thread de atualização de dados...")
    #    threading.Thread(target=update_data_loop, daemon=True).start()
     #   data_thread_started = True

if not data_thread_started:
    print("[INFO] Iniciando thread de atualização de dados...")
    threading.Thread(target=update_data_loop, daemon=True).start()
    data_thread_started = True


@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        print("[ERRO AO CARREGAR A TELA INICIAL]")
        traceback.print_exc()
        return "<h1>Erro interno no servidor</h1>", 500

@app.route('/data')
def data():
    try:
        data = get_status_data()
        return jsonify(data)
    except Exception as e:
        print("[ERRO AO OBTER DADOS DO MONITORAMENTO]")
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
        print("[ERRO AO INICIAR O SERVIDOR FLASK]")
        traceback.print_exc()
