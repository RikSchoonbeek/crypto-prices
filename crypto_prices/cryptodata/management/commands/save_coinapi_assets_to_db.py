import json

import requests

from django.conf import settings
from django.core.management.base import BaseCommand

from cryptodata.models import Currency, TickerSymbol


class Command(BaseCommand):
    help = """
    Adds the currencies available at coinapi.io to the database.
    """

    def handle(self, *args, **kwargs):
        currencydata_list = self.fetch_coinapi_currency_data_list()
        for currency_dict in currencydata_list:
            if 'name' not in currency_dict:
                continue
            instance_exists = Currency.objects.filter(
                name=currency_dict['name']).exists()
            if not instance_exists:
                currency_instance = self.create_currency(currency_dict)
                self.create_tickler_symbol(currency_dict, currency_instance)

    def fetch_coinapi_currency_data_list(self):
        url = 'https://rest.coinapi.io/v1/assets'
        headers = {'X-CoinAPI-Key': settings.COINAPI_KEY}
        response = requests.get(url, headers=headers)
        currencydata_list = json.loads(response.text)
        return currencydata_list

    def create_currency(self, currency_data):
        instance = Currency()
        instance.name = currency_data['name']
        is_crypto = True if currency_data['type_is_crypto'] else False
        instance.type_is_crypto = is_crypto
        instance.save()
        return instance

    def create_tickler_symbol(self, currency_data, currency_instance):
        instance = TickerSymbol()
        instance.symbol = currency_data['asset_id']
        instance.currency = currency_instance
        instance.save()
