from cryptodata.models import CurrencyExchangePK


def determine_str_or_int(variable):
    """
    Determines if variable is str, int type or neither.

    Returns 'str' if str
    Returns 'int' if int
    Returns None if neither
    """
    if type(variable) is str:
        return 'str'
    elif type(variable) is int:
        return 'int'
    else:
        return None


def return_currency_instance_from_exchange_pk(exchange_pk):
    """
    Takes the pk (key) of an exchange for a currency,
    returns the currency instance.

    Returns None if none can be found
    """
    exchange_pk_instance = None
    try:
        exchange_pk_instance = CurrencyExchangePK.objects.get(key=exchange_pk)
    except CurrencyExchangePK.DoesNotExist:
        pass

    if exchange_pk_instance:
        return exchange_pk_instance.currency

    return None
