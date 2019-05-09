from unittest import TestCase

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from cryptodata.models import Currency, CurrencyExchangePK, Exchange, TickerSymbol

from ._utils import return_randomized_indexes_for_model


class Command(BaseCommand):
    help = """
    Since I will be adding new exchanges to the
    get_exchange_available_currencies management command,
    for it to handle adding the currencies for those exchanges to the
    db, I will probably also need to alter the code of that
    management command.

    I want to make sure that the management command keeps doig it's
    work properly. And untill now I have been manually checking if
    it did it's work correctly, but that bacomes tedious.

    So, I write this one, to test if 
    get_exchange_available_currencies has done it's job.
    """

    def handle(self, *args, **options):
        self.stdout.write(
            f"\n# Test get_exchange_available_currencies management command #\n")

        self.empty_tables()
        self.run_save_coinapi_assets_to_db()
        self.run_get_exchange_available_currencies()

        self.perform_tests()

    def empty_tables(self):
        """
        Empty the following tables:
        - Currency
        - CurrencyExchangePK
        - Exchange
        - TickerSymbol
        """
        self.stdout.write(f"\n## Emptying tables - started ##")
        CurrencyExchangePK.objects.all().delete()
        TickerSymbol.objects.all().delete()
        Currency.objects.all().delete()
        Exchange.objects.all().delete()
        self.stdout.write(f"\n## Emptying tables - finished ##")

    def run_save_coinapi_assets_to_db(self):
        self.stdout.write(f"\n## run_save_coinapi_assets_to_db - started ##")
        call_command('save_coinapi_assets_to_db')
        self.stdout.write(f"\n## run_save_coinapi_assets_to_db - finished ##")

    def run_get_exchange_available_currencies(self):
        self.stdout.write(
            f"\n## run_get_exchange_available_currencies - started ##")
        call_command('get_exchange_available_currencies')
        self.stdout.write(
            f"\n## run_get_exchange_available_currencies - finished ##")

    def perform_tests(self):
        self.stdout.write(f"\n\n\n\n# Starting tests #\n")
        # What do I need to test?

        # For each Exchange:

        # Exchange
        # Test if the Exchange is in the DB
        self.test_exchanges()

        # Currency
        self.test_currencies()

    def test_exchanges(self):
        """
        Test if there is a model instance for each of the exchanges
        in settings.Exchanges.

        Test if the amount of exchange instances in the database is
        equal to the amount of exchanges in settings.EXCHANGES.
        """
        self.stdout.write(f"\n## Exchange tests - started ##\n")

        exchange_instances = Exchange.objects.all()
        for exchange_name in settings.EXCHANGES:
            exchange_in_db = self.test_exchange_in_db(
                exchange_name, exchange_instances)
            self.stdout.write(f"- {exchange_name} in db: {exchange_in_db}")

        self.test_exchange_sums(exchange_instances)

    def test_exchange_in_db(self, exchange_name, exchange_instances):
        for exchange_instance in exchange_instances:
            if exchange_instance.name == exchange_name:
                return True
        return False

    def test_exchange_sums(self, exchange_instances):
        self.stdout.write(f"\n### Test sum exchanges ###\n")

        sum_exchanges_in_settings = len(settings.EXCHANGES)
        sum_exchanges_in_db = len(exchange_instances)

        self.stdout.write(
            f"- exchanges in settings: {sum_exchanges_in_settings}")
        self.stdout.write(f"- exchanges in db: {sum_exchanges_in_db}")

    def test_currencies(self):
        self.stdout.write(f"\n\n\n\n## Currency tests - started ##\n")

        # Loop over currencies in random order
        # Untill a minimum of 5 currencies are found,
        # for each exchange, which have that exchange in
        # Currency.exchanges
        min_amount = 5
        self.test_min_amount_currencies_for_each_exchange(min_amount)

        # get 10 currencies that have a related exchange
        instances_amount = 15 + (len(settings.EXCHANGES) * 3)
        currency_instances = self.get_currencies_with_exchange(
            instances_amount)
        # Test if each Currency has a CurrencyExchangePK for each
        # exchange in currency.exchanges
        self.test_currencies_exchange_pks_mirror_currency_exchanges(
            currency_instances)

        # Test if this Currency has a TickerSymbol
        self.test_ticker_symbols()

    def test_min_amount_currencies_for_each_exchange(self, min_amount):
        """
        Tests if there are a minimum of min_amount currencies
        for each exchange.
        """
        self.stdout.write(
            f"\n### Test if min min_amount currencies for each exchange - started ###\n")

        currency_instances = Currency.objects.all()

        exchange_currency_count_dict = self.create_exchange_currency_count_dict()
        randomized_indexes = return_randomized_indexes_for_model(Currency)

        for index in randomized_indexes:
            currency_instance = currency_instances[index]
            exchange_currency_count_dict = self.update_exchange_count(
                currency_instance, exchange_currency_count_dict, min_amount)

            if self.check_all_exchanges_hit_min_amount(exchange_currency_count_dict):
                break

        self.display_min_min_amount_test_results(exchange_currency_count_dict)

    def create_exchange_currency_count_dict(self):
        count_dict = {}
        for exchange_name in settings.EXCHANGES:
            count_dict[exchange_name] = {
                'count': 0,
                'has_hit_min_amount': False,
            }

        return count_dict

    def update_exchange_count(self, currency_instance, exchange_currency_count_dict, min_amount):
        """
        Takes a currency, the exchange_currency_count_dict, and a
        minimum amount of currencys that needs to be found for
        each exchange.

        Adds +1 to count of each exchange that is in the currency's
        exchanges (ManyToManyField).

        Also tests if the exchange has hit min_amount. If so, the exchange's
        'has_hit_min_amount' is set to True.
        """
        exchange_set = currency_instance.exchanges.all()
        for exchange_instance in exchange_set:
            exchange_name = exchange_instance.name
            if exchange_name in exchange_currency_count_dict:
                current_count = exchange_currency_count_dict[exchange_name]['count']
                new_count = current_count + 1
                exchange_currency_count_dict[exchange_name]['count'] = new_count

                if new_count == min_amount:
                    exchange_currency_count_dict[exchange_name]['has_hit_min_amount'] = True

        return exchange_currency_count_dict

    def check_all_exchanges_hit_min_amount(self, exchange_currency_count_dict):
        """
        Returns False if any of the exchanges hasn't hit min_amount yet,
        else returns True.
        """
        for exchange_name in exchange_currency_count_dict:
            if not exchange_currency_count_dict[exchange_name]['has_hit_min_amount']:
                return False

        return True

    def display_min_min_amount_test_results(self, exchange_currency_count_dict):
        self.stdout.write(f"\n### Results: ###\n")
        for exchange_name in exchange_currency_count_dict:
            has_hit_min_amount = exchange_currency_count_dict[exchange_name]['has_hit_min_amount']
            self.stdout.write(
                f"- {exchange_name}: has_hit_min_amount: {has_hit_min_amount}")

    def get_currencies_with_exchange(self, amount):
        randomized_indexes = return_randomized_indexes_for_model(Currency)
        currency_instances = Currency.objects.all()

        filtered_currency_instances = []

        for index in randomized_indexes:
            currency_instance = currency_instances[index]
            exchange_count = currency_instance.exchanges.all().count()
            if exchange_count:
                filtered_currency_instances.append(currency_instance)
                if len(filtered_currency_instances) == amount:
                    return filtered_currency_instances

    def test_currencies_exchange_pks_mirror_currency_exchanges(self, currency_instances):
        """
        This method will test all given currency instances for 
        the following:

        If the Currency instance's CurrencyExchangePKs match
        the Currency's exchanges in a symmetrical way.

        Example to bring more clarity:

        If a Currency instance has the following related
        (ManyToMany) exchanges: 'Binance' and 'Kraken', then
        it should also have related CurrencyExchangePKs for
        both 'Binance' and 'Kraken'.

        But more specifically it should ONLY have
        CurrencyExchangePKs for 'Binance' and 'Kraken', no more
        and no less. Since those are the only two (ManyToMany)
        related exchanges of the Currency instance.
        """
        self.stdout.write(
            f"\n\n\n\n## test_currencies_exchange_pks_mirror_currency_exchanges - started ##\n")

        passed_currencies = []
        failed_currencies = []
        for currency_instance in currency_instances:
            crncy_exchng_names = self.return_crncy_exchng_names(
                currency_instance)
            crncy_exchng_pks_exchng_names = self.return_crncy_exchng_pks_exchng_names(
                currency_instance)
            if crncy_exchng_names == crncy_exchng_pks_exchng_names:
                passed_currencies.append(currency_instance)
            else:
                failed_currencies.append(currency_instance)

        self.display_exchange_pks_mirror_currency_exchanges_results(
            failed_currencies, passed_currencies)

    def return_crncy_exchng_names(self, currency_instance):
        """
        Takes currency instance, returns list of names
        of the currency_instance.exchanges.
        """
        name_set = {exch.name for exch in currency_instance.exchanges.all()}
        return name_set

    def return_crncy_exchng_pks_exchng_names(self, currency_instance):
        """
        Takes currency instance, returns list of names
        of exchanges of each related CurrencyExchangePK.exchange.
        """
        exchange_pks = currency_instance.currencyexchangepk_set.all()
        name_set = set()
        for exchange_pk in exchange_pks:
            name_set.add(exchange_pk.exchange.name)

        return name_set

    def display_exchange_pks_mirror_currency_exchanges_results(self, failed_currencies, passed_currencies):
        self.stdout.write(f"\n### Results: ###\n")

        self.stdout.write(f"\n### Passed: ###\n")
        if len(passed_currencies) > 0:
            for instance in passed_currencies:
                self.stdout.write(f"- {instance.name}")
        else:
            self.stdout.write(f"- No currencies passed")

        self.stdout.write(f"\n### Failed: ###\n")
        if len(failed_currencies) > 0:
            for instance in failed_currencies:
                self.stdout.write(f"- {instance.name}")
        else:
            self.stdout.write(f"- No currencies failed")

    def test_ticker_symbols(self):
        """
        Will test if currencies have ticker symbols.

        Will test some specific currencies, because I know in
        advance that some Kraken supported currencies should
        at leat have two symbols. Since Kraken has some of
        their own ticker symbols.
        """
        self.stdout.write(f"\n\n\n\n## Test Ticker Symbols ##\n")

        symbols_to_test = ['XBT', 'BTC', 'XDG', 'DOGE', 'FEE', 'YOYO', 'BQX']
        self.stdout.write(f"\n### Tested symbols: ###\n")
        self.stdout.write(f"{symbols_to_test}")

        existing_symbols = []
        non_existing_symbols = []
        for symbol in symbols_to_test:
            symbol_instance = None
            try:
                symbol_instance = TickerSymbol.objects.get(symbol=symbol)
            except TickerSymbol.DoesNotExist:
                pass

            if symbol_instance:
                existing_symbols.append(symbol)
            else:
                non_existing_symbols.append(symbol)

        self.display_test_ticker_symbols_results(
            existing_symbols, non_existing_symbols)

    def display_test_ticker_symbols_results(self, existing_symbols, non_existing_symbols):
        self.stdout.write(f"\n### Results: ###\n")

        if non_existing_symbols:
            self.stdout.write(f"\n### Test Failed ###\n")
            self.stdout.write(
                f"\n### The following symbols are not in the database: ###\n")
            for symbol in non_existing_symbols:
                self.stdout.write(f"- {symbol}")
        else:
            self.stdout.write(f"\n### Test Passed ###\n")
            self.stdout.write(
                f"\n### All tested symbols are in the database ###\n")

        self.stdout.write(f"\n### Symbols in database: ###\n")
        for symbol in existing_symbols:
            self.stdout.write(f"- {symbol}")
