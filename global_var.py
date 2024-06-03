import logging
_global_dict = {}


def init():
    global _global_dict
    _global_dict = {}


def set_value(key, value):
    _global_dict[key] = value


def get_value(key):
    try:
        return _global_dict[key]
    except KeyError as error:
        logging.error("Global value error: %s" % (error, ))
        return None
