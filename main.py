from binance.client import Client
import ccxt
import pandas as pd

# Замените 'your_api_key' и 'your_api_secret' на свои ключи API.
client = Client(api_key='your_api_key', api_secret='your_api_secret')

# Проверка подключения
print(client.get_system_status())

def fetch_historical_data(symbol, timeframe):
    # Инициализация клиента CCXT для получения исторических данных
    binance = ccxt.binance()
    # Получение исторических OHLCV (Open/High/Low/Close/Volume) данных для заданного символа и таймфрейма
    ohlcv = binance.fetch_ohlcv(symbol, timeframe)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

# Получение исторических данных для BTC/USDT с дневным таймфреймом
historical_data = fetch_historical_data('BTC/USDT', '1D')

def calculate_moving_averages(df):
    df['short_ma'] = df['close'].rolling(window=20).mean()  # Краткосрочное скользящее среднее
    df['long_ma'] = df['close'].rolling(window=50).mean()   # Долгосрочное скользящее среднее
    return df

# Расчет скользящих средних
historical_data = calculate_moving_averages(historical_data)
