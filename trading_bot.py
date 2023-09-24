# trading_bot.py
import ccxt
import os
from dotenv import load_dotenv

# Загрузите переменные окружения из файла .env
load_dotenv()

# Получите ваши учетные данные Binance из переменных окружения
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

# Инициализируйте клиент Binance API с поддержкой Testnet
binance = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,  # важно, чтобы избежать блокировки из-за слишком частых запросов
    'options': {
        'defaultType': 'future'  # если вы планируете торговать на фьючерсном рынке
    },
    'urls': {
        'api': {
            'public': 'https://testnet.binance.vision/api/v3',
            'private': 'https://testnet.binance.vision/api/v3',
        }
    }
})
