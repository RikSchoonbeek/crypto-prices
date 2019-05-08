from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from cryptodata.models import TradingPair, TradingPairExchangePK

from ._utils import return_randomized_indexes_for_model


class Command(BaseCommand):
    help = """
    Tests if save_available_trading_pairs does what is should
    do.
    """

    def handle(self, *args, **options):
        self.stdout.write(
            f"\n# Test save_available_trading_pairs #\n")

        # Clear tables
        # self.empty_tables()
        # Call save_available_trading_pairs
        # self.run_save_available_trading_pairs()

        # Executes tests
        self.perform_tests()

    def empty_tables(self):
        """
        Empty the following tables:
        - TradingPair
        - TradingPairExchangePK
        """
        self.stdout.write(f"\n## Emptying tables - started ##")
        TradingPairExchangePK.objects.all().delete()
        TradingPair.objects.all().delete()
        self.stdout.write(f"\n## Emptying tables - finished ##")

    def run_save_available_trading_pairs(self):
        self.stdout.write(
            f"\n## run_save_available_trading_pairs - started ##")
        call_command('save_available_trading_pairs')
        self.stdout.write(
            f"\n## run_save_available_trading_pairs - finished ##")

    def perform_tests(self):
        # Test if each exchange has at least 5 TradingPair
        min_amount = 5
        self.test_min_amount_pairs_for_each_exchange(min_amount)

        # get pairs that have a related exchange
        instances_amount = 55 + (len(settings.EXCHANGES) * 15)
        pair_instances = self.get_pairs_with_exchange(
            instances_amount)
        # Test if each TradingPair has a TradingPairExchangePK
        # for each exchange in pair.exchanges
        self.test_pairs_exchange_pks_mirror_pair_exchanges(
            pair_instances)

    def test_min_amount_pairs_for_each_exchange(self, min_amount):
        """
        Tests if there are a certain minimum of pairs
        for each exchange.
        """
        self.stdout.write(
            f"\n## Test if min {min_amount} pairs for each exchange - started ##\n")

        pair_instances = TradingPair.objects.all()
        exchange_pair_count_dict = self.create_exchange_pair_count_dict()
        randomized_indexes = return_randomized_indexes_for_model(TradingPair)

        for index in randomized_indexes:
            pair_instance = pair_instances[index]
            exchange_pair_count_dict = self.update_exchange_count(
                pair_instance, exchange_pair_count_dict, min_amount)

            if self.check_all_exchanges_hit_min_amount(exchange_pair_count_dict):
                break

        self.display_min_min_amount_test_results(exchange_pair_count_dict)

    def create_exchange_pair_count_dict(self):
        count_dict = {}
        for exchange_name in settings.EXCHANGES:
            count_dict[exchange_name] = {
                'count': 0,
                'has_hit_minimum': False,
            }

        return count_dict

    def update_exchange_count(self, pair_instance, exchange_pair_count_dict, min_amount):
        """
        Takes a pair, the exchange_pair_count_dict, and a
        minimum amount of pairs that needs to be found for
        each exchange.

        Adds +1 to count of each exchange that is in the pair's
        exchanges (ManyToManyField).

        Also tests if the exchange has hit the min amount. If 
        so, the exchange's 'has_hit_minimum' is set to True.
        """
        exchange_set = pair_instance.exchanges.all()
        for exchange_instance in exchange_set:
            exchange_name = exchange_instance.name
            if exchange_name in exchange_pair_count_dict:
                current_count = exchange_pair_count_dict[exchange_name]['count']
                new_count = current_count + 1
                exchange_pair_count_dict[exchange_name]['count'] = new_count

                if new_count == min_amount:
                    exchange_pair_count_dict[exchange_name]['has_hit_minimum'] = True

        return exchange_pair_count_dict

    def check_all_exchanges_hit_min_amount(self, exchange_pair_count_dict):
        """
        Returns False if any of the exchanges hasn't hit min_amount yet,
        else returns True.
        """
        for exchange_name in exchange_pair_count_dict:
            if not exchange_pair_count_dict[exchange_name]['has_hit_minimum']:
                return False

        return True

    def display_min_min_amount_test_results(self, exchange_pair_count_dict):
        self.stdout.write(f"\n### Results: ###\n")
        for exchange_name in exchange_pair_count_dict:
            has_hit_minimum = exchange_pair_count_dict[exchange_name]['has_hit_minimum']
            self.stdout.write(
                f"- {exchange_name}: has_hit_minimum: {has_hit_minimum}")

    def get_pairs_with_exchange(self, amount):
        randomized_indexes = return_randomized_indexes_for_model(TradingPair)
        pair_instances = TradingPair.objects.all()

        filtered_pair_instances = []

        for index in randomized_indexes:
            pair_instance = pair_instances[index]
            exchange_count = pair_instance.exchanges.all().count()
            if exchange_count:
                filtered_pair_instances.append(pair_instance)
                if len(filtered_pair_instances) == amount:
                    return filtered_pair_instances

    def test_pairs_exchange_pks_mirror_pair_exchanges(self, pair_instances):
        """
        This method will test all given pair instances for 
        the following:

        If the TradingPair instance's TradingPairExchangePKs match
        the TradingPair's exchanges in a symmetrical way.

        Example to bring more clarity:

        If a TradingPair instance has the following related
        (ManyToMany) exchanges: 'Binance' and 'Kraken', then
        it should also have related TradingPairExchangePKs for
        both 'Binance' and 'Kraken'.

        But more specifically it should ONLY have
        TradingPairExchangePKs for 'Binance' and 'Kraken', no more
        and no less. Since those are the only two (ManyToMany)
        related exchanges of the TradingPair instance.
        """
        self.stdout.write(
            f"\n\n\n\n## test_pairs_exchange_pks_mirror_pair_exchanges - started ##\n")

        passed_pairs = []
        failed_pairs = []
        for pair_instance in pair_instances:
            pair_exchng_names = self.return_pair_exchng_names(
                pair_instance)
            pair_exchng_pks_exchng_names = self.return_pair_exchng_pks_exchng_names(
                pair_instance)
            if pair_exchng_names == pair_exchng_pks_exchng_names:
                passed_pairs.append(pair_instance)
            else:
                failed_pairs.append(pair_instance)

        self.display_exchange_pks_mirror_pair_exchanges_results(
            failed_pairs, passed_pairs)

    def return_pair_exchng_names(self, pair_instance):
        """
        Takes pair instance, returns list of names
        of the pair_instance.exchanges.
        """
        name_set = {exch.name for exch in pair_instance.exchanges.all()}
        return name_set

    def return_pair_exchng_pks_exchng_names(self, pair_instance):
        """
        Takes pair instance, returns list of names
        of exchanges of each related TradingPairExchangePK.exchange.
        """
        exchange_pks = pair_instance.tradingpairexchangepk_set.all()
        name_set = set()
        for exchange_pk in exchange_pks:
            name_set.add(exchange_pk.exchange.name)

        return name_set

    def display_exchange_pks_mirror_pair_exchanges_results(self, failed_pairs, passed_pairs):
        self.stdout.write(f"\n### Results: ###\n")

        self.stdout.write(f"\n### Passed: ###\n")
        if len(passed_pairs) > 0:
            for instance in passed_pairs:
                self.stdout.write(f"Pair: {instance}")
                exchanges = [exch.name for exch in instance.exchanges.all()]
                self.stdout.write(f"- Pair.exchanges: {exchanges}")
                epks_exchanges = [
                    exch_pk.exchange.name for exch_pk in instance.tradingpairexchangepk_set.all()]
                self.stdout.write(f"- Exch_pk_exchanges: {epks_exchanges}")

        else:
            self.stdout.write(f"- No pairs passed")

        self.stdout.write(f"\n### Failed: ###\n")
        if len(failed_pairs) > 0:
            for instance in failed_pairs:
                self.stdout.write(f"- {instance}")
                exchanges = [exch.name for exch in instance.exchanges.all()]
                self.stdout.write(f"- Pair.exchanges: {exchanges}")
                epks_exchanges = [
                    exch_pk.exchange.name for exch_pk in instance.tradingpairexchangepk_set.all()]
                self.stdout.write(f"- Exch_pk_exchanges: {epks_exchanges}")
        else:
            self.stdout.write(f"- No pairs failed")
