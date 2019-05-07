import csv
import json
import os

import requests

from django.conf import settings
from django.core.management.base import BaseCommand

from cryptodata.models import Currency, CurrencyExchangePK, Exchange, TickerSymbol


class Command(BaseCommand):
    help = """
    Fetches all available currencies from the exchanges listed in
    settings.EXCHANGES, and saves them to the database, including the 
    CurrencyExchangePK and TickerSymbol of each currency.
    """

    def handle(self, *args, **options):
        for exchange_name in settings.EXCHANGES:
            self.handle_exchange(exchange_name)

    def handle_exchange(self, exchange_name):
        """
        Adds exchange to db, if it doesn't exist already. And adds
        all of the exchange's available currencies to the db,
        including the CurrencyExchangePK and TickerSymbol.
        """
        exchange_instance = self.add_update_exchange_model(exchange_name)
        self.add_exchange_available_currencies_to_db(exchange_instance)

    def add_exchange_available_currencies_to_db(self, exchange_instance):
        """
        Method responsible for adding the data of all currencies
        available on specific exchange to the database.

        BINANCE SPECIFIC INFO:
        As you will see in the code below, Binance data is handled
        somewhat differently.

        Binance doesn't seem to have an api endpoint which serves
        data for all it's individual assets. So instead I will get
        the data from Binance's trading pairs.

        Because each pair_data contains data for two different assets,
        which does not apply to Bittrex and Kraken, I need to split up
        the data for each asset, and than handle it.
        """
        exchange_name = exchange_instance.name
        all_currencies_data = self.return_available_currency_data(
            exchange_name)
        for currency_data in all_currencies_data:
            if exchange_name == 'Binance':
                # For binance, one instance of currency_data will
                # cointain two different currencies to add.
                # so, I will need to handle them both.

                # 1) Split currency_data into two formatted_currency_data
                # versions -> put them in list together.
                formatted_and_split_data = self.return_binance_formatted_data(
                    currency_data)
                # 2) call self.add_currency on each (use for loop)
                for binance_currency_data in formatted_and_split_data:
                    self.add_currency(all_currencies_data,
                                      binance_currency_data, exchange_instance, exchange_name)
            else:
                self.add_currency(all_currencies_data,
                                  currency_data, exchange_instance, exchange_name)

    def split_binance_currency_data(self, currency_data):
        """

        """

    def add_currency(self, all_currencies_data, currency_data, exchange_instance, exchange_name):
        if exchange_name == 'Binance':
            formatted_crrncy_data = currency_data
        else:
            formatted_crrncy_data = self.return_formatted_currency_data(
                all_currencies_data, currency_data, exchange_name)

        currency_name = formatted_crrncy_data['currency_name']
        currency_instance = self.add_update_currency_to_db(
            currency_name, exchange_instance
        )

        currency_exchange_pk = formatted_crrncy_data['currency_exchange_pk']
        self.add_update_currency_exchange_pk_to_db(
            currency_instance,
            exchange_instance,
            currency_exchange_pk
        )

        ticker_symbol = formatted_crrncy_data['ticker_symbol']
        self.add_update_ticker_symbol_to_db(
            currency_name, currency_instance, ticker_symbol)

    def return_formatted_currency_data(self, all_currencies_data, currency_data, exchange_name):
        """
        Takes raw data of one single currency, returns data in
        specific format (see format below).

        This makes further handling of the data more easy/convenient,
        and helps prevent repeating code.

        Returned format:
        {
            'currency_exchange_pk': ...,
            'currency_name': ...,
            'ticker_symbol': ...,
        }
        """
        if exchange_name == 'Bittrex':
            return self.return_bittrex_formatted_data(currency_data)
        if exchange_name == 'Kraken':
            return self.return_kraken_formatted_data(all_currencies_data, currency_data)

    def return_binance_formatted_data(self, currency_data):
        exchange_name = 'Binance'
        currency_exchange_pk_base = ticker_symbol_base = currency_data['baseAsset']
        currency_exchange_pk_quote = ticker_symbol_quote = currency_data['quoteAsset']
        return[
            {
                'currency_exchange_pk': currency_exchange_pk_base,
                'currency_name': self.get_currency_name(exchange_name, ticker_symbol_base),
                'ticker_symbol': ticker_symbol_base,
            },
            {
                'currency_exchange_pk': currency_exchange_pk_quote,
                'currency_name': self.get_currency_name(exchange_name, ticker_symbol_quote),
                'ticker_symbol': ticker_symbol_quote,
            }
        ]

    def return_bittrex_formatted_data(self, currency_data):
        return {
            'currency_exchange_pk': currency_data['Currency'],
            'currency_name': currency_data['CurrencyLong'],
            'ticker_symbol': currency_data['Currency'],
        }

    def return_kraken_formatted_data(self, all_data_dict, currency_data_key):
        ticker_symbol = all_data_dict[currency_data_key]['altname']
        return {
            'currency_exchange_pk': currency_data_key,
            'currency_name': self.get_currency_name('Kraken', ticker_symbol, currency_data_key),
            'ticker_symbol': ticker_symbol,
        }

    def return_available_currency_data(self, exchange_name):
        url = self.get_exchange_url(exchange_name)
        response = requests.get(url)
        data = json.loads(response.text)

        if exchange_name == 'Binance':
            currency_data = data['symbols']
        elif exchange_name == 'Bittrex' or 'Kraken':
            currency_data = data['result']

        return currency_data

    def get_exchange_url(self, exchange_name):
        if exchange_name == 'Binance':
            return 'https://api.binance.com/api/v1/exchangeInfo'
        if exchange_name == 'Bittrex':
            return 'https://api.bittrex.com/api/v1.1/public/getcurrencies'
        if exchange_name == 'Kraken':
            return 'https://api.kraken.com/0/public/Assets'

    def get_currency_name(self, exchange_name, ticker_symbol, currency_exchange_pk=None):
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
        if exchange_name == 'Kraken':
            name = self.get_kraken_currency_name(currency_exchange_pk)
            if name:
                return name

        return self.get_currency_name_from_user(exchange_name, ticker_symbol)

    def get_kraken_currency_name(self, currency_exchange_pk):
        file_path = os.path.join(
            settings.BASE_DIR, 'cryptodata/management/commands/utils/kraken_asset_code_to_name.csv')

        with open(file_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                asset_code = row[0]
                asset_name = row[1]
                if asset_code == currency_exchange_pk:
                    return asset_name

        return None

    def get_currency_name_from_user(self, exchange_name, ticker_symbol):

        while True:
            user_input = input(f"""\n
            {exchange_name} doesn't provide a name for the currency
            with the following ticker symbol:

            {ticker_symbol}

            please provide the name of the currency:

            input name > 
            """)
            if user_input:
                return user_input
            else:
                print("\nNo input detected, please try again.\n")

    def add_update_currency_to_db(self, currency_name, exchange_instance):
        """
        Adds or updates one currency in db.
        """
        currency_instance_queryset = Currency.objects.filter(
            name=currency_name)

        if currency_instance_queryset.exists():
            currency_instance = currency_instance_queryset[0]
        else:
            currency_instance = Currency()
            currency_instance.name = currency_name
            currency_instance.save()

        currency_instance.exchanges.add(exchange_instance)

        return currency_instance

    def add_update_currency_exchange_pk_to_db(self, currency_instance, exchange_instance, key):
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

    def add_update_ticker_symbol_to_db(self, currency_name, currency_instance, ticker_symbol):
        ticker_symbol_queryset = TickerSymbol.objects.filter(
            symbol=ticker_symbol)

        if not ticker_symbol_queryset.exists():
            new_instance = TickerSymbol()
            new_instance.currency = currency_instance
            new_instance.symbol = ticker_symbol
            new_instance.save()
