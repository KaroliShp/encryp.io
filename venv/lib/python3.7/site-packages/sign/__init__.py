
"""
a simple package
"""


__version__ = '0.0.1'

import inspect


def inherit(target):

    def decorate(function):
        function.__signature__ = inspect.signature(target)
        return function

    return decorate
