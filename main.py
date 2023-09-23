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

def generate_signals(df):
    signals = []
    for i in range(1, len(df)):
        # Buy Signal: Short MA crosses above Long MA
        if df['short_ma'].iloc[i] > df['long_ma'].iloc[i] and df['short_ma'].iloc[i - 1] <= df['long_ma'].iloc[i - 1]:
            signals.append(('buy', df.index[i]))
        # Sell Signal: Short MA crosses below Long MA
        elif df['short_ma'].iloc[i] < df['long_ma'].iloc[i] and df['short_ma'].iloc[i - 1] >= df['long_ma'].iloc[i - 1]:
            signals.append(('sell', df.index[i]))
    return signals

# Get trading signals
signals = generate_signals(historical_data)

def create_order(symbol, type, side, amount, price):
    order = binance.create_order(
        symbol=symbol,
        type=type,
        side=side,
        amount=amount,
        price=price
    )
    return order

# Example: Create a limit buy order for 0.01 BTC at a price of $40,000
# create_order('BTC/USDT', 'limit', 'buy', 0.01, 40000)
