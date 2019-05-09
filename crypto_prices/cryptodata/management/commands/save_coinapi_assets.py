from django.core.management.base import BaseCommand

from cryptodata.management.commands.utils.save_coinapi_assets_utils import check_currency_exists, create_currency, create_ticker_symbol, fetch_coinapi_currency_data


class Command(BaseCommand):
    help = """
    Adds the currencies available at coinapi.io to the database.
    """

    def handle(self, *args, **kwargs):
        # Fetch coinapi data -> return in useful format
        currencies_data = fetch_coinapi_currency_data()
        for currency_data in currencies_data:
            if 'name' not in currency_data:
                continue
            # Add Currency instance to db
            if check_currency_exists(currency_data):
                continue
            currency_instance = create_currency(currency_data)

            # Add TickerSymbol instance to db
            create_ticker_symbol(currency_data, currency_instance)
