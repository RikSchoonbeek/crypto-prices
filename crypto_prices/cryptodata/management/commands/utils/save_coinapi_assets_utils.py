import json
import requests

from django.conf import settings

from cryptodata.models import Currency, Exchange


def create_currency(currency_data):
    currency_name = currency_data['name']
    ticker_symbol = currency_data['asset_id']
    instance = None
    try:
        instance = Currency.objects.get(
            name=currency_name, ticker_symbol=ticker_symbol)
    except Currency.DoesNotExist:
        pass

    if not instance:
        instance = Currency()
        instance.name = currency_name
        instance.ticker_symbol = ticker_symbol
        instance.save()

    return instance


def fetch_coinapi_currency_data():
    """
    Fetches data from coinapi api, returns that data.

    Data format:
    [
        {
            "asset_id": "BTC",
            "name": "Bitcoin",
            "type_is_crypto": 1,
            "data_start": "2010-07-17",
            "data_end": "2019-05-08",
            "data_quote_start": "2014-02-24T17:43:05.0000000Z",
            "data_quote_end": "2019-05-08T00:00:00.0000000Z",
            "data_orderbook_start": "2014-02-24T17:43:05.0000000Z",
            "data_orderbook_end": "2019-05-08T00:00:00.0000000Z",
            "data_trade_start": "2010-07-17T23:09:17.0000000Z",
            "data_trade_end": "2019-05-08T00:00:00.0000000Z",
            "data_trade_count": 4196037957,
            "data_symbols_count": 17627
        },
        {
            ...
        },
        ...
    ]
    """
    url = 'https://rest.coinapi.io/v1/assets'
    headers = {'X-CoinAPI-Key': settings.COINAPI_KEY}
    response = requests.get(url, headers=headers)
    currencydata = json.loads(response.text)
    return currencydata
