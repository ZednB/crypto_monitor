import aiohttp


async def fetch_price_from_binance(pair):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={pair}"
    return await fetch_from_exchange(url)


async def fetch_price_from_bybit(pair):
    url = f"https://api.bybit.com/v2/public/tickers?symbol={pair}"
    return await fetch_from_exchange(url)


async def fetch_price_from_gateio(pair):
    url = f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={pair}"
    return await fetch_from_exchange(url)


async def fetch_from_exchange(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data
