# trading_bot.py
import requests
import time
import base64
from dotenv import load_dotenv
import os
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ed25519

# Загрузите переменные окружения из файла .env
load_dotenv()

# Получите ваши учетные данные Binance из переменных окружения
api_key = os.getenv('BINANCE_API_KEY')    # получение API-ключа Binance
private_key_path = os.getenv('PRIVATE_KEY_PATH')    # получение пути к файлу с приватным ключом

# Загрузите приватный ключ
with open(private_key_path, 'rb') as f:     # открытие файла с приватным ключом в бинарном режиме
    private_key = load_pem_private_key(data=f.read(), password=None)   # загрузка приватного ключа из файла


def sign_and_send_request(params):
    # Установите временную метку для запроса
    timestamp = int(time.time() * 1000)  # получение текущего времени в миллисекундах
    params['timestamp'] = timestamp  # добавление временной метки в параметры запроса

    # Подготовьте полезную нагрузку для подписи
    payload = '&'.join([f'{param}={value}' for param, value in params.items()])  # формирование строки параметров запроса

    # Подпишите запрос
    signature = private_key.sign(payload.encode('ASCII'))   # подпись строки параметров с использованием приватного ключа
    params['signature'] = base64.b64encode(signature).decode()   # кодирование подписи в base64 и добавление к параметрам запроса

    # Установите заголовки
    headers = {
        'X-MBX-APIKEY': api_key,   # добавление API-ключа в заголовки запроса
    }

    # Отправьте запрос
    response = requests.post(
        'https://testnet.binance.vision/api/v3/order',    # URL конечной точки для отправки запроса
        headers=headers,    # добавление заголовков к запросу
        data=params,   # добавление параметров к запросу
    )
    return response.json() # возвращение ответа от сервера в формате JSON


