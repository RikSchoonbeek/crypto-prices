from django.test import TestCase

from cryptodata.management.commands.utils.save_coinapi_assets_utils import create_currency
from cryptodata.models import Currency


class SaveCoinAPIAssetsToDBTestCase(TestCase):
    def setUp(self):
        self.existing_currency_data = {
            "asset_id": "XSC",
            "name": "Existing coin",
        }
        self.existing_currency_instance = create_currency(
            self.existing_currency_data)

        self.none_existing_currency_data = {
            "asset_id": "NXC",
            "name": "None existing coin",
        }

    def test_create_currency(self):
        """
        Tests the create_currency function.

        Checks if this function actually adds a new 
        Currency instance to the database if one with
        the given data doesn't exist.

        Also tests if a previously existing instance is
        detected (returned by the function).
        """
        # Checks if this function actually adds a new
        # Currency instance to the database if one with
        # the given data doesn't exist.
        create_currency(self.none_existing_currency_data)

        non_existing_currency_name = self.none_existing_currency_data['name']
        non_existing_currency_symbol = self.none_existing_currency_data['asset_id']
        non_existing_currency_instance = None
        try:
            non_existing_currency_instance = Currency.objects.get(
                name=non_existing_currency_name,
                ticker_symbol=non_existing_currency_symbol)
        except Currency.DoesNotExist:
            pass

        self.assertTrue(isinstance(non_existing_currency_instance, Currency))
        self.assertEqual(non_existing_currency_name,
                         non_existing_currency_instance.name)
        self.assertEqual(non_existing_currency_symbol,
                         non_existing_currency_instance.ticker_symbol)

        # Also tests if a previously existing instance is
        # detected (returned by the function).
        existing_currency_name = self.existing_currency_data['name']
        existing_currency_symbol = self.existing_currency_data['asset_id']
        existing_currency_instance_id = self.existing_currency_instance.id
        returned_currency_instance = None
        try:
            returned_currency_instance = Currency.objects.get(
                name=existing_currency_name,
                ticker_symbol=existing_currency_symbol)
        except Currency.DoesNotExist:
            pass
        returned_currency_instance_id = returned_currency_instance.id

        self.assertEqual(existing_currency_instance_id,
                         returned_currency_instance_id)
