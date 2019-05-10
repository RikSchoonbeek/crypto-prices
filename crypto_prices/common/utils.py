def check_if_dict_in_list(pk_key, test_pk_value, list_):
    """
    Takes a list of dictionaries, and the key and value of the value
    that functions as the primary key for the dict. Checks if a dict 
    with that pk is already in the list.

    If so, returns True
    Else, returns false
    """
    for list_dict in list_:
        list_dict_pk_value = list_dict[pk_key]
        if list_dict_pk_value == test_pk_value:
            return True

    return False


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
