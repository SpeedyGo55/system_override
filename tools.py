def map_val(value, fromLow, fromHigh, toLow, toHigh):
    """
    :param value:
    :param fromLow:
    :param fromHigh:
    :param toLow:
    :param toHigh:
    :return:
    """
    return (value - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow
