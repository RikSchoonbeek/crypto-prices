import random
from unittest import TestCase

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from cryptodata.models import Currency, CurrencyExchangePK, Exchange, TickerSymbol


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

        # self.empty_tables()
        # self.run_save_coinapi_assets_to_db()
        # self.run_get_exchange_available_currencies()

        self.perform_tests()

    def empty_tables(self):
        """
        Empty all the cryptodata.models tables
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
        self.test_min_five_currencies_for_each_exchange()

        # get 10 currencies that have a related exchange
        instances_amount = 10
        currency_instances = self.get_currencies_with_exchange(
            instances_amount)
        # Test if each Currency has a CurrencyExchangePK
        self.test_currencies_have_exchange_pk(currency_instances)
        # And test if CurrencyExchangePK.exchange refers to this exchange

        # Test if this Currency has a TickerSymbol

    def test_min_five_currencies_for_each_exchange(self):
        self.stdout.write(
            f"\n### Test if min five currencies for each exchange - started ###\n")

        currency_instances = Currency.objects.all()

        exchange_currency_count_dict = self.create_exchange_currency_count_dict()
        randomized_indexes = self.return_randomized_indexes()

        for index in randomized_indexes:
            # Get currency at that index
            currency_instance = currency_instances[index]
            # Loop over currency exchanges, and add count for each
            # exchange
            exchange_currency_count_dict = self.update_exchange_count(
                currency_instance, exchange_currency_count_dict)

            # test if an exchange hits 5
            if self.check_all_exchanges_hit_five(exchange_currency_count_dict):
                break
            # if all exchanges hit 5: loop can be stopped

        self.display_min_five_test_results(exchange_currency_count_dict)
        # display results

    def return_randomized_indexes(self):
        currency_instances = Currency.objects.all()
        currency_instances_count = currency_instances.count()

        random_indexes = random.sample(
            range(currency_instances_count-1), currency_instances_count-1)

        return random_indexes

    def create_exchange_currency_count_dict(self):
        count_dict = {}
        for exchange_name in settings.EXCHANGES:
            count_dict[exchange_name] = {
                'count': 0,
                'has_hit_five': False,
            }

        return count_dict

    def update_exchange_count(self, currency_instance, exchange_currency_count_dict):
        """
        Takes a currency, and the exchange_currency_count_dict.

        Adds +1 to count of each exchange that is in the currency's
        exchanges (ManyToManyField).

        Also tests if the exchange has hit five. If so, the exchange's
        'has_hit_five' is set to True.
        """
        exchange_set = currency_instance.exchanges.all()
        for exchange_instance in exchange_set:
            exchange_name = exchange_instance.name
            if exchange_name in exchange_currency_count_dict:
                current_count = exchange_currency_count_dict[exchange_name]['count']
                new_count = current_count + 1
                exchange_currency_count_dict[exchange_name]['count'] = new_count

                if new_count == 5:
                    exchange_currency_count_dict[exchange_name]['has_hit_five'] = True

        return exchange_currency_count_dict

    def check_all_exchanges_hit_five(self, exchange_currency_count_dict):
        """
        Returns False if any of the exchanges hasn't hit five yet,
        else returns True.
        """
        for exchange_name in exchange_currency_count_dict:
            if not exchange_currency_count_dict[exchange_name]['has_hit_five']:
                return False

        return True

    def display_min_five_test_results(self, exchange_currency_count_dict):
        self.stdout.write(f"\n### Results: ###\n")
        for exchange_name in exchange_currency_count_dict:
            has_hit_five = exchange_currency_count_dict[exchange_name]['has_hit_five']
            self.stdout.write(
                f"- {exchange_name}: has_hit_five: {has_hit_five}")

    def get_currencies_with_exchange(self, amount):
        randomized_indexes = self.return_randomized_indexes()
        currency_instances = Currency.objects.all()

        filtered_currency_instances = []

        for index in randomized_indexes:
            currency_instance = currency_instances[index]
            exchange_count = currency_instance.exchanges.all().count()
            if exchange_count:
                filtered_currency_instances.append(currency_instance)
                if len(filtered_currency_instances) == amount:
                    return filtered_currency_instances

    def test_currencies_have_exchange_pk(self, currency_instances):
        """
        Returns True if all currency instances have a minimum of
        one related CurrencyExchangePK, else it returns False.
        """
        self.stdout.write(f"\n## Test Currencies have CurrencyExchangePK ##\n")
        for currency_instance in currency_instances:
            currency_exchange_pk_set = currency_instance.currencyexchangepk_set.all()
            currency_has_exchange_pk = bool(currency_exchange_pk_set)
            self.stdout.write(
                f"- currency: {currency_instance.name} has exchange pk: {currency_has_exchange_pk}")
            if not currency_has_exchange_pk:
                return False

        return True
