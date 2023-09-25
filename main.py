import pandas as pd
import requests
from trading_bot import sign_and_send_request


def fetch_historical_data(symbol, interval):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}'
    response = requests.get(url)
    if response.status_code == 200:
        klines = response.json()
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'trades_count', 'taker_buy_base', 'taker_buy_quote', 'ignored'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        print(df.head())  # вывод первых строк DataFrame
        return df[['open', 'high', 'low', 'close', 'volume']]  # возвращение только выбранных столбцов
    else:
        print(f'Failed to retrieve data: {response.content}')
        return pd.DataFrame()

def calculate_moving_averages(df):
    df['short_ma'] = df['close'].rolling(window=20).mean()  # краткосрочное скользящее среднее
    df['long_ma'] = df['close'].rolling(window=50).mean()   # долгосрочное скользящее среднее
    return df  # возвращение DataFrame с новыми столбцами

def generate_signals(df, last_signal=None):
    signals = []
    for i in range(1, len(df)):
        if last_signal != 'buy' and df['short_ma'].iloc[i] > df['long_ma'].iloc[i] and df['short_ma'].iloc[i - 1] <= df['long_ma'].iloc[i - 1]:
            signals.append(('buy', df.index[i]))
        elif last_signal != 'sell' and df['short_ma'].iloc[i] < df['long_ma'].iloc[i] and df['short_ma'].iloc[i - 1] >= df['long_ma'].iloc[i - 1]:
            signals.append(('sell', df.index[i]))
    return signals


def create_order(symbol, type, side, amount, price, stop_price=None):
    params = {
        'symbol': symbol,
        'side': side,
        'type': type,
        'timeInForce': 'GTC',
        'quantity': amount,
        'price': price,
    }
    if stop_price:
        params['stopPrice'] = stop_price
    return sign_and_send_request(params)  # отправка запроса для создания заказа и возвращение ответа


def backtest(data, capital, generate_signals_function):
    position = 0
    last_signal = None
    for i in range(1, len(data)):
        df_slice = data.iloc[:i]
        signals = generate_signals_function(df_slice, last_signal)
        for signal, date in signals:
            if signal == 'buy':
                # Convert string to float before division
                position = capital / float(df_slice['close'].iloc[-1])
                last_signal = 'buy'
            elif signal == 'sell':
                # Convert string to float before multiplication
                capital = position * float(df_slice['close'].iloc[-1])
                last_signal = 'sell'
        print(f'Capital at {df_slice.index[-1]}: {capital}')
    return capital

# получение исторических данных, расчет скользящих средних, генерация сигналов и проведение бектеста
historical_data = fetch_historical_data('BTCUSDT', '1d')
historical_data = calculate_moving_averages(historical_data)
signals = generate_signals(historical_data)
backtest_result = backtest(historical_data, 10000, generate_signals)
print(f"Результат бектеста: {backtest_result}")

