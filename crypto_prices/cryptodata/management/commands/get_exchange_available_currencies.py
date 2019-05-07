import json

import requests

from django.conf import settings
from django.core.management.base import BaseCommand

from cryptodata.models import Currency, CurrencyExchangePK, Exchange, TickerSymbol


class Command(BaseCommand):
    help = """
    Fetches data from specified exchanges and saves data to database.
    
    Data that is fetched:
    - Available cryptocurrencies
    - Ticker symbols for each currency
    - Currency name (if not available, this is retrieved from
      another source)
    - Tradable pairs on specific exchange
    """

    def handle(self, *args, **options):
        for exchange_name in settings.EXCHANGES:
            self.handle_exchange(exchange_name)

    def handle_exchange(self, exchange_name):
        """

        """
        self.add_exchange_available_currencies_to_db()

    def add_exchange_available_currencies_to_db(self):
        """
        """
        all_currency_data = self.fetch_available_currency_data(url)

    def direct_to_exchange_specific_handling(self, exchange_name):
        """
        Directs the flow of the program based on which exchange is being
        handled currently.

        Each exchange has it's own unique api calls and returned data
        format, and thus, requires it's own way of handling.
        """
        if exchange_name is "Kraken":
            self.add_or_update_kraken_currencies(exchange_name)

    def add_or_update_kraken_currencies(self, exchange_name):
        """

        """
        kraken_model_instance = self.add_update_exchange_model(exchange_name)

        url = 'https://api.kraken.com/0/public/Assets'
        all_currency_data = self.fetch_available_currency_data(url)

        for one_currency_data in all_currency_data:
            # get all needed available data from one_currency_data
            # and output it in a new format, like so:

            # {
            #   'currency_exchange_pk': ...,
            #   'currency_name': ...,
            #   'ticker_symbol': ...,
            # }

            # Why? So that I can make this part unique for each exchange,
            # and make the rest of the code / methods equal for each
            # exchange, this prevents repetition of code

            formatted_currency_data = self.get_formatted_currency_data(
                one_currency_data, all_currency_data)

            ticker_symbol = currency_data[currency_exchange_pk]['altname']
            currency_name = self.get_currency_name(ticker_symbol)

            currency_instance = self.add_update_currency_model(
                currency_name, kraken_model_instance)

            self.add_update_currency_exchange_pk(
                currency_instance, kraken_model_instance, currency_exchange_pk)

            self.add_update_ticker_symbol(
                currency_name, currency_instance, ticker_symbol)

    def get_formatted_currency_data(self, one_currency_data, all_currency_data):
        """
        """
        if

    def fetch_available_currency_data(self, exchange_name):
        url = self.get_exchange_available_currencies_url(exchange_name)
        response = requests.get(url)
        data = json.loads(response.text)
        currency_data = data['result']
        return currency_data

    def get_exchange_available_currencies_url(self, exchange_name):
        if exchange_name == 'Bittrex':
            return 'https://api.bittrex.com/api/v1.1/public/getcurrencies'
        if exchange_name == 'Kraken':
            return 'https://api.kraken.com/0/public/Assets'

    def add_update_currency_data_to_db(self, currency_data, exchange_model_instance):
        """
        """
        for currency_exchange_pk in currency_data:
            ticker_symbol = self.get_ticker_symbol(
                currency_data, exchange_model_instance)
            currency_name = self.get_currency_name(ticker_symbol)

            currency_instance = self.add_update_currency_model(
                currency_name, kraken_model_instance)

            self.add_update_currency_exchange_pk(
                currency_instance, kraken_model_instance, currency_exchange_pk)

            self.add_update_ticker_symbol(
                currency_name, currency_instance, ticker_symbol)

    def get_ticker_symbol(self, currency_data, exchange_model_instance, currency_exchange_pk=None):
        exchange_name = exchange_model_instance.name
        if exchange_name == 'Bittrex':
            ticker_symbol = currency_data['Currency']
        if exchange_name == 'Kraken':
            ticker_symbol = currency_data[currency_exchange_pk]['altname']

        return ticker_symbol

    def get_currency_name(self, ticker_symbol):
        """
        Returns currency name.

        First tries to get it from the DB, based on ticker symbol,
        if not found, tries to get it from the user
        """
        ticker_symbol_instance_queryset = TickerSymbol.objects.filter(
            symbol=ticker_symbol)

        if ticker_symbol_instance_queryset.exists():
            ticker_symbol_instance = ticker_symbol_instance_queryset[0]
            currency_name = ticker_symbol_instance.currency.name
            return currency_name
        else:
            return self.get_currency_name_from_user(ticker_symbol)

    def get_currency_name_from_user(self, ticker_symbol):

        while True:
            user_input = input(f"""\n
            The current exchange doesn't provide a name for the currency
            with the following ticker symbol:

            {ticker_symbol}

            please provide the name of the currency:

            input name > 
            """)
            if user_input:
                return user_input
            else:
                print("\nNo input detected, please try again.\n")

    def get_currency_type_from_user(self, currency_name):
        """
        returns True if type is crypto,
        returns False if type is fiat
        """

        while True:
            user_input = input(f"""\n
            Please specify the type of the following currency:

            {currency_name}

            Options:
            a) crypto currency
            b) fiat currency

            input a/b > 
            """).lower()

            if user_input == 'a':
                return True
            elif user_input == 'b':
                return False
            else:
                print(f"""
                Your input was '{user_input}',
                please enter 'a' or 'b'.\n\n
                """)

    def add_update_currency_model(self, currency_name, exchange_instance, currency_type=None):
        """
        Checks if instance for currency exchange exists, if not it adds it.
        """
        # if instance already exists: update (if needed)
        # if instance doesn't exist: create + add data

        # check if currency is already in db by going through the
        # currency's ticker symbol
        currency_instance_queryset = Currency.objects.filter(
            name=currency_name)

        if currency_instance_queryset.exists():
            currency_instance = currency_instance_queryset[0]
        else:
            currency_instance = Currency()
            currency_instance.name = currency_name
            if not currency_type:
                currency_type = self.get_currency_type_from_user(currency_name)
            currency_instance.type_is_crypto = currency_type
            currency_instance.save()

        currency_instance.exchanges.add(exchange_instance)

        return currency_instance

    def add_update_currency_exchange_pk(self, currency_instance, exchange_instance, key):
        currency_exchange_pk_instance_queryset = CurrencyExchangePK.objects.filter(
            key=key)

        if not currency_exchange_pk_instance_queryset.exists():
            new_instance = CurrencyExchangePK()
            new_instance.currency = currency_instance
            new_instance.exchange = exchange_instance
            new_instance.key = key
            new_instance.key_type = self.determine_str_or_int(key).upper()
            new_instance.save()

    def determine_str_or_int(self, variable):
        if type(variable) is str:
            return 'str'
        elif type(variable) is int:
            return 'int'
        else:
            return None

    def add_update_exchange_model(self, exchange_name):
        """
        Checks if instance for current exchange exists, if not it adds it.

        Returns the instance
        """
        try:
            instance = Exchange.objects.get(name=exchange_name)
        except Exchange.DoesNotExist:
            instance = Exchange()
            instance.name = exchange_name
            instance.save()

        return instance

    def add_update_ticker_symbol(self, currency_name, currency_instance, ticker_symbol):
        ticker_symbol_queryset = TickerSymbol.objects.filter(
            symbol=ticker_symbol)

        if not ticker_symbol_queryset.exists():
            new_instance = TickerSymbol()
            new_instance.currency = currency_instance
            new_instance.symbol = ticker_symbol
            new_instance.save()
