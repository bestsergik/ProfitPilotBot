import pandas as pd
from trading_bot import sign_and_send_request

def fetch_historical_data(symbol, interval):
    params = {
        'symbol': symbol,
        'interval': interval,
    }
    response = sign_and_send_request(params)  # отправка запроса на получение исторических данных
    klines = response.get('klines', [])  # извлечение данных свечей из ответа
    # конвертация данных в DataFrame и установка временных меток в качестве индекса
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                       'quote_asset_volume', 'trades_count', 'taker_buy_base', 'taker_buy_quote',
                                       'ignored'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df[['open', 'high', 'low', 'close', 'volume']]  # возвращение только выбранных столбцов

def calculate_moving_averages(df):
    df['short_ma'] = df['close'].rolling(window=20).mean()  # краткосрочное скользящее среднее
    df['long_ma'] = df['close'].rolling(window=50).mean()   # долгосрочное скользящее среднее
    return df  # возвращение DataFrame с новыми столбцами


def generate_signals(df):
    signals = []  # список для хранения сигналов
    # проход по данным и проверка условий для генерации сигналов покупки/продажи
    for i in range(1, len(df)):
        if df['short_ma'].iloc[i] > df['long_ma'].iloc[i] and df['short_ma'].iloc[i - 1] <= df['long_ma'].iloc[i - 1]:
            signals.append(('buy', df.index[i]))
        elif df['short_ma'].iloc[i] < df['long_ma'].iloc[i] and df['short_ma'].iloc[i - 1] >= df['long_ma'].iloc[i - 1]:
            signals.append(('sell', df.index[i]))
    return signals  # возвращение списка сигналов


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


def backtest(data, capital, strategy):
    cash = capital  # начальный капитал
    position = 0  # текущая позиция
    for i in range(len(data)):
        signal = strategy(data.iloc[:i])  # получение сигнала от стратегии
        price = data['close'].iloc[i]  # текущая цена закрытия
        # выполнение действий в зависимости от сигнала
        if signal == 'buy' and cash >= price:
            position += cash // price
            cash -= position * price
        elif signal == 'sell' and position > 0:
            cash += position * price
            position = 0
    final_value = cash + position * (data['close'].iloc[-1] if position > 0 else 0)  # итоговая стоимость портфеля
    return final_value  # возвращение итоговой стоимости


# получение исторических данных, расчет скользящих средних, генерация сигналов и проведение бектеста
historical_data = fetch_historical_data('BTCUSDT', '1d')
historical_data = calculate_moving_averages(historical_data)
signals = generate_signals(historical_data)
backtest_result = backtest(historical_data, 10000, generate_signals)
print(f"Результат бектеста: {backtest_result}")

