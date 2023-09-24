import pandas as pd
from trading_bot import binance as client

# Проверка подключения (метод fetch_time не является стандартным методом ccxt, но можно использовать его, если биржа поддерживает)
# Если Binance не поддерживает fetch_time, вы можете просто пропустить этот шаг
try:
    timestamp = client.fetch_time()
    print(f"Время биржи: {timestamp}")
except Exception as e:
    print(f"Не удалось получить время биржи: {e}")

def fetch_historical_data(symbol, timeframe):
    # Используйте уже импортированный client, а не создавайте новый экземпляр binance
    ohlcv = client.fetch_ohlcv(symbol, timeframe)
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

def create_order(symbol, type, side, amount, price, stop_price=None):
    """
    Создает ордер на бирже.

    Параметры:
        symbol (str): Тикер торгуемой пары (например, 'BTC/USDT').
        type (str): Тип ордера ('LIMIT', 'MARKET', 'STOP_LOSS_LIMIT', и т.д.).
        side (str): Сторона ордера ('buy' или 'sell').
        amount (float): Количество актива для покупки/продажи.
        price (float): Цена, по которой предполагается выполнить ордер.
        stop_price (float, optional): Цена стоп-лосса. Только для типа 'STOP_LOSS_LIMIT'.

    Возвращает:
        dict: Информация об ордере.
    """
    params = {}
    if stop_price:
        params['stopPrice'] = stop_price

    order = binance.create_order(
        symbol=symbol,
        type=type,
        side=side,
        amount=amount,
        price=price,
        params=params
    )
    return order


# Example: Create a stop-limit sell order
# create_order('BTC/USDT', 'STOP_LOSS_LIMIT', 'sell', 0.01, 38000, stop_price=39000)


# Пример кода для базового бэктестирования
def backtest(data, capital, strategy):
    """
    Производит бэктестирование стратегии на исторических данных.

    Параметры:
        data (DataFrame): Исторические данные с ценами.
        capital (float): Начальный капитал.
        strategy (function): Функция стратегии торговли.

    Возвращает:
        float: Конечное значение капитала после торговли.
    """
    cash = capital
    position = 0
    for i in range(len(data)):
        signal = strategy(data.iloc[:i])
        price = data['close'].iloc[i]
        if signal == 'buy' and cash >= price:
            position += cash // price
            cash -= position * price
        elif signal == 'sell' and position > 0:
            cash += position * price
            position = 0
    final_value = cash + position * (data['close'].iloc[-1] if position > 0 else 0)
    return final_value


# Бэктестирование вашего бота
backtest(historical_data, 10000, generate_signals)
