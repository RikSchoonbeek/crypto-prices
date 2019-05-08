import random

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


def return_currency_instance_from_exchange_pk(exchange_pk, exchange_instance):
    """
    Takes the pk (key) of an exchange for a currency,
    returns the currency instance.

    Returns None if none can be found
    """
    exchange_pk_instance = None
    try:
        exchange_pk_instance = CurrencyExchangePK.objects.get(
            exchange=exchange_instance, key=exchange_pk)
    except CurrencyExchangePK.DoesNotExist:
        pass

    if exchange_pk_instance:
        return exchange_pk_instance.currency

    return None


def return_randomized_indexes_for_model(model):
    model_instances = model.objects.all()
    model_instances_count = model_instances.count()

    random_indexes = random.sample(
        range(model_instances_count-1), model_instances_count-1)

    return random_indexes
