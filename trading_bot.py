import ccxt
import os
from dotenv import load_dotenv

# Загрузите переменные окружения из файла .env
load_dotenv()

# Получите ваши учетные данные Binance из переменных окружения
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

# Initialize Binance API client
binance = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret
})
