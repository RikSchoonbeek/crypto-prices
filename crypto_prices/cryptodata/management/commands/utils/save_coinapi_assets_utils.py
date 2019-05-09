import json
import requests

from django.conf import settings

from cryptodata.models import Currency, Exchange, TickerSymbol


def check_currency_exists(currency_data):
    """
    Checks if currency exist by checking if it's ticker symbol exists.

    If ticker symbol doesn't exist, this means that the currency
    also doesnt, and vice versa.
    """
    ticker_symbol_instance = None
    ticker_symbol = currency_data['asset_id']
    try:
        ticker_symbol_instance = TickerSymbol.objects.get(symbol=ticker_symbol)
    except TickerSymbol.DoesNotExist:
        pass

    currency_exists = bool(ticker_symbol_instance)
    return currency_exists


def create_currency(currency_data):
    instance = Currency()
    instance.name = currency_data['name']
    instance.save()
    return instance


def create_ticker_symbol(currency_data, currency_instance):
    instance = TickerSymbol()
    instance.symbol = currency_data['asset_id']
    instance.currency = currency_instance
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
