from binance.client import Client

# Замените 'your_api_key' и 'your_api_secret' на свои ключи API.
client = Client(api_key='your_api_key', api_secret='your_api_secret')

# Проверка подключения
print(client.get_system_status())
