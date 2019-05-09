import json
import requests

from django.conf import settings
from django.core.management.base import BaseCommand

from cryptodata.models import Currency, Exchange, TradingPair, TradingPairExchangePK

from ._utils import determine_str_or_int, return_currency_instance_from_exchange_pk


class Command(BaseCommand):
    help = """
    Fetches all available trading pairs for each of the
    exchanges in the Django main settings, and saves each
    trading pair to the database.

    Besides the pair, also saves the pair's key that is being
    used for the exchange's api.
    """

    def handle(self, *args, **kwargs):

        for exchange_name in settings.EXCHANGES:
            exchange_instance = Exchange.objects.get(name=exchange_name)
            # Fetch raw trading pairs data of current exchange
            all_pair_raw_data = self.return_api_pair_data(exchange_name)
            # Loop over each pair (raw data)
            for raw_pair_data in all_pair_raw_data:
                # Standardize data format
                formatted_pair_data = self.standardize_pair_data_format(
                    all_pair_raw_data, exchange_name, raw_pair_data)
                # Save / update TradingPair to DB
                trading_pair_instance = self.save_trading_pair(
                    formatted_pair_data)
                # Save / update TradingPairExchangePK to DB
                self.save_trading_pair_exchange_pk(
                    exchange_instance, formatted_pair_data, trading_pair_instance)

    def return_api_pair_data(self, exchange_name):
        endpoint = self.return_api_endpoint(exchange_name)
        response = requests.get(endpoint)
        parsed_response = json.loads(response.text)

        if exchange_name == 'Binance':
            all_pair_raw_data = parsed_response['symbols']
        elif exchange_name == 'Bittrex' or 'Kraken':
            all_pair_raw_data = parsed_response['result']

        return all_pair_raw_data

    def return_api_endpoint(self, exchange_name):
        if exchange_name == 'Binance':
            return 'https://api.binance.com/api/v1/exchangeInfo'
        if exchange_name == 'Bittrex':
            return 'https://api.bittrex.com/api/v1.1/public/getmarkets'
        if exchange_name == 'Kraken':
            return 'https://api.kraken.com/0/public/AssetPairs'

    def standardize_pair_data_format(self, all_pair_raw_data, exchange_name, raw_data):
        """
        Formats the raw data into the format shown below,
        then returns the formatted data.

        {
            'currency1_instance': ...,
            'currency2_instance': ...,
            'exchange_instance': ...,
            'exchange_pk': ...,
        }
        """
        exchange_instance = Exchange.objects.get(name=exchange_name)
        if exchange_name == 'Binance':
            formatted_data = self.standardize_binance_data(
                exchange_instance, raw_data)
        if exchange_name == 'Bittrex':
            formatted_data = self.standardize_bittrex_data(
                exchange_instance, raw_data)
        if exchange_name == 'Kraken':
            pair_key = raw_data
            formatted_data = self.standardize_kraken_data(
                all_pair_raw_data, exchange_instance, pair_key)

        return formatted_data

    def standardize_binance_data(self, exchange_instance, raw_data):
        currency1_exchange_pk = raw_data['baseAsset']
        currency2_exchange_pk = raw_data['quoteAsset']
        currency1_instance = return_currency_instance_from_exchange_pk(
            currency1_exchange_pk, exchange_instance)
        currency2_instance = return_currency_instance_from_exchange_pk(
            currency2_exchange_pk, exchange_instance)
        exchange_pk = raw_data['symbol']

        formatted_data = {
            'currency1_instance': currency1_instance,
            'currency2_instance': currency2_instance,
            'exchange_instance': exchange_instance,
            'exchange_pk': exchange_pk,
        }
        return formatted_data

    def standardize_bittrex_data(self, exchange_instance, raw_data):
        currency1_exchange_pk = raw_data['MarketCurrency']
        currency2_exchange_pk = raw_data['BaseCurrency']
        currency1_instance = return_currency_instance_from_exchange_pk(
            currency1_exchange_pk, exchange_instance)
        currency2_instance = return_currency_instance_from_exchange_pk(
            currency2_exchange_pk, exchange_instance)
        exchange_pk = raw_data['MarketName']

        formatted_data = {
            'currency1_instance': currency1_instance,
            'currency2_instance': currency2_instance,
            'exchange_instance': exchange_instance,
            'exchange_pk': exchange_pk,
        }
        return formatted_data

    def standardize_kraken_data(self, all_pair_raw_data, exchange_instance, pair_key):
        currency1_exchange_pk = all_pair_raw_data[pair_key]['base']
        currency2_exchange_pk = all_pair_raw_data[pair_key]['quote']
        currency1_instance = return_currency_instance_from_exchange_pk(
            currency1_exchange_pk, exchange_instance)
        currency2_instance = return_currency_instance_from_exchange_pk(
            currency2_exchange_pk, exchange_instance)
        exchange_pk = pair_key
        formatted_data = {
            'currency1_instance': currency1_instance,
            'currency2_instance': currency2_instance,
            'exchange_instance': exchange_instance,
            'exchange_pk': exchange_pk,
        }
        return formatted_data

    def save_trading_pair(self, trading_pair_data):
        currency1_instance = trading_pair_data['currency1_instance']
        currency2_instance = trading_pair_data['currency2_instance']
        exchange_instance = trading_pair_data['exchange_instance']
        trading_pair = None
        try:
            trading_pair = TradingPair.objects.get(
                currency1=currency1_instance.id, currency2=currency2_instance.id)
        except TradingPair.DoesNotExist:
            pass

        if trading_pair:
            trading_pair.exchanges.add(exchange_instance)
            return trading_pair
        else:
            new_instance = TradingPair()
            new_instance.currency1 = currency1_instance
            new_instance.currency2 = currency2_instance
            new_instance.save()
            new_instance.exchanges.add(exchange_instance)

            return new_instance

    def save_trading_pair_exchange_pk(self, exchange_instance, trading_pair_data, trading_pair_instance):
        key = trading_pair_data['exchange_pk']
        exchange_pk_instance = None
        try:
            exchange_pk_instance = TradingPairExchangePK.objects.get(
                exchange=exchange_instance.id, key=key, trading_pair=trading_pair_instance.id)
        except TradingPairExchangePK.DoesNotExist:
            pass

        if not exchange_pk_instance:
            new_instance = TradingPairExchangePK()
            new_instance.trading_pair = trading_pair_instance
            new_instance.exchange = exchange_instance
            new_instance.key = key
            key_type = determine_str_or_int(key)
            new_instance.key_type = key_type.upper()
            new_instance.save()
