# from tortoise import Tortoise
#
# from app.models import CurrencyPair
#
#
# async def create_currency_pair(base_currency: str, quote_currency: str):
#     existing_pair = await CurrencyPair.get_or_none(base_currency=base_currency, quote_currency=quote_currency)
#     if existing_pair:
#         print(f'Пара валют уже существует: {existing_pair.base_currency}/{existing_pair.quote_currency}')
#     else:
#         new_pair = await CurrencyPair.create(base_currency=base_currency, quote_currency=quote_currency)
#         print(f'Создана пара валют: {new_pair.base_currency}/{new_pair.quote_currency}')
#
#
# async def main():
#     await Tortoise.init(
#         db_url='postgres://username:password@localhost:5432/crypto_monitor',
#         modules={'models': ['models']}
#     )
#     await Tortoise.generate_schemas()
#
#     # Создание валютных пар
#     await create_currency_pair('BTC', 'USDT')
#     await create_currency_pair('BTC', 'ETH')
#     await create_currency_pair('BTC', 'XMR')
#     await create_currency_pair('SOL', 'BTC')
#     await create_currency_pair('BTC', 'RUB')
#     await create_currency_pair('DOGE', 'BTC')  # Эта строка теперь будет работать корректно
#
#     await Tortoise.close_connections()








import asyncio
from tortoise import Tortoise
from app.config import TORTOISE_ORM
from app.models import CurrencyPair
from app.tasks import check_price  # Импортируем только нужную функцию
from app.utils import fetch_price_from_binance, fetch_price_from_bybit, fetch_price_from_gateio


async def init():
    print("Инициализация базы данных")
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    await create_initial_pairs()


async def create_initial_pairs():
    print("Создание начальных пар валют")
    pairs = [
        {"base_currency": "BTC", "quote_currency": "USDT"},
        {"base_currency": "BTC", "quote_currency": "ETH"},
        {"base_currency": "BTC", "quote_currency": "XMR"},
        {"base_currency": "SOL", "quote_currency": "BTC"},
        {"base_currency": "BTC", "quote_currency": "RUB"},
        {"base_currency": "DOGE", "quote_currency": "BTC"},
    ]
    for pair in pairs:
        try:
            currency_pair, created = await CurrencyPair.get_or_create(
                base_currency=pair['base_currency'],
                quote_currency=pair['quote_currency']
            )
            if created:
                print(f"Создана пара валют: {pair['base_currency']}/{pair['quote_currency']}")
            else:
                print(f"Пара валют уже существует: {pair['base_currency']}/{pair['quote_currency']}")
        except Exception as e:
            print(f"Ошибка при создании валютной пары {pair}: {e}")


async def check_prices_for_pair(pair):
    binance_price = await fetch_price_from_binance(pair)
    bybit_price = await fetch_price_from_bybit(pair)
    gateio_price = await fetch_price_from_gateio(pair)

    prices = [binance_price, bybit_price, gateio_price]
    best_price = max(prices)
    return best_price


async def run_monitoring():
    print("Запуск мониторинга цен")
    pairs = [
        'BTCUSDT',
        'ETHBTC',
        'XMRBTC',
        'SOLBTC',
        'BTCRUB',
        'DOGEBTC']
    old_prices = [27000.0, 0.04, 0.002287, 0.002366, 3900027.0, 1.73e-06]   # Задай стартовые цены
    for pair, old_price in zip(pairs, old_prices):
        print("Проверка цены для пары")
        await check_price(pair, old_price)


async def main():
    await init()
    while True:
        await run_monitoring()
        await asyncio.sleep(60)

if __name__ == '__main__':
    print("Запуск программы")
    asyncio.run(main())
