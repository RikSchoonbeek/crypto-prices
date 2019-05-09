from django.test import TestCase

from cryptodata.management.commands.utils.save_coinapi_assets_utils import check_currency_exists, create_currency, create_ticker_symbol
from cryptodata.models import Currency, TickerSymbol


class SaveCoinAPIAssetsToDBTestCase(TestCase):
    def setUp(self):
        self.currency_data = {
            "asset_id": "BTC",
            "name": "Bitcoin",
        }
        self.currency_instance = create_currency(self.currency_data)
        create_ticker_symbol(self.currency_data, self.currency_instance)

    def test_check_currency_exists(self):
        existing_currency_data = self.currency_data

        non_existing_currency_data = {
            "asset_id": "AAA",
            "name": "None Existing Coin Name",
        }

        existing_currency_exists = check_currency_exists(
            existing_currency_data)
        non_existing_currency_exists = check_currency_exists(
            non_existing_currency_data)

        self.assertTrue(existing_currency_exists)
        self.assertFalse(non_existing_currency_exists)

    def test_create_currency(self):
        """
        Tests the create_currency function.

        This means that it checks if this function actually adds a
        new Currency instance to the database.
        """
        currency_name = self.currency_data['name']
        db_instance = None
        try:
            db_instance = Currency.objects.get(name=currency_name)
        except Currency.DoesNotExist:
            pass

        self.assertIsNotNone(db_instance)
        self.assertEqual(db_instance.name, currency_name)

    def test_create_ticker_symbol(self):

        symbol = self.currency_data['asset_id']
        db_instance = None
        try:
            db_instance = TickerSymbol.objects.get(
                currency=self.currency_instance, symbol=symbol)
        except TickerSymbol.DoesNotExist:
            pass

        self.assertIsNotNone(db_instance)
        self.assertEqual(db_instance.symbol, symbol)
        self.assertEqual(db_instance.currency.id, self.currency_instance.id)
