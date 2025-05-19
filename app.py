from flask import Flask, render_template, jsonify
from monitor import get_status_data
import threading
import time

app = Flask(__name__)

# Atualiza dados em background
def update_data_loop():
    while True:
        get_status_data()
        time.sleep(5)  # intervalo

threading.Thread(target=update_data_loop, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    return jsonify(get_status_data())

if __name__ == '__main__':
    app.run(debug=True)
