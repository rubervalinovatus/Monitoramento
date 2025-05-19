import requests
import pytz
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Fuso horário de Cuiabá
CUIABA_TZ = pytz.timezone('America/Cuiaba')

# Máximo de registros por unidade
MAX_HISTORY_LEN = 100  # mínimo 24 para verificar 2 minutos

# Sites e hospitais
SITES = {
    'Alto Garças': 'https://altogarcas.celk.com.br/',
    'Alto Paraguai': 'https://altoparaguai.celk.com.br/',
    'Aripuanã': 'https://aripuana.celk.com.br/',
    'Brasnorte': 'https://brasnorte.celk.com.br/',
    'Cassilândia': 'https://cassilandia.celk.com.br/',
    'Chapada dos Guimarães': 'https://chapadadosguimaraes.celk.com.br/',
    'Confresa': 'https://confresa.celk.com.br/',
    'Mirassol D\'Oeste': 'https://mirassoldoeste.celk.com.br/',
    'Nortelândia': 'https://nortelandia.celk.com.br/',
    'Nossa Senhora do Livramento': 'https://nossasenhoradolivramento.celk.com.br/',
    'Nova Maringá': 'https://novamaringa.celk.com.br/',
    'Santo Antônio do Leverger': 'https://santoantoniodoleverger.celk.com.br/',
    'São José do Rio Claro': 'https://saojosedorioclaro.celk.com.br/',
    'Vila Bela': 'https://vilabela.celk.com.br/',
    'Várzea Grande': 'https://varzeagrande.celk.com.br/',
    # Hospitais
    'Hospital Aparecida': 'https://hmaparecida.celk.com.br/',
    'Hospital Aripuanã': 'https://hospitalaripuana.celk.com.br/',
    'Hospital Brasnorte': 'https://hospitalbrasnorte.celk.com.br/',
    'Hospital Confresa': 'https://hospitalconfresa.celk.com.br/',
    'Hospital Cotriguaçu': 'https://hospitalcotriguacu.celk.com.br/',
    'Hospital Livramento': 'https://hospitalnossasenhoradolivramento.celk.com.br/',
    'Hospital Nova Xavantina': 'https://hospitalnovaxavantina.celk.com.br/',
    'Hospital Salto do Céu': 'https://hospitalsaltodoceu.celk.com.br/',
    'Hospital São José do Rio Claro': 'https://hospitalsjrioclaro.celk.com.br/',
    'Hospital Várzea Grande': 'https://hospitalvarzeagrande.celk.com.br/',
}

ORDERED_NAMES = list(SITES.keys())

# Histórico de status e horários
history = {site: [] for site in SITES}
timestamps = []

# Lock para evitar concorrência
lock = threading.Lock()

def get_status_color(name):
    try:
        data = history[name]
        if len(data) < 2:
            return 'green' if data and data[-1] == 1 else 'red'
        if data[-1] != data[-2]:
            return 'yellow'
        return 'green' if data[-1] == 1 else 'red'
    except Exception as e:
        print(f"[ERRO STATUS_COLOR] {name}: {e}")
        return 'gray'

def get_alerts():
    offline_alerts = []
    for nome, historico in history.items():
        try:
            if len(historico) >= 24 and all(status == 0 for status in historico[-24:]):
                offline_alerts.append(nome)
        except Exception as e:
            print(f"[ERRO ALERTA] {nome}: {e}")
    return offline_alerts

def check_site(nome, url):
    try:
        response = requests.get(url, timeout=5)
        return nome, 1 if response.status_code == 200 else 0
    except Exception as e:
        print(f"[ERRO CONEXÃO] {nome}: {e}")
        return nome, 0

def get_status_data():
    try:
        current_dt = datetime.now(CUIABA_TZ)
        current_time = current_dt.strftime('%H:%M:%S')

        status_dict = {}

        # Faz requisições com limite de 5 simultâneas
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_site = {executor.submit(check_site, nome, url): nome for nome, url in SITES.items()}
            for future in as_completed(future_to_site):
                nome, status = future.result()
                status_dict[nome] = status

        with lock:
            # Atualiza timestamps
            if len(timestamps) >= MAX_HISTORY_LEN:
                timestamps.pop(0)
            timestamps.append(current_time)

            # Atualiza históricos
            for nome, status in status_dict.items():
                if len(history[nome]) >= MAX_HISTORY_LEN:
                    history[nome].pop(0)
                history[nome].append(status)

            status_colors = {
                nome: get_status_color(nome)
                for nome in ORDERED_NAMES
            }

            offline_alerts = get_alerts()

            return {
                "timestamps": timestamps.copy(),
                "data": {nome: history[nome].copy() for nome in ORDERED_NAMES},
                "status_colors": status_colors,
                "alerts": offline_alerts
            }

    except Exception as e:
        print(f"[ERRO GERAL] Falha ao coletar dados: {e}")
        return {
            "timestamps": [],
            "data": {},
            "status_colors": {},
            "alerts": []
        }
