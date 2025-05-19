import requests
import pytz
from datetime import datetime

# Fuso horário de Cuiabá
cuiaba_tz = pytz.timezone('America/Cuiaba')

# Sites e hospitais
sites = {
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

# Ordem personalizada fixa
ordered_names = [
    'Alto Garças',
    'Alto Paraguai',
    'Aripuanã',
    'Brasnorte',
    'Cassilândia',
    'Chapada dos Guimarães',
    'Confresa',
    'Mirassol D\'Oeste',
    'Nortelândia',
    'Nossa Senhora do Livramento',
    'Nova Maringá',
    'Santo Antônio do Leverger',
    'São José do Rio Claro',
    'Vila Bela',
    'Várzea Grande',
    'Hospital Aparecida',
    'Hospital Aripuanã',
    'Hospital Brasnorte',
    'Hospital Confresa',
    'Hospital Cotriguaçu',
    'Hospital Livramento',
    'Hospital Nova Xavantina',
    'Hospital Salto do Céu',
    'Hospital São José do Rio Claro',
    'Hospital Várzea Grande',
]

# Dados armazenados
max_len = 100  # para armazenar histórico suficiente (mínimo 24 para 2 minutos)
history = {site: [] for site in sites}
timestamps = []

def get_status_color(name):
    data = history[name]
    if len(data) < 2:
        return 'green' if data[-1] == 1 else 'red'
    if data[-1] != data[-2]:
        return 'yellow'
    return 'green' if data[-1] == 1 else 'red'

def get_alerts():
    offline_alerts = []
    for nome, historico in history.items():
        if len(historico) < 24:
            continue
        # Se os últimos 24 pontos estão todos como 0 (fora do ar)
        if all(status == 0 for status in historico[-24:]):
            offline_alerts.append(nome)
    return offline_alerts

def get_status_data():
    current_dt = datetime.now(cuiaba_tz)
    current_time = current_dt.strftime('%H:%M:%S')

    if len(timestamps) >= max_len:
        timestamps.pop(0)
    timestamps.append(current_time)

    for nome, url in sites.items():
        try:
            response = requests.get(url, timeout=5)
            status = 1 if response.status_code == 200 else 0
        except Exception:
            status = 0

        if len(history[nome]) >= max_len:
            history[nome].pop(0)
        history[nome].append(status)

    status_colors = {nome: get_status_color(nome) for nome in ordered_names if nome in sites}
    offline_alerts = get_alerts()

    return {
        "timestamps": timestamps.copy(),
        "data": {nome: history[nome].copy() for nome in ordered_names if nome in sites},
        "status_colors": status_colors,
        "alerts": offline_alerts  # Lista com nomes das unidades fora por mais de 2 minutos
    }
