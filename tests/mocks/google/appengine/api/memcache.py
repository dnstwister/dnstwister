""" Mock of memcache.
"""
import collections


__DATA = collections.defaultdict(lambda: None)


def set(key, value, _=0):
    """ Set value.
    """
    __DATA[key] = value


def get(key):
    """ Get value, or None.
    """
    return __DATA[key]


def reset():
    """ Reset the dict.
    """
    __DATA.clear()
